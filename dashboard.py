from flask import Flask, jsonify, render_template_string
import requests

app = Flask(__name__)
ORION = "http://localhost:1026/v2"

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Smart Home · Digital Twin</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #f7f7f5;
    --surface: #ffffff;
    --border: #e8e8e4;
    --text: #111110;
    --sub: #888884;
    --on: #1a7f4b;
    --on-bg: #eaf5ef;
    --off: #c0392b;
    --off-bg: #fdf0ee;
    --warn: #b45309;
    --warn-bg: #fef8ee;
    --blue: #1d4ed8;
    --blue-bg: #eff4ff;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    font-size: 14px;
  }

  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky; top: 0; z-index: 10;
  }
  .brand {
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: .04em;
    display: flex; align-items: center; gap: .5rem;
  }
  .brand-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--on);
    animation: blink 2s ease infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }
  .header-right { display:flex; align-items:center; gap:1.25rem; }
  #clock { font-family:'DM Mono',monospace; font-size:12px; color:var(--sub); }
  #status-badge {
    font-size: 11px; color: var(--sub);
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 100px; padding: 3px 10px;
  }

  main { max-width: 1080px; margin: 0 auto; padding: 2rem; }

  .summary {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
  }
  .stat {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1.25rem;
  }
  .stat-label { font-size: 11px; color: var(--sub); letter-spacing:.05em; text-transform:uppercase; margin-bottom:.5rem; }
  .stat-value { font-family:'DM Mono',monospace; font-size: 1.6rem; font-weight:500; }
  .stat-unit  { font-size:12px; color:var(--sub); margin-left:2px; font-weight:400; }

  .section-title {
    font-size: 11px; font-weight:500; color: var(--sub);
    letter-spacing: .08em; text-transform: uppercase;
    margin-bottom: 1rem;
  }

  .devices {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    transition: box-shadow .15s, border-color .15s;
    animation: fadeUp .3s ease both;
  }
  .card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.06); border-color:#d4d4cf; }
  @keyframes fadeUp {
    from { opacity:0; transform:translateY(8px); }
    to   { opacity:1; transform:translateY(0); }
  }

  .card-header {
    display: flex; align-items: flex-start;
    justify-content: space-between; margin-bottom: 1rem;
  }
  .card-icon-name { display:flex; align-items:center; gap:.65rem; }
  .icon {
    width:38px; height:38px; border-radius:9px;
    background: var(--bg); border:1px solid var(--border);
    display:flex; align-items:center; justify-content:center;
    font-size:1.1rem; flex-shrink:0;
  }
  .card-name { font-weight:500; font-size:.95rem; }
  .card-loc  { font-size:11px; color:var(--sub); margin-top:2px; }

  .pill {
    font-family:'DM Mono',monospace; font-size:11px; font-weight:500;
    padding:3px 10px; border-radius:100px; white-space:nowrap;
  }
  .pill.on     { background:var(--on-bg);   color:var(--on);   }
  .pill.off    { background:var(--off-bg);  color:var(--off);  }
  .pill.active { background:var(--warn-bg); color:var(--warn); }
  .pill.live   { background:var(--blue-bg); color:var(--blue); }
  .pill.idle   { background:var(--bg); color:var(--sub); border:1px solid var(--border); }

  .attrs { display:flex; flex-direction:column; }
  .attr-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:.4rem 0; border-bottom:1px solid var(--border);
  }
  .attr-row:last-child { border-bottom:none; }
  .attr-key { font-size:12px; color:var(--sub); }
  .attr-val { font-family:'DM Mono',monospace; font-size:12px; font-weight:500; }
  .attr-val.green { color:var(--on); }
  .attr-val.red   { color:var(--off); }
  .attr-val.amber { color:var(--warn); }

  .bar-wrap { width:60px; height:3px; background:var(--border); border-radius:2px; margin-left:.75rem; }
  .bar-fill  { height:100%; border-radius:2px; background:#111110; transition:width .5s ease; }

  #error-msg {
    text-align:center; padding:3rem; color:var(--sub);
    font-size:13px; display:none;
  }

  @media(max-width:640px){
    .summary { grid-template-columns:repeat(2,1fr); }
    main { padding:1rem; }
  }
</style>
</head>
<body>

<header>
  <div class="brand"><div class="brand-dot"></div>Smart Home &middot; Digital Twin</div>
  <div class="header-right">
    <div id="clock"></div>
    <div id="status-badge">&#9679; live</div>
  </div>
</header>

<main>
  <div class="summary">
    <div class="stat">
      <div class="stat-label">Devices online</div>
      <div class="stat-value" id="s-online">&#8212;</div>
    </div>
    <div class="stat">
      <div class="stat-label">Current draw</div>
      <div class="stat-value" id="s-kw">&#8212;<span class="stat-unit">kW</span></div>
    </div>
    <div class="stat">
      <div class="stat-label">Temperature</div>
      <div class="stat-value" id="s-temp">&#8212;<span class="stat-unit">&deg;C</span></div>
    </div>
    <div class="stat">
      <div class="stat-label">Today&rsquo;s usage</div>
      <div class="stat-value" id="s-kwh">&#8212;<span class="stat-unit">kWh</span></div>
    </div>
  </div>

  <div class="section-title">All devices</div>
  <div class="devices" id="devices"></div>
  <div id="error-msg">Cannot reach Orion Context Broker &mdash; make sure Docker is running.</div>
</main>

