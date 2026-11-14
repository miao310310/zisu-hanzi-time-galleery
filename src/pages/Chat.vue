<script setup>
import {computed,ref,onBeforeUnmount,onDeactivated,nextTick} from 'vue';
import {useRoute} from 'vue-router';
import {streamChat,demoMode} from '../services/api';
import {scripts} from '../data';
import SourceList from '../components/SourceList.vue';

const route=useRoute();
const question=ref(String(route.query.q||''));
const messages=ref([]);
const busy=ref(false);
const error=ref('');
const box=ref(null);
const questionInput=ref(null);
let controller;
let lastQuestion='';

const context={
  character:route.query.char||null,
  script:route.query.script||null,
  document_ids:route.query.id?[String(route.query.id)]:[]
};

const currentScript=computed(()=>scripts.find(item=>item.name===context.script));
const contextTitle=computed(()=>{
  const scriptName=currentScript.value?.name||context.script;
  if(scriptName&&context.character)return `${scriptName} · 「${context.character}」`;
  if(scriptName)return scriptName;
  if(context.character)return `「${context.character}」`;
  return '';
});
const contextReturn=computed(()=>{
  if(currentScript.value)return {path:'/study',query:{script:currentScript.value.name}};
  if(context.character)return {path:'/explore',query:{char:context.character}};
  return null;
});
const quickQuestions=[
  {title:'认识一种书体',description:'从线条、结构与时代线索开始。',prompt:'请介绍小篆的特点，并给我三个观察建议。'},
  {title:'赏析一件作品',description:'先建立一套适合初学者的观看顺序。',prompt:'欣赏一件碑帖作品时，我可以先从哪些方面开始观察？'},
  {title:'临写前先观察',description:'从主笔、重心和留白进入结构练习。',prompt:'我准备临写一个汉字。请告诉我如何从主笔、重心和留白开始观察。'}
];

function stop(){
  controller?.abort();
}

async function send(q=question.value){
  if(busy.value||!q.trim()) return;
  lastQuestion=q;
  question.value='';
  error.value='';
  messages.value.push({role:'user',text:q});
  const reply={role:'assistant',text:'',sources:[],status:'生成中'};
  messages.value.push(reply);
  const target=messages.value.at(-1);
  busy.value=true;
  controller=new AbortController();

  try{
    await streamChat({
      question:q,
      context,
      history:messages.value.slice(0,-2).filter(m=>m.role==='user'||m.status==='已完成').map(m=>({role:m.role,content:m.text})),
      signal:controller.signal,
      onDelta:text=>{
        target.text+=text;
        nextTick(()=>{
          if(box.value) box.value.scrollTop=box.value.scrollHeight;
        });
      },
      onSources:s=>target.sources=s
    });
    target.status='已完成';
  }catch(e){
    target.status=e.name==='AbortError'?'已停止':'生成失败';
    if(e.name!=='AbortError') error.value=e.message;
  }finally{
    busy.value=false;
  }
}

function clear(){
  if(busy.value) return;
  messages.value=[];
  error.value='';
}

function useQuickQuestion(prompt){
  question.value=prompt;
  nextTick(()=>questionInput.value?.focus());
}

onDeactivated(stop);
onBeforeUnmount(stop);
</script>

