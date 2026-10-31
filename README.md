# 모바일 청첩장

Astro로 만든 정적 페이지, Node 내장 SQLite를 쓰는 방명록 API, 자동 HTTPS를 처리하는 Caddy를 Docker Compose로 묶었습니다.

```
wedding/
├─ web/                     # 청첩장 페이지 (Astro)
│  ├─ src/config.ts         # ★ 이름·날짜·장소·계좌·인사말 등 모든 문구
│  ├─ src/assets/cover.jpg  # ★ 메인 사진
│  ├─ src/assets/gallery/   # ★ 갤러리 사진 (파일명 순 정렬, 자동 WebP 변환)
│  └─ public/og.jpg         # ★ 카카오톡 미리보기 이미지 (1200×630)
├─ api/server.mjs           # 방명록 API (의존성 없음)
├─ Caddyfile                # HTTPS + /api 프록시
├─ docker-compose.yml
└─ .env.example
```

## 1. 내용 채우기

1. `web/src/config.ts`의 문구를 모두 실제 정보로 바꿉니다.
2. 사진을 교체합니다. 지금 들어 있는 사진은 모두 임시 이미지입니다.
   - `web/src/assets/cover.jpg`: 세로 사진 권장 (3:4 비율로 잘림)
   - `web/src/assets/gallery/`: 기존 파일을 지우고 `01.jpg`, `02.jpg` … 순서로 넣기 (원본 크기 그대로 넣어도 빌드할 때 자동으로 줄임)
   - `web/public/og.jpg`: 1200×630
3. 배경음악을 쓰려면 `web/public/bgm.mp3`를 넣고 `config.bgm = '/bgm.mp3'`로 설정합니다.

## 2. 외부 키 발급

| 항목 | 발급처 | 설정 위치 |
|---|---|---|
| 네이버 지도 | [네이버 클라우드 플랫폼](https://console.ncloud.com) → Application Services → Maps → Application 등록 (Dynamic Map 선택, Web 서비스 URL에 도메인 등록) | `config.naverMapKeyId` (Client ID) |
| 카카오톡 공유 | [카카오 디벨로퍼스](https://developers.kakao.com) → 애플리케이션 추가 → 플랫폼 → Web 사이트 도메인 등록 | `config.share.kakaoJsKey` (JavaScript 키) |

키를 비워두면 지도 자리에는 안내 문구가 나오고, 카카오 공유 버튼은 숨겨집니다.

## 3. 로컬에서 미리보기 (Windows)

```bash
# 터미널 1: 방명록 API
cd api && node server.mjs

# 터미널 2: 페이지 (저장하면 자동 새로고침)
cd web && npm install && npm run dev
```

브라우저에서 http://localhost:4321 을 엽니다. 크롬 개발자도구의 모바일 보기(Ctrl+Shift+M)로 확인하세요.

## 4. 홈서버 배포 (Rocky Linux)

```bash
# 1) 프로젝트 폴더를 서버로 복사 (node_modules, dist 제외)
#    예: scp -r wedding/ user@server:~/   또는 git 사용

# 2) 방화벽 열기
sudo firewall-cmd --permanent --add-service=http --add-service=https
sudo firewall-cmd --permanent --add-port=443/udp
sudo firewall-cmd --reload

# 3) 환경변수 설정
cd ~/wedding
cp .env.example .env
vi .env          # DOMAIN, ADMIN_PASSWORD 수정

# 4) 실행 (처음에는 이미지 빌드로 몇 분 걸림)
docker compose up -d --build
docker compose logs -f web    # 인증서 발급 로그 확인
```

**사전 조건**
- 도메인 DNS의 A 레코드가 집 공인 IP를 가리켜야 합니다.
- 공유기에서 80, 443 포트를 서버로 포트포워딩해야 합니다.
- 두 조건이 맞으면 Caddy가 Let's Encrypt 인증서를 자동으로 발급하고 갱신합니다.

**내용을 수정한 뒤에는** 같은 명령으로 다시 빌드합니다: `docker compose up -d --build web`

## 5. 방명록 관리

- 부적절한 글은 해당 글의 ✕ 버튼을 누르고 `.env`의 `ADMIN_PASSWORD`를 입력하면 삭제됩니다.
- 같은 IP에서 10분에 작성 5회, 삭제 시도 10회까지만 허용합니다.
- 백업:
  ```bash
  docker compose exec api node -e "new (require('node:sqlite').DatabaseSync)('/data/guestbook.db').exec(\"VACUUM INTO '/data/backup.db'\")"
  docker compose cp api:/data/backup.db ./guestbook-backup.db
  docker compose exec api rm /data/backup.db
  ```

## 6. 카카오톡 미리보기가 안 바뀔 때

카카오는 미리보기를 캐시합니다. 내용을 바꾼 뒤에는 [카카오 공유 디버거](https://developers.kakao.com/tool/debugger/sharing)에서 주소를 입력하고 **캐시 초기화**를 눌러주세요.

## 참고: Cloudflare를 앞에 둘 경우

포트를 열기 어렵거나 집 IP를 숨기고 싶다면 Cloudflare Tunnel을 쓸 수 있습니다. 이때는 모든 요청이 Cloudflare IP로 들어오므로, 방명록의 IP 제한이 제대로 동작하도록 Caddyfile의 `reverse_proxy`에 Cloudflare를 신뢰 프록시로 추가하고, 클라이언트 IP를 `CF-Connecting-IP` 헤더에서 읽도록 바꿔야 합니다.