<script>
const ICONS = { SmartPlug:'🔌', Camera:'📷', SmartTV:'📺', SmartMeter:'⚡', TemperatureSensor:'🌡️' };
const NAMES = { SmartPlug:'Smart Plug', Camera:'CCTV Camera', SmartTV:'Smart TV', SmartMeter:'Smart Meter', TemperatureSensor:'Temp Sensor' };
const SHOW  = {
  SmartPlug:         ['state','power_w','voltage_v'],
  Camera:            ['motionDetected','recording','fps'],
  SmartTV:           ['state','channel','volume','app'],
  SmartMeter:        ['current_kw','kwh_today','voltage_v','tariff'],
  TemperatureSensor: ['temperature','humidity','heatIndex'],
};
const UNITS   = { power_w:'W', voltage_v:'V', fps:'fps', current_kw:'kW', kwh_today:'kWh', temperature:'°C', humidity:'%', heatIndex:'°C', volume:'%' };
const MAX_VAL = { power_w:1500, current_kw:5, kwh_today:20, volume:100, temperature:45, humidity:100, fps:30 };

function pillFor(e){
  const t=e.type, a=e;
  if(t==='Camera'){
    if(a.motionDetected?.value===true||a.motionDetected?.value==='true') return ['active','motion'];
    if(a.recording?.value===true||a.recording?.value==='true') return ['live','recording'];
    return ['idle','idle'];
  }
  const s=a.state?.value;
  if(s==='on') return ['on','on'];
  if(s==='off') return ['off','off'];
  return ['idle','—'];
}

function fmtVal(key, raw){
  if(raw===null||raw===undefined) return '—';
  if(typeof raw==='boolean') return raw?'yes':'no';
  const n=parseFloat(raw);
  if(!isNaN(n)){
    if(['kwh_today','current_kw'].includes(key)) return n.toFixed(3);
    if(['temperature','heatIndex','humidity'].includes(key)) return n.toFixed(1);
    if(key==='power_w') return n.toFixed(1);
    return String(raw);
  }
  return String(raw);
}

function valCls(key, val){
  if(key==='state') return val==='on'?'green':val==='off'?'red':'';
  if(['motionDetected','recording'].includes(key)) return (val===true||val==='true')?'amber':'';
  return '';
}

function makeCard(e, idx){
  const [pCls, pLbl] = pillFor(e);
  const keys = SHOW[e.type] || Object.keys(e).filter(k=>!['id','type'].includes(k));

  const rows = keys.map(key=>{
    if(!e[key]) return '';
    const raw  = e[key].value;
    const disp = fmtVal(key, raw);
    const unit = UNITS[key]||'';
    const cls  = valCls(key, raw);
    const max  = MAX_VAL[key];
    const skip = ['state','motionDetected','recording','tariff','app','channel'].includes(key);
    const pct  = (!skip && max!=null) ? Math.min(100,Math.max(0,parseFloat(raw)/max*100)) : null;
    const bar  = pct!=null ? `<div class="bar-wrap"><div class="bar-fill" style="width:${pct.toFixed(1)}%"></div></div>` : '';
    return `<div class="attr-row">
      <span class="attr-key">${key.replace(/([A-Z])/g,' $1').toLowerCase()}</span>
      <div style="display:flex;align-items:center">
        <span class="attr-val ${cls}">${disp}${unit?'<span style="opacity:.5;font-weight:400;font-size:10px;margin-left:2px">'+unit+'</span>':''}</span>
        ${bar}
      </div>
    </div>`;
  }).join('');

  return `<div class="card" style="animation-delay:${idx*55}ms">
    <div class="card-header">
      <div class="card-icon-name">
        <div class="icon">${ICONS[e.type]||'▪'}</div>
        <div>
          <div class="card-name">${NAMES[e.type]||e.type}</div>
          <div class="card-loc">${e.location?.value||''}</div>
        </div>
      </div>
      <span class="pill ${pCls}">${pLbl}</span>
    </div>
    <div class="attrs">${rows}</div>
  </div>`;
}

function updateSummary(data){
  const online = data.filter(e=>e.state?.value==='on'||e.type==='SmartMeter'||e.type==='TemperatureSensor').length;
  document.getElementById('s-online').innerHTML = `${online}<span class="stat-unit"> / ${data.length}</span>`;
  const m=data.find(e=>e.type==='SmartMeter');
  document.getElementById('s-kw').innerHTML  = m?`${(+m.current_kw?.value||0).toFixed(2)}<span class="stat-unit">kW</span>`:`&#8212;<span class="stat-unit">kW</span>`;
  document.getElementById('s-kwh').innerHTML = m?`${(+m.kwh_today?.value||0).toFixed(3)}<span class="stat-unit">kWh</span>`:`&#8212;<span class="stat-unit">kWh</span>`;
  const s=data.find(e=>e.type==='TemperatureSensor');
  document.getElementById('s-temp').innerHTML= s?`${(+s.temperature?.value||0).toFixed(1)}<span class="stat-unit">&deg;C</span>`:`&#8212;<span class="stat-unit">&deg;C</span>`;
}

async function fetchAndRender(){
  try{
    const r=await fetch('/api/entities');
    if(!r.ok) throw 0;
    const data=await r.json();
    if(!Array.isArray(data)||!data.length) throw 0;
    document.getElementById('error-msg').style.display='none';
    document.getElementById('devices').innerHTML=data.map((e,i)=>makeCard(e,i)).join('');
    updateSummary(data);
    document.getElementById('status-badge').textContent='● live';
  } catch{
    document.getElementById('error-msg').style.display='block';
    document.getElementById('status-badge').textContent='○ offline';
  }
}

setInterval(()=>{
  const t=new Date();
  document.getElementById('clock').textContent=
    t.toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
},1000);

fetchAndRender();
setInterval(fetchAndRender,3000);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/entities")
def api():
    try:
        r = requests.get(f"{ORION}/entities?limit=20", timeout=3)
        return jsonify(r.json() if r.ok else [])
    except:
        return jsonify([])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
