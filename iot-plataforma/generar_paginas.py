#!/usr/bin/env python3
"""Genera el sistema multipágina: una página independiente por opción."""
import pathlib
OUT = pathlib.Path('/home/user/iot-plataforma')

CSS = """
:root{--bg:#f4f7fb;--card:#fff;--line:#dbe5ef;--text:#0f2237;--muted:#5b7186;--blue:#0284c7;--blue2:#2563eb;--green:#059669;--amber:#d97706;--red:#e11d48;--violet:#7c3aed;--radius:18px;--shadow:0 8px 28px rgba(15,44,74,.06)}
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:radial-gradient(900px 500px at 90% -10%,rgba(2,132,199,.10),transparent 60%),var(--bg);color:var(--text);line-height:1.55}
button,input{font:inherit}
header{position:sticky;top:0;z-index:40;background:rgba(255,255,255,.93);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.nav{max-width:1240px;margin:auto;padding:12px 20px;display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}
.logo{display:flex;align-items:center;gap:11px;font-weight:900;color:var(--text);text-decoration:none}
.logo-mark{width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,var(--blue),var(--violet));display:grid;place-items:center;color:#fff;font-size:1.2rem}
.logo small{display:block;font-weight:600;color:var(--muted);font-size:.72rem}
.nav nav{display:flex;gap:5px;flex-wrap:wrap}.nav nav a{font-size:.85rem;color:var(--muted);font-weight:600;padding:8px 11px;border-radius:99px;text-decoration:none}
.nav nav a:hover{background:#eaf2fd;color:var(--blue)}.nav nav a.active{background:linear-gradient(135deg,var(--blue),var(--blue2));color:#fff}
.pill{display:inline-flex;align-items:center;gap:7px;font-size:.8rem;font-weight:700;padding:7px 12px;border-radius:99px;border:1px solid var(--line);background:#fff}
.dot{width:9px;height:9px;border-radius:50%;background:var(--green);box-shadow:0 0 0 4px rgba(5,150,105,.15)}
.wrap{max-width:1240px;margin:auto;padding:30px 20px 60px}
.kicker{color:var(--blue);font-weight:800;letter-spacing:.13em;text-transform:uppercase;font-size:.75rem}
h1{font-size:clamp(1.8rem,4vw,2.8rem);letter-spacing:-.02em;line-height:1.1;margin:8px 0 10px}
.grad{background:linear-gradient(90deg,var(--blue),var(--violet));-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--muted);max-width:840px}
.btn{display:inline-flex;align-items:center;gap:8px;padding:11px 16px;border-radius:999px;font-weight:700;border:1px solid var(--line);background:#fff;color:var(--text);cursor:pointer;box-shadow:0 2px 10px rgba(15,44,74,.05);text-decoration:none;transition:.15s}
.btn:hover{transform:translateY(-1px)}.btn.primary{background:linear-gradient(135deg,var(--blue),var(--blue2));color:#fff;border:none}
.btn.danger{background:#fff1f2;border-color:#fecdd3;color:#9f1239}.btn.danger.on{background:var(--red);color:#fff}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow)}
.card h2{font-size:1.15rem;margin-bottom:6px}.card h3{font-size:1.02rem;margin-bottom:8px}.card p,.card li{color:var(--muted)}.card ul{padding-left:18px}.card li{margin:6px 0}
.grid{display:grid;grid-template-columns:1.5fr .95fr;gap:18px;margin-top:18px}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:18px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0}.kpi{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:18px;box-shadow:var(--shadow)}
.kpi span{color:var(--muted);font-size:.8rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em}.kpi b{font-size:1.8rem;display:block;margin:4px 0 2px}.kpi small{color:var(--muted)}.kpi.alert{border-color:#fda4af;background:#fff7f8}
canvas.chart{width:100%;height:290px;display:block;background:#f8fbff;border:1px solid var(--line);border-radius:14px}
.metric{display:flex;justify-content:space-between;gap:10px;padding:11px 0;border-bottom:1px solid var(--line)}.metric:last-child{border:none}.metric span{color:var(--muted)}.metric b{text-align:right}
.badge{font-size:.74rem;font-weight:800;padding:4px 9px;border-radius:99px}.b-ok{background:#dcfce7;color:#166534}.b-warn{background:#fef3c7;color:#92400e}.b-bad{background:#ffe4e6;color:#9f1239}.b-info{background:#e0f2fe;color:#075985}.b-violet{background:#ede9fe;color:#5b21b6}
.alarmbox{margin-top:14px;padding:13px 14px;border-radius:13px;background:#fffbeb;border:1px solid #fde68a;color:#92400e;font-size:.9rem}.alarmbox.bad{background:#fff1f2;border-color:#fda4af;color:#9f1239}
table{width:100%;border-collapse:collapse;font-size:.88rem}th,td{padding:10px 11px;border-bottom:1px solid var(--line);text-align:left}th{background:#e8f2fd;color:#0c4a6e}td{color:var(--muted)}td b{color:var(--text)}
.scrollbox{max-height:320px;overflow:auto;border:1px solid var(--line);border-radius:13px}
pre{background:#0f2237;color:#e6f0fa;padding:16px;border-radius:13px;overflow:auto;font-size:.8rem;line-height:1.55}
.log{font-family:Consolas,Menlo,monospace;font-size:.78rem;background:#0f2237;color:#dbeafe;border-radius:13px;padding:15px;height:260px;overflow:auto;line-height:1.65}
.log .t{color:#7dd3fc}.log .ok{color:#86efac}.log .warn{color:#fde68a}.log .err{color:#fda4af}
.tabs{display:flex;gap:7px;flex-wrap:wrap}.tab{border:1px solid var(--line);background:#fff;color:var(--muted);padding:7px 12px;border-radius:99px;cursor:pointer;font-weight:700;font-size:.82rem}.tab.active{background:var(--blue);color:#fff;border-color:transparent}
.switch{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid var(--line)}
.sw{width:52px;height:29px;border-radius:99px;background:#cbd5e1;border:none;cursor:pointer;position:relative;flex:none;transition:.2s}.sw::after{content:"";position:absolute;top:3px;left:3px;width:23px;height:23px;border-radius:50%;background:#fff;transition:.2s}.sw.on{background:var(--green)}.sw.on::after{left:26px}
input[type=range]{width:100%;accent-color:var(--blue)}input[type=text],input[type=number]{padding:11px 13px;border:1px solid var(--line);border-radius:12px;background:#fff;color:var(--text)}
.agent{display:flex;gap:12px;padding:12px;border:1px solid var(--line);border-radius:13px;margin:9px 0;background:#f8fbff}.agent .ico{font-size:1.4rem}.agent b{display:block}.agent p{font-size:.88rem;color:var(--muted)}.agent.active{border-color:#7dd3fc;background:#f0f9ff}.agent.done{border-color:#bbf7d0;background:#f7fef9}
.chat{display:flex;flex-direction:column;gap:10px;margin-top:12px;max-height:340px;overflow:auto}.msg{padding:12px 14px;border-radius:14px;font-size:.92rem;max-width:92%}.msg.user{align-self:flex-end;background:#e0f2fe;color:#0c4a6e}.msg.ia{align-self:flex-start;background:#f1f5f9;border:1px solid var(--line)}
.cards-nav{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:20px}.mod-card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow);text-decoration:none;color:var(--text);transition:.2s;display:block}.mod-card:hover{transform:translateY(-4px);border-color:#7dd3fc}.mod-card .ico{font-size:2rem}.mod-card p{color:var(--muted);font-size:.92rem;margin:6px 0 12px}.mod-card b.go{color:var(--blue)}
.pager{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-top:28px}
footer{border-top:1px solid var(--line);background:#fff}footer .wrap{padding-top:24px;padding-bottom:32px;color:var(--muted)}
#loader{position:fixed;inset:0;z-index:999;background:linear-gradient(180deg,#fff,#eef4fb);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;transition:opacity .6s,visibility .6s}
#loader.hide{opacity:0;visibility:hidden}
.loader-logo-wrap{position:relative;width:170px;height:170px;display:grid;place-items:center}
.loader-ring{position:absolute;inset:0;border-radius:50%;border:5px solid #dbeafe;border-top-color:var(--blue);border-right-color:var(--violet);animation:spin 1s linear infinite}
.loader-ring.r2{inset:14px;border-width:3px;border-bottom-color:var(--green);border-top-color:transparent;animation:spinRev 1.6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}@keyframes spinRev{to{transform:rotate(-360deg)}}
.loader-logo{width:104px;height:104px;border-radius:28px;background:linear-gradient(135deg,var(--blue),var(--blue2) 55%,var(--violet));display:grid;place-items:center;font-size:3rem;color:#fff;box-shadow:0 18px 40px rgba(37,99,235,.35);animation:pulse 1.4s ease-in-out infinite}
@keyframes pulse{50%{transform:scale(1.06)}}
.loader-bar{width:min(340px,80vw);height:9px;background:#e2e8f0;border-radius:99px;overflow:hidden}.loader-bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--blue),var(--green),var(--violet))}
.loader-steps{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;max-width:540px;padding:0 16px}.loader-steps span{font-size:.75rem;font-weight:700;padding:5px 10px;border-radius:99px;background:#fff;border:1px solid var(--line);color:var(--muted)}.loader-steps span.on{background:#e0f2fe;color:#075985}.loader-steps span.done{background:#dcfce7;color:#166534}
.toast{position:fixed;right:18px;bottom:18px;z-index:80;background:#0f2237;color:#fff;padding:13px 17px;border-radius:13px;opacity:0;transform:translateY(10px);transition:.3s;max-width:min(420px,90vw);font-size:.9rem}.toast.show{opacity:1;transform:none}
@media(max-width:950px){.kpis,.cards-nav{grid-template-columns:repeat(2,1fr)}.grid,.grid2,.grid3{grid-template-columns:1fr}.nav nav{display:none}}
"""

