import {characters,scripts} from '../data';
import {createSSEParser} from './sse';
export const demoMode=import.meta.env.VITE_API_MODE!=='api';
const base=(import.meta.env.VITE_API_BASE||'/api').replace(/\/$/,'');
function demoReply(question){
  const script=scripts.find(item=>question.includes(item.name));
  const character=characters.find(item=>question.includes(item.character));
  if(script)return `${script.name}：${script.description}\n\n你可以先按这个顺序观察：${script.overview.tip}`;
  if(character)return `${character.character}：${character.description}\n\n试着把它的整体轮廓、主笔与留白分开看，再回到具体笔画。`;
  if(/临写|临摹|主笔|重心|留白/.test(question))return '临写前先找一个字最影响稳定感的主笔，再比较上下、左右的留白是否均衡。先用慢速试笔确认结构，不要一开始就追求笔画的形状或速度。';
  if(/碑帖|作品|赏析|观察/.test(question))return '赏析一件碑帖时，可以先退后看整体章法和行列，再看单字的重心与留白，最后观察线条的转折、轻重和节奏。不要急着给作品贴固定标签，把你实际看到的细节记下来更重要。';
  return '你可以询问六种书体的特点、如何赏析碑帖，或日、山、水、木的形与意。';
}
export async function getCharacter(char,signal){if(demoMode){const item=characters.find(x=>x.character===char);if(!item)throw new Error('当前示例未收录此字，请选择日、山、水、木。');return item}const r=await fetch(base+'/characters/'+encodeURIComponent(char),{signal});if(!r.ok)throw new Error(r.status===404?'暂未收录这个字':'查询失败，请稍后重试。');const item=await r.json();if(typeof item.character!=='string'||typeof item.description!=='string')throw new Error('接口返回格式不正确。');return item}
export async function streamChat({question,context,history=[],signal,onDelta,onSources}){if(demoMode){const answer=demoReply(question)+'\n\n这是本地预设答疑演示，不是真实模型回答；资料引用尚未接入。';for(const char of answer){if(signal.aborted)throw new DOMException('已停止','AbortError');await new Promise(r=>setTimeout(r,20));if(signal.aborted)throw new DOMException('已停止','AbortError');onDelta(char)}return}const r=await fetch(base+'/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question,context,history}),signal});if(!r.ok){const error=await r.json().catch(()=>({}));const message=typeof error.message==='string'?error.message:typeof error.detail==='string'?error.detail:'伴学服务暂不可用，请重试。';throw new Error(message)}if(!r.body)throw new Error('响应内容为空');let done=false;const parser=createSSEParser((type,raw)=>{if(raw==='[DONE]'){done=true;return}const obj=JSON.parse(raw);if(type==='error')throw new Error(obj.message||'生成失败');if(type==='delta'&&typeof obj.text==='string')onDelta(obj.text);if(type==='sources'&&Array.isArray(obj.sources))onSources(obj.sources);if(type==='done')done=true});const reader=r.body.getReader(),decoder=new TextDecoder();try{while(true){const part=await reader.read();if(part.done)break;parser.feed(decoder.decode(part.value,{stream:true}));if(done)break}parser.feed(decoder.decode());parser.finish();if(!done)throw new Error('连接提前结束，可重试回答。')}finally{await reader.cancel();reader.releaseLock()}}

