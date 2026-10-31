# 1) Astro 빌드
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# 2) Caddy로 정적 파일 서빙 + HTTPS 자동 발급
FROM caddy:2-alpine
COPY --from=build /app/dist /srv
