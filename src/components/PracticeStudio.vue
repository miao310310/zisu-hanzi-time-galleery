<script setup>
import {computed, nextTick, onBeforeUnmount, onMounted, ref, watch} from 'vue';
import {practiceCharacters} from '../data';

const props=defineProps({modelValue:{type:String,default:'日'}});
const emit=defineEmits(['update:modelValue']);

const canvasRef=ref(null);
const activeStroke=ref(0);
const activeEvolution=ref(0);
const isStrokeDemo=ref(false);
const isEvolutionPlaying=ref(false);
const guideKey=ref(0);
const writtenStrokes=ref([]);
const status=ref('');
const reducedMotion=ref(false);
const canvasSize=360;

let activePointerId=null;
let currentDrawing=null;
let strokeTimer=null;
let evolutionTimer=null;
let resizeObserver=null;
let motionQuery=null;

const practiceItem=computed(()=>practiceCharacters.find(item=>item.char===props.modelValue)||practiceCharacters[0]);
const currentStroke=computed(()=>practiceItem.value.strokes[activeStroke.value]||practiceItem.value.strokes[0]);
const currentEvolution=computed(()=>practiceItem.value.stages[activeEvolution.value]||practiceItem.value.stages[0]);
const strokeStatus=computed(()=>writtenStrokes.value.length?`已试写 ${writtenStrokes.value.length} 笔；可撤销、清空或保存。`:'尚未落笔，先观察左侧范字，再在米字格中试写。');

function selectCharacter(character){
  emit('update:modelValue',character);
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
  status.value=count>1?`已写下一笔。${activeStroke.value<practiceItem.value.strokes.length-1?'可以继续下一笔，也可以回看范字。':'这个字的分步范字已完成，可继续调整自己的试笔。'}`:'这一笔太短了，试着慢慢写完整。';
  if(count>1&&activeStroke.value<practiceItem.value.strokes.length-1){
    window.setTimeout(()=>{activeStroke.value+=1;},180);
  }
}

function undoStroke(){
  if(!writtenStrokes.value.length)return;
  writtenStrokes.value=writtenStrokes.value.slice(0,-1);
  status.value='已撤销最后一笔。';
  redrawCanvas();
}

