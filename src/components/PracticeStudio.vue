<script setup>
import {computed, nextTick, onActivated, onBeforeUnmount, onDeactivated, onMounted, ref, watch} from 'vue';
import {characters,practiceCharacters} from '../data';
import {loadPracticeDraft, savePracticeDraft} from '../services/practiceDrafts';
import {useLibrary} from '../stores/library';

const props=defineProps({modelValue:{type:String,default:'日'}});
const emit=defineEmits(['update:modelValue']);
const lib=useLibrary();

const canvasRef=ref(null);
const activeStroke=ref(0);
const activeEvolution=ref(0);
const isStrokeDemo=ref(false);
const isEvolutionPlaying=ref(false);
const guideKey=ref(0);
const writtenStrokes=ref([]);
const status=ref('');
const draftNotice=ref('试笔草稿仅保存在当前浏览器，不会上传。');
const reducedMotion=ref(false);
const evolutionInput=ref(props.modelValue);
const evolutionNotice=ref('');
const canvasSize=360;

let activePointerId=null;
let currentDrawing=null;
let strokeTimer=null;
let evolutionTimer=null;
let resizeObserver=null;
let motionQuery=null;
let strokeAdvanceTimer=null;
let canvasTracking=false;
let motionTracking=false;

const practiceItem=computed(()=>practiceCharacters.find(item=>item.char===props.modelValue)||practiceCharacters[0]);
const currentStroke=computed(()=>practiceItem.value.strokes[activeStroke.value]||practiceItem.value.strokes[0]);
const currentEvolution=computed(()=>practiceItem.value.stages[activeEvolution.value]||practiceItem.value.stages[0]);
const characterRecord=computed(()=>characters.find(item=>item.character===practiceItem.value.char));
const characterDescription=computed(()=>characterRecord.value?.description||'暂未收录这个汉字的形意说明。');
const strokeStatus=computed(()=>writtenStrokes.value.length?`已试写 ${writtenStrokes.value.length} 笔；可撤销、清空或保存。`:'尚未落笔，先观察左侧范字，再在米字格中试写。');

function selectCharacter(character){
  persistDraft();
  evolutionInput.value=character;
  evolutionNotice.value='';
  emit('update:modelValue',character);
}

function findEvolutionCharacter(){
  const chars=Array.from(evolutionInput.value.trim());
  if(chars.length!==1){
    evolutionNotice.value='请输入一个汉字；当前已收录「日、木」的完整演变资料。';
    return;
  }
  if(!practiceCharacters.some(item=>item.char===chars[0])){
    evolutionNotice.value=`「${chars[0]}」暂未收录完整演变资料；当前可探索「日、木」。`;
    return;
  }
  selectCharacter(chars[0]);
}

function toggleEvolutionSave(){
  lib.toggle(practiceItem.value.char);
}

function stopStrokeDemo(){
  isStrokeDemo.value=false;
  if(strokeTimer){
    window.clearTimeout(strokeTimer);
    strokeTimer=null;
  }
}

function stopEvolutionDemo(){
  isEvolutionPlaying.value=false;
  if(evolutionTimer){
    window.clearTimeout(evolutionTimer);
    evolutionTimer=null;
  }
}

function stopStrokeAdvance(){
  if(strokeAdvanceTimer){
    window.clearTimeout(strokeAdvanceTimer);
    strokeAdvanceTimer=null;
  }
}

function browserStorage(){
  try{
    return window.localStorage;
  }catch{
    return null;
  }
}

function persistDraft(){
  const result=savePracticeDraft(browserStorage(),practiceItem.value.char,writtenStrokes.value);
  if(!result.available){
    draftNotice.value='浏览器当前不允许保存本机草稿；你仍可将试笔保存为 PNG。';
    return false;
  }
  draftNotice.value='试笔草稿仅保存在当前浏览器，不会上传。';
  return true;
}

function restoreDraft(){
  const result=loadPracticeDraft(browserStorage(),practiceItem.value.char);
  writtenStrokes.value=result.strokes;
  if(!result.available){
    draftNotice.value='浏览器当前不允许读取本机草稿；你仍可在此试笔并保存为 PNG。';
    return;
  }
  draftNotice.value='试笔草稿仅保存在当前浏览器，不会上传。';
  if(result.strokes.length){
    status.value=`已恢复「${practiceItem.value.char}」的上次试笔草稿。`;
  }
}

function prepareCanvas(){
  const canvas=canvasRef.value;
  if(!canvas)return null;
  const rect=canvas.getBoundingClientRect();
  const cssSize=Math.min(rect.width,rect.height);
  if(!cssSize)return null;
  const pixelRatio=Math.min(window.devicePixelRatio||1,2);
  const backingSize=Math.round(cssSize*pixelRatio);
  if(canvas.width!==backingSize||canvas.height!==backingSize){
    canvas.width=backingSize;
    canvas.height=backingSize;
  }
  const context=canvas.getContext('2d');
  context.setTransform(backingSize/canvasSize,0,0,backingSize/canvasSize,0,0);
  return context;
}

