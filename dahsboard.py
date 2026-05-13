from flask import Flask, jsonify, render_template_string
import requests

app = Flask(__name__)
ORION = "http://localhost:1026/v2"

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Smart Home Digital Twin</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;500;700&display=swap');
  *{margin:0;padding:0;box-sizing:border-box}
  :root{
    --bg:#050a0f;--panel:#0a1520;--border:#0f3050;
    --cyan:#00d4ff;--green:#00ff88;--amber:#ffaa00;
    --red:#ff3355;--dim:#1a3a5c;
  }
  body{background:var(--bg);color:#c8e8ff;font-family:'Share Tech Mono',monospace;overflow:hidden;height:100vh}
  #canvas-wrap{position:fixed;inset:0;z-index:0}
  canvas{display:block}

  /* HUD overlay */
  #hud{position:fixed;inset:0;z-index:10;pointer-events:none;display:grid;
       grid-template-columns:280px 1fr 280px;grid-template-rows:56px 1fr 56px}

  /* Top bar */
  #topbar{grid-column:1/-1;display:flex;align-items:center;justify-content:space-between;
          padding:0 1.5rem;background:linear-gradient(180deg,rgba(5,10,15,.95) 60%,transparent);
          border-bottom:1px solid var(--border)}
  .logo{font-family:'Rajdhani',sans-serif;font-weight:700;font-size:1.3rem;
        color:var(--cyan);letter-spacing:.15em;text-transform:uppercase}
  .logo span{color:#fff;opacity:.5}
  #clock{font-size:.75rem;color:var(--cyan);opacity:.7}
  .status-dot{width:8px;height:8px;border-radius:50%;background:var(--green);
              box-shadow:0 0 8px var(--green);animation:pulse 2s infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

  /* Left panel */
  #left-panel{grid-row:2;padding:1rem .75rem;display:flex;flex-direction:column;gap:.5rem;
              background:linear-gradient(90deg,rgba(5,10,15,.9) 70%,transparent);pointer-events:all;
              overflow-y:auto}
  /* Right panel */
  #right-panel{grid-row:2;grid-column:3;padding:1rem .75rem;display:flex;flex-direction:column;gap:.5rem;
               background:linear-gradient(270deg,rgba(5,10,15,.9) 70%,transparent);pointer-events:all;
               overflow-y:auto}

  .device-card{background:var(--panel);border:1px solid var(--border);border-radius:4px;
               padding:.6rem .8rem;cursor:pointer;transition:border-color .2s}
  .device-card:hover{border-color:var(--cyan)}
  .device-card.active{border-color:var(--cyan);box-shadow:0 0 12px rgba(0,212,255,.2)}
  .d-header{display:flex;align-items:center;gap:.5rem;margin-bottom:.4rem}
  .d-icon{font-size:1rem;width:20px;text-align:center}
  .d-name{font-family:'Rajdhani',sans-serif;font-weight:700;font-size:.9rem;color:#fff;letter-spacing:.05em}
  .d-loc{font-size:.65rem;color:var(--cyan);opacity:.6;margin-left:auto}
  .d-attrs{display:flex;flex-wrap:wrap;gap:.2rem .6rem}
  .attr{font-size:.65rem}
  .attr-key{color:#4a8ab0}
  .attr-val{color:var(--cyan)}
  .attr-val.on{color:var(--green)}
  .attr-val.off{color:var(--red)}
  .attr-val.motion{color:var(--amber)}

  /* Bottom bar */
  #bottombar{grid-column:1/-1;display:flex;align-items:center;justify-content:center;gap:2rem;
             background:linear-gradient(0deg,rgba(5,10,15,.95) 60%,transparent);
             border-top:1px solid var(--border);font-size:.65rem;color:var(--cyan);opacity:.6}

  /* Tooltip */
  #tooltip{position:fixed;background:rgba(5,10,15,.95);border:1px solid var(--cyan);
           border-radius:4px;padding:.5rem .75rem;font-size:.7rem;pointer-events:none;
           display:none;z-index:20;min-width:160px}
  #tooltip b{font-family:'Rajdhani',sans-serif;color:var(--cyan);font-size:.85rem}

  /* Scan line effect */
  body::after{content:'';position:fixed;inset:0;background:repeating-linear-gradient(
    0deg,transparent,transparent 2px,rgba(0,212,255,.015) 2px,rgba(0,212,255,.015) 4px);
    pointer-events:none;z-index:5}

  /* Scrollbar */
  #left-panel::-webkit-scrollbar,#right-panel::-webkit-scrollbar{width:3px}
  #left-panel::-webkit-scrollbar-thumb,#right-panel::-webkit-scrollbar-thumb{background:var(--dim)}
