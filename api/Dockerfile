FROM node:24-alpine
WORKDIR /app
COPY server.mjs .
ENV NODE_ENV=production \
    DB_PATH=/data/guestbook.db \
    NODE_NO_WARNINGS=1
RUN mkdir /data && chown node:node /data
USER node
VOLUME /data
EXPOSE 3000
CMD ["node", "server.mjs"]