PAGES = [
    ("index", "🏠 Panel", "Panel general"),
    ("campo", "🌡️ Campo e IoT", "Módulo 1 · Campo e IoT"),
    ("automatizacion", "🏭 Automatización", "Módulo 2 · Automatización"),
    ("integracion", "🔀 Integración IoT", "Módulo 3 · Integración IoT"),
    ("backend", "🗄️ Backend", "Módulo 4 · Backend"),
    ("ia", "🤖 Inteligencia Artificial", "Módulo 5 · Inteligencia Artificial"),
    ("presentacion", "📊 Presentación", "Módulo 6 · Presentación"),
]

def header(active):
    links = "".join(
        f'<a href="{slug}.html" class="{"active" if slug==active else ""}">{label}</a>'
        for slug, label, _ in PAGES)
    return f"""<header><div class="nav">
    <a class="logo" href="index.html"><span class="logo-mark">⚙️</span><span>Campo → IA<small>Sistema IoT Industrial · multipágina</small></span></a>
    <nav>{links}</nav>
    <span class="pill"><span class="dot"></span><span class="clock">En línea</span></span>
    </div></header>"""

def footer(active):
    i = [p[0] for p in PAGES].index(active)
    prev = PAGES[i-1] if i > 0 else None
    nxt = PAGES[i+1] if i < len(PAGES)-1 else None
    pager = '<div class="pager">'
    pager += f'<a class="btn" href="{prev[0]}.html">← {prev[1]}</a>' if prev else '<span></span>'
    pager += f'<a class="btn primary" href="{nxt[0]}.html">{nxt[1]} →</a>' if nxt else '<a class="btn" href="index.html">← Volver al Panel</a>'
    pager += '</div>'
    return f"""{pager}<footer><div class="wrap"><b style="color:var(--text)">Campo → IA</b> · Cada opción vive en su propia página · ESP32 · OpenPLC · Modbus TCP/IP · Node-RED · FastAPI · PostgreSQL · LangGraph · Chart.js</div></footer>
    <div class="toast" id="toast"></div>"""

