<script setup>
import {ref,onActivated,onDeactivated,onBeforeUnmount} from 'vue';
import {scripts} from '../data';
const frames=[{name:'字溯 · 汉字时光馆',title:'从一刀一凿，到笔墨千年',description:'一座可以漫游的汉字博物馆',glyph:'字溯'},...scripts.map(s=>({...s,title:s.name+' · '+s.title})),{name:'AI 书法问答',title:'不只看见，还可以继续追问',description:'从汉字源流到临习观察，与书法伴学一起探索。',glyph:'问'}];
const current=ref(0);let timer;
function start(){clearInterval(timer);timer=setInterval(()=>{if(!document.hidden)current.value=(current.value+1)%frames.length},3000)}
function select(index){current.value=(index+frames.length)%frames.length;start()}
onActivated(start);onDeactivated(()=>clearInterval(timer));onBeforeUnmount(()=>clearInterval(timer));
</script>
<template><section class="cover-carousel" aria-label="首页、六类字体和 AI 书法问答主题轮播"><article v-for="(frame,i) in frames" :key="i" :class="['cover-frame','cover-theme-'+i,{visible:current===i}]" :aria-hidden="current!==i"><div class="cover-texture"></div><img v-if="i===1" class="cover-bone" src="/images/reference-oracle-bone.webp" alt=""><span v-else class="cover-calligraphy" aria-hidden="true">{{frame.glyph}}</span><div class="cover-shade"></div><div class="cover-caption"><span class="cover-label">字溯 · {{i===0?'线上时光馆':frame.era||frame.name}}</span><h2>{{frame.title}}</h2><p>{{frame.description}}</p></div></article><div class="cover-navigation"><div class="cover-bars" aria-label="选择轮播画面"><button v-for="(frame,i) in frames" :key="i" :class="{active:current===i}" :aria-label="'第'+(i+1)+'幅：'+frame.name" :aria-current="current===i?'true':undefined" @click="select(i)"><span></span></button></div><div class="cover-arrows"><button aria-label="上一幅画面" @click="select(current-1)">←</button><button aria-label="下一幅画面" @click="select(current+1)">→</button></div></div></section><div class="cover-read-hint">向下浏览，走近文字的故事 <span>↓</span></div></template>