function drawPaper(context){
  context.clearRect(0,0,canvasSize,canvasSize);
  context.fillStyle='#fffdf8';
  context.fillRect(0,0,canvasSize,canvasSize);
  context.strokeStyle='rgba(140,49,48,.24)';
  context.lineWidth=1;
  context.setLineDash([6,6]);
  context.strokeRect(22,22,canvasSize-44,canvasSize-44);
  context.beginPath();
  context.moveTo(canvasSize/2,22);
  context.lineTo(canvasSize/2,canvasSize-22);
  context.moveTo(22,canvasSize/2);
  context.lineTo(canvasSize-22,canvasSize/2);
  context.moveTo(22,22);
  context.lineTo(canvasSize-22,canvasSize-22);
  context.moveTo(canvasSize-22,22);
  context.lineTo(22,canvasSize-22);
  context.stroke();
  context.setLineDash([]);
  context.fillStyle='rgba(35,57,88,.11)';
  context.font='250px "STKaiti", "KaiTi", serif';
  context.textAlign='center';
  context.textBaseline='middle';
  context.fillText(practiceItem.value.char,canvasSize/2,canvasSize/2+14);
}

function drawStroke(context,points){
  if(!context||!points.length)return;
  context.save();
  context.strokeStyle='#233958';
  context.lineWidth=7;
  context.lineCap='round';
  context.lineJoin='round';
  context.beginPath();
  context.moveTo(points[0].x,points[0].y);
  if(points.length===1){
    context.lineTo(points[0].x+.01,points[0].y+.01);
  }else{
    points.slice(1).forEach(point=>context.lineTo(point.x,point.y));
  }
  context.stroke();
  context.restore();
}

function redrawCanvas(){
  const context=prepareCanvas();
  if(!context)return;
  drawPaper(context);
  writtenStrokes.value.forEach(points=>drawStroke(context,points));
}

function pointFromEvent(event){
  const rect=canvasRef.value.getBoundingClientRect();
  return {
    x:(event.clientX-rect.left)*canvasSize/rect.width,
    y:(event.clientY-rect.top)*canvasSize/rect.height
  };
}

function beginWriting(event){
  if(event.pointerType==='mouse'&&event.button!==0)return;
  if(activePointerId!==null)return;
  event.preventDefault();
  activePointerId=event.pointerId;
  event.currentTarget.setPointerCapture?.(event.pointerId);
  currentDrawing=[pointFromEvent(event)];
  writtenStrokes.value=[...writtenStrokes.value,currentDrawing];
  drawStroke(prepareCanvas(),currentDrawing);
  status.value='正在试写这一笔…';
}

function continueWriting(event){
  if(activePointerId!==event.pointerId||!currentDrawing)return;
  event.preventDefault();
  const point=pointFromEvent(event);
  const previous=currentDrawing[currentDrawing.length-1];
  currentDrawing.push(point);
  drawStroke(prepareCanvas(),[previous,point]);
}

function finishWriting(event){
  if(activePointerId!==event.pointerId)return;
  const count=currentDrawing?.length||0;
  if(event.currentTarget.hasPointerCapture?.(event.pointerId)){
    event.currentTarget.releasePointerCapture(event.pointerId);
  }
  activePointerId=null;
  currentDrawing=null;
  if(count<2){
    writtenStrokes.value=writtenStrokes.value.slice(0,-1);
    status.value='这一笔太短了，试着慢慢写完整。';
    redrawCanvas();
    return;
  }
  status.value=`已写下一笔。${activeStroke.value<practiceItem.value.strokes.length-1?'可以继续下一笔，也可以回看范字。':'这个字的分步范字已完成，可继续调整自己的试笔。'}`;
  persistDraft();
  if(activeStroke.value<practiceItem.value.strokes.length-1){
    stopStrokeAdvance();
    strokeAdvanceTimer=window.setTimeout(()=>{
      activeStroke.value+=1;
      strokeAdvanceTimer=null;
    },180);
  }
}

function undoStroke(){
  if(!writtenStrokes.value.length)return;
  writtenStrokes.value=writtenStrokes.value.slice(0,-1);
  status.value='已撤销最后一笔。';
  persistDraft();
  redrawCanvas();
}

function clearCanvas(){
  writtenStrokes.value=[];
  status.value='画布已清空，可以重新试写。';
  persistDraft();
  redrawCanvas();
}

function downloadPractice(){
  if(!writtenStrokes.value.length){
    status.value='先写下一笔，再保存你的试笔。';
    return;
  }
  const link=document.createElement('a');
  link.href=canvasRef.value.toDataURL('image/png');
  link.download=`${practiceItem.value.char}-字溯试笔.png`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  status.value='已生成 PNG 图片，可在浏览器下载记录中查看。';
}

function selectStroke(index){
  stopStrokeDemo();
  activeStroke.value=Math.max(0,Math.min(index,practiceItem.value.strokes.length-1));
  guideKey.value+=1;
}

function toggleStrokeDemo(){
  if(isStrokeDemo.value){
    stopStrokeDemo();
    return;
  }
  if(reducedMotion.value){
    selectStroke((activeStroke.value+1)%practiceItem.value.strokes.length);
    return;
  }
  activeStroke.value=0;
  guideKey.value+=1;
  isStrokeDemo.value=true;
  const advance=()=>{
    strokeTimer=window.setTimeout(()=>{
      if(!isStrokeDemo.value)return;
      if(activeStroke.value<practiceItem.value.strokes.length-1){
        activeStroke.value+=1;
        guideKey.value+=1;
        advance();
      }else{
        stopStrokeDemo();
      }
    },1150);
  };
  advance();
}

function selectEvolution(index, shouldFocus=false){
  stopEvolutionDemo();
  activeEvolution.value=Math.max(0,Math.min(index,practiceItem.value.stages.length-1));
  if(shouldFocus){
    requestAnimationFrame(()=>document.getElementById(`evolution-tab-${activeEvolution.value}`)?.focus());
  }
}

