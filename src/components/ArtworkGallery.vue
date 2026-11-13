<script setup>
defineProps({
  script: {
    type: Object,
    required: true
  }
});
</script>

<template>
  <section class="artwork-gallery" :aria-labelledby="`gallery-heading-${script.name}`">
    <div class="artwork-gallery-heading">
      <div>
        <span class="sub">03 / 作品展廊</span>
        <h2 :id="`gallery-heading-${script.name}`">{{ script.name }}作品</h2>
      </div>
      <p>以一件为主展，另外两件作为对照，组织本展的观看顺序。</p>
    </div>

    <div class="artwork-grid">
      <figure v-for="(work, index) in script.works" :key="work.image" :class="['artwork-card',{'artwork-card--featured':index===0}]">
        <div class="artwork-media">
          <img :src="work.image" :alt="work.title" loading="lazy" decoding="async">
          <span aria-hidden="true">{{String(index+1).padStart(2,'0')}} / {{String(script.works.length).padStart(2,'0')}}</span>
        </div>
        <figcaption>
          <span class="artwork-card-role">{{index===0?'主展阅读':'对照资料'}}</span>
          <h3>{{ work.title }}</h3>
          <p>{{ work.caption }}</p>
        </figcaption>
      </figure>
    </div>

    <p class="asset-note">资料图由团队整理并压缩用于页面展示；作品信息与图片使用授权仍需在提交前逐项核验、补充来源。</p>
  </section>
</template>
