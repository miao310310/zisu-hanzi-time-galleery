<script setup>
import {scripts} from '../data';
import ObservationLab from '../components/ObservationLab.vue';
</script>

<template>
  <section class="section script-catalog-page">
    <header class="script-catalog-heading">
      <div>
        <span class="sub">六种书体 / SIX CHAPTERS</span>
        <h1>历代字体</h1>
      </div>
      <p>从甲骨、青铜到纸上的笔墨，依次浏览六种书体，带着一个明确的观察问题进入专题。</p>
    </header>

    <div class="script-catalog" aria-label="六种书体专题目录">
      <RouterLink v-for="(s,i) in scripts" :key="s.name" class="script-catalog-card" :to="'/scripts/'+i">
        <div class="script-catalog-poster">
          <img :src="s.poster" :alt="`${s.name}专题海报`" loading="lazy" decoding="async">
          <span class="script-catalog-index" aria-hidden="true">{{String(i+1).padStart(2,'0')}}</span>
          <span class="script-catalog-image-label" aria-hidden="true">专题海报</span>
        </div>
        <div class="script-catalog-copy">
          <div class="script-catalog-meta"><span>{{String(i+1).padStart(2,'0')}} / {{String(scripts.length).padStart(2,'0')}}</span><span>{{s.era}}</span></div>
          <h2>{{s.name}} · {{s.title}}</h2>
          <p class="script-catalog-description">{{s.description}}</p>
          <div class="script-catalog-observation">
            <span>本展观察</span>
            <p>{{s.overview.tip}}</p>
          </div>
          <span class="script-catalog-action">阅读{{s.name}}专题 <span aria-hidden="true">↗</span></span>
        </div>
      </RouterLink>
    </div>
    <p class="quiet">年代仅为概览，各书体发展存在交叠。行书、草书为不同书体，此处合为一个浏览入口。</p>

    <ObservationLab class="scripts-lab"/>
  </section>
</template>
