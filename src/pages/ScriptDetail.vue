<script setup>
import {computed} from 'vue';
import {useRoute} from 'vue-router';
import {scripts} from '../data';
import ArtworkGallery from '../components/ArtworkGallery.vue';
const route=useRoute();
const index=computed(()=>/^\d+$/.test(String(route.params.id))?Number(route.params.id):-1);
const item=computed(()=>scripts[index.value]);
function readMore(){document.getElementById('script-reading')?.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'})}
</script>
<template>
  <section v-if="item" class="detail-page">
    <div class="script-cover">
      <div class="script-cover-copy">
        <span class="sub">{{String(index+2).padStart(2,'0')}} / 08 · {{item.era}}</span>
        <h1>{{item.name}}</h1>
        <h2>{{item.title}}</h2>
        <p>{{item.description}}</p>
        <button class="underlink" @click="readMore">向下阅读本展介绍 ↓</button>
      </div>
      <figure class="script-poster">
        <img :src="item.poster" :alt="`${item.name}专题海报`">
        <figcaption>书体导览 · 团队整理素材</figcaption>
      </figure>
    </div>

    <div id="script-reading" class="script-reading">
      <span class="sub">01 / 本页讲什么</span>
      <h2>{{item.overview.heading}}</h2>
      <p>{{item.overview.body}}</p>
      <p class="quiet">年代标签用于概览，不代表字体只存在于该时期。资料正在整理，重要结论应结合可靠来源核查。</p>
    </div>

    <section class="detail-content detail-learning">
      <div class="detail-learning-heading">
        <div>
          <span class="sub">02 / 本展观察路径</span>
          <h2>这一次，重点看什么？</h2>
        </div>
        <p>{{item.overview.tip}}</p>
      </div>
      <div class="analysis-grid">
        <article v-for="(block, blockIndex) in item.analysisBlocks" :key="block.title" class="analysis-card">
          <span class="sub">0{{blockIndex+1}} / {{block.eyebrow}}</span>
          <h3>{{block.title}}</h3>
          <p>{{block.body}}</p>
        </article>
      </div>
      <aside class="analysis-ai">
        <div>
          <span class="sub">带着问题继续</span>
          <p>把刚才的观察带进书法伴学，继续追问这一专题。</p>
        </div>
        <RouterLink class="primary" :to="{path:'/chat',query:{q:item.question,script:item.name}}">向 AI 提问 ↗</RouterLink>
      </aside>
    </section>

    <ArtworkGallery :script="item" />

    <div class="detail-next">
      <RouterLink :to="index===0?'/':'/scripts/'+(index-1)">← 上一展</RouterLink>
      <RouterLink :to="index===5?'/chat':'/scripts/'+(index+1)">{{index===5?'前往 AI 书法问答':'继续探索 · '+scripts[index+1].name}} →</RouterLink>
    </div>
  </section>
  <section v-else class="section">
    <h2>没有找到这个字体专题</h2>
    <RouterLink to="/">返回首页 →</RouterLink>
  </section>
</template>
