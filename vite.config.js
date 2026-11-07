import {defineConfig} from 'vite';
import vue from '@vitejs/plugin-vue';
export default defineConfig({
  base:process.env.GITHUB_PAGES==='true'?'/zisu-hanzi-time-galleery/':'/',
  plugins:[vue()],
  server:{proxy:{'/api':{target:process.env.API_PROXY_TARGET||'http://127.0.0.1:8000',changeOrigin:true}}}
});
