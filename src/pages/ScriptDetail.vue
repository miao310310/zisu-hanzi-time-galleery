<script setup>
import {computed} from 'vue';
import {useRoute} from 'vue-router';
import {scripts} from '../data';
import ArtworkGallery from '../components/ArtworkGallery.vue';
const route=useRoute();
const index=computed(()=>/^\d+$/.test(String(route.params.id))?Number(route.params.id):-1);
const item=computed(()=>scripts[index.value]);
const notes=[
 ['从契刻的痕迹认识文字','甲骨文专题围绕线条、轮廓与象形意趣展开。先观察形体如何组织，再理解文字与记录之间的联系。','留意线条的转折与各部分的位置；不要把现代装饰字体当成甲骨字形。'],
 ['在青铜器上读见文字','金文专题关注青铜器文字的形态与布局。观察单字之外，也可以留意文字如何在器物表面排列。','比较线条粗细、字内空间与整体布局，不同器物上的文字可能各有面貌。'],
 ['在线条中发现秩序','小篆专题从圆转、匀整和修长结构入手。观察笔画之间的距离，体会整齐而不僵硬的视觉节奏。','从整体长宽比例开始，再比较左右两侧的呼应关系。'],
 ['看见横向舒展的力量','隶书专题以扁平结构与横向展开为观察入口。将注意力放在主笔、收笔和字的重心上。','观察横画的展开如何影响重心；不同作品的笔画形态并不完全相同。'],
 ['一笔一画，读懂结构','楷书专题关注清晰的点画与端正的结构。通过比较笔画长短、间距和留白，建立临习前的观察习惯。','不急着描摹，先找出主笔、重心和最明显的空间关系。'],
 ['笔势之间，感受节奏','这里将行书与草书合为一个展览入口。二者是不同书体；欣赏时既要观察连贯的笔势，也要注意各自的结构特点。','观察笔画如何呼应、疏密如何变化；连笔多寡不能单独作为区分书体的依据。']
];
function readMore(){document.getElementById('script-reading')?.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'})}
</script>
<template><section v-if="item" class="detail-page"><div class="script-cover"><div class="script-cover-copy"><span class="sub">{{String(index+2).padStart(2,'0')}} / 08 · {{item.era}}</span><h1>{{item.name}}</h1><h2>{{item.title}}</h2><p>{{item.description}}</p><button class="underlink" @click="readMore">向下阅读本展介绍 ↓</button></div><figure class="script-poster"><img :src="item.poster" :alt="`${item.name}专题海报`"><figcaption>书体导览 · 团队整理素材</figcaption></figure></div>
<div id="script-reading" class="script-reading"><span class="sub">01 / 本页讲什么</span><h2>{{notes[index][0]}}</h2><p>{{notes[index][1]}}</p><p class="quiet">年代标签用于概览，不代表字体只存在于该时期。资料正在整理，重要结论应结合可靠来源核查。</p></div>
<section class="detail-content"><span class="sub">02 / 怎样欣赏</span><div class="observation-grid"><article><span class="sub">看整体</span><h3>先看结构</h3><p>{{notes[index][2]}}</p></article><article><span class="sub">看局部</span><h3>再看线条</h3><p>观察粗细、曲直、转折与留白，用自己的话描述最明显的特征。</p></article><article><span class="sub">带着问题</span><h3>继续追问</h3><p>将你的观察交给书法伴学，询问欣赏方法与临习建议。</p><RouterLink class="underlink" :to="{path:'/chat',query:{q:`请介绍${item.name}的特点，并给我三个欣赏作品时的观察建议`,script:item.name}}">向 AI 提问 ↗</RouterLink></article></div></section>
<ArtworkGallery :script="item" />
<div class="detail-next"><RouterLink :to="index===0?'/':'/scripts/'+(index-1)">← 上一展</RouterLink><RouterLink :to="index===5?'/chat':'/scripts/'+(index+1)">{{index===5?'前往 AI 书法问答':'继续探索 · '+scripts[index+1].name}} →</RouterLink></div></section><section v-else class="section"><h2>没有找到这个字体专题</h2><RouterLink to="/">返回首页 →</RouterLink></section></template>
