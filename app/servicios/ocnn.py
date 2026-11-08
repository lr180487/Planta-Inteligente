"""OCNN — One-Class CNN: autoencoder convolucional 1D en NumPy.

Patrones complejos: la red aprende a reconstruir ventanas temporales
normales (conv 1D -> ReLU -> maxpool -> dense -> reconstrucción).
Una ventana anómala se reconstruye mal; el error de reconstrucción
(comparado con el de las normales) es el score de anomalía.

Implementado a mano con backprop analítico (im2col + GEMM implícito),
sin frameworks de deep learning: solo NumPy.

Arquitectura (ventana N):
    Conv1(1->8, k=3) -> ReLU -> MaxPool(2)      (8, N/2)
    Conv2(8->4, k=3) -> ReLU                   (4, N/2)
    Dense(4*N/2 -> 16) -> ReLU
    Dense(16 -> N) -> Sigmoid                  reconstrucción
"""
from __future__ import annotations

import numpy as np


def _im2col(x: np.ndarray, k: int) -> np.ndarray:
    """x: (C, L) -> (C*k, L); fila (c*k + j) = canal c con desplazamiento j.

    El elemento (c, i, j) del patch i (x[i+j-1]) queda en la fila
    c*k + j, columna i. El orden (C, k, L) hace que el reshape sea exacto.
    """
    C, L = x.shape
    xp = np.pad(x, ((0, 0), (1, 1)))
    idx = np.arange(L)[:, None] + np.arange(k)[None, :]
    return xp[:, idx].transpose(0, 2, 1).reshape(C * k, L)


def _col2im(col: np.ndarray, k: int, shape: tuple) -> np.ndarray:
    """Inversa exacta de _im2col (acumulativa). col: (C*k, L) -> (C, L).

    _im2col lee po_pad[c, i + t] en la fila c*k + t, columna i; la inversa
    acumula en out[c, i + t] += col[c*k + t, i].
    """
    C, L = shape
    out = np.zeros((C, L + 2))
    idx = np.arange(L)[:, None] + np.arange(k)[None, :]
    tmp = col.reshape(C, k, L).transpose(0, 2, 1)  # (C, L, k)
    # np.add.at: los índices i+t se repiten, así que += no acumula
    np.add.at(out, (slice(None), idx), tmp)
    return out[:, 1:-1]