function moveEvolution(step){
  selectEvolution((activeEvolution.value+step+practiceItem.value.stages.length)%practiceItem.value.stages.length,true);
}

function toggleEvolutionDemo(){
  if(isEvolutionPlaying.value){
    stopEvolutionDemo();
    return;
  }
  if(reducedMotion.value){
    selectEvolution((activeEvolution.value+1)%practiceItem.value.stages.length);
    return;
  }
  activeEvolution.value=0;
  isEvolutionPlaying.value=true;
  const advance=()=>{
    evolutionTimer=window.setTimeout(()=>{
      if(!isEvolutionPlaying.value)return;
      if(activeEvolution.value<practiceItem.value.stages.length-1){
        activeEvolution.value+=1;
        advance();
      }else{
        stopEvolutionDemo();
      }
    },1450);
  };
  advance();
}

function scrubEvolution(event){
  selectEvolution(Number(event.target.value));
}

function resetPractice(){
  stopStrokeDemo();
  stopEvolutionDemo();
  stopStrokeAdvance();
  activeStroke.value=0;
  activeEvolution.value=0;
  writtenStrokes.value=[];
  status.value='';
  guideKey.value+=1;
  nextTick(()=>{
    restoreDraft();
    redrawCanvas();
  });
}

function updateMotionPreference(event){
  reducedMotion.value=event.matches;
  if(event.matches){
    stopStrokeDemo();
    stopEvolutionDemo();
  }
}

function startCanvasTracking(){
  if(canvasTracking)return;
  if('ResizeObserver' in window){
    resizeObserver=new ResizeObserver(redrawCanvas);
    resizeObserver.observe(canvasRef.value);
  }
  window.addEventListener('resize',redrawCanvas);
  canvasTracking=true;
}

function stopCanvasTracking(){
  if(!canvasTracking)return;
  resizeObserver?.disconnect();
  resizeObserver=null;
  window.removeEventListener('resize',redrawCanvas);
  canvasTracking=false;
}

function startMotionTracking(){
  if(motionTracking)return;
  motionQuery=window.matchMedia('(prefers-reduced-motion: reduce)');
  reducedMotion.value=motionQuery.matches;
  motionQuery.addEventListener?.('change',updateMotionPreference);
  motionTracking=true;
}

function stopMotionTracking(){
  if(!motionTracking)return;
  motionQuery?.removeEventListener?.('change',updateMotionPreference);
  motionQuery=null;
  motionTracking=false;
}

watch(()=>practiceItem.value.char,value=>{
  evolutionInput.value=value;
  resetPractice();
});

onMounted(()=>{
  restoreDraft();
  redrawCanvas();
  startCanvasTracking();
  startMotionTracking();
});

onActivated(()=>{
  startCanvasTracking();
  startMotionTracking();
  nextTick(redrawCanvas);
});

onDeactivated(()=>{
  stopStrokeDemo();
  stopEvolutionDemo();
  stopStrokeAdvance();
  persistDraft();
  stopCanvasTracking();
  stopMotionTracking();
});

onBeforeUnmount(()=>{
  stopStrokeDemo();
  stopEvolutionDemo();
  stopStrokeAdvance();
  persistDraft();
  stopCanvasTracking();
  stopMotionTracking();
});
</script>

