import { defineConfig } from 'astro/config';

export default defineConfig({
  vite: {
    server: {
      // 로컬 개발 시 방명록 API(node ../api/server.mjs)로 프록시
      proxy: { '/api': 'http://localhost:3000' },
    },
  },
});
