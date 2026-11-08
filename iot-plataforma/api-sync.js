/* Sincronización frontend <-> backend FastAPI (mismo origen).
   Si la API no responde (p. ej. abriendo el HTML con otro servidor),
   la web sigue funcionando en modo local sin errores. */
(function () {
  var API = ''; // mismo origen: /api/...
  var enLinea = false;

  function avisar(msg) {
    if (typeof window.toast === 'function') { window.toast(msg); return; }
    var d = document.createElement('div');
    d.textContent = msg;
    d.style.cssText = 'position:fixed;bottom:22px;left:50%;transform:translateX(-50%);background:#111827;color:#fff;padding:12px 18px;border-radius:10px;z-index:400;font:600 .9rem system-ui';
    document.body.appendChild(d); setTimeout(function () { d.remove(); }, 3400);
  }

  function peticion(ruta, opciones) {
    var ctrl = new AbortController();
    var t = setTimeout(function () { ctrl.abort(); }, 3000);
    return fetch(API + ruta, Object.assign({ signal: ctrl.signal, headers: { 'Content-Type': 'application/json' } }, opciones || {}))
      .then(function (r) { clearTimeout(t); if (!r.ok) throw new Error(r.status); return r.json(); });
  }
  var get = function (r) { return peticion(r); };
  var post = function (r, cuerpo) { return peticion(r, { method: 'POST', body: JSON.stringify(cuerpo || {}) }); };

  window.PlantaAPI = { get: get, post: post, enLinea: function () { return enLinea; } };

  /* Indicador de estado en el encabezado */
  function pintarEstado() {
    var el = document.getElementById('apiStatus');
    if (!el) {
      var nav = document.querySelector('header .nav');
      if (!nav) return;
      el = document.createElement('span');
      el.id = 'apiStatus';
      el.style.cssText = 'font-size:.74rem;font-weight:700;padding:6px 10px;border-radius:99px;border:1px solid #dbeafe;background:#f8fafc;color:#64748b;white-space:nowrap';
      nav.appendChild(el);
    }
    el.textContent = enLinea ? '● Servidor conectado' : '● Modo local';
    el.style.color = enLinea ? '#047857' : '#64748b';
    el.style.background = enLinea ? '#ecfdf5' : '#f8fafc';
  }

  function salud() {
    return get('/api/salud').then(function () { enLinea = true; }).catch(function () { enLinea = false; })
      .then(pintarEstado);
  }

  /* Sincronizar dispositivos ESP32 guardados en este navegador (Campo) */
  var ultimaFirma = '';
  function sincronizarDispositivos() {
    if (!enLinea) return;
    var devs = [];
    try { devs = JSON.parse(localStorage.getItem('iot_devices') || '[]'); } catch (e) { }
    if (!Array.isArray(devs) || !devs.length) return;
    var firma = JSON.stringify(devs.map(function (d) { return [d.id, d.connected]; }));
    if (firma === ultimaFirma) return;
    ultimaFirma = firma;
    post('/api/dispositivos/sincronizar', {
      dispositivos: devs.map(function (d) {
        return { chip_id: d.id, nombre: d.name || '', tipo: d.type || '', wifi: d.wifi || '', conectado: !!d.connected };
      })
    }).catch(function () { });
  }

  /* Detectar si alguien conectó un ESP32 nuevo */
  function vigilarEsp32() {
    if (!enLinea) return;
    get('/api/esp32/conectados').then(function (r) {
      var actuales = (r.conectados || []).map(function (d) { return d.chip_id; });
      var conocidos = null;
      try { conocidos = JSON.parse(localStorage.getItem('iot_esp32_conocidos') || 'null'); } catch (e) { }
      if (Array.isArray(conocidos)) {
        (r.conectados || []).forEach(function (d) {
          if (conocidos.indexOf(d.chip_id) < 0) {
            avisar('📡 Se detectó un ESP32 conectado: ' + (d.nombre || d.chip_id) + ' (' + d.chip_id + ')');
          }
        });
      }
      try { localStorage.setItem('iot_esp32_conocidos', JSON.stringify(actuales)); } catch (e) { }
    }).catch(function () { });
  }

  document.addEventListener('DOMContentLoaded', function () {
    salud().then(function () { sincronizarDispositivos(); vigilarEsp32(); });
    setInterval(salud, 20000);
    setInterval(sincronizarDispositivos, 8000);
    setInterval(vigilarEsp32, 10000);
  });
})();
