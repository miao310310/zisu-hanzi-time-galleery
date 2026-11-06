<script setup>
import {ref,watch} from 'vue';
import {useRoute} from 'vue-router';
import {useLibrary} from './stores/library';

const menu=ref(false),route=useRoute(),lib=useLibrary();
watch(()=>route.fullPath,()=>menu.value=false);
function focusMain(){document.getElementById('main')?.focus()}
</script>
<template><a class="skip-link" href="#main" @click.prevent="focusMain">跳至正文</a><header class="museum-header"><RouterLink class="brand" to="/"><span class="seal">字溯</span><div><b>字溯</b><small>汉字时光馆</small></div></RouterLink><nav :class="{open:menu}" aria-label="主导航"><RouterLink to="/">时光馆</RouterLink><RouterLink to="/scripts">历代字体</RouterLink><RouterLink to="/explore">汉字溯源</RouterLink><RouterLink to="/chat">书法问答</RouterLink><RouterLink to="/about">关于字溯</RouterLink></nav><div class="header-tools"><RouterLink to="/study" :aria-label="'打开学习字匣，'+lib.saved.length+'项收藏'">学习字匣 <small>{{lib.saved.length}}</small></RouterLink><button class="menu-toggle" :aria-expanded="menu" aria-label="展开或收起导航" @click="menu=!menu">☰</button></div></header><main id="main" tabindex="-1"><RouterView v-slot="{ Component }"><Transition name="page-turn" mode="out-in"><KeepAlive :max="12"><component :is="Component" :key="route.fullPath" /></KeepAlive></Transition></RouterView></main><footer class="museum-footer"><div><h2>循一笔一画，<br>见千年中国。</h2><span class="sub">字溯 · 汉字时光馆</span></div><div><span class="sub">馆内导览</span><RouterLink to="/scripts">历代字体 ↗</RouterLink><RouterLink to="/explore">汉字溯源 ↗</RouterLink><RouterLink to="/study">学习字匣 ↗</RouterLink><RouterLink to="/about">关于字溯 ↗</RouterLink></div><div><span class="sub">观展须知</span><p>本站用于汉字与书法科普。示例内容待学术校对，AI 回答请核查。装饰大字不代表历史字形。</p><p>首页甲骨图来自用户指定的<a href="https://6td6vp2rag6zy.kimi.site/" target="_blank" rel="noopener noreferrer">参考站</a>，仅用于设计预览，参赛前需核实来源与使用授权。</p></div></footer></template>




