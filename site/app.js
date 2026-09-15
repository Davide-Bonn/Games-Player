// ══════════════════════════════════════════════
//  Games Player – Web Version
// ══════════════════════════════════════════════

// ── Config ──
const GESTURE_LIST = [
  "pinch_index","pinch_middle","left_blink","right_blink","both_blink","mouth_open","mouth_close"
];
const GESTURE_LABELS = {
  pinch_index:"Thumb + Index Pinch", pinch_middle:"Thumb + Middle Pinch",
  left_blink:"Left Eye Blink", right_blink:"Right Eye Blink",
  both_blink:"Both Eyes Blink", mouth_open:"Open Mouth", mouth_close:"Close Mouth"
};
const GESTURE_DESCS = {
  pinch_index:"Touch your thumb tip to your index finger tip",
  pinch_middle:"Touch your thumb tip to your middle finger tip",
  left_blink:"Close only your left eye",right_blink:"Close only your right eye",
  both_blink:"Close both eyes briefly",mouth_open:"Open your mouth wide",
  mouth_close:"Close your mouth after opening it"
};
const GESTURE_TIPS = {
  pinch_index:"Hold your hand up clearly and slowly bring thumb and index together",
  pinch_middle:"Keep index finger extended while touching thumb to middle finger",
  left_blink:"Try to close just your left eye - keep the right one open",
  right_blink:"Close just your right eye - keep the left one open",
  both_blink:"Close both eyes at the same time for a brief moment",
  mouth_open:"Open your mouth wide - like you're saying 'aah'",
  mouth_close:"Open your mouth first, then close it - the close triggers the action"
};
const ACTIONS = ["JUMP","SLIDE","LEFT","RIGHT","NONE"];
const ACTION_LABELS = {JUMP:"Jump",SLIDE:"Slide / Duck",LEFT:"Move Left",RIGHT:"Move Right",NONE:"Not Assigned"};
const DEFAULT_MAP = {
  pinch_index:"JUMP",pinch_middle:"SLIDE",left_blink:"LEFT",
  right_blink:"RIGHT",both_blink:"NONE",mouth_open:"NONE",mouth_close:"NONE"
};

let config = JSON.parse(localStorage.getItem("gesture_config")) || {...DEFAULT_MAP};
let firstLaunch = localStorage.getItem("first_launch") !== "false";

// ── Camera / Gesture Detection ──
let cameraStream = null;
let handsDetector = null;
let faceMeshDetector = null;
let activeGestures = {};
let gestureCallbacks = [];
let mouthWasOpen = false;
let cooldowns = {};
const COOLDOWN_MS = 400;
const ACTIVE_MS = 500;

function getActiveGestures(){
  const now = Date.now();
  const s = new Set();
  for(const[g,t] of Object.entries(activeGestures)){if(now-t<ACTIVE_MS)s.add(g);}
  return s;
}

function emitGesture(gesture){
  const now = Date.now();
  if(now-(cooldowns[gesture]||0)<COOLDOWN_MS) return;
  cooldowns[gesture]=now;
  activeGestures[gesture]=now;
  const action = config[gesture];
  if(action && action!=="NONE"){
    for(const cb of gestureCallbacks) cb(action, gesture);
  }
}

async function initCamera(videoEl){
  try{
    cameraStream = await navigator.mediaDevices.getUserMedia({video:{facingMode:"user",width:640,height:480}});
    videoEl.srcObject = cameraStream;
    await videoEl.play();
  } catch(e){console.warn("Camera not available:",e);}
}

function stopCamera(){
  if(cameraStream){cameraStream.getTracks().forEach(t=>t.stop());cameraStream=null;}
}

async function initDetectors(videoEl){
  if(!window.Hands||!window.FaceMesh) {
    console.warn("MediaPipe not loaded yet");
    return;
  }
  // Hands
  handsDetector = new Hands({locateFile:f=>`https://cdn.jsdelivr.net/npm/@mediapipe/hands/${f}`});
  handsDetector.setOptions({maxNumHands:1,modelComplexity:1,minDetectionConfidence:0.7,minTrackingConfidence:0.5});
  handsDetector.onResults(onHandResults);

  // Face Mesh
  faceMeshDetector = new FaceMesh({locateFile:f=>`https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${f}`});
  faceMeshDetector.setOptions({maxNumFaces:1,refineLandmarks:true,minDetectionConfidence:0.5,minTrackingConfidence:0.5});
  faceMeshDetector.onResults(onFaceResults);

  // Start detection loop
  detectLoop(videoEl);
}

