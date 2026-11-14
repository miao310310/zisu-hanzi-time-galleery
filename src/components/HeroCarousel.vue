<script setup>
import { onActivated, onBeforeUnmount, onDeactivated, onMounted, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';
import { scripts } from '../data';
import { demoMode } from '../services/api';

const ROTATION_DELAY = 3000;

const frames = [
  {
    name: '字溯 · 汉字时光馆',
    title: '从一刀一凿，到笔墨千年',
    description: '一座可以漫游的汉字博物馆。',
    glyph: '字溯',
    label: 'DIGITAL CULTURE MUSEUM',
    action: '开始碑帖赏析',
    to: '/study'
  },
  ...scripts.map((script, index) => ({
    ...script,
    title: `${script.name} · ${script.title}`,
    label: `${script.era} · 书体专题`,
    action: `赏析${script.name}作品`,
    to: {path: '/study', query: {script: script.name}}
  })),
  {
    name: 'AI 书法问答',
    title: '不只看见，还可以继续追问',
    description: demoMode ? '公开演示版展示问答交互与上下文衔接；接入后端后可获得实时回答。' : '从汉字源流到临习观察，与书法伴学一起探索。',
    glyph: '问',
    label: 'AI LEARNING COMPANION',
    action: demoMode ? '查看答疑演示' : '进入 AI 答疑',
    to: '/chat'
  }
];

const current = ref(0);
const isActive = ref(true);
const isPointerInside = ref(false);
const isFocusInside = ref(false);
const isUserPaused = ref(false);
const loadedPosterIndexes = ref([0, 1]);
let timer;

function displayIndex(index) {
  return String(index + 1).padStart(2, '0');
}

function prefersReducedMotion() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
}

function normalizeIndex(index) {
  return (index + frames.length) % frames.length;
}

function isPosterLoaded(index) {
  return loadedPosterIndexes.value.includes(index);
}

function preloadPoster(index) {
  const normalizedIndex = normalizeIndex(index);
  if (!frames[normalizedIndex].poster || isPosterLoaded(normalizedIndex)) {
    return;
  }
  loadedPosterIndexes.value = [...loadedPosterIndexes.value, normalizedIndex];
}

function stopRotation() {
  window.clearInterval(timer);
  timer = undefined;
}

function syncRotation() {
  stopRotation();

  if (document.hidden || !isActive.value || isUserPaused.value || isPointerInside.value || isFocusInside.value || prefersReducedMotion()) {
    return;
  }

  timer = window.setInterval(() => {
    if (!document.hidden) {
      current.value = (current.value + 1) % frames.length;
    }
  }, ROTATION_DELAY);
}

function select(index) {
  current.value = normalizeIndex(index);
  preloadPoster(current.value);
  preloadPoster(current.value + 1);
  syncRotation();
}

function toggleRotation() {
  isUserPaused.value = !isUserPaused.value;
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
  preloadPoster(current.value);
  preloadPoster(current.value + 1);
  syncRotation();
});

watch(current, index => {
  preloadPoster(index);
  preloadPoster(index + 1);
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
          <img
            v-if="isPosterLoaded(index)"
            :src="frame.poster"
            :alt="`${frame.name}专题导览海报`"
            :loading="current === index ? 'eager' : 'lazy'"
            :fetchpriority="current === index ? 'high' : 'low'"
          >
          <div v-else class="artifact-placeholder" aria-hidden="true">资料图准备中</div>
          <figcaption><span>{{displayIndex(index)}} / 08</span>{{ frame.name }} · 书体导览</figcaption>
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
        <span class="cover-cta">{{ frame.action || '查看专题' }} <span aria-hidden="true">↗</span></span>
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
        <button
          class="cover-play-toggle"
          type="button"
          :aria-label="isUserPaused ? '继续自动轮播' : '暂停自动轮播'"
          :aria-pressed="!isUserPaused"
          :disabled="prefersReducedMotion()"
          @click="toggleRotation"
        >
          <span aria-hidden="true">{{ isUserPaused ? '▶' : 'Ⅱ' }}</span>
        </button>
        <button aria-label="上一幅画面" @click="select(current - 1)">←</button>
        <button aria-label="下一幅画面" @click="select(current + 1)">→</button>
      </div>
    </div>

    <div class="cover-read-hint">向下浏览，走近文字的故事 <span>↓</span></div>
  </section>
</template>
