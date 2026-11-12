<script setup>
import {scripts} from '../data';
</script>
<template><section class="section"><span class="sub">六种书体 / SIX CHAPTERS</span><h1>历代字体</h1><p class="intro">从甲骨、青铜到纸上的笔墨，选择一个专题，继续向下阅读。</p><div class="cards"><RouterLink v-for="(s,i) in scripts" :key="s.name" class="card script-index-card" :to="'/scripts/'+i"><div class="script-card-poster"><img :src="s.poster" :alt="`${s.name}专题海报`" loading="lazy" decoding="async"></div><div><small>{{s.era}}</small><h3>{{s.name}} · {{s.title}}</h3><p>{{s.description}}</p><p>进入专题 ↗</p></div></RouterLink></div><p class="quiet">年代仅为概览，各书体发展存在交叠。行书、草书为不同书体，此处合为一个浏览入口。</p></section></template>