<template>
  <section class="practice-studio" aria-labelledby="practice-studio-title">
    <header class="studio-heading">
      <div>
        <span class="sub">WRITE · WATCH · TRACE</span>
        <h2 id="practice-studio-title">范字试笔</h2>
      </div>
      <p>先看结构与笔势，再用鼠标、触控笔或手指慢慢写一遍。</p>
    </header>

    <div class="character-picker" role="tablist" aria-label="选择试笔汉字">
      <button v-for="item in practiceCharacters" :key="item.char" type="button" :class="{active:practiceItem.char===item.char}" :aria-selected="practiceItem.char===item.char" role="tab" @click="selectCharacter(item.char)">
        <strong>{{item.char}}</strong>
        <small>{{item.pinyin}}</small>
      </button>
    </div>

    <div class="practice-workbench">
      <section class="reference-panel" aria-labelledby="reference-title">
        <div class="panel-label"><span id="reference-title">楷体分步范字</span><small>第 {{activeStroke+1}} / {{practiceItem.strokes.length}} 笔</small></div>
        <div class="reference-paper">
          <svg viewBox="0 0 300 300" role="img" :aria-label="`${practiceItem.char}字第${activeStroke+1}笔范字示意`">
            <path class="grid-line" d="M18 18 H282 V282 H18 Z M150 18 V282 M18 150 H282 M18 18 L282 282 M282 18 L18 282"/>
            <text x="150" y="188" class="reference-glyph">{{practiceItem.char}}</text>
            <path v-for="(stroke,index) in practiceItem.strokes" :key="`${practiceItem.char}-${guideKey}-${index}`" :d="stroke.outline||stroke.path" class="guide-stroke" :style="{transformOrigin:stroke.origin||'center'}" :class="{complete:index<activeStroke,'is-current':index===activeStroke,'is-demoing':isStrokeDemo&&index===activeStroke}"/>
          </svg>
        </div>
        <div class="stroke-note">
          <span class="stroke-number">0{{activeStroke+1}}</span>
          <div>
            <h3>{{currentStroke.name}} <small>{{currentStroke.direction}}</small></h3>
            <p>{{currentStroke.tip}}</p>
          </div>
        </div>
        <div class="stroke-controls">
          <button type="button" @click="selectStroke(activeStroke-1)" :disabled="activeStroke===0">← 上一笔</button>
          <button type="button" @click="selectStroke(activeStroke+1)" :disabled="activeStroke===practiceItem.strokes.length-1">下一笔 →</button>
          <button type="button" class="stroke-demo" @click="toggleStrokeDemo">{{isStrokeDemo?'停止演示':'自动演示'}}</button>
        </div>
      </section>

      <section class="canvas-panel" aria-labelledby="canvas-title">
        <div class="panel-label"><span id="canvas-title">我的试笔</span><small>{{writtenStrokes.length}} 笔</small></div>
        <div class="canvas-paper">
          <canvas ref="canvasRef" aria-label="汉字米字格试笔画布，可使用鼠标、触控笔或手指书写" @pointerdown="beginWriting" @pointermove="continueWriting" @pointerup="finishWriting" @pointercancel="finishWriting"></canvas>
          <span class="practice-seal" aria-hidden="true">习</span>
        </div>
        <div class="canvas-actions">
          <button type="button" @click="undoStroke" :disabled="!writtenStrokes.length">撤销一笔</button>
          <button type="button" @click="clearCanvas" :disabled="!writtenStrokes.length">清空重写</button>
          <button type="button" @click="downloadPractice" :disabled="!writtenStrokes.length">保存试笔</button>
        </div>
        <p class="practice-status" role="status">{{status||strokeStatus}}</p>
        <p class="practice-disclaimer">范字为楷体风格的结构与笔势示意，不提供书法评分；请以老师指导和经核验的碑帖资料为准。</p>
        <p class="practice-draft-note">{{draftNotice}}</p>
      </section>
    </div>

    <section class="character-evolution" aria-labelledby="evolution-title">
      <form class="character-search" @submit.prevent="findEvolutionCharacter">
        <label for="evolution-character-input">输入一个汉字</label>
        <div class="character-search-row">
          <input id="evolution-character-input" v-model="evolutionInput" maxlength="1" inputmode="text" autocomplete="off" aria-describedby="evolution-search-help" placeholder="日或木">
          <button type="submit"><span aria-hidden="true">⌕</span> 寻字</button>
        </div>
        <div class="character-search-suggestions" aria-label="可探索的汉字">
          <span>试着寻</span>
          <button v-for="item in practiceCharacters" :key="`search-${item.char}`" type="button" :aria-pressed="practiceItem.char===item.char" @click="selectCharacter(item.char)">{{item.char}}</button>
        </div>
        <p id="evolution-search-help" class="character-search-help" :class="{error:evolutionNotice}" role="status">{{evolutionNotice||'当前已收录「日、木」的六阶段演变资料。'}}</p>
      </form>

      <article class="evolution-current" aria-labelledby="evolution-title">
        <div class="evolution-current-label" aria-hidden="true">本次寻字</div>
        <div class="evolution-current-main">
          <Transition name="evolution-current-glyph" mode="out-in">
            <span :key="`${practiceItem.char}-${activeEvolution}`" class="evolution-current-glyph" aria-hidden="true">{{currentEvolution.glyph}}</span>
          </Transition>
          <button type="button" class="evolution-save" @click="toggleEvolutionSave">{{lib.saved.includes(practiceItem.char)?'已收藏此字':'收藏此字'}}</button>
        </div>
        <p class="evolution-current-pinyin">{{practiceItem.pinyin}}</p>
        <h2 id="evolution-title">看「{{practiceItem.char}}」如何一路演变</h2>
        <p class="evolution-current-description">{{characterDescription}}</p>
      </article>

      <section class="evolution-playback" aria-label="字形演变播放控制">
        <div class="evolution-playback-actions">
          <button type="button" class="evolution-replay" @click="toggleEvolutionDemo">{{isEvolutionPlaying?'暂停演变':'↻ 重播演变'}}</button>
          <div class="evolution-step-actions">
            <button type="button" aria-label="上一阶段" :disabled="activeEvolution===0" @click="selectEvolution(activeEvolution-1)">‹</button>
            <button type="button" aria-label="下一阶段" :disabled="activeEvolution===practiceItem.stages.length-1" @click="selectEvolution(activeEvolution+1)">›</button>
          </div>
        </div>
        <div class="evolution-progress-copy" aria-live="polite">
          <strong>{{String(activeEvolution+1).padStart(2,'0')}} / {{String(practiceItem.stages.length).padStart(2,'0')}}</strong>
          <span>{{activeEvolution===0?'从象形线索出发':activeEvolution===practiceItem.stages.length-1?'六个阶段已看完，可重播或拖动回顾':'拖动时间，继续向下一阶段观察'}}</span>
        </div>
        <label class="evolution-range-label" for="evolution-range">拖动时间</label>
        <input id="evolution-range" class="evolution-range" type="range" min="0" :max="practiceItem.stages.length-1" :value="activeEvolution" :aria-valuetext="`${currentEvolution.era}，第${activeEvolution+1}阶段`" @input="scrubEvolution">
        <p class="evolution-stage-note"><b>{{currentEvolution.period}} · {{currentEvolution.era}}</b>{{currentEvolution.note}}</p>
      </section>

      <section class="evolution-gallery" aria-label="六个字形演变阶段">
        <button v-for="(stage,index) in practiceItem.stages" :id="`evolution-tab-${index}`" :key="stage.era" type="button" :class="{active:activeEvolution===index}" :aria-pressed="activeEvolution===index" @click="selectEvolution(index)" @keydown.left.prevent="moveEvolution(-1)" @keydown.right.prevent="moveEvolution(1)" @keydown.home.prevent="selectEvolution(0,true)" @keydown.end.prevent="selectEvolution(practiceItem.stages.length-1,true)">
          <span class="evolution-gallery-period">{{stage.period}}</span>
          <span :class="['evolution-gallery-glyph',`glyph-${practiceItem.char}`,`stage-${index}`]" aria-hidden="true">{{stage.glyph}}</span>
          <strong>{{stage.era}}</strong>
          <small>{{index===0?'起点':index===practiceItem.stages.length-1?'流变':`第 ${index+1} 站`}}</small>
        </button>
      </section>
      <p class="academic-note">说明：甲骨、金文字形为形意科普示意，并非器物原始字形或可用于考证的摹本；参赛定稿前应替换为团队已核验、标注来源的资料图。</p>
    </section>
  </section>