</style>
</head>
<body>
<div id="canvas-wrap"><canvas id="c"></canvas></div>

<div id="hud">
  <div id="topbar">
    <div class="logo">Smart<span>Home</span> · Digital Twin</div>
    <div class="status-dot"></div>
    <div id="clock">--:--:--</div>
  </div>

  <div id="left-panel">
    <div style="font-size:.65rem;color:var(--cyan);opacity:.5;margin-bottom:.25rem;letter-spacing:.1em">DEVICES · LEFT WING</div>
    <div id="cards-left"></div>
  </div>

  <div></div><!-- center spacer -->

  <div id="right-panel">
    <div style="font-size:.65rem;color:var(--cyan);opacity:.5;margin-bottom:.25rem;letter-spacing:.1em">DEVICES · RIGHT WING</div>
    <div id="cards-right"></div>
  </div>

  <div id="bottombar">
    <span>ORION CONTEXT BROKER · NGSI-v2</span>
    <span>·</span>
    <span id="entity-count">0 ENTITIES</span>
    <span>·</span>
    <span>REFRESH 3s</span>
    <span>·</span>
    <span>DRAG TO ORBIT · SCROLL TO ZOOM</span>
  </div>
</div>

<div id="tooltip"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ── Three.js scene setup ─────────────────────────────────────────────
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true});
renderer.setPixelRatio(devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x050a0f, 0.04);

const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 200);
camera.position.set(14, 10, 14);
camera.lookAt(0, 0, 0);

function resize(){
  const w=innerWidth, h=innerHeight;
  renderer.setSize(w,h);
  camera.aspect=w/h;
  camera.updateProjectionMatrix();
}
resize();
window.addEventListener('resize', resize);

// ── Orbit controls (manual, no OrbitControls dependency) ─────────────
let isDragging=false, prevMouse={x:0,y:0};
let spherical={theta:Math.PI/4, phi:Math.PI/3.5, r:20};

canvas.addEventListener('mousedown', e=>{isDragging=true; prevMouse={x:e.clientX,y:e.clientY}});
canvas.addEventListener('mouseup', ()=>isDragging=false);
canvas.addEventListener('mousemove', e=>{
  if(!isDragging) return;
  spherical.theta -= (e.clientX-prevMouse.x)*0.005;
  spherical.phi   -= (e.clientY-prevMouse.y)*0.005;
  spherical.phi = Math.max(0.2, Math.min(Math.PI/2.2, spherical.phi));
  prevMouse={x:e.clientX,y:e.clientY};
});
canvas.addEventListener('wheel', e=>{
  spherical.r = Math.max(8, Math.min(35, spherical.r + e.deltaY*0.02));
});

// Touch support
let lastTouch=null;
canvas.addEventListener('touchstart', e=>{lastTouch={x:e.touches[0].clientX,y:e.touches[0].clientY}});
canvas.addEventListener('touchmove', e=>{
  if(!lastTouch) return;
  spherical.theta -= (e.touches[0].clientX-lastTouch.x)*0.005;
  spherical.phi   -= (e.touches[0].clientY-lastTouch.y)*0.005;
  spherical.phi = Math.max(0.2, Math.min(Math.PI/2.2, spherical.phi));
  lastTouch={x:e.touches[0].clientX,y:e.touches[0].clientY};
});

// ── Materials ─────────────────────────────────────────────────────────
const MAT = {
  wall:    new THREE.MeshLambertMaterial({color:0x0a1a2e}),
  floor:   new THREE.MeshLambertMaterial({color:0x061018}),
  ceiling: new THREE.MeshLambertMaterial({color:0x060e18}),
  glass:   new THREE.MeshLambertMaterial({color:0x00aaff, transparent:true, opacity:.15}),
  trim:    new THREE.MeshLambertMaterial({color:0x0f3050}),
};

// ── Helper: box ───────────────────────────────────────────────────────
function box(w,h,d,mat,x,y,z,castShadow=false){
  const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat);
  m.position.set(x,y,z);
  m.castShadow=castShadow;
  m.receiveShadow=true;
  scene.add(m);
  return m;
}

// ── Build house shell ─────────────────────────────────────────────────
// Floor
box(16,0.2,12, MAT.floor, 0,-0.1,0);

// Walls
box(16,4,0.2, MAT.wall, 0,2,-6);   // back
box(16,4,0.2, MAT.wall, 0,2,6);    // front (removed center for door)
box(0.2,4,12, MAT.wall, -8,2,0);   // left
box(0.2,4,12, MAT.wall, 8,2,0);    // right

