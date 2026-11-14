<script setup>
import {computed, ref, watch} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import {practiceCharacters, scripts} from '../data';
import {demoMode} from '../services/api';
import {useLibrary} from '../stores/library';
import ArtworkGallery from '../components/ArtworkGallery.vue';
import PracticeStudio from '../components/PracticeStudio.vue';

const lib=useLibrary();
const route=useRoute();
const router=useRouter();
const supportedCharacters=practiceCharacters.map(item=>item.char);
const activeScriptIndex=ref(0);
const char=ref('日');
const routeNotice=ref('');

const selectedScript=computed(()=>scripts[activeScriptIndex.value]||scripts[0]);

function resolveScript(value){
  const requested=String(value||'');
  const byName=scripts.findIndex(item=>item.name===requested);
  if(byName>=0)return byName;
  const byIndex=Number(requested);
  return Number.isInteger(byIndex)&&scripts[byIndex]?byIndex:0;
}

function applyRouteCharacter(value){
  const requested=String(value||'');
  if(supportedCharacters.includes(requested)){
    char.value=requested;
    routeNotice.value='';
    return;
  }
  if(requested){
    routeNotice.value=`「${requested}」暂未收录分步范字与演变资料，已为你打开可体验的示例字。`;
  }
}

function chooseScript(index){
  activeScriptIndex.value=index;
  router.replace({
    path:'/study',
    query:{...route.query,script:scripts[index].name}
  });
}

watch(()=>route.query.script,value=>{
  activeScriptIndex.value=resolveScript(value);
},{immediate:true});

watch(()=>route.query.char,applyRouteCharacter,{immediate:true});
</script>

<template>
  <section class="section appreciation-page">
    <header class="appreciation-hero">
      <div>
        <span class="sub">APPRECIATE · OBSERVE · TRACE</span>
        <h1>碑帖赏析与临写</h1>
        <p>先从一类书体与一件作品开始观察，再把看到的重心、留白和笔势，带到可实际操作的范字试笔中。</p>
      </div>
    </header>

    <section class="appreciation-selector" aria-labelledby="appreciation-selector-title">
      <div>
        <span class="sub">01 / 选择书体</span>
        <h2 id="appreciation-selector-title">今天想从哪一种笔墨开始？</h2>
      </div>
      <div class="appreciation-tabs" aria-label="选择书体进行碑帖赏析">
        <button
          v-for="(item,index) in scripts"
          :key="item.name"
          type="button"
          :aria-pressed="activeScriptIndex===index"
          :class="{active:activeScriptIndex===index}"
          @click="chooseScript(index)"
        >
          <span>{{String(index+1).padStart(2,'0')}}</span>
          <strong>{{item.name}}</strong>
          <small>{{item.era}}</small>
        </button>
      </div>
    </section>

    <section id="appreciation-focus" class="appreciation-focus" :aria-labelledby="`appreciation-title-${selectedScript.name}`">
      <figure class="appreciation-poster">
        <img :src="selectedScript.poster" :alt="`${selectedScript.name}赏析导览海报`" loading="eager" decoding="async">
        <figcaption>团队整理素材 · 参赛前请补充作品来源与授权依据</figcaption>
      </figure>

      <div class="appreciation-copy">
        <span class="sub">02 / {{selectedScript.era}} · {{selectedScript.name}}</span>
        <h2 :id="`appreciation-title-${selectedScript.name}`">{{selectedScript.name}} · {{selectedScript.title}}</h2>
        <p>{{selectedScript.description}}</p>
        <p class="appreciation-tip"><b>本次观察：</b>{{selectedScript.overview.tip}}</p>
        <div class="appreciation-observation-grid">
          <article v-for="(block,index) in selectedScript.analysisBlocks" :key="block.title">
            <span>{{String(index+1).padStart(2,'0')}} · {{block.eyebrow}}</span>
            <h3>{{block.title}}</h3>
            <p>{{block.body}}</p>
          </article>
        </div>
        <div class="appreciation-actions">
          <RouterLink class="underlink" :to="`/scripts/${activeScriptIndex}`">阅读{{selectedScript.name}}专题深读 ↗</RouterLink>
          <RouterLink class="underlink" :to="{path:'/chat',query:{q:selectedScript.question,script:selectedScript.name}}">{{demoMode?'查看相关答疑演示':'带着观察向 AI 提问'}} ↗</RouterLink>
        </div>
      </div>
    </section>

    <ArtworkGallery :script="selectedScript" />

    <section id="practice-studio" class="practice-entry" aria-labelledby="practice-entry-title">
      <div>
        <span class="sub">03 / 结构试笔</span>
        <h2 id="practice-entry-title">把观察带到一笔一画里。</h2>
      </div>
      <div>
        <p>目前可试笔的「日、木」是现代结构与笔势示意，帮助你练习观察方法；它们不是上方碑帖的数字摹本，也不会给出书法评分。</p>
        <p v-if="routeNotice" class="study-route-notice" role="status">{{routeNotice}}</p>
      </div>
    </section>

    <PracticeStudio v-model="char" />

    <section id="my-library" class="learning-record" aria-labelledby="learning-record-title">
      <div class="learning-record-heading">
        <div>
          <span class="sub">MY LEARNING RECORD</span>
          <h2 id="learning-record-title">我的字匣</h2>
        </div>
        <RouterLink class="underlink" to="/explore">从一个汉字继续溯源 ↗</RouterLink>
      </div>
      <p class="quiet">{{lib.notice||'收藏与浏览记录仅保存在当前浏览器。'}}</p>
      <div class="library-grid">
        <div v-for="group in [{title:'我的收藏',items:lib.saved},{title:'最近浏览',items:lib.recent}]" :key="group.title">
          <h3>{{group.title}} · {{group.items.length}}</h3>
          <div class="toolbar">
            <RouterLink v-for="item in group.items" :key="item" class="pill" :to="{path:'/explore',query:{char:item}}">{{item}}</RouterLink>
            <p v-if="!group.items.length" class="quiet">还没有记录，先去探索一个汉字吧。</p>
          </div>
        </div>
      </div>
    </section>
  </section>
