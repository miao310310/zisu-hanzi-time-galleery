<script setup>
import { onActivated, onBeforeUnmount, onDeactivated, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { scripts } from '../data';

const ROTATION_DELAY = 3000;

const frames = [
  {
    name: '字溯 · 汉字时光馆',
    title: '从一刀一凿，到笔墨千年',
    description: '一座可以漫游的汉字博物馆。',
    glyph: '字溯',
    label: 'DIGITAL CULTURE MUSEUM',
    to: '/about'
  },
  ...scripts.map((script, index) => ({
    ...script,
    title: `${script.name} · ${script.title}`,
    label: `${script.era} · 书体专题`,
    to: `/scripts/${index}`
  })),
  {
    name: 'AI 书法问答',
    title: '不只看见，还可以继续追问',
    description: '从汉字源流到临习观察，与书法伴学一起探索。',
    glyph: '问',
    label: 'AI LEARNING COMPANION',
    to: '/chat'
  }
];

const current = ref(0);
const isActive = ref(true);
const isPointerInside = ref(false);
const isFocusInside = ref(false);
let timer;

function displayIndex(index) {
  return String(index + 1).padStart(2, '0');
}

function prefersReducedMotion() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
}

function stopRotation() {
  window.clearInterval(timer);
  timer = undefined;
}

function syncRotation() {
  stopRotation();

  if (!isActive.value || isPointerInside.value || isFocusInside.value || prefersReducedMotion()) {
    return;
  }

  timer = window.setInterval(() => {
    if (!document.hidden) {
      current.value = (current.value + 1) % frames.length;
    }
  }, ROTATION_DELAY);
}

function select(index) {
  current.value = (index + frames.length) % frames.length;
  syncRotation();
}

function handleFocusOut(event) {
  if (!event.currentTarget.contains(event.relatedTarget)) {
    isFocusInside.value = false;
    syncRotation();
  }
}

function handleVisibilityChange() {
  syncRotation();
}

onMounted(() => {
  document.addEventListener('visibilitychange', handleVisibilityChange);
  syncRotation();
});

onActivated(() => {
  isActive.value = true;
  syncRotation();
});

onDeactivated(() => {
  isActive.value = false;
  stopRotation();
});

onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange);
  stopRotation();
});
</script>

<template>
  <section
    class="cover-carousel"
    aria-label="首页、六类字体和 AI 书法问答主题轮播"
    @mouseenter="isPointerInside = true; syncRotation()"
    @mouseleave="isPointerInside = false; syncRotation()"
    @focusin="isFocusInside = true; syncRotation()"
    @focusout="handleFocusOut"
  >
    <div class="cover-texture" aria-hidden="true"></div>

    <RouterLink
      v-for="(frame, index) in frames"
      :key="frame.name"
      :to="frame.to"
      :class="['cover-frame', `cover-theme-${index}`, { visible: current === index }]"
      :aria-hidden="current !== index"
      :tabindex="current === index ? 0 : -1"
    >
      <div class="cover-artwork" aria-hidden="true">
        <figure v-if="frame.poster" class="artifact-panel artifact-panel-poster">
          <img :src="frame.poster" alt="">
          <figcaption>{{ frame.name }} · 书体导览</figcaption>
        </figure>
        <div v-else class="carousel-specimen">
          <span class="carousel-specimen-number">{{ displayIndex(index) }}</span>
          <span class="carousel-specimen-label">{{ frame.label }}</span>
          <span :class="['carousel-glyph', { 'is-wordmark': index === 0 }]">{{ frame.glyph }}</span>
          <span class="carousel-specimen-note">字溯 · 主题导览</span>
        </div>
      </div>

      <div class="cover-shade"></div>
      <div class="cover-caption">
        <span class="cover-label">{{ displayIndex(index) }} / 08 · {{ frame.label }}</span>
        <h2>{{ frame.title }}</h2>
        <p>{{ frame.description }}</p>
        <span class="cover-cta">查看专题 <span aria-hidden="true">↗</span></span>
      </div>
    </RouterLink>

    <div class="cover-navigation">
      <div class="cover-bars" aria-label="选择轮播画面">
        <button
          v-for="(frame, index) in frames"
          :key="frame.name"
          :class="{ active: current === index }"
          :aria-label="`第 ${displayIndex(index)} 幅：${frame.name}`"
          :aria-current="current === index ? 'true' : undefined"
          @click="select(index)"
        >
          <span></span>
        </button>
      </div>
      <div class="cover-arrows">
        <button aria-label="上一幅画面" @click="select(current - 1)">←</button>
        <button aria-label="下一幅画面" @click="select(current + 1)">→</button>
      </div>
    </div>

    <div class="cover-read-hint">向下浏览，走近文字的故事 <span>↓</span></div>
  </section>
</template>