COMMON_JS = """
const $=id=>document.getElementById(id);
const fmt=(n,d=1)=>Number(n).toFixed(d);
function toast(m){const t=$('toast');if(!t)return;t.textContent=m;t.classList.add('show');clearTimeout(t._h);t._h=setTimeout(()=>t.classList.remove('show'),3200)}
function now(){return new Date().toLocaleTimeString('es-PE',{hour12:false})}
setInterval(()=>document.querySelectorAll('.clock').forEach(e=>e.textContent='En línea · '+now()),1000);
function log(el,type,msg){if(!el)return;const d=document.createElement('div');d.innerHTML=`<span class="t">[${now()}]</span> <span class="${type}">●</span> ${msg}`;el.appendChild(d);el.scrollTop=el.scrollHeight;while(el.children.length>90)el.removeChild(el.firstChild)}
function drawLine(cv,data,color,thr,thrLabel){
  const ctx=cv.getContext('2d'),w=cv.width,h=cv.height,p=30;ctx.clearRect(0,0,w,h);
  ctx.strokeStyle='rgba(71,111,145,.22)';ctx.beginPath();ctx.moveTo(p,8);ctx.lineTo(p,h-p);ctx.lineTo(w-8,h-p);ctx.stroke();
  if(thr!=null){const y=h-p-(thr/110)*(h-2*p);ctx.strokeStyle='rgba(225,29,72,.65)';ctx.setLineDash([6,5]);ctx.beginPath();ctx.moveTo(p,y);ctx.lineTo(w-8,y);ctx.stroke();ctx.setLineDash([]);ctx.fillStyle='#be123c';ctx.font='12px system-ui';ctx.fillText(thrLabel||'Umbral',w-110,y-7)}
  if(data.length<2)return;const max=Math.max(110,...data)*1.05;
  const g=ctx.createLinearGradient(0,0,0,h);g.addColorStop(0,color+'44');g.addColorStop(1,color+'00');
  ctx.beginPath();data.forEach((v,i)=>{const x=p+i/55*(w-p-14),y=h-p-(v/max)*(h-2*p);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});
  ctx.strokeStyle=color;ctx.lineWidth=2.5;ctx.stroke();ctx.lineTo(p+(data.length-1)/55*(w-p-14),h-p);ctx.lineTo(p,h-p);ctx.closePath();ctx.fillStyle=g;ctx.fill();
}
"""

def page(slug, title, body, extra_js="", loader=False):
    loader_html = """
<div id="loader"><div class="loader-logo-wrap"><div class="loader-ring"></div><div class="loader-ring r2"></div><div class="loader-logo">⚙️</div></div>
<h1 style="font-size:1.7rem">Campo <span class="grad">→ IA</span></h1><p id="loadMsg" style="color:var(--muted)">Iniciando sistema…</p>
<div class="loader-bar"><i id="loadBar"></i></div><div id="loadPct" style="font-weight:800;color:var(--blue)">0%</div>
<div class="loader-steps" id="loadSteps"><span>🌡️ ESP32</span><span>🏭 OpenPLC</span><span>🔀 Node-RED</span><span>🗄️ Backend</span><span>🤖 IA</span><span>📊 Interfaz</span></div></div>
<script>(function(){const msgs=["Iniciando sistema…","Conectando sensores ESP32…","Sincronizando OpenPLC…","Cargando Node-RED…","Conectando FastAPI y PostgreSQL…","Preparando agentes LangGraph…","Renderizando interfaz…"];const steps=[...document.querySelectorAll('#loadSteps span')];const t0=Date.now(),D=5000;(function tick(){const el=Math.min(Date.now()-t0,D),p=Math.floor(el/D*100);loadBar.style.width=p+'%';loadPct.textContent=p+'%';loadMsg.textContent=msgs[Math.min(Math.floor(el/D*msgs.length),msgs.length-1)];steps.forEach((s,i)=>{const th=(i+1)/steps.length*100;s.className=p>=th?'done':(p>=th-16?'on':'')});if(el<D)requestAnimationFrame(tick);else setTimeout(()=>loader.classList.add('hide'),250)})()})();</script>
""" if loader else ""
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · Campo → IA</title><style>{CSS}</style></head><body>
{loader_html}{header(slug)}<main class="wrap">{body}</main>{footer(slug)}
<script>{COMMON_JS}{extra_js}</script></body></html>"""

# ---------- INDEX / PANEL ----------
index_body = """
<div class="kicker">Panel general · Página independiente</div>
<h1>Del sensor en campo a la <span class="grad">inteligencia artificial</span>.</h1>
<p class="sub">Sistema completo en <b>7 páginas independientes</b> (modo claro profesional). Cada opción del menú abre su propia página con su demo funcional. El loader de 5 segundos con spinner alrededor del logo se mantiene en esta portada.</p>
<div class="actions"><button class="btn primary" id="btnToggle">⏸ Pausar adquisición</button><button class="btn" id="btnSpike">⚠ Forzar pico térmico</button><button class="btn danger" id="btnEmergency">🛑 Parada de emergencia</button></div>
<div class="kpis">
 <div class="kpi" id="kpiTempCard"><span>Temperatura</span><b id="kTemp">—</b><small>ESP32 · tanque 01</small></div>
 <div class="kpi"><span>Humedad</span><b id="kHum">—</b><small>Ambiente de planta</small></div>
 <div class="kpi"><span>Nivel</span><b id="kLevel">—</b><small>Control PLC</small></div>
 <div class="kpi"><span>Alarmas</span><b id="kAlarms">0</b><small>Umbral: 80 °C</small></div>
