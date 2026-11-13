<script setup>
import {onBeforeUnmount, onMounted, ref} from 'vue';
import HeroCarousel from '../components/HeroCarousel.vue';
import {scripts} from '../data';

const active=ref(0);

function selectTimeline(nextIndex, shouldFocus=false){
  active.value=Math.max(0,Math.min(nextIndex,scripts.length-1));
  if(shouldFocus){
    requestAnimationFrame(()=>document.getElementById(`timeline-tab-${active.value}`)?.focus());
  }
}

function moveTimeline(step){
  selectTimeline((active.value+step+scripts.length)%scripts.length,true);
}

let revealObserver;
onMounted(()=>{
  const revealItems=document.querySelectorAll('#main .fade-in');
  if(!('IntersectionObserver' in window)){
    revealItems.forEach(item=>item.classList.add('active'));
    return;
  }
  revealObserver=new IntersectionObserver(entries=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        entry.target.classList.add('active');
        revealObserver.unobserve(entry.target);
      }
    });
  },{threshold:.12});
  revealItems.forEach(item=>revealObserver.observe(item));
});
onBeforeUnmount(()=>revealObserver?.disconnect());
</script>

<template>
  <div class="home-heading">
    <div>
      <span class="sub">ZISU / DIGITAL CULTURE MUSEUM</span>
      <h1>让文字的来处，成为新的发现。</h1>
    </div>
  </div>

  <HeroCarousel/>

  <section class="exhibition-manifesto fade-in">
    <div>
      <span class="sub">汉字源流 / A WRITING CIVILIZATION</span>
      <h2>每一种字形，<br>都是时间留下的笔触。</h2>
    </div>
    <div class="exhibition-manifesto-copy">
      <p>汉字在甲骨、青铜、石碑与纸张之间不断改变，也在实用与审美之间找到新的秩序。字溯以六类代表性书体为线索，邀请你从“看见”开始，走近一段书写史。</p>
      <RouterLink class="underlink" to="/scripts">从六种书体开始 ↗</RouterLink>
    </div>
  </section>

  <section id="timeline" class="museum-timeline fade-in">
    <div class="heading">
      <div>
        <span class="sub">A RIVER OF WRITING</span>
        <h2>循字入史</h2>
      </div>
      <p>选一种书体，先看一件重点作品，再进入专题深读。</p>
    </div>
    <p class="quiet">各类书体的发展存在交叠，以下为概览线索。</p>

    <div class="timeline-selector" role="tablist" aria-label="六种书体导览">
      <button v-for="(s,i) in scripts" :id="`timeline-tab-${i}`" :key="s.name" class="timeline-tab" :class="{active:active===i}" role="tab" :aria-selected="active===i" aria-controls="timeline-panel" @click="selectTimeline(i)" @keydown.left.prevent="moveTimeline(-1)" @keydown.right.prevent="moveTimeline(1)" @keydown.home.prevent="selectTimeline(0,true)" @keydown.end.prevent="selectTimeline(scripts.length-1,true)">
        <span>0{{i+1}}</span>
        <strong>{{s.name}}</strong>
        <small>{{s.era}}</small>
      </button>
    </div>

    <article id="timeline-panel" class="timeline-feature" role="tabpanel" :aria-labelledby="`timeline-tab-${active}`">
      <figure class="timeline-feature-media">
        <img :src="scripts[active].poster" :alt="`${scripts[active].name}专题海报`" loading="lazy" decoding="async">
      </figure>
      <div class="timeline-feature-copy">
        <span class="sub">0{{active+1}} / 六境 · {{scripts[active].era}}</span>
        <h3>{{scripts[active].name}} · {{scripts[active].title}}</h3>
        <p>{{scripts[active].description}}</p>
        <p class="timeline-feature-tip">{{scripts[active].overview.tip}}</p>
        <div class="timeline-feature-actions">
          <RouterLink class="primary" :to="'/scripts/'+active">进入{{scripts[active].name}}专题 ↗</RouterLink>
          <RouterLink class="underlink" to="/scripts">比较六种书体 ↗</RouterLink>
        </div>
      </div>
    </article>
  </section>

  <section class="home-ai-bridge fade-in">
    <span class="home-ai-mark" aria-hidden="true">问</span>
    <div>
      <span class="sub">YOUR NEXT QUESTION</span>
      <h2>看见一笔，<br>再问明白它。</h2>
    </div>
    <div class="home-ai-copy">
      <p>带着正在看的书体、作品或汉字进入对话。字溯伴学会围绕汉字源流、书体特点与临习观察继续回答。</p>
      <RouterLink class="primary" :to="{path:'/chat',query:{q:`请介绍${scripts[active].name}的特点，并给我三个欣赏相关作品的观察建议`,script:scripts[active].name}}">带着{{scripts[active].name}}去提问 ↗</RouterLink>
    </div>
  </section>
</template>