</template>

<style scoped>
.appreciation-page{padding-top:clamp(36px,6vw,74px)}
.appreciation-hero{padding:0 0 44px;border-bottom:1px solid var(--line)}
.appreciation-hero h1{margin:12px 0 18px}.appreciation-hero>div>p{max-width:650px;margin:0;color:var(--muted);font-size:15px;line-height:2}
.appreciation-selector{padding:48px 0 38px}.appreciation-selector h2,.practice-entry h2,.learning-record h2{margin:12px 0 0;font-size:clamp(27px,3.2vw,39px)}
.appreciation-tabs{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;margin-top:26px}.appreciation-tabs button{min-height:90px;padding:13px 10px;border:1px solid var(--line);border-radius:11px;background:#fffdf8;color:var(--ink);text-align:left;transition:background .2s,border-color .2s,color .2s,transform .2s}.appreciation-tabs button:hover{border-color:#a5b3ae;transform:translateY(-2px)}.appreciation-tabs button.active{background:var(--ink);border-color:var(--ink);color:#fff}.appreciation-tabs span,.appreciation-tabs small{display:block;color:var(--muted);font-size:10px;letter-spacing:.08em}.appreciation-tabs button.active span,.appreciation-tabs button.active small{color:#c7d5d0}.appreciation-tabs strong{display:block;margin:13px 0 5px;font-size:16px}
.appreciation-focus{display:grid;grid-template-columns:minmax(240px,.66fr) minmax(0,1.34fr);gap:clamp(30px,5vw,66px);padding:clamp(26px,5vw,52px);border-radius:18px;background:#edf2f0}.appreciation-poster{min-height:440px;margin:0;overflow:hidden;border-radius:12px;background:#dbe2df}.appreciation-poster img{display:block;width:100%;height:100%;object-fit:cover;object-position:center top;filter:saturate(.86) contrast(1.03)}.appreciation-poster figcaption{padding:11px 13px;color:var(--muted);font-size:10px;line-height:1.65;background:#fffdf8}
.appreciation-copy>p{max-width:680px;color:var(--muted);font-size:14px;line-height:2}.appreciation-copy h2{margin:12px 0;font-size:clamp(30px,3.6vw,46px);line-height:1.24}.appreciation-tip{padding:14px 16px;border-left:3px solid #789187;background:#fffdf8}.appreciation-tip b{color:var(--ink)}
.appreciation-observation-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:22px}.appreciation-observation-grid article{padding:16px;border:1px solid rgba(111,132,123,.25);border-radius:10px;background:#f8fbf9}.appreciation-observation-grid span{color:#60776d;font-size:10px;font-weight:700;letter-spacing:.08em}.appreciation-observation-grid h3{margin:11px 0 7px;font-size:15px;line-height:1.45}.appreciation-observation-grid p{margin:0;color:var(--muted);font-size:12px;line-height:1.75}.appreciation-actions{display:flex;flex-wrap:wrap;gap:22px;margin-top:24px}
.practice-entry{display:grid;grid-template-columns:minmax(0,.82fr) minmax(300px,1.18fr);gap:50px;align-items:end;margin-top:72px;padding:0 0 30px;border-bottom:1px solid var(--line)}.practice-entry>div:last-child>p{margin:0;color:var(--muted);font-size:13px;line-height:2}.practice-entry .study-route-notice{margin-top:13px;padding:10px 12px;border-left:3px solid #8c3130;background:#f3ede2;color:var(--ink)}
.learning-record{margin-top:72px;padding:36px;border:1px solid var(--line);border-radius:16px;background:#fffdf8}.learning-record-heading{display:flex;align-items:end;justify-content:space-between;gap:24px}.learning-record>.quiet{margin:16px 0 0}.library-grid{margin-top:24px}.library-grid h3{font-size:15px}.library-grid .toolbar{margin:13px 0 0}
@media(max-width:760px){.appreciation-page{padding-top:30px}.appreciation-focus,.practice-entry{grid-template-columns:1fr;gap:25px}.appreciation-hero{padding-bottom:32px}.appreciation-selector{padding:35px 0 26px}.appreciation-tabs{display:flex;overflow:auto;padding-bottom:5px}.appreciation-tabs button{min-width:94px;flex:0 0 94px}.appreciation-focus{padding:20px 16px;border-radius:14px}.appreciation-poster{min-height:340px}.appreciation-copy h2{font-size:31px}.appreciation-observation-grid{grid-template-columns:1fr}.practice-entry{margin-top:48px}.learning-record{margin-top:48px;padding:23px 18px}.learning-record-heading{align-items:start;flex-direction:column;gap:14px}}
</style>