</div>
<div class="grid"><div class="card"><h2>📈 Temperatura en tiempo real</h2><canvas class="chart" id="chart" width="720" height="290"></canvas><div class="alarmbox" id="alarmBox">✅ Sistema normal</div></div>
<div class="card"><h2>Estado del proceso</h2>
<div class="metric"><span>Promedio</span><b id="mAvg">—</b></div><div class="metric"><span>Máximo</span><b id="mMax">—</b></div>
<div class="metric"><span>Bomba (PLC)</span><b id="mPump">—</b></div><div class="metric"><span>Lecturas</span><b id="mCount">0</b></div>
<div class="metric"><span>Reintentos Node-RED</span><b id="mRetries">0</b></div></div></div>
<h2 style="margin-top:30px">Ir a cada módulo (página independiente)</h2>
<div class="cards-nav">
 <a class="mod-card" href="campo.html"><span class="ico">🌡️</span><h3>1 · Campo e IoT</h3><p>Sensores → ESP32: adquisición, filtrado y calibración en vivo.</p><b class="go">Abrir página →</b></a>
 <a class="mod-card" href="automatizacion.html"><span class="ico">🏭</span><h3>2 · Automatización industrial</h3><p>OpenPLC, Modbus TCP/IP, histéresis y enclavamientos.</p><b class="go">Abrir página →</b></a>
 <a class="mod-card" href="integracion.html"><span class="ico">🔀</span><h3>3 · Integración IoT</h3><p>Node-RED: transformación, reintentos y alarmas.</p><b class="go">Abrir página →</b></a>
 <a class="mod-card" href="backend.html"><span class="ico">🗄️</span><h3>4 · Backend y persistencia</h3><p>FastAPI, Pydantic, SQLAlchemy y PostgreSQL.</p><b class="go">Abrir página →</b></a>
 <a class="mod-card" href="ia.html"><span class="ico">🤖</span><h3>5 · Inteligencia artificial</h3><p>LangGraph: Analyzer, Processor, Responder y Verifier.</p><b class="go">Abrir página →</b></a>
 <a class="mod-card" href="presentacion.html"><span class="ico">📊</span><h3>6 · Presentación</h3><p>HTML, JavaScript, Tailwind CSS y Chart.js.</p><b class="go">Abrir página →</b></a>
</div>"""
index_js = """
const S={run:true,em:false,spike:0,t:0,temp:52,hum:48,level:62,pump:false,alarm:false,data:[],max:-Infinity,n:0,ret:0};
function tick(){if(!S.run)return;S.t++;let v=52+Math.sin(S.t/9)*9+Math.sin(S.t/3.7)*3+(Math.random()*3-1.5);if(S.spike>0){v+=27;S.spike--}if(S.em)S.temp=Math.max(24,v-2);else S.temp=v;
S.hum=Math.max(20,Math.min(95,52+Math.sin(S.t/14)*10));S.level=Math.max(5,Math.min(98,S.level+(S.pump?-.4:.55)));
if(S.em)S.pump=false;else{if(S.temp>80)S.pump=true;else if(S.temp<74)S.pump=false}
S.alarm=S.temp>80&&!S.em;S.max=Math.max(S.max,S.temp);S.n++;if(Math.random()<.1)S.ret++;
S.data.push(S.temp);if(S.data.length>56)S.data.shift();
kTemp.textContent=fmt(S.temp)+' °C';kHum.textContent=fmt(S.hum,0)+' %';kLevel.textContent=fmt(S.level,0)+' %';kAlarms.textContent=S.alarm?1:0;
kpiTempCard.classList.toggle('alert',S.alarm);
const avg=S.data.reduce((a,b)=>a+b,0)/S.data.length;mAvg.textContent=fmt(avg)+' °C';mMax.textContent=fmt(S.max)+' °C';
mPump.innerHTML=S.em?'<span class="badge b-bad">DETENIDA</span>':S.pump?'<span class="badge b-warn">ENCENDIDA</span>':'<span class="badge b-ok">APAGADA</span>';
mCount.textContent=S.n;mRetries.textContent=S.ret;
alarmBox.className='alarmbox'+(S.alarm||S.em?' bad':'');alarmBox.textContent=S.em?'🛑 Emergencia activa · estado seguro':S.alarm?'🚨 Alarma crítica > 80 °C · PLC activó enfriamiento':'✅ Sistema normal · Umbral 80 °C';
drawLine(chart,S.data,S.alarm?'#e11d48':'#0284c7',80,'Umbral 80 °C')}
setInterval(tick,800);for(let i=0;i<26;i++)tick();
btnToggle.onclick=e=>{S.run=!S.run;e.target.textContent=S.run?'⏸ Pausar adquisición':'▶ Reanudar adquisición'};
btnSpike.onclick=()=>{S.spike=9;toast('⚠ Pico térmico forzado')};
btnEmergency.onclick=e=>{S.em=!S.em;e.target.classList.toggle('on',S.em);e.target.textContent=S.em?'▶ Restablecer sistema':'🛑 Parada de emergencia';toast(S.em?'🛑 Emergencia activada':'✅ Sistema restablecido')};
"""

# ---------- CAMPO ----------
campo_body = """
<div class="kicker">Módulo 01 · Página independiente</div><h1>🌡️ Campo e <span class="grad">IoT</span></h1>
<p class="sub">Sensores → ESP32 → adquisición y calibración. Ajusta offset y ganancia y observa cómo cambian la lectura cruda, la calibrada y la trama publicada.</p>
<div class="grid"><div class="card"><h2>Lectura en vivo (calibrada)</h2><canvas class="chart" id="chart" width="720" height="290"></canvas>
<div class="grid2" style="margin-top:14px"><div class="metric"><span>Valor crudo (ADC)</span><b id="mRaw">—</b></div><div class="metric"><span>Valor calibrado</span><b id="mCal">—</b></div></div></div>
<div class="card"><h2>Calibración de dos puntos</h2>
<label><b>Offset:</b> <span id="offVal">0.0 °C</span></label><input type="range" id="off" min="-5" max="5" step="0.1" value="0">
<label style="display:block;margin-top:14px"><b>Ganancia:</b> <span id="gainVal">1.000</span></label><input type="range" id="gain" min="0.90" max="1.10" step="0.005" value="1">
<div class="metric"><span>Dispositivo</span><b>esp32-tanque-01</b></div><div class="metric"><span>Filtro</span><b>Mediana (5 muestras)</b></div>
<div class="metric"><span>Calidad</span><b id="mQ"><span class="badge b-ok">BUENA</span></b></div>
<h3 style="margin-top:14px">Trama publicada (MQTT → Node-RED)</h3>
<pre id="jsonBox">{}</pre></div></div>
<div class="grid3"><div class="card"><h3>🔌 Sensores típicos</h3><ul><li>Temperatura / humedad (SHT31, DS18B20)</li><li>Presión y nivel (4–20 mA, ultrasónico)</li><li>Caudal y vibración para mantenimiento predictivo</li></ul></div>
<div class="card"><h3>🛡 Robustez en campo</h3><ul><li>Watchdog y reconexión Wi-Fi automática</li><li>Buffer local ante cortes y reenvío</li><li>Detección de sensor desconectado o congelado</li></ul></div>
<div class="card"><h3>💻 Firmware (extracto)</h3><pre>float t = medianFilter(readRaw());
t = (t + OFFSET) * GAIN;
if (t < -20 || t > 120)
  publishAlarm("OUT_OF_RANGE");</pre></div></div>"""
campo_js = """
let off=0,gain=1,t=0;const data=[];
function tick(){t++;const raw=52+Math.sin(t/9)*9+Math.sin(t/3.7)*3+(Math.random()*3-1.5);const cal=(raw+off)*gain;
data.push(cal);if(data.length>56)data.shift();mRaw.textContent=fmt(raw)+' °C';mCal.textContent=fmt(cal)+' °C';
const bad=cal<-20||cal>120;mQ.innerHTML=bad?'<span class="badge b-bad">FUERA DE RANGO</span>':'<span class="badge b-ok">BUENA</span>';
jsonBox.textContent=JSON.stringify({device_id:'esp32-tanque-01',temperature_c:+fmt(cal,2),raw_c:+fmt(raw,2),cal_offset:off,cal_gain:gain,quality:bad?'bad':'good',ts:new Date().toISOString()},null,2);
drawLine(chart,data,'#0284c7',80,'Umbral 80 °C')}
offEl=$('off'),gainEl=$('gain');
offEl.oninput=e=>{off=parseFloat(e.target.value);offVal.textContent=fmt(off)+' °C';toast('Calibración: offset '+fmt(off)+' °C')};
gainEl.oninput=e=>{gain=parseFloat(e.target.value);gainVal.textContent=gain.toFixed(3)};
setInterval(tick,800);for(let i=0;i<26;i++)tick();
"""

# ---------- AUTOMATIZACION ----------
auto_body = """
<div class="kicker">Módulo 02 · Página independiente</div><h1>🏭 Automatización <span class="grad">industrial</span></h1>
<p class="sub">OpenPLC · Modbus TCP/IP · lógica de control. El control crítico y la seguridad viven en el PLC: si cae la web o internet, el proceso sigue protegido.</p>
<div class="actions"><button class="btn" id="btnSpike">⚠ Forzar pico térmico</button><button class="btn danger" id="btnEm">🛑 Parada de emergencia</button></div>
<div class="grid"><div class="card"><h2>Proceso: temperatura y nivel</h2><canvas class="chart" id="chart" width="720" height="290"></canvas><div class="alarmbox" id="alarmBox">✅ Normal</div></div>
<div class="card"><h2>Lógica de control</h2>
<div class="switch"><span><b>Modo automático</b><br><small style="color:var(--muted)">Histéresis: ON &gt; 80 °C · OFF &lt; 74 °C</small></span><button class="sw on" id="swAuto"></button></div>
<div class="switch"><span><b>Bomba manual</b><br><small style="color:var(--muted)">Solo en modo manual</small></span><button class="sw" id="swPump"></button></div>
<div class="metric"><span>Temperatura</span><b id="mTemp">—</b></div><div class="metric"><span>Nivel</span><b id="mLevel">—</b></div>
<h3 style="margin-top:14px">Mapa Modbus TCP/IP en vivo</h3>
<div class="metric"><span>Holding 40001 · Nivel ×100</span><b id="rLevel">—</b></div>
<div class="metric"><span>Coil 00001 · Bomba</span><b id="rPump">0</b></div>
<div class="metric"><span>Coil 00002 · Alarma crítica</span><b id="rAlarm">0</b></div>
<div class="metric"><span>Scan PLC</span><b>10 ms · estable</b></div></div></div>
<div class="card" style="margin-top:18px"><h2>Programa OpenPLC (Texto Estructurado)</h2><pre>(* Histéresis + enclavamiento de seguridad *)
IF Temp &gt; 80.0 AND NOT Parada_Emergencia THEN Bomba := TRUE;
ELSIF Temp &lt; 74.0 THEN Bomba := FALSE; END_IF;

