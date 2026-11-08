"""Prueba del OCNN: gradiente analítico vs numérico y convergencia."""
import sys
import numpy as np

sys.path.insert(0, "/home/user/planta-backend")
from app.servicios.ocnn import OCNN  # noqa: E402


def loss_fn(ocnn, x, p):
    for w, nw in zip(ocnn._params(), p):
        w[:] = nw
    rec = ocnn.forward(x)
    return float(np.mean((rec - x) ** 2))


def grad_numeric(ocnn, x, eps=1e-4):
    ocnn2 = OCNN(ocnn.n, seed=123)
    for w, nw in zip(ocnn2._params(), ocnn._params()):
        w[:] = nw
    p = [w.copy() for w in ocnn2._params()]
    out = [np.zeros_like(w) for w in p]
    for i, w in enumerate(p):
        for k in range(w.size):
            orig = w.flat[k]
            w.flat[k] = orig + eps
            lp = loss_fn(ocnn2, x, p)
            w.flat[k] = orig - eps
            lm = loss_fn(ocnn2, x, p)
            w.flat[k] = orig
            out[i].flat[k] = (lp - lm) / (2 * eps)
    return out


def main():
    rng = np.random.default_rng(1)
    ocnn = OCNN(6)
    x = rng.random((2, 6))
    # forward y backward analítico
    rec = ocnn.forward(x)
    grads = ocnn.backward(x, rec)
    # referencia: loss analítica
    loss = float(np.mean((rec - x) ** 2))
    # gradiente numérico
    gn = grad_numeric(ocnn, x)
    max_rel = 0.0
    for ga, gb in zip(grads, gn):
        denom = np.maximum(1e-8, np.maximum(np.abs(ga), np.abs(gb)))
        max_rel = max(max_rel, float(np.max(np.abs(ga - gb) / denom)))
    print(f"loss inicial: {loss:.4f}")
    print(f"gradiente: error relativo máximo = {max_rel:.2e}")
    assert max_rel < 1e-3, f"gradiente incorrecto: {max_rel}"

    # convergencia del entrenamiento
    ocnn2 = OCNN(8)
    M = 40
    data = np.concatenate([
        np.sin(np.linspace(0, 6, 8))[None, :] + 0.05 * rng.standard_normal((M, 8)),
    ])
    data = np.tile(np.sin(np.linspace(0, 6, 8))[None, :], (M, 1)) + 0.05 * rng.standard_normal((M, 8))
    data = (data - data.min()) / (data.max() - data.min() + 1e-9)
    hist = ocnn2.fit(data, epochs=600, lr=0.05)
    print(f"pérdida antes: {hist[0]:.4f} -> después: {hist[-1]:.6f}")
    assert hist[-1] < 0.02, "no converge"

    # score: anómala debe salir más alta que normal
    rng2 = np.random.default_rng(5)
    mu = float(np.mean((ocnn2.forward(data) - data) ** 2))
    sd = float(np.std((ocnn2.forward(data) - data) ** 2) + 1e-6)
    anta = np.tile(np.array([0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1])[None, :], (1, 1))
    sc_normal = ocnn2.score(data[:5], mu, sd)
    sc_anta = ocnn2.score(anta, mu, sd)
    print(f"score normal={sc_normal:.3f}  anómala={sc_anta:.3f}")
    assert sc_anta > sc_normal
    print("OCNN OK: gradiente verificado y converge")


if __name__ == "__main__":
    main()
