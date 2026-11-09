import { defineConfig } from 'astro/config';

// 예전 주소(/1 ~ /11)로 공유된 링크가 계속 열리도록: /4 는 최종 디자인인 / 로, 나머지는 /list/<번호> 로
const redirects = Object.fromEntries(
  Array.from({ length: 11 }, (_, i) => i + 1).map((n) => [`/${n}`, n === 4 ? '/' : `/list/${n}/`]),
);

export default defineConfig({
  redirects,
  vite: {
    server: {
      // 로컬 개발 시 방명록 API(node ../api/server.mjs)로 프록시
      proxy: { '/api': 'http://localhost:3000' },
    },
  },
});
