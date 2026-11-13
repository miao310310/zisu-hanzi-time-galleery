<script setup>
import {ref,onBeforeUnmount,nextTick} from 'vue';
import {useRoute} from 'vue-router';
import {streamChat,demoMode} from '../services/api';
import SourceList from '../components/SourceList.vue';

const route=useRoute();
const question=ref(String(route.query.q||''));
const messages=ref([]);
const busy=ref(false);
const error=ref('');
const box=ref(null);
let controller;
let lastQuestion='';

const context={
  character:route.query.char||null,
  script:route.query.script||null,
  document_ids:route.query.id?[String(route.query.id)]:[]
};

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

onBeforeUnmount(stop);
</script>

<template>
  <section class="section chat-tour-page">
    <div class="ai-cover ai-cover--compact">
      <span class="sub">与文字对话 / AI LEARNING COMPANION</span>
      <h1>有字可寻，<br>有问可答。</h1>
      <p>围绕汉字源流、书体特点、碑帖观察与临习入门，继续追问你刚刚看到的内容。</p>
      <span class="ai-cover-glyph" aria-hidden="true">问</span>
      <a class="underlink" href="#chat-conversation" @click.prevent="box?.scrollIntoView({behavior:'smooth'})">开始提问 ↓</a>
    </div>

    <section class="chat-workspace" aria-labelledby="chat-workspace-title">
      <div class="chat-workspace-heading">
        <div>
          <span class="sub">带着观察继续</span>
          <h2 id="chat-workspace-title">把问题交给字溯伴学。</h2>
        </div>
        <div>
          <p class="mode">{{demoMode?'演示模式：本地预设内容逐字显示，非真实 AI。':'AI 接口模式：回答由团队配置的模型生成；重要信息请结合资料来源核查。'}}</p>
          <p v-if="context.character||context.script" class="quiet">当前上下文：{{context.character||context.script}}</p>
        </div>
      </div>

      <div class="toolbar">
        <button @click="question='小篆有什么特点？'">认识小篆</button>
        <button @click="question='请解释山字的形与意'">探索山字</button>
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
        <input v-model="question" aria-label="你的问题" placeholder="想了解哪个汉字或书体？" :disabled="busy">
        <button v-if="busy" type="button" class="primary" @click="stop">停止生成</button>
        <button v-else class="primary" :disabled="!question.trim()">发送 →</button>
      </form>
    </section>
  </section>
</template>