IF Sobrepresion OR Parada_Emergencia THEN
    Bomba := FALSE; Valvula := FALSE; Alarma_Critica := TRUE;
END_IF;
MB_Nivel := REAL_TO_INT(Nivel * 100.0);  (* Modbus 40001 *)</pre></div>"""
auto_js = """
let t=0,auto=true,man=false,em=false,spike=0,pump=false;const data=[];let temp=52,level=62;
function tick(){t++;temp=52+Math.sin(t/9)*9+(Math.random()*3-1.5);if(spike>0){temp+=27;spike--}level=Math.max(5,Math.min(98,level+(pump?-.4:.55)));
if(em)pump=false;else if(auto){if(temp>80)pump=true;else if(temp<74)pump=false}else pump=man;
const al=temp>80&&!em;data.push(temp);if(data.length>56)data.shift();
mTemp.textContent=fmt(temp)+' °C';mLevel.textContent=fmt(level,0)+' %';rLevel.textContent=Math.round(level*100);rPump.textContent=pump?1:0;rAlarm.textContent=al?1:0;
alarmBox.className='alarmbox'+(al||em?' bad':'');alarmBox.textContent=em?'🛑 Emergencia: estado seguro':al?'🚨 Alarma crítica · enfriamiento '+(auto?'automático ON':'manual'):'✅ Normal · histéresis 74–80 °C';
drawLine(chart,data,al?'#e11d48':'#0284c7',80,'Umbral 80 °C')}
swAuto.onclick=e=>{auto=!auto;e.target.classList.toggle('on',auto);toast('PLC en modo '+(auto?'AUTOMÁTICO':'MANUAL'))};
swPump.onclick=e=>{if(auto){toast('En automático la bomba la gobierna el PLC');return}man=!man;e.target.classList.toggle('on',man)};
btnSpike.onclick=()=>spike=9;
btnEm.onclick=e=>{em=!em;e.target.classList.toggle('on',em);e.target.textContent=em?'▶ Restablecer':'🛑 Parada de emergencia'};
setInterval(tick,800);for(let i=0;i<26;i++)tick();
"""

# ---------- INTEGRACION ----------
integ_body = """
<div class="kicker">Módulo 03 · Página independiente</div><h1>🔀 Integración <span class="grad">IoT</span></h1>
<p class="sub">Node-RED · transformación · reintentos · alarmas. Prueba el simulador de entrega: a veces el backend “falla” y verás el reintento con backoff hasta confirmar.</p>
<div class="actions"><button class="btn primary" id="btnSend">▶ Enviar lectura de prueba</button><button class="btn" id="btnFail">Simular caída del backend (30 s de fallos)</button></div>
<div class="grid"><div><h3 style="margin-bottom:10px">Registro del flujo</h3><div class="log" id="log"></div></div>
<div class="card"><h2>Transformación en vivo</h2><p>Entrada (ESP32, cruda) → Salida (API, normalizada):</p>
<pre id="ioBox">Pulsa “Enviar lectura de prueba”…</pre>
<div class="metric"><span>Mensajes entregados</span><b id="mOk">0</b></div><div class="metric"><span>Reintentos</span><b id="mRet">0</b></div><div class="metric"><span>Alarmas generadas</span><b id="mAl">0</b></div></div></div>
<div class="grid3"><div class="card"><h3>🔄 Reintentos</h3><p>Backoff exponencial 1 s → 2 s → 4 s, máximo 3 intentos, con cola persistente.</p></div>
<div class="card"><h3>🚨 Alarmas</h3><p>Umbral + duración + severidad, con deduplicación y deadband anti-tormentas.</p></div>
<div class="card"><h3>🔔 Notificación</h3><p>Webhook / correo / Telegram cuando una alarma crítica se confirma.</p></div></div>"""
integ_js = """
let ok=0,ret=0,al=0,failUntil=0;const L=$('log');
log(L,'ok','Node-RED iniciado · flujo activo (MQTT in → función → HTTP out)');
function send(){
 const raw={device_id:'esp32-tanque-01',temp_f:+( (52+Math.random()*38)*9/5+32 ).toFixed(1),ts:Date.now()};
 const attempt=(n)=>{const fail=Date.now()<failUntil||Math.random()<.18;
  if(fail&&n<3){ret++;mRet.textContent=ret;log(L,'warn',`Intento ${n} falló (backend 503) · reintento en ${Math.pow(2,n-1)} s…`);setTimeout(()=>attempt(n+1),600)}
  else if(fail){log(L,'err','Entrega fallida tras 3 intentos · mensaje encolado')}
  else{ok++;const out={device_id:raw.device_id,temperature_c:+(((raw.temp_f-32)*5/9).toFixed(2)),quality:'good',ts:new Date(raw.ts).toISOString()};
   ioBox.textContent='ENTRADA:\\n'+JSON.stringify(raw,null,2)+'\\n\\nSALIDA → POST /api/v1/readings:\\n'+JSON.stringify(out,null,2);
   log(L,'ok',`Entregado en intento ${n} · temp ${out.temperature_c} °C (F→C normalizado)`);
   if(out.temperature_c>80){al++;mAl.textContent=al;log(L,'err','ALARMA CRÍTICA generada · webhook enviado')} mOk.textContent=ok}};
 attempt(1)}