class OCNN:
    def __init__(self, n: int, seed: int = 7):
        rng = np.random.default_rng(seed)
        self.n = n
        self.h = n // 2
        self.W1 = rng.standard_normal((8, 3)) * np.sqrt(2 / 9)
        self.b1 = np.zeros(8)
        self.W2 = rng.standard_normal((4, 24)) * np.sqrt(2 / 24)
        self.b2 = np.zeros(4)
        self.W3 = rng.standard_normal((16, 4 * self.h)) * np.sqrt(2 / (4 * self.h))
        self.b3 = np.zeros(16)
        self.W4 = rng.standard_normal((n, 16)) * np.sqrt(1 / 16)
        self.b4 = np.zeros(n)
        self._ctx = {}

    def _params(self) -> list:
        return [self.W1, self.b1, self.W2, self.b2, self.W3, self.b3,
                self.W4, self.b4]

    # ------------------------------ forward ------------------------------
    def forward(self, x: np.ndarray):
        """x: (M, N) normalizado a [0,1]. devuelve reconstrucción (M, N)."""
        M, N = x.shape
        h = self.h
        W1, b1, W2, b2 = self.W1, self.b1, self.W2, self.b2
        W3, b3, W4, b4 = self.W3, self.b3, self.W4, self.b4
        x_col1, y1, r1, pool_idx, po1 = [], [], [], [], []
        x_col2, y2, r2 = [], [], []
        for m in range(M):
            c1 = _im2col(x[m][None, :], 3)          # (3, N)
            v1 = W1 @ c1 + b1[:, None]              # (8, N)
            r1m = np.maximum(v1, 0)
            a = r1m[:, 0::2]
            b = r1m[:, 1::2]
            po1.append(np.maximum(a, b))            # (8, h)
            pool_idx.append(np.where(a >= b, 0, 1))
            x_col1.append(c1)
            y1.append(v1)
            r1.append(r1m)
            c2 = _im2col(po1[m], 3)                 # (24, h)
            v2 = W2 @ c2 + b2[:, None]              # (4, h)
            r2.append(np.maximum(v2, 0))
            x_col2.append(c2)
            y2.append(v2)
        flat = np.stack([r2[m].ravel() for m in range(M)])  # (M, 4h)
        d3 = flat @ W3.T + b3
        r3 = np.maximum(d3, 0)
        z4 = r3 @ W4.T + b4
        rec = 1 / (1 + np.exp(-z4))
        self._ctx = {"x_col1": x_col1, "y1": y1, "r1": r1, "pool_idx": pool_idx,
                     "x_col2": x_col2, "y2": y2, "flat": flat, "d3": d3,
                     "r3": r3}
        return rec

    # ------------------------------ backward ------------------------------
    def backward(self, x: np.ndarray, rec: np.ndarray) -> list:
        """dL/dx = rec - x (MSE). devuelve lista de gradientes."""
        M, N = x.shape
        h = self.h
        W1, b1, W2, b2 = self.W1, self.b1, self.W2, self.b2
        W3, b3, W4, b4 = self.W3, self.b3, self.W4, self.b4
        ctx = self._ctx
        d4 = (rec - x) * rec * (1 - rec) * (2.0 / (M * N))  # derivada de la MSE media
        gW1, gb1 = np.zeros_like(W1), np.zeros_like(b1)
        gW2, gb2 = np.zeros_like(W2), np.zeros_like(b2)
        gW3, gb3 = np.zeros_like(W3), np.zeros_like(b3)
        gW4, gb4 = np.zeros_like(W4), np.zeros_like(b4)

        gW4 = d4.T @ ctx["r3"]                      # (N, 16)
        gb4 = d4.sum(axis=0)
        dr3 = d4 @ W4                               # (M, 16)
        d3 = dr3 * (ctx["d3"] > 0)
        gW3 = d3.T @ ctx["flat"]                    # (16, 4h)
        gb3 = d3.sum(axis=0)
        dflat = d3 @ W3                             # (M, 4h)

        for m in range(M):
            dy2 = dflat[m].reshape(4, h) * (ctx["y2"][m] > 0)   # (4, h)
            gW2 += dy2 @ ctx["x_col2"][m].T        # (4, 24)
            gb2 += dy2.sum(axis=1)
            dx_col2 = W2.T @ dy2                    # (24, h)
            dpo1 = _col2im(dx_col2, 3, (8, h))      # (8, h)
            # unpool (maxpool backward por índice)
            dr1 = np.zeros_like(ctx["r1"][m])       # (8, N)
            idx = ctx["pool_idx"][m]
            dr1[:, 0::2] = np.where(idx == 0, dpo1, 0)
            dr1[:, 1::2] = np.where(idx == 1, dpo1, 0)
            dy1 = dr1 * (ctx["y1"][m] > 0)
            gW1 += dy1 @ ctx["x_col1"][m].T         # (8, 3)
            gb1 += dy1.sum(axis=1)
            dx_col1 = W1.T @ dy1                    # (3, N)
            # d x[m] (no se usa más arriba, pero completa la chain)
            _col2im(dx_col1, 3, (1, N))

        return [gW1, gb1, gW2, gb2, gW3, gb3, gW4, gb4]

    # ------------------------------ entrenamiento ------------------------------
    def fit(self, x: np.ndarray, epochs: int = 350, lr: float = 0.03,
            momentum: float = 0.9) -> list:
        """Entrena sobre ventanas normales; devuelve la pérdida por epoch."""
        M, N = x.shape
        h = self.h
        W1, b1, W2, b2 = self.W1, self.b1, self.W2, self.b2
        W3, b3, W4, b4 = self.W3, self.b3, self.W4, self.b4
        p = [W1, b1, W2, b2, W3, b3, W4, b4]
        v = [np.zeros_like(w) for w in p]
        hist = []
        for _ in range(epochs):
            rec = self.forward(x)
            loss = float(np.mean((rec - x) ** 2))
            hist.append(loss)
            grads = self.backward(x, rec)
            for i, w in enumerate(p):
                v[i] = momentum * v[i] - lr * grads[i]
                w += v[i]
        return hist

    # ------------------------------ scoring ------------------------------
    def score(self, x: np.ndarray, err_normal: float, std_normal: float) -> float:
        """Error de reconstrucción normalizado: 0=normal, 1=anómalo."""
        rec = self.forward(x)
        err = float(np.mean((rec - x) ** 2))
        z = (err - err_normal) / max(std_normal, 1e-6)
        return float(np.clip(1 / (1 + np.exp(-1.5 * z)), 0.0, 1.0))