async function detectLoop(videoEl){
  if(!cameraStream) return;
  try{
    if(handsDetector && videoEl.readyState>=2) await handsDetector.send({image:videoEl});
    if(faceMeshDetector && videoEl.readyState>=2) await faceMeshDetector.send({image:videoEl});
  }catch(e){}
  requestAnimationFrame(()=>detectLoop(videoEl));
}

function onHandResults(results){
  if(!results.multiHandLandmarks||!results.multiHandLandmarks.length) return;
  const lm = results.multiHandLandmarks[0];
  const thumbY=lm[4].y, indexY=lm[8].y, middleY=lm[12].y;
  if(Math.abs(thumbY-indexY)<0.045) emitGesture("pinch_index");
  if(Math.abs(thumbY-middleY)<0.045) emitGesture("pinch_middle");
}

function onFaceResults(results){
  if(!results.multiFaceLandmarks||!results.multiFaceLandmarks.length) return;
  const lm = results.multiFaceLandmarks[0];
  const leftGap=lm[145].y-lm[159].y;
  const rightGap=lm[373].y-lm[386].y;
  const leftClosed=leftGap<0.004, rightClosed=rightGap<0.004;

  if(leftClosed&&rightClosed) emitGesture("both_blink");
  else{if(leftClosed) emitGesture("left_blink"); if(rightClosed) emitGesture("right_blink");}

  const mouthGap=Math.abs(lm[13].y-lm[14].y);
  const mouthOpen=mouthGap>0.03;
  if(mouthOpen) emitGesture("mouth_open");
  if(mouthWasOpen&&!mouthOpen) emitGesture("mouth_close");
  mouthWasOpen=mouthOpen;
}

// ── UI Navigation ──
function showScreen(id){
  document.querySelectorAll(".screen").forEach(s=>s.classList.remove("active"));
  document.getElementById(id+"-screen").classList.add("active");
  if(id==="settings") renderSettings();
  if(id==="tutorial") startTutorial();
  if(id==="menu"){stopTutorial(); renderGesturePreview();}
}

// ── Settings ──
function renderSettings(){
  const list=document.getElementById("settings-list");
  list.innerHTML="";
  GESTURE_LIST.forEach(g=>{
    const action=config[g]||"NONE";
    const mapped=action!=="NONE";
    const row=document.createElement("div");
    row.className="setting-row";
    row.innerHTML=`
      <canvas class="setting-icon" width="44" height="44"></canvas>
      <div class="setting-info"><h3>${GESTURE_LABELS[g]}</h3><p>${GESTURE_DESCS[g]}</p></div>
      <button class="setting-action ${mapped?"mapped":"unmapped"}" data-gesture="${g}">${ACTION_LABELS[action]}</button>
    `;
    row.querySelector("button").addEventListener("click",()=>{
      const idx=ACTIONS.indexOf(config[g]||"NONE");
      config[g]=ACTIONS[(idx+1)%ACTIONS.length];
      renderSettings();
    });
    list.appendChild(row);
    drawGestureIconCanvas(row.querySelector("canvas"), g);
  });
}

function saveConfig(){localStorage.setItem("gesture_config",JSON.stringify(config));showScreen("menu");}
function resetConfig(){config={...DEFAULT_MAP};renderSettings();}

function renderGesturePreview(){
  const el=document.getElementById("gesture-preview");
  el.innerHTML="";
  GESTURE_LIST.forEach(g=>{
    const a=config[g];
    if(a&&a!=="NONE"){
      const chip=document.createElement("span");
      chip.className="gesture-chip";
      chip.innerHTML=`${GESTURE_LABELS[g]} <span class="chip-arrow">&rarr;</span> ${ACTION_LABELS[a]}`;
      el.appendChild(chip);
    }
  });
}

// ── Tutorial ──
let tutStep=0;
let tutCamActive=false;

function startTutorial(){
  tutStep=0;
  renderTutStep();
  const vid=document.getElementById("tut-video");
  if(!tutCamActive){
    initCamera(vid).then(()=>{initDetectors(vid);tutCamActive=true;});
  }
  gestureCallbacks.push(onTutGesture);
}
function endTutorial(){
  gestureCallbacks=gestureCallbacks.filter(c=>c!==onTutGesture);
  showScreen("menu");
}
function stopTutorial(){
  gestureCallbacks=gestureCallbacks.filter(c=>c!==onTutGesture);
}
function tutPrev(){if(tutStep>0){tutStep--;renderTutStep();}}
function tutNext(){
  if(tutStep<GESTURE_LIST.length-1){tutStep++;renderTutStep();}
  else endTutorial();
}

function onTutGesture(action, gesture){
  if(gesture===GESTURE_LIST[tutStep]){
    const st=document.getElementById("tut-status");
    st.className="status-badge detected";
    st.querySelector(".status-text").textContent="Detected!";
  }
}