btnSend.onclick=send;
btnFail.onclick=()=>{failUntil=Date.now()+30000;log(L,'err','Backend marcado como CAÍDO por 30 s · observa los reintentos');toast('Backend caído 30 s: envía lecturas y mira el log')};
"""

# ---------- BACKEND ----------
backend_body = """
<div class="kicker">Módulo 04 · Página independiente</div><h1>🗄️ Backend y <span class="grad">persistencia</span></h1>
<p class="sub">FastAPI · Pydantic · SQLAlchemy · PostgreSQL. Las lecturas llegan validadas y se almacenan; en esta demo la “base de datos” vive en tu navegador con la misma estructura de la API real.</p>
<div class="actions"><button class="btn primary" id="btnToggle">⏸ Pausar ingesta</button><button class="btn" id="btnExport">⬇ Exportar CSV</button><button class="btn" id="btnClear">🗑 Limpiar historial</button></div>
<div class="kpis"><div class="kpi"><span>Total lecturas</span><b id="kTotal">0</b><small>tabla readings</small></div><div class="kpi"><span>Temp. promedio</span><b id="kAvg">—</b><small>SELECT AVG(...)</small></div><div class="kpi"><span>Rechazadas (422)</span><b id="kRej">0</b><small>validación Pydantic</small></div><div class="kpi"><span>API</span><b style="font-size:1.2rem;padding-top:8px"><span class="badge b-ok">200 / 201 OK</span></b><small>FastAPI · OpenAPI</small></div></div>
<div class="card"><h2>Últimas lecturas · GET /api/v1/readings</h2><div class="scrollbox"><table><thead><tr><th>#</th><th>Timestamp</th><th>Dispositivo</th><th>Temperatura</th><th>Humedad</th><th>Nivel</th><th>Calidad</th></tr></thead><tbody id="tbody"><tr><td colspan="7">Esperando…</td></tr></tbody></table></div></div>
<div class="grid2"><div class="card"><h2>Esquema Pydantic</h2><pre>class ReadingIn(BaseModel):
    device_id: str
    temperature_c: float = Field(ge=-20, le=120)
    quality: str = "good"

@app.post("/api/v1/readings", status_code=201)
def create_reading(data: ReadingIn,
                   db: Session = Depends(get_db)):
    row = Reading(**data.model_dump())
    db.add(row); db.commit()
    return {"id": row.id, "status": "stored"}</pre></div>
