<script setup>
import {ref,computed,watch,onMounted,onBeforeUnmount} from 'vue';
import {useRoute,useRouter} from 'vue-router';
import {scripts} from '../data';
const route=useRoute(),router=useRouter();
const pages=[{name:'首页',path:'/'},...scripts.map((s,i)=>({name:s.name,path:'/scripts/'+i})),{name:'AI 书法问答',path:'/chat'}];
const current=computed(()=>pages.findIndex(p=>p.path===route.path));
const paused=ref(false),reading=ref(false),hidden=ref(document.hidden),progress=ref(0);
const running=computed(()=>current.value>=0&&!paused.value&&!reading.value&&!hidden.value);
let timer,lastTick=0,navigating=false;
function inspectScroll(){reading.value=window.scrollY>100}
function pauseForInteraction(event){if(event.target.closest('main')&&event.target.closest('button,a,input,textarea,select'))paused.value=true}
function visibility(){hidden.value=document.hidden;progress.value=0;lastTick=performance.now()}
async function move(index,manual=false){if(navigating)return;if(manual)paused.value=true;progress.value=0;navigating=true;try{await router.replace(pages[(index+pages.length)%pages.length].path)}finally{navigating=false;lastTick=performance.now()}}
function toggle(){if(running.value){paused.value=true;return}window.scrollTo({top:0,behavior:'instant'});reading.value=false;paused.value=false;progress.value=0;lastTick=performance.now()}
watch(()=>route.fullPath,()=>{progress.value=0;if(Object.keys(route.query).length)paused.value=true;lastTick=performance.now()});
onMounted(()=>{inspectScroll();if(Object.keys(route.query).length)paused.value=true;lastTick=performance.now();window.addEventListener('scroll',inspectScroll,{passive:true});document.addEventListener('visibilitychange',visibility);document.addEventListener('pointerdown',pauseForInteraction);document.addEventListener('focusin',pauseForInteraction);timer=setInterval(()=>{const now=performance.now(),elapsed=now-lastTick;lastTick=now;if(running.value&&!navigating){progress.value+=elapsed/3000;if(progress.value>=1)move(current.value+1)}else progress.value=0},50)});
onBeforeUnmount(()=>{clearInterval(timer);window.removeEventListener('scroll',inspectScroll);document.removeEventListener('visibilitychange',visibility);document.removeEventListener('pointerdown',pauseForInteraction);document.removeEventListener('focusin',pauseForInteraction)});
</script>
<template><aside v-if="current>=0" class="tour-controls" aria-label="八页循环导览"><div class="tour-status"><span>{{String(current+1).padStart(2,'0')}} / 08</span><span>{{running?'每 3 秒自动翻页':reading?'阅读中 · 已暂停':'已暂停 · 自由浏览'}}</span></div><div class="tour-buttons"><button aria-label="上一页" @click="move(current-1,true)">←</button><div class="tour-tabs"><button v-for="(page,i) in pages" :key="page.path" :class="{active:i===current}" :aria-current="i===current?'page':undefined" @click="move(i,true)">{{page.name}}</button></div><button aria-label="下一页" @click="move(current+1,true)">→</button><button class="tour-play" :aria-label="running?'暂停自动轮播':'回到顶部并播放轮播'" @click="toggle">{{running?'Ⅱ 暂停':'▶ 播放'}}</button></div><div class="tour-progress" aria-hidden="true"><span :style="{transform:`scaleX(${progress})`}"></span></div></aside></template>