function clearCanvas(){
  writtenStrokes.value=[];
  status.value='画布已清空，可以重新试写。';
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

function selectEvolution(index){
  stopEvolutionDemo();
  activeEvolution.value=Math.max(0,Math.min(index,practiceItem.value.stages.length-1));
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

function resetPractice(){
  stopStrokeDemo();
  stopEvolutionDemo();
  activeStroke.value=0;
  activeEvolution.value=0;
  writtenStrokes.value=[];
  status.value='';
  guideKey.value+=1;
  nextTick(redrawCanvas);
}

function updateMotionPreference(event){
  reducedMotion.value=event.matches;
  if(event.matches){
    stopStrokeDemo();
    stopEvolutionDemo();
  }
}

watch(()=>practiceItem.value.char,resetPractice);

onMounted(()=>{
  redrawCanvas();
  if('ResizeObserver' in window){
    resizeObserver=new ResizeObserver(redrawCanvas);
    resizeObserver.observe(canvasRef.value);
  }
  window.addEventListener('resize',redrawCanvas);
  motionQuery=window.matchMedia('(prefers-reduced-motion: reduce)');
  reducedMotion.value=motionQuery.matches;
  motionQuery.addEventListener?.('change',updateMotionPreference);
});

onBeforeUnmount(()=>{
  stopStrokeDemo();
  stopEvolutionDemo();
  resizeObserver?.disconnect();
  window.removeEventListener('resize',redrawCanvas);
  motionQuery?.removeEventListener?.('change',updateMotionPreference);
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
        <div class="panel-label"><span id="reference-title">分步范字</span><small>第 {{activeStroke+1}} / {{practiceItem.strokes.length}} 笔</small></div>
        <div class="reference-paper">
          <svg viewBox="0 0 300 300" role="img" :aria-label="`${practiceItem.char}字第${activeStroke+1}笔范字示意`">
            <path class="grid-line" d="M18 18 H282 V282 H18 Z M150 18 V282 M18 150 H282 M18 18 L282 282 M282 18 L18 282"/>
            <text x="150" y="188" class="reference-glyph">{{practiceItem.char}}</text>
            <path v-for="(stroke,index) in practiceItem.strokes" :key="`${practiceItem.char}-${guideKey}-${index}`" :d="stroke.path" pathLength="1" class="guide-stroke" :class="{complete:index<activeStroke,'is-current':index===activeStroke,'is-demoing':isStrokeDemo&&index===activeStroke}"/>
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
        <p class="practice-disclaimer">范字为现代结构与笔势示意，不提供书法评分；请以老师指导和经核验的碑帖资料为准。</p>
      </section>
    </div>

    <section class="evolution-studio" aria-labelledby="evolution-title">
      <header class="evolution-heading">
        <div>
          <span class="sub">TRACE A CHARACTER</span>
          <h2 id="evolution-title">看「{{practiceItem.char}}」如何逐步演变</h2>
        </div>
        <button type="button" class="evolution-play" @click="toggleEvolutionDemo">{{isEvolutionPlaying?'暂停演变':reducedMotion?'下一阶段':'播放演变'}}</button>
      </header>

      <div class="evolution-tabs" role="tablist" aria-label="字形演变阶段">
        <button v-for="(stage,index) in practiceItem.stages" :key="stage.era" type="button" role="tab" :aria-selected="activeEvolution===index" :class="{active:activeEvolution===index}" @click="selectEvolution(index)">
          <span>0{{index+1}}</span>
          <strong>{{stage.era}}</strong>
          <small>{{stage.period}}</small>
        </button>
      </div>

      <article class="evolution-focus" aria-live="polite">
        <div :class="['evolution-glyph',`glyph-${practiceItem.char}`,`stage-${activeEvolution}`]" aria-hidden="true">{{currentEvolution.glyph}}</div>
        <div class="evolution-copy">
          <span class="sub">0{{activeEvolution+1}} / {{currentEvolution.period}} · {{currentEvolution.era}}</span>
          <h3>{{activeEvolution===0?'从物象轮廓出发':activeEvolution===practiceItem.stages.length-1?'笔势仍要守住结构':'笔画与结构的重新组织'}}</h3>
          <p>{{currentEvolution.note}}</p>
          <p class="evolution-status">当前第 {{activeEvolution+1}} / {{practiceItem.stages.length}} 阶段。点击时间线可前后对照。</p>
        </div>
      </article>
      <p class="academic-note">说明：甲骨、金文字形为形意科普示意，并非器物原始字形或可用于考证的摹本；参赛定稿前应替换为团队已核验、标注来源的资料图。</p>
    </section>
  </section>
</template>

<style scoped>
.practice-studio{margin-top:38px;padding:36px;border:1px solid var(--line);border-radius:20px;background:#f4f0e7}.studio-heading,.evolution-heading{display:flex;align-items:end;justify-content:space-between;gap:28px}.studio-heading h2,.evolution-heading h2{margin:9px 0 0;font-size:30px}.studio-heading>p{max-width:360px;margin:0;color:var(--muted);font-size:13px;line-height:1.9}.character-picker{display:flex;gap:9px;margin:28px 0;flex-wrap:wrap}.character-picker button{min-width:74px;border:1px solid var(--line);border-radius:10px;background:#fffdf8;color:var(--ink);padding:11px 14px;transition:background .2s,border-color .2s,color .2s}.character-picker button.active{background:var(--ink);border-color:var(--ink);color:#fff}.character-picker strong{display:block;font:25px/1.15 KaiTi,STKaiti,serif}.character-picker small{display:block;margin-top:5px;font-size:10px;letter-spacing:1px}.practice-workbench{display:grid;grid-template-columns:1fr 1fr;gap:18px}.reference-panel,.canvas-panel{padding:22px;border:1px solid var(--line);border-radius:14px;background:#fffdf8;min-width:0}.panel-label{display:flex;justify-content:space-between;gap:12px;align-items:center;font-size:13px;font-weight:650}.panel-label small{color:var(--muted);font-size:11px;font-weight:500}.reference-paper,.canvas-paper{position:relative;max-width:360px;aspect-ratio:1;margin:20px auto 0;background:#fbf8f0;overflow:hidden}.reference-paper svg,.canvas-paper canvas{display:block;width:100%;height:100%}.grid-line{fill:none;stroke:#cfbaa1;stroke-width:1;stroke-dasharray:5 5;opacity:.8}.reference-glyph{font-family:KaiTi,STKaiti,serif;font-size:210px;text-anchor:middle;fill:#233958;opacity:.06}.guide-stroke{fill:none;stroke:#aab3ad;stroke-width:10;stroke-linecap:round;stroke-linejoin:round;opacity:.35;transition:stroke .25s,opacity .25s,stroke-width .25s}.guide-stroke.complete{stroke:#78887f;opacity:.72}.guide-stroke.is-current{stroke:#8c3130;stroke-width:13;opacity:1}.guide-stroke.is-demoing{stroke-dasharray:1;stroke-dashoffset:1;animation:draw-stroke .92s ease forwards}@keyframes draw-stroke{to{stroke-dashoffset:0}}.stroke-note{display:flex;gap:15px;margin-top:18px}.stroke-number{display:grid;place-items:center;width:40px;height:40px;border-radius:50%;background:#e8ded0;color:#8c3130;font-size:12px;font-weight:700;flex:0 0 auto}.stroke-note h3{margin:0;font-size:17px}.stroke-note h3 small{font-size:11px;font-weight:400;color:var(--muted);margin-left:6px}.stroke-note p{margin:6px 0 0;color:var(--muted);font-size:12px;line-height:1.8}.stroke-controls,.canvas-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}.stroke-controls button,.canvas-actions button,.evolution-play{border:1px solid var(--line);border-radius:8px;background:transparent;color:var(--ink);padding:9px 12px;font-size:12px;transition:background .2s,border-color .2s,color .2s}.stroke-controls .stroke-demo,.evolution-play{background:var(--ink);border-color:var(--ink);color:#fff}.stroke-controls button:not(:disabled):hover,.canvas-actions button:not(:disabled):hover{background:#ece6d9}.canvas-paper{border:1px solid #d5c7b3;touch-action:none}.canvas-paper canvas{cursor:crosshair}.practice-seal{position:absolute;right:12px;bottom:12px;border:1px solid #8c3130;color:#8c3130;padding:4px;font:15px KaiTi,serif;opacity:.55}.practice-status{min-height:22px;margin:14px 0 0;color:var(--ink);font-size:12px;line-height:1.8}.practice-disclaimer{margin:6px 0 0;color:var(--muted);font-size:11px;line-height:1.8}.evolution-studio{margin-top:42px;padding-top:34px;border-top:1px solid var(--line)}.evolution-play{flex:0 0 auto}.evolution-tabs{display:grid;grid-template-columns:repeat(6,1fr);gap:7px;margin:24px 0}.evolution-tabs button{position:relative;min-height:76px;border:1px solid var(--line);border-radius:10px;background:#fffdf8;color:var(--muted);padding:10px 8px;text-align:left;transition:background .2s,border-color .2s,color .2s}.evolution-tabs button.active{background:#e5ece8;border-color:#698276;color:var(--ink)}.evolution-tabs span,.evolution-tabs small{display:block;font-size:10px}.evolution-tabs strong{display:block;margin:8px 0 4px;font-size:13px}.evolution-focus{display:grid;grid-template-columns:minmax(180px,.7fr) 1.3fr;gap:30px;align-items:center;padding:28px;border-radius:14px;background:#fffdf8}.evolution-glyph{display:grid;place-items:center;min-height:210px;border:1px dashed #cdbda8;background:radial-gradient(circle at center,#eee3d2 0,transparent 66%);font:110px/1 KaiTi,STKaiti,serif;color:#233958;letter-spacing:3px}.evolution-glyph.glyph-山.stage-0,.evolution-glyph.glyph-山.stage-1{font-size:59px;letter-spacing:-3px}.evolution-glyph.glyph-水.stage-0,.evolution-glyph.glyph-水.stage-1{font-size:100px}.evolution-glyph.glyph-木.stage-0,.evolution-glyph.glyph-木.stage-1{font-family:serif}.evolution-copy h3{margin:12px 0;font-size:23px}.evolution-copy p{margin:0;color:var(--muted);font-size:13px;line-height:1.9}.evolution-copy .evolution-status{margin-top:14px;color:var(--ink);font-size:12px}.academic-note{margin:14px 0 0;color:var(--muted);font-size:11px;line-height:1.8}.practice-studio button:focus-visible{outline:2px solid #8c3130;outline-offset:3px}.practice-studio button:disabled{opacity:.45;cursor:not-allowed}@media(max-width:760px){.practice-studio{margin-top:28px;padding:22px 16px;border-radius:15px}.studio-heading,.evolution-heading{display:block}.studio-heading h2,.evolution-heading h2{font-size:25px}.studio-heading>p{margin-top:14px}.character-picker{margin:22px 0}.character-picker button{flex:1;min-width:58px;padding:10px 6px}.practice-workbench{grid-template-columns:1fr;gap:14px}.reference-panel,.canvas-panel{padding:16px}.reference-paper,.canvas-paper{max-width:330px}.stroke-controls button,.canvas-actions button{flex:1;padding:10px 8px}.evolution-play{margin-top:15px}.evolution-tabs{display:flex;overflow:auto;padding-bottom:4px}.evolution-tabs button{min-width:92px;flex:0 0 92px}.evolution-focus{grid-template-columns:1fr;gap:20px;padding:20px}.evolution-glyph{min-height:180px}.evolution-copy h3{font-size:20px}}@media(prefers-reduced-motion:reduce){.guide-stroke,.character-picker button,.stroke-controls button,.canvas-actions button,.evolution-tabs button{transition:none}.guide-stroke.is-demoing{animation:none;stroke-dashoffset:0}}
</style>