<div class="card"><h2>Diseño de datos</h2><ul><li><b>Índices:</b> (device_id, created_at) para consultas históricas rápidas.</li><li><b>Migraciones</b> versionadas y pruebas de API.</li><li><b>Versionado:</b> /api/v1 · autenticación · paginación.</li><li>Prueba: cada ~25 lecturas se inyecta un valor fuera de rango y Pydantic lo <b>rechaza (422)</b>.</li></ul></div></div>"""
backend_js = """
let run=true,t=0,rows=[],rej=0;
function tick(){if(!run)return;t++;let temp=52+Math.sin(t/9)*9+(Math.random()*3-1.5);
 if(t%25===0){rej++;kRej.textContent=rej;toast('⚠ Lectura fuera de rango rechazada · HTTP 422 (Pydantic)');return}
 rows.push({id:rows.length+1,ts:now(),temp,hum:52+Math.sin(t/14)*10,level:62+Math.sin(t/20)*8});if(rows.length>240)rows.shift();
 kTotal.textContent=rows.length;kAvg.textContent=fmt(rows.reduce((a,r)=>a+r.temp,0)/rows.length)+' °C';
 tbody.innerHTML=rows.slice(-10).reverse().map(r=>`<tr><td><b>${r.id}</b></td><td>${r.ts}</td><td>esp32-tanque-01</td><td><b>${fmt(r.temp)} °C</b></td><td>${fmt(r.hum,0)} %</td><td>${fmt(r.level,0)} %</td><td><span class="badge b-ok">good</span></td></tr>`).join('')}
