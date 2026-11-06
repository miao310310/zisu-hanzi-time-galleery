<script setup>
import {ref} from 'vue';
import HeroCarousel from '../components/HeroCarousel.vue';
import ObservationLab from '../components/ObservationLab.vue';
import {scripts,characters} from '../data';
import {useLibrary} from '../stores/library';
const lib=useLibrary(),active=ref(0);
const daily=characters[Math.floor(Date.now()/86400000)%characters.length];
function enterTimeline(){document.getElementById('timeline')?.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'})}
</script>
<template>
<div class="home-heading"><div><span class="sub">ZISU / DIGITAL CULTURE MUSEUM</span><h1>让文字的来处，成为新的发现。</h1></div><RouterLink to="/about">认识字溯 ↗</RouterLink></div><HeroCarousel/><div class="journey-strip"><RouterLink to="/scripts"><span>01</span><div><b>进入六境</b><small>沿书体认识文字</small></div><i>↗</i></RouterLink><RouterLink to="/explore"><span>02</span><div><b>寻一个字</b><small>从熟悉的字开始</small></div><i>↗</i></RouterLink><RouterLink to="/study"><span>03</span><div><b>积累与练习</b><small>把观察变成收获</small></div><i>↗</i></RouterLink></div>
<section class="origin-section"><div><span class="sub">字有来处 / THE ORIGIN OF CHARACTERS</span><h2>见字，<br>也见时间。</h2></div><p>文字在甲骨、青铜、石碑与纸张之间留下不同的面貌。以六类代表性字体为线索，慢慢看、细细读，在一次次观察与追问中，走近汉字的来处。</p></section>
<section class="daily-section"><div class="daily-glyph"><small>每日一字 · {{new Date().getMonth()+1}}月{{new Date().getDate()}}日</small><span>{{daily.character}}</span></div><div><span class="sub">CHARACTER OF THE DAY</span><h2>今日，从「{{daily.character}}」开始。</h2><p>{{daily.description}}</p><div class="actions"><RouterLink class="underlink" :to="{path:'/explore',query:{char:daily.character}}">读它的故事 ↗</RouterLink><button class="textlink" :aria-pressed="lib.saved.includes(daily.character)" @click="lib.toggle(daily.character)">{{lib.saved.includes(daily.character)?'已收藏 −':'收藏此字 ＋'}}</button><RouterLink class="textlink" :to="{path:'/chat',query:{q:'请介绍'+daily.character+'字的形与意',char:daily.character}}">问一问 ↗</RouterLink></div><p v-if="lib.notice" role="status" class="quiet">{{lib.notice}}</p></div></section>
<section id="timeline" class="museum-timeline"><div class="heading"><div><span class="sub">A RIVER OF WRITING</span><h2>循字入史</h2></div><p>点击任一书体，展开一段笔墨旅程。</p></div><p class="quiet">各类书体的发展存在交叠，以下为概览线索。</p><article v-for="(s,i) in scripts" :key="s.name" :class="['timeline-row',{expanded:active===i}]"><div class="timeline-era"><span>{{s.era}}</span><small>0{{i+1}} / 六境</small></div><div class="timeline-body"><button class="timeline-toggle" :aria-expanded="active===i" :aria-controls="'era-'+i" @click="active=active===i?-1:i"><span class="timeline-number">0{{i+1}}</span><h3>{{s.name}}</h3><span class="timeline-motto">{{s.title}}</span><span>{{active===i?'−':'＋'}}</span></button><div v-if="active===i" :id="'era-'+i" class="timeline-detail"><p>{{s.description}}</p><RouterLink class="underlink" :to="'/scripts/'+i">查看{{s.name}}专题 ↗</RouterLink></div></div></article></section>
<ObservationLab/><section class="museum-portals"><RouterLink to="/explore" class="portal"><span class="sub">ONE CHARACTER, MANY STORIES</span><h2>一个字，<br>藏着怎样的故事。</h2><p>从日、山、水、木开始，读字义，观结构，留下你的发现。</p><span class="underlink">开始寻字 ↗</span></RouterLink><RouterLink to="/chat" class="portal portal-ink"><span class="portal-watermark" aria-hidden="true">问</span><span class="sub">YOUR LEARNING COMPANION</span><h2>不只看见，<br>还可以继续追问。</h2><p>带着正在浏览的字体进入对话，探索汉字源流与临习入门。</p><span class="underlink">向字溯提问 ↗</span></RouterLink></section>
</template>