function renderTutStep(){
  const g=GESTURE_LIST[tutStep];
  const a=config[g]||"NONE";
  document.getElementById("tut-step-label").textContent=`Step ${tutStep+1} of ${GESTURE_LIST.length}`;
  document.getElementById("tut-gesture-name").textContent=GESTURE_LABELS[g];
  document.getElementById("tut-gesture-action").textContent=a!=="NONE"?`Mapped to: ${ACTION_LABELS[a]}`:"Not assigned (skip)";
  document.getElementById("tut-gesture-desc").textContent=GESTURE_DESCS[g];
  document.getElementById("tut-tip").textContent=GESTURE_TIPS[g];
  const st=document.getElementById("tut-status");
  st.className="status-badge";
  st.querySelector(".status-text").textContent="Try the gesture now...";

  // Dots
  const dots=document.getElementById("tut-dots");
  dots.innerHTML="";
  for(let i=0;i<GESTURE_LIST.length;i++){
    const d=document.createElement("div");
    d.className="dot"+(i===tutStep?" active":i<tutStep?" done":"");
    dots.appendChild(d);
  }

  // Nav buttons
  document.getElementById("tut-prev").style.visibility=tutStep>0?"visible":"hidden";
  const next=document.getElementById("tut-next");
  next.textContent=tutStep<GESTURE_LIST.length-1?"Next →":"Done";
  next.className=tutStep<GESTURE_LIST.length-1?"pill accent":"pill accent-green";

  // Icon
  drawGestureIconCanvas(document.getElementById("tut-icon"), g, true);
}

