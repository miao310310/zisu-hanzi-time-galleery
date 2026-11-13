import {createApp} from 'vue';
import {createPinia} from 'pinia';
import {createRouter,createWebHashHistory} from 'vue-router';
import App from './App.vue';
import Home from './pages/Home.vue';
import './style.css';
const router=createRouter({history:createWebHashHistory(),routes:[{path:'/',component:Home},{path:'/scripts',component:()=>import('./pages/Scripts.vue')},{path:'/scripts/:id',component:()=>import('./pages/ScriptDetail.vue')},{path:'/explore',component:()=>import('./pages/Explore.vue')},{path:'/study',component:()=>import('./pages/Study.vue')},{path:'/chat',component:()=>import('./pages/Chat.vue')},{path:'/:pathMatch(.*)*',redirect:'/'}],scrollBehavior:()=>({top:0})});
createApp(App).use(createPinia()).use(router).mount('#app');