<template>
  <section class="section chat-tour-page">
    <div class="ai-cover ai-cover--compact">
      <span class="sub">与文字对话 / AI LEARNING COMPANION</span>
      <h1>看得见，<br>问得深。</h1>
      <p>围绕汉字源流、书体特点、碑帖赏析与临写观察，继续追问你刚刚看到的内容。</p>
      <span class="ai-cover-glyph" aria-hidden="true">问</span>
      <a class="underlink" href="#chat-conversation" @click.prevent="box?.scrollIntoView({behavior:'smooth'})">开始提问 ↓</a>
    </div>

    <section class="chat-workspace" aria-labelledby="chat-workspace-title">
      <div class="chat-workspace-heading">
        <div>
          <span class="sub">带着观察继续</span>
          <h2 id="chat-workspace-title">从一个具体问题，开始书法答疑。</h2>
        </div>
        <div>
          <p class="mode">{{demoMode?'演示模式：本地预设内容逐字显示，非真实 AI。':'AI 接口模式：回答由团队配置的模型生成；重要信息请结合资料来源核查。'}}</p>
          <p v-if="context.character||context.script" class="quiet">当前上下文：{{context.character||context.script}}</p>
        </div>
      </div>

      <aside v-if="contextTitle" class="chat-context-card" aria-label="当前学习上下文">
        <div>
          <span class="sub">CURRENT LEARNING CONTEXT</span>
          <strong>正在围绕 {{contextTitle}} 继续提问</strong>
          <p>问题会携带当前页面的书体或汉字上下文，便于把观察延续到答疑中。</p>
        </div>
        <RouterLink v-if="contextReturn" class="underlink" :to="contextReturn">返回学习页面 ↗</RouterLink>
      </aside>

      <section class="chat-quick-questions" aria-labelledby="quick-question-title">
        <div><span class="sub">START WITH A QUESTION</span><h3 id="quick-question-title">不知道怎么问？从这里开始。</h3></div>
        <div class="chat-quick-grid">
          <button v-for="item in quickQuestions" :key="item.title" type="button" @click="useQuickQuestion(item.prompt)">
            <strong>{{item.title}}</strong><span>{{item.description}}</span><i aria-hidden="true">↗</i>
          </button>
        </div>
      </section>

      <div v-if="messages.length" class="toolbar chat-actions">
        <button :disabled="busy" @click="clear">清空对话</button>
      </div>

      <div id="chat-conversation" ref="box" class="conversation" aria-live="polite">
        <p v-if="!messages.length" class="quiet">从一个汉字或字体开始，提出你的第一个问题。</p>
        <article v-for="(m,i) in messages" :key="i" :class="['bubble',m.role]">
          <small>{{m.role==='user'?'你':'字溯伴学'}} <span v-if="m.status">· {{m.status}}</span></small>
          <p>{{m.text||(m.status==='生成失败'?'本次未收到回答，请查看下方错误提示。':m.status==='已停止'?'已停止生成。':'正在等待回答…')}}</p>
          <SourceList v-if="m.role==='assistant'&&m.status==='已完成'" :sources="m.sources"/>
        </article>
      </div>

      <p v-if="error" class="error" role="alert">{{error}} <button :disabled="busy" @click="send(lastQuestion)">重试</button></p>
      <form class="lookup-form" @submit.prevent="send()">
        <input ref="questionInput" v-model="question" aria-label="你的问题" placeholder="想了解哪个汉字、作品或书体？" :disabled="busy">
        <button v-if="busy" type="button" class="primary" @click="stop">停止生成</button>
        <button v-else class="primary" :disabled="!question.trim()">发送 →</button>
      </form>
    </section>
  </section>
</template>

<style scoped>
.chat-context-card{display:flex;align-items:end;justify-content:space-between;gap:24px;margin:26px 0 0;padding:19px 21px;border:1px solid #cdd9d5;border-radius:12px;background:#edf3f1}.chat-context-card strong{display:block;margin-top:9px;font-size:15px}.chat-context-card p{max-width:600px;margin:8px 0 0;color:var(--muted);font-size:12px;line-height:1.8}.chat-context-card .underlink{flex:0 0 auto;font-size:12px}
.chat-quick-questions{padding:30px 0 24px}.chat-quick-questions h3{margin:9px 0 0;font-size:20px}.chat-quick-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:18px}.chat-quick-grid button{position:relative;min-height:126px;padding:18px 42px 18px 18px;border:1px solid var(--line);border-radius:12px;background:#fffdf8;color:var(--ink);text-align:left;transition:background .2s,border-color .2s,transform .2s}.chat-quick-grid button:hover{border-color:#92a8a2;background:#f1f6f4;transform:translateY(-2px)}.chat-quick-grid strong,.chat-quick-grid span{display:block}.chat-quick-grid strong{font-size:15px}.chat-quick-grid span{margin-top:10px;color:var(--muted);font-size:12px;line-height:1.7}.chat-quick-grid i{position:absolute;right:17px;bottom:16px;color:#5e7e76;font-style:normal}.chat-actions{margin:0 0 18px}
@media(max-width:750px){.chat-context-card{display:block;padding:17px}.chat-context-card .underlink{display:inline-block;margin-top:14px}.chat-quick-questions{padding:26px 0 20px}.chat-quick-grid{grid-template-columns:1fr}.chat-quick-grid button{min-height:100px}}
</style>