setInterval(tick,800);for(let i=0;i<14;i++)tick();
btnToggle.onclick=e=>{run=!run;e.target.textContent=run?'⏸ Pausar ingesta':'▶ Reanudar ingesta'};
btnClear.onclick=()=>{rows=[];tbody.innerHTML='<tr><td colspan="7">Historial limpio</td></tr>';kTotal.textContent=0};
btnExport.onclick=()=>{const csv='id,timestamp,temperature_c,humidity_pct,level_pct\\n'+rows.map(r=>[r.id,r.ts,fmt(r.temp,2),fmt(r.hum,1),fmt(r.level,1)].join(',')).join('\\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download='lecturas_iot.csv';a.click();toast('⬇ CSV exportado: '+rows.length+' lecturas')};
"""

# ---------- IA ----------
ia_body = """
<div class="kicker">Módulo 05 · Página independiente</div><h1>🤖 Inteligencia <span class="grad">artificial</span></h1>
<p class="sub">LangGraph · LangChain · Analyzer · Processor · Responder · Verifier. En segundo plano esta página mantiene una serie de datos simulada; el asistente responde <b>solo</b> con cifras calculadas de esa serie y verificadas.</p>
<div class="kpis"><div class="kpi"><span>Temperatura actual*</span><b id="kTemp">—</b><small>serie en vivo de esta página</small></div><div class="kpi"><span>Promedio*</span><b id="kAvg">—</b><small>ventana reciente</small></div><div class="kpi"><span>Máximo*</span><b id="kMax">—</b><small>sesión</small></div><div class="kpi"><span>Consultas IA</span><b id="kQ">0</b><small>verificadas</small></div></div>
<p style="color:var(--muted);font-size:.82rem">* Datos simulados localmente para la demo del asistente.</p>
<div class="grid"><div class="card"><h2>Grafo de agentes</h2>
<div class="agent" id="ag-analyzer"><span class="ico">🔍</span><div><b>Analyzer</b><p>Interpreta intención, variable y rango temporal.</p></div></div>
<div class="agent" id="ag-processor"><span class="ico">🧮</span><div><b>Processor</b><p>Consulta los datos y calcula estadísticas reales.</p></div></div>
<div class="agent" id="ag-responder"><span class="ico">✍️</span><div><b>Responder</b><p>Redacta con contexto y recomendación accionable.</p></div></div>
<div class="agent" id="ag-verifier"><span class="ico">✅</span><div><b>Verifier</b><p>Contrasta cada cifra antes de entregar la respuesta.</p></div></div>
<pre>graph.add_edge("analyzer", "processor")
graph.add_edge("processor", "responder")
graph.add_edge("responder", "verifier")
graph.add_conditional_edges("verifier", route,
    {"ok": END, "retry": "responder"})</pre></div>
<div class="card"><h2>Asistente del proceso</h2>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin:10px 0"><button class="btn qbtn">¿Cómo está la temperatura?</button><button class="btn qbtn">¿Cuál fue la máxima?</button><button class="btn qbtn">Dame un resumen</button><button class="btn" id="btnSpike">⚠ Forzar pico y preguntar</button></div>
<div style="display:flex;gap:8px;flex-wrap:wrap"><input type="text" id="chatInput" placeholder="Pregunta sobre temperatura, máxima o resumen…" style="flex:1;min-width:200px"><button class="btn primary" id="btnAsk">Preguntar</button></div>
<div class="chat" id="chat"><div class="msg ia">Hola. Pregúntame por la temperatura, la máxima o un resumen. Cada respuesta pasa por el <b>Verifier</b>.</div></div></div></div>"""
ia_js = """
let t=0,spike=0,queries=0;const data=[];let max=-Infinity;
function tick(){t++;let v=52+Math.sin(t/9)*9+(Math.random()*3-1.5);if(spike>0){v+=27;spike--}data.push(v);if(data.length>56)data.shift();max=Math.max(max,v);
kTemp.textContent=fmt(v)+' °C';kAvg.textContent=fmt(data.reduce((a,b)=>a+b,0)/data.length)+' °C';kMax.textContent=fmt(max)+' °C'}
setInterval(tick,800);for(let i=0;i<26;i++)tick();
function stats(){return{cur:data[data.length-1],avg:data.reduce((a,b)=>a+b,0)/data.length,max,min:Math.min(...data),n:data.length}}
function answer(q){const s=stats();q=q.toLowerCase();
 if(q.includes('máx')||q.includes('max')||q.includes('pico')||q.includes('alarma'))return `La temperatura máxima de la sesión es ${fmt(s.max)} °C (umbral de alarma: 80 °C). ${s.max>80?'Se superó el umbral: el PLC debería haber activado el enfriamiento.':'No se ha superado el umbral.'} Actualmente estamos en ${fmt(s.cur)} °C.`;
 if(q.includes('resumen'))return `Resumen: actual ${fmt(s.cur)} °C · promedio ${fmt(s.avg)} °C · mín. ${fmt(s.min)} °C · máx. ${fmt(s.max)} °C, sobre ${s.n} muestras de la ventana. Recomendación: ${s.cur>80?'revisar el sobrecalentamiento ahora.':'continuar operación normal.'}`;
 return `La temperatura actual es ${fmt(s.cur)} °C (promedio ${fmt(s.avg)} °C, mín. ${fmt(s.min)} °C, máx. ${fmt(s.max)} °C). ${s.cur>80?'⚠ Estamos sobre el umbral de 80 °C.':'Estamos dentro del rango seguro.'}`}
function ask(q){if(!q.trim())return;chat.insertAdjacentHTML('beforeend',`<div class="msg user">${q.replace(/</g,'&lt;')}</div>`);
 const ids=['analyzer','processor','responder','verifier'];ids.forEach(id=>$('ag-'+id).classList.remove('active','done'));let i=0;
 (function step(){if(i>0)$('ag-'+ids[i-1]).classList.replace('active','done');
  if(i>=ids.length){queries++;kQ.textContent=queries;chat.insertAdjacentHTML('beforeend',`<div class="msg ia">${answer(q)}<br><small>✅ <b>Verifier:</b> cifras contrastadas contra la serie en vivo · unidades °C correctas.</small></div>`);chat.scrollTop=chat.scrollHeight;return}
  $('ag-'+ids[i]).classList.add('active');i++;setTimeout(step,600)})()}
btnAsk.onclick=()=>{ask(chatInput.value);chatInput.value=''};
chatInput.addEventListener('keydown',e=>{if(e.key==='Enter')btnAsk.click()});
document.querySelectorAll('.qbtn').forEach(b=>b.onclick=()=>ask(b.textContent));
btnSpike.onclick=()=>{spike=8;setTimeout(()=>ask('¿Cuál fue la máxima?'),6500);toast('Pico forzado · la IA responderá en unos segundos')};
"""

# ---------- PRESENTACION ----------
pres_body = """
<div class="kicker">Módulo 06 · Página independiente</div><h1>📊 <span class="grad">Presentación</span></h1>
<p class="sub">HTML · JavaScript · Tailwind CSS · Chart.js. Todo el sistema multipágina que estás navegando <b>es</b> este módulo: modo claro profesional, responsive y con datos en vivo.</p>
<div class="card" style="margin-top:18px"><div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:12px"><h2>Gráfico en vivo (patrón Chart.js)</h2>
<div class="tabs"><button class="tab active" data-v="temp">Temperatura</button><button class="tab" data-v="hum">Humedad</button><button class="tab" data-v="level">Nivel</button></div></div>
<canvas class="chart" id="chart" width="720" height="290"></canvas></div>
<div class="grid3"><div class="card"><h3>🎨 Diseño</h3><ul><li>Modo claro profesional, sombras suaves</li><li>Tipografía del sistema, alto contraste</li><li>Semáforos por estado y severidad</li></ul></div>
<div class="card"><h3>📱 Responsive</h3><ul><li>Grillas que colapsan en móvil</li><li>Navegación fija entre páginas</li><li>Legible a distancia en planta</li></ul></div>
<div class="card"><h3>🧩 Stack</h3><pre>HTML5 · CSS (utilidades tipo Tailwind)
JavaScript vanilla · Canvas ≈ Chart.js
fetch('/api/v1/readings/latest')</pre></div></div>
<div class="card" style="margin-top:18px"><h2>Mapa del sitio (7 páginas independientes)</h2>
<table><tr><th>Página</th><th>Archivo</th><th>Contenido</th></tr>
<tr><td><b>Panel</b></td><td>index.html</td><td>Portada con loader 5 s, KPIs y acceso a módulos</td></tr>
<tr><td><b>Campo e IoT</b></td><td>campo.html</td><td>ESP32 y calibración interactiva</td></tr>
<tr><td><b>Automatización</b></td><td>automatizacion.html</td><td>OpenPLC y Modbus en vivo</td></tr>
<tr><td><b>Integración IoT</b></td><td>integracion.html</td><td>Node-RED, reintentos y alarmas</td></tr>
<tr><td><b>Backend</b></td><td>backend.html</td><td>FastAPI, tabla y exportación CSV</td></tr>
<tr><td><b>Inteligencia Artificial</b></td><td>ia.html</td><td>Agentes LangGraph y chat verificado</td></tr>
<tr><td><b>Presentación</b></td><td>presentacion.html</td><td>Esta página: diseño y gráficos</td></tr></table></div>"""
pres_js = """
let t=0;const S={temp:[],hum:[],level:[]};let act='temp';
const C={temp:'#0284c7',hum:'#059669',level:'#7c3aed'};
function tick(){t++;S.temp.push(52+Math.sin(t/9)*9+(Math.random()*3-1.5));S.hum.push(52+Math.sin(t/14)*10);S.level.push(62+Math.sin(t/20)*10);
Object.values(S).forEach(a=>{if(a.length>56)a.shift()});drawLine(chart,S[act],C[act],act==='temp'?80:null,'Umbral 80 °C')}
document.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-v]').forEach(x=>x.classList.remove('active'));b.classList.add('active');act=b.dataset.v;tick()});
setInterval(tick,800);for(let i=0;i<26;i++)tick();
"""

files = {
    'index.html': page('index', 'Panel general', index_body, index_js, loader=True),
    'campo.html': page('campo', 'Campo e IoT', campo_body, campo_js),
    'automatizacion.html': page('automatizacion', 'Automatización industrial', auto_body, auto_js),
    'integracion.html': page('integracion', 'Integración IoT', integ_body, integ_js),
    'backend.html': page('backend', 'Backend y persistencia', backend_body, backend_js),
    'ia.html': page('ia', 'Inteligencia artificial', ia_body, ia_js),
    'presentacion.html': page('presentacion', 'Presentación', pres_body, pres_js),
}
for name, html in files.items():
    (OUT / name).write_text(html, encoding='utf-8')
    print('✔', name, len(html), 'bytes')