</template>

<style scoped>
.practice-studio{margin-top:38px;padding:36px;border:1px solid var(--line);border-radius:20px;background:#f4f0e7}.studio-heading,.evolution-heading{display:flex;align-items:end;justify-content:space-between;gap:28px}.studio-heading h2,.evolution-heading h2{margin:9px 0 0;font-size:30px}.studio-heading>p{max-width:360px;margin:0;color:var(--muted);font-size:13px;line-height:1.9}.character-picker{display:flex;gap:9px;margin:28px 0;flex-wrap:wrap}.character-picker button{min-width:74px;border:1px solid var(--line);border-radius:10px;background:#fffdf8;color:var(--ink);padding:11px 14px;transition:background .2s,border-color .2s,color .2s}.character-picker button.active{background:var(--ink);border-color:var(--ink);color:#fff}.character-picker strong{display:block;font:25px/1.15 KaiTi,STKaiti,serif}.character-picker small{display:block;margin-top:5px;font-size:10px;letter-spacing:1px}.practice-workbench{display:grid;grid-template-columns:1fr 1fr;gap:18px}.reference-panel,.canvas-panel{padding:22px;border:1px solid var(--line);border-radius:14px;background:#fffdf8;min-width:0}.panel-label{display:flex;justify-content:space-between;gap:12px;align-items:center;font-size:13px;font-weight:650}.panel-label small{color:var(--muted);font-size:11px;font-weight:500}.reference-paper,.canvas-paper{position:relative;max-width:360px;aspect-ratio:1;margin:20px auto 0;background:#fbf8f0;overflow:hidden}.reference-paper svg,.canvas-paper canvas{display:block;width:100%;height:100%}.grid-line{fill:none;stroke:#cfbaa1;stroke-width:1;stroke-dasharray:5 5;opacity:.8}.reference-glyph{font-family:KaiTi,STKaiti,serif;font-size:210px;text-anchor:middle;fill:#233958;opacity:.06}.guide-stroke{fill:none;stroke:#aab3ad;stroke-width:10;stroke-linecap:round;stroke-linejoin:round;opacity:.35;transition:stroke .25s,opacity .25s,stroke-width .25s}.guide-stroke.complete{stroke:#78887f;opacity:.72}.guide-stroke.is-current{stroke:#8c3130;stroke-width:13;opacity:1}.guide-stroke.is-demoing{stroke-dasharray:1;stroke-dashoffset:1;animation:draw-stroke .92s ease forwards}@keyframes draw-stroke{to{stroke-dashoffset:0}}.stroke-note{display:flex;gap:15px;margin-top:18px}.stroke-number{display:grid;place-items:center;width:40px;height:40px;border-radius:50%;background:#e8ded0;color:#8c3130;font-size:12px;font-weight:700;flex:0 0 auto}.stroke-note h3{margin:0;font-size:17px}.stroke-note h3 small{font-size:11px;font-weight:400;color:var(--muted);margin-left:6px}.stroke-note p{margin:6px 0 0;color:var(--muted);font-size:12px;line-height:1.8}.stroke-controls,.canvas-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}.stroke-controls button,.canvas-actions button,.evolution-play{border:1px solid var(--line);border-radius:8px;background:transparent;color:var(--ink);padding:9px 12px;font-size:12px;transition:background .2s,border-color .2s,color .2s}.stroke-controls .stroke-demo,.evolution-play{background:var(--ink);border-color:var(--ink);color:#fff}.stroke-controls button:not(:disabled):hover,.canvas-actions button:not(:disabled):hover{background:#ece6d9}.canvas-paper{border:1px solid #d5c7b3;touch-action:none}.canvas-paper canvas{cursor:crosshair}.practice-seal{position:absolute;right:12px;bottom:12px;border:1px solid #8c3130;color:#8c3130;padding:4px;font:15px KaiTi,serif;opacity:.55}.practice-status{min-height:22px;margin:14px 0 0;color:var(--ink);font-size:12px;line-height:1.8}.practice-disclaimer{margin:6px 0 0;color:var(--muted);font-size:11px;line-height:1.8}.evolution-studio{margin-top:42px;padding-top:34px;border-top:1px solid var(--line)}.evolution-play{flex:0 0 auto}.evolution-tabs{display:grid;grid-template-columns:repeat(6,1fr);gap:7px;margin:24px 0}.evolution-tabs button{position:relative;min-height:76px;border:1px solid var(--line);border-radius:10px;background:#fffdf8;color:var(--muted);padding:10px 8px;text-align:left;transition:background .2s,border-color .2s,color .2s}.evolution-tabs button.active{background:#e5ece8;border-color:#698276;color:var(--ink)}.evolution-tabs span,.evolution-tabs small{display:block;font-size:10px}.evolution-tabs strong{display:block;margin:8px 0 4px;font-size:13px}.evolution-focus{display:grid;grid-template-columns:minmax(180px,.7fr) 1.3fr;gap:30px;align-items:center;padding:28px;border-radius:14px;background:#fffdf8}.evolution-glyph{display:grid;place-items:center;min-height:210px;border:1px dashed #cdbda8;background:radial-gradient(circle at center,#eee3d2 0,transparent 66%);font:110px/1 KaiTi,STKaiti,serif;color:#233958;letter-spacing:3px}.evolution-glyph.glyph-山.stage-0,.evolution-glyph.glyph-山.stage-1{font-size:59px;letter-spacing:-3px}.evolution-glyph.glyph-水.stage-0,.evolution-glyph.glyph-水.stage-1{font-size:100px}.evolution-glyph.glyph-木.stage-0,.evolution-glyph.glyph-木.stage-1{font-family:serif}.evolution-copy h3{margin:12px 0;font-size:23px}.evolution-copy p{margin:0;color:var(--muted);font-size:13px;line-height:1.9}.evolution-copy .evolution-status{margin-top:14px;color:var(--ink);font-size:12px}.academic-note{margin:14px 0 0;color:var(--muted);font-size:11px;line-height:1.8}.practice-studio button:focus-visible{outline:2px solid #8c3130;outline-offset:3px}.practice-studio button:disabled{opacity:.45;cursor:not-allowed}@media(max-width:760px){.practice-studio{margin-top:28px;padding:22px 16px;border-radius:15px}.studio-heading,.evolution-heading{display:block}.studio-heading h2,.evolution-heading h2{font-size:25px}.studio-heading>p{margin-top:14px}.character-picker{margin:22px 0}.character-picker button{flex:1;min-width:58px;padding:10px 6px}.practice-workbench{grid-template-columns:1fr;gap:14px}.reference-panel,.canvas-panel{padding:16px}.reference-paper,.canvas-paper{max-width:330px}.stroke-controls button,.canvas-actions button{flex:1;padding:10px 8px}.evolution-play{margin-top:15px}.evolution-tabs{display:flex;overflow:auto;padding-bottom:4px}.evolution-tabs button{min-width:92px;flex:0 0 92px}.evolution-focus{grid-template-columns:1fr;gap:20px;padding:20px}.evolution-glyph{min-height:180px}.evolution-copy h3{font-size:20px}}@media(prefers-reduced-motion:reduce){.guide-stroke,.character-picker button,.stroke-controls button,.canvas-actions button,.evolution-tabs button{transition:none}.guide-stroke.is-demoing{animation:none;stroke-dashoffset:0}}
.practice-draft-note{margin:6px 0 0;color:var(--muted);font-size:11px;line-height:1.8}

/* 分笔范字使用封闭轮廓，避免把楷体笔画画成统一粗细的直线。 */
.reference-glyph{opacity:.1}
.guide-stroke{fill:#a8b5ae;stroke:none;opacity:.34;transform-box:fill-box;transform-origin:center;transition:fill .25s ease,opacity .25s ease,filter .25s ease,transform .25s ease}
.guide-stroke.complete{fill:#6f857a;opacity:.78;filter:drop-shadow(0 1px 0 rgba(34,56,50,.12))}
.guide-stroke.is-current{fill:#933a38;opacity:1;filter:drop-shadow(0 2px 1px rgba(102,38,34,.2))}
.guide-stroke.is-demoing{animation:ink-reveal .72s cubic-bezier(.19,.8,.32,1) both}
@keyframes ink-reveal{0%{opacity:.12;transform:scale(.72,.9)}60%{opacity:1;transform:scale(1.035,.985)}100%{opacity:1;transform:scale(1)}}
@media(prefers-reduced-motion:reduce){.guide-stroke.is-demoing{animation:none;transform:none}}

/* 演变区采用“六个时代卡 + 单一重点展”的阅读路径，避免同一信息重复堆叠。 */
.evolution-studio{
  margin-top:48px;
  padding:clamp(28px,4vw,48px);
  border:1px solid var(--line);
  border-radius:18px;
  background:#f1ede4;
}

.evolution-heading{
  align-items:center;
  padding-bottom:24px;
  border-bottom:1px solid var(--line);
}

.evolution-heading h2{
  margin-top:10px;
  font-size:clamp(30px,3.7vw,46px);
  line-height:1.3;
}

.evolution-play{
  min-height:48px;
  padding:12px 19px;
  border-radius:10px;
  font-weight:650;
  white-space:nowrap;
}

.evolution-tabs{
  gap:10px;
  margin:28px 0 34px;
}

.evolution-tabs button{
  min-height:116px;
  padding:17px 14px;
  border-radius:14px;
  background:#fffdf8;
}

.evolution-tabs button:hover{
  border-color:#91a49e;
  background:#f8fbf9;
  transform:translateY(-2px);
}

.evolution-tabs button.active{
  background:#e2ebe7;
  border-color:#6e897e;
}

.evolution-tabs strong{
  margin:15px 0 6px;
  color:var(--ink);
  font-size:18px;
}

.evolution-focus{
  grid-template-columns:minmax(260px,.82fr) minmax(0,1.18fr);
  gap:clamp(30px,5vw,68px);
  min-height:336px;
  padding:clamp(26px,4vw,42px);
  border:1px solid rgba(220,213,197,.72);
  border-radius:18px;
  background:#fffdf8;
}

.evolution-glyph{
  min-height:286px;
  font-size:clamp(112px,12vw,172px);
  border-color:#d9c4a8;
  background:radial-gradient(circle at center,#f0e6d6 0,transparent 68%);
}

.evolution-copy h3{
  margin:15px 0;
  font-size:clamp(25px,2.8vw,36px);
  line-height:1.34;
}

.evolution-copy>p{
  max-width:560px;
  font-size:14px;
  line-height:2;
}

.evolution-copy .evolution-status{
  margin-top:20px;
  font-size:12px;
}

.evolution-panel-enter-active,
.evolution-panel-leave-active{
  transition:opacity .2s ease,transform .2s ease;
}

.evolution-panel-enter-from,
.evolution-panel-leave-to{
  opacity:0;
  transform:translateY(6px);
}

@media(max-width:760px){
  .evolution-studio{margin-top:34px;padding:26px 16px;border-radius:15px}
  .evolution-heading{padding-bottom:20px}
  .evolution-heading h2{font-size:27px}
  .evolution-tabs{gap:8px;margin:22px 0 24px}
  .evolution-tabs button{min-width:104px;min-height:96px;padding:13px 11px}
  .evolution-tabs strong{margin-top:11px;font-size:16px}
  .evolution-focus{grid-template-columns:1fr;gap:23px;min-height:0;padding:20px}
  .evolution-glyph{min-height:210px;font-size:120px}
  .evolution-copy h3{font-size:25px}
}

/* “寻字”把演变阅读改为当前字、时间进度和六阶段总览三层，不再使用横排卡片与重点面板。 */
.character-evolution{
  margin:52px -36px -36px;
  overflow:hidden;
  border-top:1px solid var(--line);
  background:#f8f5ee;
}

.character-search{
  padding:clamp(28px,4vw,50px) clamp(24px,5vw,64px) 30px;
  background:#263f63;
  color:#fffdf8;
}

.character-search label{
  display:block;
  font-size:15px;
  font-weight:650;
  letter-spacing:.04em;
}

.character-search-row{
  display:grid;
  grid-template-columns:minmax(0,1fr) auto;
  gap:0;
  align-items:end;
  margin-top:16px;
  border-bottom:1px solid rgba(255,253,248,.82);
}

.character-search-row input{
  min-width:0;
  height:94px;
  border:0;
  outline:0;
  background:transparent;
  color:#fffdf8;
  font:clamp(54px,7vw,82px)/1 'Songti SC','SimSun',serif;
}

.character-search-row input::placeholder{color:#d8e0e8;opacity:.72}

.character-search-row button{
  align-self:stretch;
  min-width:146px;
  border:0;
  background:#fffdf8;
  color:#263f63;
  font-size:18px;
  font-weight:650;
}

.character-search-row button span{font-size:31px;line-height:0;vertical-align:-3px}

.character-search-suggestions{
  display:flex;
  flex-wrap:wrap;
  align-items:center;
  gap:12px;
  margin-top:27px;
}

.character-search-suggestions>span{margin-right:4px;color:#e2e9ef;font-size:13px}

.character-search-suggestions button{
  width:52px;
  height:52px;
  border:1px solid rgba(255,253,248,.84);
  background:transparent;
  color:#fffdf8;
  font:28px/1 'Songti SC','SimSun',serif;
  transition:background .2s,color .2s;
}

.character-search-suggestions button[aria-pressed=true],
.character-search-suggestions button:hover{background:#fffdf8;color:#263f63}

.character-search-help{
  min-height:20px;
  margin:15px 0 0;
  color:#d9e3ec;
  font-size:11px;
  line-height:1.7;
}

.character-search-help.error{color:#ffd8d2}

.evolution-current{
  position:relative;
  padding:clamp(36px,5vw,70px) clamp(24px,5vw,64px) 42px;
  background:#fffdf8;
}

.evolution-current-label{
  position:absolute;
  top:43px;
  left:clamp(18px,3vw,36px);
  color:var(--muted);
  font:15px/1.25 'Songti SC','SimSun',serif;
  letter-spacing:.08em;
  writing-mode:vertical-rl;
}

.evolution-current-main{
  display:flex;
  align-items:center;
  gap:clamp(22px,4vw,50px);
  margin-left:clamp(36px,6vw,92px);
}

.evolution-current-glyph{
  display:block;
  min-width:0;
  color:#202020;
  font:clamp(110px,16vw,200px)/.85 'Songti SC','SimSun',serif;
  letter-spacing:-.12em;
}

.evolution-save{
  align-self:center;
  min-height:56px;
  padding:13px 20px;
  border:1px solid #b8c2cd;
  background:transparent;
  color:#263f63;
  font-size:15px;
}

.evolution-save:hover{border-color:#263f63;background:#eef2f4}

.evolution-current-pinyin{
  margin:20px 0 4px clamp(36px,6vw,92px);
  color:#9e3834;
  font-size:18px;
  font-weight:700;
  letter-spacing:.08em;
}

.evolution-current h2{
  position:absolute;
  width:1px;
  height:1px;
  overflow:hidden;
  clip:rect(0 0 0 0);
  white-space:nowrap;
}

.evolution-current-description{
  max-width:580px;
  margin:0 0 0 clamp(36px,6vw,92px);
  color:#262626;
  font:clamp(18px,2.2vw,26px)/1.7 'Songti SC','SimSun',serif;
}

.evolution-playback{
  padding:30px clamp(24px,5vw,64px) 28px;
  border-top:1px solid var(--line);
  border-bottom:1px solid var(--line);
  background:#f8f5ee;
}

.evolution-playback-actions{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:18px;
}

.evolution-replay{
  min-height:58px;
  padding:13px 24px;
  border:0;
  background:#263f63;
  color:#fffdf8;
  font-size:16px;
  font-weight:650;
}

.evolution-replay:hover{background:#36557a}

.evolution-step-actions{display:flex;gap:10px}

.evolution-step-actions button{
  display:grid;
  width:58px;
  height:58px;
  place-items:center;
  border:1px solid #cbd1d2;
  background:#fffdf8;
  color:#263f63;
  font-size:42px;
  font-weight:300;
  line-height:1;
}

.evolution-step-actions button:hover:not(:disabled){border-color:#263f63;background:#eef2f4}

.evolution-step-actions button:disabled{opacity:.42;cursor:not-allowed}

.evolution-progress-copy{
  display:flex;
  align-items:baseline;
  flex-wrap:wrap;
  gap:14px;
  margin-top:24px;
}

.evolution-progress-copy strong{color:#9e3834;font:700 28px/1 'Songti SC','SimSun',serif}
.evolution-progress-copy span{color:var(--muted);font-size:13px;line-height:1.7}

.evolution-range-label{display:block;margin-top:23px;color:var(--muted);font-size:13px}

.evolution-range{
  display:block;
  width:100%;
  height:20px;
  margin-top:10px;
  accent-color:#9e3834;
  cursor:pointer;
}

.evolution-stage-note{
  margin:18px 0 0;
  color:var(--muted);
  font-size:12px;
  line-height:1.9;
}

.evolution-stage-note b{margin-right:10px;color:var(--ink)}

.evolution-gallery{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:clamp(18px,3vw,34px) clamp(12px,2.5vw,26px);
  padding:clamp(36px,5vw,64px) clamp(24px,5vw,64px) clamp(40px,6vw,76px);
  background:#fffdf8;
}

.evolution-gallery button{
  min-width:0;
  padding:0;
  border:0;
  background:transparent;
  color:#202020;
  text-align:center;
}

.evolution-gallery-period{
  display:block;
  min-height:22px;
  margin-bottom:10px;
  color:var(--muted);
  font:600 13px/1.5 'Songti SC','SimSun',serif;
}

.evolution-gallery-glyph{
  display:grid;
  min-height:clamp(142px,18vw,226px);
  place-items:center;
  border:1px solid #cfd2d1;
  background:#fbf9f4;
  color:#202020;
  font:clamp(62px,8vw,112px)/1 'Songti SC','SimSun',serif;
  transition:background .22s,color .22s,transform .22s,border-color .22s;
}

.evolution-gallery strong{
  display:block;
  margin-top:17px;
  font:650 clamp(21px,2.7vw,34px)/1.2 'Songti SC','SimSun',serif;
}

.evolution-gallery small{display:block;margin-top:7px;color:var(--muted);font-size:12px}

.evolution-gallery button:hover .evolution-gallery-glyph{border-color:#6d8791;transform:translateY(-3px)}

.evolution-gallery button.active .evolution-gallery-glyph{
  border-color:#263f63;
  background:#263f63;
  color:#fffdf8;
  transform:rotate(-3deg);
}

.evolution-gallery button.active strong{color:#9e3834}

.evolution-current-glyph-enter-active,
.evolution-current-glyph-leave-active{transition:opacity .16s ease,transform .16s ease}
.evolution-current-glyph-enter-from,.evolution-current-glyph-leave-to{opacity:0;transform:translateY(6px)}

.character-evolution button:focus-visible,
.character-evolution input:focus-visible{outline:2px solid #9e3834;outline-offset:4px}

@media(max-width:760px){
  .character-evolution{margin:40px -16px -22px}
  .character-search{padding:27px 22px 24px}
  .character-search-row input{height:74px;font-size:56px}
  .character-search-row button{min-width:104px;font-size:15px}
  .character-search-row button span{font-size:24px}
  .character-search-suggestions{gap:8px;margin-top:20px}
  .character-search-suggestions button{width:44px;height:44px;font-size:24px}
  .character-search-help{margin-top:11px}
  .evolution-current{padding:32px 22px 30px}
  .evolution-current-label{top:34px;left:17px;font-size:12px}
  .evolution-current-main{gap:16px;margin-left:32px}
  .evolution-current-glyph{font-size:112px}
  .evolution-save{min-height:46px;padding:10px 12px;font-size:12px}
  .evolution-current-pinyin,.evolution-current-description{margin-left:32px}
  .evolution-current-pinyin{margin-top:18px;font-size:15px}
  .evolution-current-description{font-size:18px}
  .evolution-playback{padding:22px}
  .evolution-replay{min-height:50px;padding:11px 16px;font-size:14px}
  .evolution-step-actions{gap:8px}
  .evolution-step-actions button{width:50px;height:50px;font-size:34px}
  .evolution-progress-copy{gap:10px;margin-top:20px}
  .evolution-progress-copy strong{font-size:24px}
  .evolution-gallery{gap:28px 14px;padding:34px 22px 44px}
  .evolution-gallery-glyph{min-height:118px;font-size:58px}
  .evolution-gallery strong{margin-top:12px;font-size:21px}
  .evolution-gallery small{font-size:10px}
}
</style>
