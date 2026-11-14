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
      <RouterLink class="underlink" to="/study">从六种书体开始赏析 ↗</RouterLink>
    </div>
  </section>

  <section id="timeline" class="museum-timeline fade-in">
    <div class="heading">
      <div>
        <span class="sub">A RIVER OF WRITING</span>
        <h2>从六体进入赏析</h2>
      </div>
      <p>选一种书体，先看作品资料与观察线索，再用示例字进行结构试笔。</p>
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
          <RouterLink class="primary" :to="{path:'/study',query:{script:scripts[active].name}}">赏析{{scripts[active].name}}作品 ↗</RouterLink>
          <RouterLink class="underlink" :to="'/scripts/'+active">阅读书体专题 ↗</RouterLink>
        </div>
      </div>
    </article>
  </section>

  <section class="home-next-step fade-in">
    <div>
      <span class="sub">NEXT STEP / 从看见到练习</span>
      <h2>先读作品，<br>再落下一笔。</h2>
    </div>
    <div class="home-next-step-copy">
      <p>你选择的书体会带入碑帖赏析页；先观察主展与对照资料，再用“日、木”进行结构试笔。遇到疑问时，可继续进入 AI 书法答疑。</p>
      <div class="home-next-step-actions">
        <RouterLink class="primary" :to="{path:'/study',query:{script:scripts[active].name}}">进入{{scripts[active].name}}赏析 ↗</RouterLink>
        <RouterLink class="underlink" :to="{path:'/chat',query:{q:scripts[active].question,script:scripts[active].name}}">带着问题去答疑 ↗</RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.home-next-step {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, .92fr);
  gap: clamp(28px, 6vw, 80px);
  align-items: end;
  margin: 72px 0 64px;
  padding: clamp(30px, 5vw, 56px);
  border: 1px solid var(--line);
  border-radius: 18px;
  background: #edf2f0;
}

.home-next-step h2 {
  margin: 14px 0 0;
  font-size: clamp(30px, 3.8vw, 48px);
  line-height: 1.26;
}

.home-next-step-copy p {
  max-width: 500px;
  margin: 0;
  color: var(--muted);
  font-size: 14px;
  line-height: 2;
}

.home-next-step-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 18px;
  margin-top: 24px;
}

@media (max-width: 750px) {
  .home-next-step {
    grid-template-columns: 1fr;
    gap: 22px;
    margin: 48px 0 40px;
    padding: 28px 23px;
  }

  .home-next-step h2 { font-size: 31px; }
  .home-next-step-copy p { font-size: 13px; }
}
</style>
