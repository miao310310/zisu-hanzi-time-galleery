<script setup>
import {ref,watch} from 'vue';
import {useRoute} from 'vue-router';
import {useLibrary} from './stores/library';

const menu=ref(false),route=useRoute(),lib=useLibrary();
watch(()=>route.fullPath,()=>menu.value=false);
function focusMain(){document.getElementById('main')?.focus()}
</script>
<template>
  <a class="skip-link" href="#main" @click.prevent="focusMain">跳至正文</a>

  <header class="museum-header">
    <RouterLink class="brand" to="/">
      <span class="seal">字溯</span>
      <div><b>字溯</b><small>汉字时光馆</small></div>
    </RouterLink>

    <nav :class="{open:menu}" aria-label="主导航">
      <RouterLink to="/" title="首页六体导览" aria-label="字脉初览：首页六体导览">字脉初览</RouterLink>
      <RouterLink to="/study" title="碑帖赏析与临写" aria-label="观碑试笔：碑帖赏析与临写">观碑试笔</RouterLink>
      <RouterLink to="/chat" title="AI 书法答疑" aria-label="墨问智答：AI 书法答疑">墨问智答</RouterLink>
    </nav>

    <div class="header-tools">
      <RouterLink to="/study#my-library" :aria-label="'打开我的学习记录，'+lib.saved.length+'项收藏'">
        我的记录 <small>{{lib.saved.length}}</small>
      </RouterLink>
      <button class="menu-toggle" :aria-expanded="menu" aria-label="展开或收起导航" @click="menu=!menu">☰</button>
    </div>
  </header>

  <main id="main" tabindex="-1">
    <RouterView v-slot="{ Component }">
      <Transition name="page-turn" mode="out-in">
        <KeepAlive :max="12"><component :is="Component" :key="route.fullPath" /></KeepAlive>
      </Transition>
    </RouterView>
  </main>

  <footer class="museum-footer">
    <div><h2>循一笔一画，<br>见千年中国。</h2><span class="sub">字溯 · 汉字时光馆</span></div>
    <div>
      <span class="sub">三条学习路径</span>
      <RouterLink to="/" aria-label="字脉初览：首页六体导览">字脉初览 ↗</RouterLink>
      <RouterLink to="/study" aria-label="观碑试笔：碑帖赏析与临写">观碑试笔 ↗</RouterLink>
      <RouterLink to="/chat" aria-label="墨问智答：AI 书法答疑">墨问智答 ↗</RouterLink>
    </div>
    <div>
      <span class="sub">观展须知</span>
      <p>本站用于汉字与书法科普。示例内容待学术校对，AI 回答请核查。装饰大字不代表历史字形。</p>
      <p>首页与专题展廊资料图来自团队整理素材包，仅用于项目展示；参赛提交前请逐项补充作品来源，并核验图片授权或公版依据。</p>
    </div>
  </footer>
</template>