// Ceiling
box(16,0.15,12, MAT.ceiling, 0,4.08,0);

// Interior divider wall
box(0.15,4,5, MAT.wall, 0,2,-3.5);
box(0.15,4,4, MAT.wall, 0,2,4);

// Skirting / trim strips
for(let z of[-6,6]){ box(16,0.1,0.08, MAT.trim, 0,0.05,z) }
for(let x of[-8,8]){ box(0.08,0.1,12, MAT.trim, x,0.05,0) }

// Grid floor lines (decorative)
const gridHelper = new THREE.GridHelper(16,16, 0x0f3050, 0x061828);
gridHelper.position.y=0.01;
scene.add(gridHelper);

// ── Ambient & directional light ────────────────────────────────────────
const ambient = new THREE.AmbientLight(0x0a1a2e, 2);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0x4488aa, 1.5);
sun.position.set(10,15,10);
sun.castShadow=true;
sun.shadow.mapSize.set(1024,1024);
scene.add(sun);

// ── Device 3D objects ─────────────────────────────────────────────────
const deviceObjects = {};

// 1. Smart Plug (Living Room — left zone)
{
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.4,0.6,0.3),
    new THREE.MeshLambertMaterial({color:0x112233}));
  body.castShadow=true;
  const led = new THREE.Mesh(new THREE.SphereGeometry(0.07,8,8),
    new THREE.MeshLambertMaterial({color:0xff0000, emissive:0xff0000, emissiveIntensity:1}));
  led.position.set(0,0.2,0.16);
  g.add(body,led);
  g.position.set(-5.5, 0.5, -2);
  scene.add(g);
  deviceObjects['SmartPlug'] = {group:g, led, light:null, type:'plug'};

  const pl = new THREE.PointLight(0x00ff00, 0, 2);
  pl.position.set(-5.5,1,-2);
  scene.add(pl);
  deviceObjects['SmartPlug'].light = pl;
}

// 2. CCTV Camera (Front door — front wall)
{
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.CylinderGeometry(0.15,0.18,0.5,12),
    new THREE.MeshLambertMaterial({color:0x0d1f30}));
  const lens = new THREE.Mesh(new THREE.SphereGeometry(0.1,12,12),
    new THREE.MeshLambertMaterial({color:0x000a14, emissive:0x001122, emissiveIntensity:.5}));
  lens.position.z=0.25;
  const led = new THREE.Mesh(new THREE.SphereGeometry(0.05,8,8),
    new THREE.MeshLambertMaterial({color:0x440000, emissive:0xff0000, emissiveIntensity:0}));
  led.position.set(0.15,0.15,0.2);
  g.add(body,lens,led);
  g.rotation.x=Math.PI/2;
  g.position.set(3,3.5,5.8);
  scene.add(g);
  deviceObjects['Camera'] = {group:g, led, light:null, type:'camera'};

  const pl = new THREE.PointLight(0xff2200, 0, 3);
  pl.position.set(3,3,5);
  scene.add(pl);
  deviceObjects['Camera'].light = pl;
}

// 3. Smart TV (Bedroom — right zone, back wall)
{
  const g = new THREE.Group();
  const frame = new THREE.Mesh(new THREE.BoxGeometry(2.4,1.4,0.1),
    new THREE.MeshLambertMaterial({color:0x040d14}));
  const screen = new THREE.Mesh(new THREE.BoxGeometry(2.2,1.2,0.05),
    new THREE.MeshLambertMaterial({color:0x000509, emissive:0x001122, emissiveIntensity:0}));
  screen.position.z=0.06;
  const stand = new THREE.Mesh(new THREE.BoxGeometry(0.15,0.5,0.15),
    new THREE.MeshLambertMaterial({color:0x040d14}));
  stand.position.y=-0.95;
  g.add(frame,screen,stand);
  g.position.set(5,2,-5.8);
  scene.add(g);
  deviceObjects['SmartTV'] = {group:g, screen, light:null, type:'tv'};

  const pl = new THREE.PointLight(0x0066ff, 0, 5);
  pl.position.set(5,2,-4);
  scene.add(pl);
  deviceObjects['SmartTV'].light = pl;
}

