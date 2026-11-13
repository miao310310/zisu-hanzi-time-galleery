<script setup>
import {ref,watch} from 'vue';
import {useRoute} from 'vue-router';
import {useLibrary} from '../stores/library';
import PracticeStudio from '../components/PracticeStudio.vue';

const lib=useLibrary();
const route=useRoute();
const supportedCharacters=['日','山','水','木'];
const char=ref(supportedCharacters.includes(String(route.query.char))?String(route.query.char):'日');

watch(()=>route.query.char,value=>{
  const requested=String(value||'');
  if(supportedCharacters.includes(requested)){
    char.value=requested;
  }
});
</script>

<template>
  <section class="section">
    <span class="sub">学习字匣 / PERSONAL COLLECTION</span>
    <h2>把喜欢的字，留在身边</h2>
    <p class="quiet">{{lib.notice||'收藏与浏览记录保存在当前浏览器。'}}</p>

    <div class="library-grid">
      <div v-for="group in [{title:'我的收藏',items:lib.saved},{title:'最近浏览',items:lib.recent}]" :key="group.title">
        <h3>{{group.title}} · {{group.items.length}}</h3>
        <div class="toolbar">
          <RouterLink v-for="c in group.items" :key="c" class="pill" :to="{path:'/explore',query:{char:c}}">{{c}}</RouterLink>
          <p v-if="!group.items.length" class="quiet">还没有记录，先去探索一个汉字吧。</p>
        </div>
      </div>
    </div>

    <PracticeStudio v-model="char"/>
  </section>
</template>