// ── Gesture Icon Drawing ──
function drawGestureIconCanvas(canvas, gesture, large=false){
  const ctx=canvas.getContext("2d");
  const w=canvas.width, h=canvas.height;
  ctx.clearRect(0,0,w,h);
  const cx=w/2, cy=h/2, r=large?35:16;

  ctx.strokeStyle="#636368"; ctx.lineWidth=large?2:1.5;
  ctx.fillStyle="#00e5ff";

  if(gesture.includes("blink")){
    ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();
    const le=cx-r*.4, re=cx+r*.4, ey=cy-r*.15;
    const lc=gesture==="left_blink"||gesture==="both_blink";
    const rc=gesture==="right_blink"||gesture==="both_blink";
    ctx.fillStyle="#fff";
    if(lc){ctx.strokeStyle="#00e5ff";ctx.lineWidth=large?3:2;ctx.beginPath();ctx.moveTo(le-r*.25,ey);ctx.lineTo(le+r*.25,ey);ctx.stroke();}
    else{ctx.beginPath();ctx.arc(le,ey,r*.18,0,Math.PI*2);ctx.fill();ctx.fillStyle="#0a0a0f";ctx.beginPath();ctx.arc(le,ey,r*.08,0,Math.PI*2);ctx.fill();}
    ctx.fillStyle="#fff";
    if(rc){ctx.strokeStyle="#00e5ff";ctx.lineWidth=large?3:2;ctx.beginPath();ctx.moveTo(re-r*.25,ey);ctx.lineTo(re+r*.25,ey);ctx.stroke();}
    else{ctx.beginPath();ctx.arc(re,ey,r*.18,0,Math.PI*2);ctx.fill();ctx.fillStyle="#0a0a0f";ctx.beginPath();ctx.arc(re,ey,r*.08,0,Math.PI*2);ctx.fill();}
    ctx.strokeStyle="#636368";ctx.lineWidth=1;ctx.beginPath();ctx.arc(cx,cy+r*.25,r*.2,0,Math.PI);ctx.stroke();
  } else if(gesture==="mouth_open"){
    ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();
    ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(cx-r*.3,cy-r*.2,r*.15,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.arc(cx+r*.3,cy-r*.2,r*.15,0,Math.PI*2);ctx.fill();
    ctx.fillStyle="#00e5ff";ctx.beginPath();ctx.ellipse(cx,cy+r*.25,r*.25,r*.3,0,0,Math.PI*2);ctx.fill();
    ctx.fillStyle="#0a0a0f";ctx.beginPath();ctx.ellipse(cx,cy+r*.25,r*.15,r*.18,0,0,Math.PI*2);ctx.fill();
  } else if(gesture==="mouth_close"){
    ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();
    ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(cx-r*.3,cy-r*.2,r*.15,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.arc(cx+r*.3,cy-r*.2,r*.15,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle="#00e5ff";ctx.lineWidth=large?3:2;ctx.beginPath();ctx.moveTo(cx-r*.25,cy+r*.3);ctx.lineTo(cx+r*.25,cy+r*.3);ctx.stroke();
  } else if(gesture==="pinch_index"||gesture==="pinch_middle"){
    const clr=gesture==="pinch_index"?"#00e5ff":"#ff2d78";
    ctx.fillStyle=clr;ctx.beginPath();ctx.arc(cx,cy-r*.5,r*.2,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle="#636368";ctx.lineWidth=large?2.5:1.5;
    ctx.beginPath();ctx.moveTo(cx-r*.3,cy+r*.7);ctx.lineTo(cx,cy-r*.3);ctx.stroke();
    ctx.beginPath();ctx.moveTo(cx+r*.1,cy+r*.7);ctx.lineTo(cx,cy-r*.3);ctx.stroke();
    if(gesture==="pinch_middle"){ctx.beginPath();ctx.moveTo(cx-r*.4,cy-r*.1);ctx.lineTo(cx-r*.5,cy-r*.7);ctx.stroke();}
    ctx.beginPath();ctx.moveTo(cx+r*.3,cy+r*.3);ctx.lineTo(cx+r*.5,cy);ctx.stroke();
    ctx.beginPath();ctx.moveTo(cx+r*.4,cy+r*.5);ctx.lineTo(cx+r*.6,cy+r*.2);ctx.stroke();
  }
}

// ══════════════════════════════════════════════
//  GAMES
// ══════════════════════════════════════════════
let currentGame=null;
let gameRunning=false;
let useCamera=false;

function startGame(type, cam){
  useCamera=cam;
  showScreen("game");
  const canvas=document.getElementById("game-canvas");
  const panel=document.getElementById("game-cam-panel");

  if(cam){
    panel.classList.remove("hidden");
    const vid=document.getElementById("game-video");
    initCamera(vid).then(()=>initDetectors(vid));
    renderIndicators();
  } else {
    panel.classList.add("hidden");
  }

  gameRunning=true;
  gestureCallbacks.push(onGameGesture);
  if(type==="dino") currentGame=new DinoGame(canvas);
  else currentGame=new SubwayGame(canvas);
  currentGame.start();
}

function exitGame(){
  gameRunning=false;
  gestureCallbacks=gestureCallbacks.filter(c=>c!==onGameGesture);
  if(currentGame){currentGame.stop();currentGame=null;}
  showScreen("menu");
}

let gameActions=[];
function onGameGesture(action){gameActions.push(action);}

function renderIndicators(){
  const el=document.getElementById("gesture-indicators");
  el.innerHTML="<div style='font-size:12px;color:var(--text3);margin-bottom:4px'>GESTURES</div>";
  GESTURE_LIST.forEach(g=>{
    const a=config[g];
    if(!a||a==="NONE") return;
    const div=document.createElement("div");
    div.className="indicator";div.id=`ind-${g}`;
    div.innerHTML=`<span class="ind-dot"></span>${GESTURE_LABELS[g]} → ${ACTION_LABELS[a]}`;
    el.appendChild(div);
  });
}
function updateIndicators(){
  const active=getActiveGestures();
  GESTURE_LIST.forEach(g=>{
    const el=document.getElementById(`ind-${g}`);
    if(el) el.className=active.has(g)?"indicator active":"indicator";
  });
}

// ── Dino Game (Chrome T-Rex Style) ──
class DinoGame{
  constructor(canvas){
    this.canvas=canvas;this.ctx=canvas.getContext("2d");
    this.resize();this.frameId=null;
    this.hiScore=parseInt(localStorage.getItem("dino_hi"))||0;
    this.reset();
  }
  resize(){
    this.canvas.width=this.canvas.clientWidth;
    this.canvas.height=this.canvas.clientHeight;
    this.W=this.canvas.width;this.H=this.canvas.height;
    this.GROUND=this.H-60;
  }
  reset(){
    this.dino={x:60,y:this.GROUND,w:44,h:48,vy:0,jumping:false,ducking:false,frame:0};
    this.obstacles=[];this.clouds=[];this.speed=6;this.score=0;
    this.spawnTimer=0;this.gameOver=false;this.groundOff=0;this.started=false;
    for(let i=0;i<3;i++) this.clouds.push({x:100+Math.random()*this.W,y:30+Math.random()*80,w:46,s:0.5+Math.random()*0.5});
  }
  start(){this.reset();this.loop();}
  stop(){if(this.frameId) cancelAnimationFrame(this.frameId);}
  loop(){
    if(!gameRunning) return;
    this.update();this.draw();
    if(useCamera) updateIndicators();
    this.frameId=requestAnimationFrame(()=>this.loop());
  }
  update(){
    if(this.gameOver){
      if(this._restartPressed){this.reset();this._restartPressed=false;}
      return;
    }
    while(gameActions.length){
      const a=gameActions.shift();
      if((a==="UP"||a==="JUMP")&&!this.dino.jumping){this.started=true;this.dino.jumping=true;this.dino.vy=-13;this.dino.ducking=false;}
      if((a==="DOWN"||a==="SLIDE")&&!this.dino.jumping){this.started=true;this.dino.ducking=true;}
    }
    if(!this.started) return;
    this.dino.frame++;
    this.score++;this.speed=6+this.score*0.002;
    this.groundOff=(this.groundOff+this.speed)%20;
    if(this.dino.jumping){this.dino.y+=this.dino.vy;this.dino.vy+=0.7;if(this.dino.y>=this.GROUND){this.dino.y=this.GROUND;this.dino.jumping=false;this.dino.vy=0;}}
    this.spawnTimer++;
    if(this.spawnTimer>=Math.max(40,80-this.speed*2)){
      this.spawnTimer=0;
      if(Math.random()<0.25&&this.speed>8){
        const birdY=this.GROUND-[25,50,75][Math.floor(Math.random()*3)];
        this.obstacles.push({type:"bird",x:this.W+20,y:birdY,w:42,h:18,frame:0});
      } else {
        const shapes=[[18,36],[24,40],[16,48],[36,36]];
        const s=shapes[Math.floor(Math.random()*shapes.length)];
        this.obstacles.push({type:"cactus",x:this.W+20,y:this.GROUND-s[1],w:s[0],h:s[1]});
      }
    }
    this.obstacles.forEach(o=>{o.x-=this.speed+(o.type==="bird"?1:0);if(o.frame!==undefined)o.frame++;});
    this.obstacles=this.obstacles.filter(o=>o.x+o.w>-20);
    this.clouds.forEach(c=>{c.x-=c.s;if(c.x+c.w<0){c.x=this.W+50;c.y=30+Math.random()*80;}});
    const dr=this.dino.ducking?{x:this.dino.x,y:this.GROUND-22,w:55,h:22}:{x:this.dino.x,y:this.dino.y,w:this.dino.w,h:this.dino.h};
    for(const o of this.obstacles){
      if(dr.x+4<o.x+o.w&&dr.x+dr.w-4>o.x&&dr.y+4<o.y+o.h&&dr.y+dr.h>o.y){
        if(o.type==="bird"&&this.dino.ducking) continue;
        this.gameOver=true;
        if(this.score>this.hiScore){this.hiScore=this.score;localStorage.setItem("dino_hi",this.hiScore);}
      }
    }
    this.dino.ducking=false;
  }
  draw(){
    const ctx=this.ctx,W=this.W,H=this.H,G=this.GROUND;
    const FG="#535353",BG="#f7f7f7",LT="#a0a0a0";
    ctx.fillStyle=BG;ctx.fillRect(0,0,W,H);
    // Clouds
    ctx.fillStyle=LT;
    this.clouds.forEach(c=>{
      ctx.fillRect(c.x+10,c.y,26,6);ctx.fillRect(c.x+6,c.y+4,34,6);
      ctx.fillRect(c.x,c.y+8,46,6);ctx.fillRect(c.x+4,c.y+12,36,4);
    });
    // Ground line
    ctx.fillStyle=FG;ctx.fillRect(0,G,W,2);
    ctx.fillStyle=LT;
    for(let x=-this.groundOff;x<W;x+=20){
      const w=4+Math.abs(((x*7)%11)-5);
      ctx.fillRect(x,G+4+((x*3)%7),w,2);
    }
    // Obstacles
    this.obstacles.forEach(o=>{
      ctx.fillStyle=FG;
      if(o.type==="cactus"){
        const cx=o.x+o.w/2;
        ctx.fillRect(cx-3,o.y,6,o.h);
        if(o.w>20){
          ctx.fillRect(o.x,o.y+8,o.w,6);
          ctx.fillRect(o.x,o.y+8,4,o.h*0.4);
          ctx.fillRect(o.x+o.w-4,o.y+8,4,o.h*0.4);
        }
        if(o.h>40){
          ctx.fillRect(cx-8,o.y+o.h*0.5,4,o.h*0.3);
          ctx.fillRect(cx+4,o.y+o.h*0.3,4,o.h*0.35);
          ctx.fillRect(cx-8,o.y+o.h*0.5,12,4);
          ctx.fillRect(cx+4,o.y+o.h*0.3,8,4);
        }
      } else {
        const wing=(o.frame>>4)&1;
        const bx=o.x,by=o.y;
        ctx.fillRect(bx+6,by+6,30,8);
        ctx.fillRect(bx,by+8,6,4);
        ctx.fillRect(bx+10,by+4,8,4);
        if(wing){ctx.fillRect(bx+14,by-6,4,10);ctx.fillRect(bx+10,by-8,12,4);}
        else{ctx.fillRect(bx+14,by+14,4,8);ctx.fillRect(bx+10,by+20,12,4);}
        ctx.fillStyle=BG;ctx.fillRect(bx+30,by+8,4,3);
      }
    });
    // Dino
    const d=this.dino;
    ctx.fillStyle=FG;
    if(d.ducking){
      const dy=G-22;
      ctx.fillRect(d.x,dy,55,22);
      ctx.fillRect(d.x+45,dy-6,10,8);
      ctx.fillStyle=BG;ctx.fillRect(d.x+49,dy-4,4,3);
      ctx.fillStyle=FG;
      const lo=d.jumping?0:(d.frame>>3)&1;
      if(lo){ctx.fillRect(d.x+6,dy+22,6,8);ctx.fillRect(d.x+20,dy+22,6,0);}
      else{ctx.fillRect(d.x+6,dy+22,6,0);ctx.fillRect(d.x+20,dy+22,6,8);}
    } else {
      const dy=d.y;
      ctx.fillRect(d.x+8,dy,28,10);
      ctx.fillRect(d.x+4,dy+8,36,12);
      ctx.fillRect(d.x+28,dy-10,16,14);
      ctx.fillRect(d.x+24,dy-14,20,8);
      ctx.fillStyle=BG;ctx.fillRect(d.x+36,dy-12,6,4);
      ctx.fillStyle=FG;
      ctx.fillRect(d.x+14,dy+18,20,10);
      ctx.fillRect(d.x+8,dy+26,10,6);
      ctx.fillRect(d.x-2,dy+18,8,4);
      const lo=d.jumping?0:(d.frame>>3)&1;
      if(lo){ctx.fillRect(d.x+12,dy+28,6,10);ctx.fillRect(d.x+26,dy+28,6,4);}
      else{ctx.fillRect(d.x+12,dy+28,6,4);ctx.fillRect(d.x+26,dy+28,6,10);}
    }
    // Score
    ctx.fillStyle=FG;ctx.font="bold 16px 'Courier New',monospace";ctx.textAlign="right";
    const sc=String(this.score).padStart(5,"0");
    const hi=String(this.hiScore).padStart(5,"0");
    ctx.fillStyle=LT;ctx.fillText(`HI ${hi}`,W-90,30);
    ctx.fillStyle=FG;ctx.fillText(sc,W-20,30);
    ctx.textAlign="left";
    // Game over
    if(this.gameOver){
      ctx.fillStyle=FG;ctx.font="bold 24px 'Courier New',monospace";ctx.textAlign="center";
      ctx.fillText("G A M E   O V E R",W/2,H/2-30);
      // Restart icon (circular arrow)
      const rx=W/2,ry=H/2+10;
      ctx.strokeStyle=FG;ctx.lineWidth=3;
      ctx.beginPath();ctx.arc(rx,ry,16,0,Math.PI*1.5);ctx.stroke();
      ctx.fillStyle=FG;ctx.beginPath();ctx.moveTo(rx,ry-18);ctx.lineTo(rx+8,ry-12);ctx.lineTo(rx,ry-6);ctx.fill();
      ctx.fillStyle="#98989f";ctx.font="14px 'Courier New',monospace";
      ctx.fillText("ENTER to restart | ESC to close",W/2,H/2+50);
      ctx.textAlign="left";
    }
    // Waiting to start
    if(!this.started&&!this.gameOver){
      ctx.fillStyle=FG;ctx.font="16px 'Courier New',monospace";ctx.textAlign="center";
      ctx.fillText("Press SPACE or UP to start",W/2,H/2);
      ctx.textAlign="left";
    }
  }
}

// ── Subway Runner ──
class SubwayGame{
  constructor(canvas){
    this.canvas=canvas;this.ctx=canvas.getContext("2d");
    this.resize();this.frameId=null;this.reset();
  }
  resize(){
    this.canvas.width=this.canvas.clientWidth;this.canvas.height=this.canvas.clientHeight;
    this.W=this.canvas.width;this.H=this.canvas.height;
    this.LW=this.W/3;
    this.CENTERS=[this.LW/2, this.LW*1.5, this.LW*2.5];
  }
  reset(){
    this.lane=1;this.px=this.CENTERS[1];this.py=this.H-140;
    this.vy=0;this.jumping=false;this.sliding=false;this.slideTmr=0;
    this.obstacles=[];this.speed=5;this.score=0;this.spawnTmr=0;
    this.gameOver=false;this.groundOff=0;this.frame=0;
  }
  start(){this.reset();this.loop();}
  stop(){if(this.frameId) cancelAnimationFrame(this.frameId);}
  loop(){
    if(!gameRunning) return;
    this.update();this.draw();
    if(useCamera) updateIndicators();
    this.frameId=requestAnimationFrame(()=>this.loop());
  }
  update(){
    if(this.gameOver){if(this._restartPressed){this.reset();this._restartPressed=false;}return;}
    while(gameActions.length){
      const a=gameActions.shift();
      if((a==="UP"||a==="JUMP")&&!this.jumping&&!this.sliding){this.jumping=true;this.vy=-15;}
      if((a==="DOWN"||a==="SLIDE")&&!this.jumping&&!this.sliding){this.sliding=true;this.slideTmr=30;}
      if(a==="LEFT"&&this.lane>0) this.lane--;
      if(a==="RIGHT"&&this.lane<2) this.lane++;
    }
    this.frame++;this.score++;this.speed=5+this.score*0.001;
    this.groundOff=(this.groundOff+this.speed)%40;
    // Smooth lane
    this.px+=(this.CENTERS[this.lane]-this.px)*0.25;
    // Jump
    if(this.jumping){this.py+=this.vy;this.vy+=0.8;if(this.py>=this.H-140){this.py=this.H-140;this.jumping=false;this.vy=0;}}
    if(this.sliding){this.slideTmr--;if(this.slideTmr<=0)this.sliding=false;}
    // Spawn
    this.spawnTmr++;
    if(this.spawnTmr>=Math.max(35,70-this.speed*3)){
      this.spawnTmr=0;
      const n=this.speed>7&&Math.random()<0.35?2:1;
      const lanes=[...Array(3).keys()].sort(()=>Math.random()-0.5).slice(0,n);
      lanes.forEach(l=>{
        const types=this.speed<6.5?["barrier","barrier","overhead"]:["barrier","overhead","train"];
        const t=types[Math.floor(Math.random()*types.length)];
        let h=t==="barrier"?40:t==="overhead"?25:140;
        this.obstacles.push({type:t,lane:l,x:this.CENTERS[l],y:-h,w:t==="barrier"?50:this.LW-10,h,speed:this.speed});
      });
    }
    this.obstacles.forEach(o=>{o.y+=this.speed;});
    this.obstacles=this.obstacles.filter(o=>o.y<this.H+20);
    // Collision
    const pw=50,ph=this.sliding?30:70;
    const prx=this.px-pw/2,pry=(this.sliding?this.py+40:this.py);
    for(const o of this.obstacles){
      const ox=o.x-o.w/2;
      if(prx<ox+o.w&&prx+pw>ox&&pry<o.y+o.h&&pry+ph>o.y){
        if(o.type==="barrier"&&this.jumping&&this.py<this.H-170) continue;
        if(o.type==="overhead"&&this.sliding) continue;
        this.gameOver=true;
      }
    }
  }
  draw(){
    const ctx=this.ctx,W=this.W,H=this.H,LW=this.LW;
    ctx.fillStyle="#23192d";ctx.fillRect(0,0,W,H);
    // Lanes
    for(let i=0;i<3;i++){ctx.fillStyle=i%2===0?"#372d42":"#2d253a";ctx.fillRect(i*LW,0,LW,H);}
    // Lane dashes
    ctx.strokeStyle="#6e5590";ctx.lineWidth=3;
    for(let i=1;i<3;i++){const x=i*LW;for(let y=-40+(this.groundOff%40);y<H;y+=40){ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x,y+20);ctx.stroke();}}
    // Obstacles
    this.obstacles.forEach(o=>{
      const r={x:o.x-o.w/2,y:o.y,w:o.w,h:o.h};
      if(o.type==="barrier"){
        ctx.fillStyle="#ff3755";ctx.beginPath();ctx.roundRect(r.x,r.y,r.w,r.h,5);ctx.fill();
        ctx.strokeStyle="#fff";ctx.lineWidth=1;ctx.stroke();
      } else if(o.type==="overhead"){
        ctx.strokeStyle="#b49200";ctx.lineWidth=4;
        ctx.beginPath();ctx.moveTo(r.x+6,r.y+r.h);ctx.lineTo(r.x+6,r.y+r.h+55);ctx.stroke();
        ctx.beginPath();ctx.moveTo(r.x+r.w-6,r.y+r.h);ctx.lineTo(r.x+r.w-6,r.y+r.h+55);ctx.stroke();
        ctx.fillStyle="#ffc800";ctx.beginPath();ctx.roundRect(r.x,r.y,r.w,r.h,4);ctx.fill();
      } else {
        ctx.fillStyle="#8232dc";ctx.beginPath();ctx.roundRect(r.x,r.y,r.w,r.h,8);ctx.fill();
        ctx.fillStyle="#ff64c8";ctx.fillRect(r.x+3,r.y+r.h/2-5,r.w-6,10);
        ctx.fillStyle="#c8a0ff";
        for(let wy=r.y+18;wy<r.y+r.h-20;wy+=28){ctx.beginPath();ctx.roundRect(r.x+8,wy,14,12,3);ctx.fill();ctx.beginPath();ctx.roundRect(r.x+r.w-22,wy,14,12,3);ctx.fill();}
        ctx.strokeStyle="#c878ff";ctx.lineWidth=2;ctx.beginPath();ctx.roundRect(r.x,r.y,r.w,r.h,8);ctx.stroke();
      }
    });
    // Player
    const cx=this.px,py=this.py;
    if(this.sliding){
      ctx.fillStyle="#00aae0";ctx.beginPath();ctx.roundRect(cx-28,py+40,56,30,8);ctx.fill();
      ctx.strokeStyle="#ff50b4";ctx.lineWidth=2;ctx.beginPath();ctx.roundRect(cx-28,py+40,56,30,8);ctx.stroke();
    } else {
      const lo=this.jumping?0:(this.frame>>3)&1?5:0;
      ctx.fillStyle="#00d2ff";
      ctx.fillRect(cx-12,py+65,10,10+lo);ctx.fillRect(cx+2,py+65,10,10+(5-lo));
      ctx.beginPath();ctx.roundRect(cx-25,py+22,50,48,10);ctx.fill();
      ctx.fillStyle="#ff50b4";ctx.fillRect(cx-21,py+38,42,8);
      ctx.strokeStyle="#ff50b4";ctx.lineWidth=2;ctx.beginPath();ctx.roundRect(cx-25,py+22,50,48,10);ctx.stroke();
      // Head
      ctx.fillStyle="#00e6ff";ctx.beginPath();ctx.arc(cx,py+14,16,0,Math.PI*2);ctx.fill();
      ctx.strokeStyle="#ff50b4";ctx.lineWidth=2;ctx.beginPath();ctx.arc(cx,py+14,16,0,Math.PI*2);ctx.stroke();
      ctx.fillStyle="#ff50b4";ctx.beginPath();ctx.roundRect(cx-14,py,28,12,5);ctx.fill();
      // Eyes
      ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(cx-5,py+12,4,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(cx+5,py+12,4,0,Math.PI*2);ctx.fill();
      ctx.fillStyle="#1a1a1a";ctx.beginPath();ctx.arc(cx-4,py+12,2,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(cx+6,py+12,2,0,Math.PI*2);ctx.fill();
    }
    // HUD
    ctx.fillStyle="#ffdc32";ctx.font="bold 20px -apple-system,Segoe UI,sans-serif";ctx.textAlign="left";
    ctx.fillText(`Score: ${this.score}`,10,28);
    ctx.fillStyle="#a0a0a8";ctx.font="14px -apple-system,Segoe UI,sans-serif";ctx.fillText(`Speed: ${this.speed.toFixed(1)}`,10,48);
    if(this.gameOver){
      ctx.fillStyle="rgba(0,0,0,0.55)";ctx.fillRect(0,0,W,H);
      ctx.textAlign="center";ctx.fillStyle="#ff375f";ctx.font="bold 36px -apple-system,Segoe UI,sans-serif";ctx.fillText("GAME OVER",W/2,H/2-40);
      ctx.fillStyle="#fff";ctx.font="bold 24px -apple-system,Segoe UI,sans-serif";ctx.fillText(`Score: ${this.score}`,W/2,H/2+5);
      ctx.fillStyle="#98989f";ctx.font="16px -apple-system,Segoe UI,sans-serif";ctx.fillText("Press ENTER to restart | ESC to close",W/2,H/2+40);
      ctx.textAlign="left";
    }
  }
}

// ── Keyboard Input ──
document.addEventListener("keydown",e=>{
  if(!gameRunning||!currentGame) return;
  if(currentGame.gameOver){
    if(e.key==="Enter"){currentGame._restartPressed=true;e.preventDefault();}
    if(e.key==="Escape"){exitGame();e.preventDefault();}
    return;
  }
  switch(e.key){
    case"ArrowUp":case"w":case"W":case" ":gameActions.push("UP");e.preventDefault();break;
    case"ArrowDown":case"s":case"S":gameActions.push("DOWN");e.preventDefault();break;
    case"ArrowLeft":case"a":case"A":gameActions.push("LEFT");e.preventDefault();break;
    case"ArrowRight":case"d":case"D":gameActions.push("RIGHT");e.preventDefault();break;
    case"Escape":exitGame();e.preventDefault();break;
  }
});

// ── Init ──
renderGesturePreview();
if(firstLaunch){
  localStorage.setItem("first_launch","false");
  showScreen("tutorial");
}