// 4. Smart Meter (Utility — left back)
{
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.7,1.0,0.25),
    new THREE.MeshLambertMaterial({color:0x0a1525}));
  const display = new THREE.Mesh(new THREE.BoxGeometry(0.5,0.3,0.05),
    new THREE.MeshLambertMaterial({color:0x003300, emissive:0x00ff00, emissiveIntensity:0.3}));
  display.position.set(0,0.15,0.13);
  const dial = new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.08,0.05,16),
    new THREE.MeshLambertMaterial({color:0x0f3050}));
  dial.rotation.x=Math.PI/2;
  dial.position.set(0,-0.25,0.13);
  g.add(body,display,dial);
  g.position.set(-7.8,1.2,-3);
  scene.add(g);
  deviceObjects['SmartMeter'] = {group:g, display, light:null, type:'meter'};

  const pl = new THREE.PointLight(0x00ff44, 0.4, 3);
  pl.position.set(-7,1.5,-3);
  scene.add(pl);
  deviceObjects['SmartMeter'].light = pl;
}

// 5. Temperature Sensor (Kitchen — front right)
{
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.CylinderGeometry(0.18,0.18,0.5,16),
    new THREE.MeshLambertMaterial({color:0x0a1a2e}));
  const top = new THREE.Mesh(new THREE.SphereGeometry(0.18,16,8,0,Math.PI*2,0,Math.PI/2),
    new THREE.MeshLambertMaterial({color:0x0d2040}));
  top.position.y=0.25;
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.18,0.02,8,16),
    new THREE.MeshLambertMaterial({color:0x00d4ff, emissive:0x00d4ff, emissiveIntensity:0.5}));
  ring.position.y=0.1;
  g.add(body,top,ring);
  g.position.set(5, 0.25, 4);
  scene.add(g);
  deviceObjects['TemperatureSensor'] = {group:g, ring, light:null, type:'sensor'};

  const pl = new THREE.PointLight(0x00d4ff, 0.6, 4);
  pl.position.set(5,1,4);
  scene.add(pl);
  deviceObjects['TemperatureSensor'].light = pl;
}

// Room label plates
function makeLabel(text, x, y, z){
  // Placeholder — pure geometry markers for rooms
  const plate = new THREE.Mesh(new THREE.BoxGeometry(1.5,0.05,0.4),
    new THREE.MeshLambertMaterial({color:0x0f3050}));
  plate.position.set(x,y,z);
  scene.add(plate);
}
makeLabel('Living Room', -4, 0.03, -2);
makeLabel('Bedroom',      4, 0.03, -4);
makeLabel('Kitchen',      4, 0.03,  4);

// ── Particle field (ambient atmosphere) ───────────────────────────────
const particleGeo = new THREE.BufferGeometry();
const pCount = 200;
const pPos = new Float32Array(pCount*3);
for(let i=0;i<pCount*3;i++) pPos[i]=(Math.random()-0.5)*20;
particleGeo.setAttribute('position', new THREE.BufferAttribute(pPos,3));
const particles = new THREE.Points(particleGeo,
  new THREE.PointsMaterial({color:0x00d4ff,size:0.04,transparent:true,opacity:0.3}));
scene.add(particles);

// ── Update device 3D states from API data ────────────────────────────
function applyState(entities){
  entities.forEach(e => {
    const type = e.type;
    const obj  = deviceObjects[type];
    if(!obj) return;

    if(type==='SmartPlug'){
      const on = e.state?.value==='on';
      obj.led.material.color.setHex(on?0x00ff00:0xff2200);
      obj.led.material.emissive.setHex(on?0x00ff00:0xff2200);
      obj.light.intensity = on? (e.power_w?.value||0)/500 : 0;
      obj.light.color.setHex(on?0x00ff88:0xff0000);
    }
    else if(type==='Camera'){
      const motion = e.motionDetected?.value===true||e.motionDetected?.value==='true';
      const rec    = e.recording?.value===true||e.recording?.value==='true';
      obj.led.material.emissive.setHex(rec?0xff0000:0x000000);
      obj.led.material.emissiveIntensity = rec?1:0;
      obj.light.intensity = motion?0.8:0;
    }
    else if(type==='SmartTV'){
      const on = e.state?.value==='on';
      const colors=[0x0033ff,0x003399,0x1100cc,0x004488,0x0066cc];
      const col = colors[Math.floor(Math.random()*colors.length)];
      obj.screen.material.emissive.setHex(on?col:0x000000);
      obj.screen.material.emissiveIntensity = on?0.8:0;
      obj.light.intensity = on?1.2:0;
    }
    else if(type==='SmartMeter'){
      const kw = e.current_kw?.value||0;
      const intensity = Math.min(kw/3, 1);
      obj.display.material.emissiveIntensity = 0.2+intensity*0.8;
      obj.light.intensity = 0.3+intensity*0.5;
    }
    else if(type==='TemperatureSensor'){
      const temp = e.temperature?.value||22;
      // Cool blue → warm amber based on temperature
      const t = Math.max(0,Math.min(1,(temp-18)/17));
      const r = Math.floor(t*255);
      const b = Math.floor((1-t)*255);
      const col = (r<<16)|(0<<8)|b;
      obj.ring.material.emissive.setHex(col|(0x001100));
      obj.light.color.setHex(col|0x000088);
    }
  });
}

