// 방명록 API — 외부 의존성 없이 Node 내장 모듈(node:sqlite)만 사용
import http from 'node:http';
import { DatabaseSync } from 'node:sqlite';
import { randomBytes, scryptSync, timingSafeEqual } from 'node:crypto';
import { mkdirSync } from 'node:fs';
import path from 'node:path';

const PORT = Number(process.env.PORT ?? 3000);
const DB_PATH = process.env.DB_PATH ?? './data/guestbook.db';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD ?? '';

mkdirSync(path.dirname(DB_PATH), { recursive: true });
const db = new DatabaseSync(DB_PATH);
db.exec(`
  PRAGMA journal_mode = WAL;
  CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    message TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    ip TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
  );
`);

const sql = {
  list: db.prepare('SELECT id, name, message, created_at AS createdAt FROM entries ORDER BY id DESC LIMIT ? OFFSET ?'),
  count: db.prepare('SELECT COUNT(*) AS n FROM entries'),
  insert: db.prepare('INSERT INTO entries (name, message, password_hash, ip) VALUES (?, ?, ?, ?)'),
  hashOf: db.prepare('SELECT password_hash FROM entries WHERE id = ?'),
  remove: db.prepare('DELETE FROM entries WHERE id = ?'),
};

// ── 비밀번호 해시 ────────────────────────────────────────────
function hashPassword(pw) {
  const salt = randomBytes(16);
  return `${salt.toString('hex')}:${scryptSync(pw, salt, 32).toString('hex')}`;
}

function verifyPassword(pw, stored) {
  const [salt, hash] = stored.split(':');
  return timingSafeEqual(Buffer.from(hash, 'hex'), scryptSync(pw, Buffer.from(salt, 'hex'), 32));
}

function isAdmin(pw) {
  if (!ADMIN_PASSWORD) return false;
  const a = Buffer.from(pw);
  const b = Buffer.from(ADMIN_PASSWORD);
  return a.length === b.length && timingSafeEqual(a, b);
}

// ── IP별 요청 제한 (메모리) ──────────────────────────────────
const hits = new Map();
function rateLimited(key, max, windowMs) {
  const now = Date.now();
  const recent = (hits.get(key) ?? []).filter((t) => now - t < windowMs);
  const limited = recent.length >= max;
  if (!limited) recent.push(now);
  hits.set(key, recent);
  return limited;
}
setInterval(() => {
  const now = Date.now();
  for (const [key, times] of hits) if (times.every((t) => now - t > 3_600_000)) hits.delete(key);
}, 600_000).unref();

// ── 유틸 ─────────────────────────────────────────────────────
// Caddy가 설정하는 X-Forwarded-For의 첫 값이 실제 클라이언트 IP
const clientIp = (req) => (req.headers['x-forwarded-for']?.split(',')[0] ?? req.socket.remoteAddress ?? '').trim();

const clean = (v) =>
  typeof v === 'string'
    ? v
        .replace(/[\u0000-\u0009\u000B-\u001F\u007F]/g, '')
        .replace(/\n{3,}/g, '\n\n')
        .trim()
    : '';

const len = (s) => [...s].length;

function send(res, status, body) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(JSON.stringify(body));
}

function readJson(req, limit = 16_384) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (c) => {
      size += c.length;
      if (size > limit) {
        reject(new Error('too large'));
        req.destroy();
      } else chunks.push(c);
    });
    req.on('end', () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}'));
      } catch {
        reject(new Error('bad json'));
      }
    });
    req.on('error', reject);
  });
}

// ── 라우트 ───────────────────────────────────────────────────
async function handle(req, res) {
  const url = new URL(req.url, 'http://localhost');
  const ip = clientIp(req);

  if (url.pathname === '/api/health') return send(res, 200, { ok: true });

  if (url.pathname === '/api/guestbook' && req.method === 'GET') {
    const limit = Math.min(Math.max(Number(url.searchParams.get('limit')) || 10, 1), 30);
    const offset = Math.max(Number(url.searchParams.get('offset')) || 0, 0);
    return send(res, 200, { items: sql.list.all(limit, offset), total: sql.count.get().n });
  }

  if (url.pathname === '/api/guestbook' && req.method === 'POST') {
    if (rateLimited(`post:${ip}`, 5, 600_000)) return send(res, 429, { error: '잠시 후 다시 작성해 주세요' });
    const body = await readJson(req);
    const name = clean(body.name);
    const message = clean(body.message);
    const password = typeof body.password === 'string' ? body.password : '';

    if (len(name) < 1 || len(name) > 20) return send(res, 400, { error: '이름은 1~20자로 입력해 주세요' });
    if (len(message) < 1 || len(message) > 500) return send(res, 400, { error: '메시지는 1~500자로 입력해 주세요' });
    if (len(password) < 4 || len(password) > 20) return send(res, 400, { error: '비밀번호는 4~20자로 입력해 주세요' });

    const { lastInsertRowid } = sql.insert.run(name, message, hashPassword(password), ip);
    return send(res, 201, { id: Number(lastInsertRowid) });
  }

  const del = url.pathname.match(/^\/api\/guestbook\/(\d+)$/);
  if (del && req.method === 'DELETE') {
    if (rateLimited(`del:${ip}`, 10, 600_000)) return send(res, 429, { error: '잠시 후 다시 시도해 주세요' });
    const { password = '' } = await readJson(req);
    const row = sql.hashOf.get(Number(del[1]));
    if (!row) return send(res, 404, { error: '이미 삭제된 메시지입니다' });
    if (typeof password !== 'string' || !(isAdmin(password) || verifyPassword(password, row.password_hash))) {
      return send(res, 403, { error: '비밀번호가 일치하지 않습니다' });
    }
    sql.remove.run(Number(del[1]));
    return send(res, 200, { ok: true });
  }

  send(res, 404, { error: 'not found' });
}

const server = http.createServer((req, res) =>
  handle(req, res).catch((err) => {
    console.error(err);
    if (!res.headersSent) send(res, 400, { error: '요청을 처리하지 못했습니다' });
  }),
);

server.listen(PORT, () => console.log(`guestbook api listening on :${PORT}`));

for (const sig of ['SIGTERM', 'SIGINT']) {
  process.on(sig, () => server.close(() => (db.close(), process.exit(0))));
}
