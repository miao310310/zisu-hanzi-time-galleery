import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createRouter, createWebHashHistory } from 'vue-router';
import App from './App.vue';
import { scripts } from './data';
import Home from './pages/Home.vue';
import './style.css';

const defaultTitle = '字溯 · 汉字时光馆';
const defaultDescription = '从六类书体、汉字源流到范字试笔，建立可继续探索的汉字与书法学习路径。';

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'home', component: Home, meta: { title: defaultTitle, description: defaultDescription } },
    { path: '/scripts', name: 'scripts', component: () => import('./pages/Scripts.vue'), meta: { title: '六体专题索引 · 字溯', description: '从甲骨文到行草，比较六类代表性书体的形态、作品与观察线索。' } },
    { path: '/scripts/:id', name: 'script-detail', component: () => import('./pages/ScriptDetail.vue') },
    { path: '/explore', name: 'explore', component: () => import('./pages/Explore.vue'), meta: { title: '汉字溯源 · 字溯', description: '从熟悉的一个字出发，查看已收录的形意科普资料与后续练习入口。' } },
    { path: '/study', name: 'study', component: () => import('./pages/Study.vue'), meta: { title: '碑帖赏析与临写 · 字溯', description: '选择一类书体，观察团队整理的作品资料，再以分步范字完成结构试笔。' } },
    { path: '/chat', name: 'chat', component: () => import('./pages/Chat.vue'), meta: { title: 'AI 书法答疑 · 字溯', description: '围绕汉字源流、书体特点、碑帖观察与临习入门继续追问。' } },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ],
  scrollBehavior: () => ({ top: 0 })
});

function updateMeta(selector, content) {
  document.querySelector(selector)?.setAttribute('content', content);
}

router.afterEach(to => {
  const item = to.name === 'script-detail' ? scripts[Number(to.params.id)] : null;
  const title = item ? `${item.name} · ${item.title} · 字溯` : (to.meta.title || defaultTitle);
  const description = item ? item.description : (to.meta.description || defaultDescription);

  document.title = title;
  updateMeta('meta[name="description"]', description);
  updateMeta('meta[property="og:title"]', title);
  updateMeta('meta[property="og:description"]', description);
});

createApp(App).use(createPinia()).use(router).mount('#app');