// ── Render loop ────────────────────────────────────────────────────────
let t=0;
function animate(){
  requestAnimationFrame(animate);
  t+=0.01;

  // Orbit camera
  camera.position.x = Math.sin(spherical.theta)*Math.sin(spherical.phi)*spherical.r;
  camera.position.y = Math.cos(spherical.phi)*spherical.r;
  camera.position.z = Math.cos(spherical.theta)*Math.sin(spherical.phi)*spherical.r;
  camera.lookAt(0,1,0);

  // Gentle float animations
  if(deviceObjects['SmartPlug'])
    deviceObjects['SmartPlug'].group.position.y = 0.5 + Math.sin(t*1.2)*0.02;
  if(deviceObjects['TemperatureSensor'])
    deviceObjects['TemperatureSensor'].ring.rotation.y = t*0.8;

  // TV flicker when on
  const tv = deviceObjects['SmartTV'];
  if(tv && tv.screen.material.emissiveIntensity > 0.1){
    tv.screen.material.emissiveIntensity = 0.6+Math.sin(t*8)*0.2;
    tv.light.intensity = 1+Math.sin(t*8)*0.3;
  }

  // Particle drift
  particles.rotation.y = t*0.02;

  renderer.render(scene, camera);
}
animate();

// ── UI Cards ──────────────────────────────────────────────────────────
const ICONS = {SmartPlug:'🔌', Camera:'📷', SmartTV:'📺', SmartMeter:'⚡', TemperatureSensor:'🌡️'};
let allEntities=[];

function renderCards(entities){
  allEntities=entities;
  const left  = document.getElementById('cards-left');
  const right = document.getElementById('cards-right');
  left.innerHTML=''; right.innerHTML='';
  document.getElementById('entity-count').textContent=entities.length+' ENTITIES';

  entities.forEach((e,i)=>{
    const card = document.createElement('div');
    card.className='device-card';
    card.dataset.type=e.type;

    const attrs = Object.entries(e)
      .filter(([k])=>!['id','type'].includes(k))
      .map(([k,v])=>{
        const val=v.value;
        let cls='attr-val';
        if(val===true||val==='on')  cls+=' on';
        if(val===false||val==='off')cls+=' off';
        if(k==='motionDetected'&&val===true) cls+=' motion';
        return `<span class="attr"><span class="attr-key">${k}:</span> <span class="${cls}">${
          typeof val==='boolean'?val.toString():val
        }</span></span>`;
      }).join('');

    card.innerHTML=`
      <div class="d-header">
        <span class="d-icon">${ICONS[e.type]||'▪'}</span>
        <span class="d-name">${e.type}</span>
        <span class="d-loc">${e.location?.value||''}</span>
      </div>
      <div class="d-attrs">${attrs}</div>`;

    card.addEventListener('click',()=>{
      document.querySelectorAll('.device-card').forEach(c=>c.classList.remove('active'));
      card.classList.add('active');
      zoomToDevice(e.type);
    });

    (i%2===0?left:right).appendChild(card);
  });
  applyState(entities);
}

function zoomToDevice(type){
  const positions={
    SmartPlug:        {theta:Math.PI*1.1, phi:1.0, r:12},
    Camera:           {theta:Math.PI*0.4, phi:0.6, r:10},
    SmartTV:          {theta:Math.PI*0.05,phi:0.8, r:12},
    SmartMeter:       {theta:Math.PI*1.4, phi:0.9, r:12},
    TemperatureSensor:{theta:Math.PI*0.2, phi:0.8, r:12},
  };
  const p=positions[type];
  if(p){spherical.theta=p.theta;spherical.phi=p.phi;spherical.r=p.r;}
}

// ── Data fetch ─────────────────────────────────────────────────────────
async function fetchData(){
  try{
    const r=await fetch('/api/entities');
    const data=await r.json();
    if(Array.isArray(data)) renderCards(data);
  }catch(e){console.warn('Fetch error',e)}
}

// Clock
function updateClock(){
  document.getElementById('clock').textContent=new Date().toLocaleTimeString();
}
setInterval(updateClock,1000);
updateClock();

fetchData();
setInterval(fetchData,3000);
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
    except Exception as e:
        return jsonify([])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
