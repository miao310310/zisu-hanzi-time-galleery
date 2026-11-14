<script setup>
import {onBeforeUnmount, onMounted} from 'vue';
import HeroCarousel from '../components/HeroCarousel.vue';
import {scripts} from '../data';

const timelineMarks=['刻','铸','篆','隶','楷','行'];

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

  <section id="timeline" class="museum-timeline fade-in" aria-labelledby="timeline-title">
    <header class="writing-history-heading">
      <span class="sub">A RIVER OF WRITING</span>
      <h2 id="timeline-title">循字入史</h2>
      <p>点击任一时代，走近一种书体。</p>
    </header>

    <div class="writing-history" aria-label="六种书体的时间线">
      <article v-for="(script,index) in scripts" :key="script.name" class="writing-era">
        <div class="writing-era-rail" aria-hidden="true">
          <span>{{timelineMarks[index]}}</span>
        </div>
        <RouterLink class="writing-era-card" :to="`/scripts/${index}`" :aria-label="`阅读${script.name}专题`">
          <p class="writing-era-period">{{script.era}}</p>
          <span class="writing-era-index">{{String(index+1).padStart(2,'0')}}</span>
          <h3>{{script.name}}</h3>
          <p class="writing-era-title">{{script.title}}，{{script.description}}</p>
          <figure class="writing-era-media">
            <img :src="script.works[0].image" :alt="script.works[0].title" :loading="index===0?'eager':'lazy'" decoding="async">
            <figcaption>{{script.works[0].title}} · 点击进入专题赏析 ↗</figcaption>
          </figure>
        </RouterLink>
      </article>
    </div>
  </section>

  <section class="home-next-step fade-in">
    <div>
      <span class="sub">NEXT STEP / 从看见到练习</span>
      <h2>先读作品，<br>再落下一笔。</h2>
    </div>
    <div class="home-next-step-copy">
      <p>从任一书体进入专题后，可继续查看作品资料与观察线索；再用“日、木”进行结构试笔，或带着问题进入书法答疑。</p>
      <div class="home-next-step-actions">
        <RouterLink class="primary" to="/study">进入碑帖赏析 ↗</RouterLink>
        <RouterLink class="underlink" to="/chat">带着问题去答疑 ↗</RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.writing-history-heading {
  margin: 0 0 clamp(48px, 7vw, 92px);
}

.writing-history-heading .sub {
  color: var(--red);
  font-weight: 700;
  letter-spacing: .24em;
}

.writing-history-heading h2 {
  max-width: 760px;
  margin: 20px 0 14px;
  color: #1f2020;
  font-size: clamp(62px, 9vw, 132px);
  font-weight: 650;
  letter-spacing: .02em;
  line-height: .98;
}

.writing-history-heading p {
  margin: 0;
  color: var(--muted);
  font-size: clamp(16px, 1.8vw, 22px);
  line-height: 1.7;
}

.writing-history {
  position: relative;
  max-width: 920px;
  padding-bottom: 8px;
}

.writing-history::before {
  position: absolute;
  top: 4px;
  bottom: 62px;
  left: 31px;
  width: 1px;
  background: var(--red);
  content: '';
}

.writing-era {
  position: relative;
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  column-gap: clamp(24px, 4vw, 46px);
  padding-bottom: clamp(58px, 9vw, 112px);
}

.writing-era:last-child { padding-bottom: 0; }

.writing-era-rail {
  z-index: 1;
  display: flex;
  justify-content: center;
  padding-top: 6px;
}

.writing-era-rail span {
  display: grid;
  width: 54px;
  height: 54px;
  place-items: center;
  border: 1px solid var(--red);
  border-radius: 50%;
  background: var(--paper);
  color: var(--red);
  font-family: 'Songti SC', 'SimSun', serif;
  font-size: 18px;
}

.writing-era-card {
  display: block;
  min-width: 0;
  max-width: 680px;
  color: var(--ink);
}

.writing-era-card:focus-visible {
  outline: 2px solid var(--red);
  outline-offset: 9px;
}

.writing-era-period {
  margin: 0;
  color: #2a2b2a;
  font-family: 'Songti SC', 'SimSun', serif;
  font-size: clamp(20px, 2.3vw, 29px);
  font-weight: 650;
  line-height: 1.35;
}

.writing-era-index {
  display: block;
  margin-top: 28px;
  color: var(--red);
  font-size: 13px;
  letter-spacing: .1em;
}

.writing-era h3 {
  margin: 8px 0 12px;
  color: #202020;
  font-size: clamp(48px, 6.2vw, 80px);
  font-weight: 650;
  letter-spacing: .02em;
  line-height: 1;
}

.writing-era-title {
  margin: 0;
  color: var(--muted);
  font-family: 'Songti SC', 'SimSun', serif;
  font-size: clamp(16px, 1.7vw, 21px);
  font-weight: 600;
  line-height: 1.8;
}

.writing-era-media {
  margin: 22px 0 0;
  overflow: hidden;
  background: #e8e0d0;
}

.writing-era-media img {
  display: block;
  width: 100%;
  min-height: 280px;
  max-height: 460px;
  object-fit: cover;
  object-position: center;
  filter: saturate(.86) contrast(1.02);
  transition: transform .45s ease, filter .45s ease;
}

.writing-era-media figcaption {
  padding: 12px 14px;
  border-top: 1px solid rgba(118, 101, 80, .18);
  background: #fffdf8;
  color: var(--muted);
  font-size: 11px;
  line-height: 1.7;
}

.writing-era-card:hover .writing-era-media img {
  filter: saturate(.98) contrast(1.04);
  transform: scale(1.018);
}

.writing-era-card:hover h3 { color: var(--red); }

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
  .writing-history-heading { margin-bottom: 46px; }
  .writing-history-heading h2 { font-size: clamp(55px, 18vw, 78px); }
  .writing-history-heading p { max-width: 280px; font-size: 16px; }

  .writing-history::before {
    top: 2px;
    bottom: 48px;
    left: 22px;
  }

  .writing-era {
    grid-template-columns: 46px minmax(0, 1fr);
    column-gap: 18px;
    padding-bottom: 64px;
  }

  .writing-era-rail { padding-top: 4px; }
  .writing-era-rail span { width: 42px; height: 42px; font-size: 15px; }
  .writing-era-period { font-size: 20px; }
  .writing-era-index { margin-top: 20px; }
  .writing-era h3 { margin-top: 7px; font-size: clamp(43px, 15vw, 62px); }
  .writing-era-title { font-size: 16px; }
  .writing-era-media { margin-top: 16px; }
  .writing-era-media img { min-height: 210px; max-height: 310px; }

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
