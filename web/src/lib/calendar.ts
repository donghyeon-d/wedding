import { config } from '../config';

/** 예식 일정 (시작·끝은 UTC 'YYYYMMDDTHHMMSSZ') — .ics 파일과 구글 캘린더 링크가 같이 쓴다 */
export function calendarEvent() {
  const { groom, bride, venue } = config;
  const start = new Date(config.date);
  const startMs = start.getTime();
  const end = new Date(start.getTime() + 2 * 60 * 60 * 1000); // 예식 + 식사 약 2시간
  const fmt = (d: Date) => d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
  return {
    startMs,
    endMs: end.getTime(),
    start: fmt(start),
    end: fmt(end),
    title: `${groom.lastName}${groom.firstName} ♥ ${bride.lastName}${bride.firstName} 결혼식`,
    location: `${venue.name}${venue.hall ? ` ${venue.hall}` : ''}, ${venue.address}`,
    details: `${config.siteUrl}`,
  };
}

export function googleCalendarUrl() {
  const e = calendarEvent();
  const q = new URLSearchParams({
    action: 'TEMPLATE',
    text: e.title,
    dates: `${e.start}/${e.end}`,
    location: e.location,
    details: e.details,
    ctz: 'Asia/Seoul',
  });
  return `https://calendar.google.com/calendar/render?${q}`;
}

/**
 * 안드로이드: 기기 캘린더 앱(구글·삼성 캘린더)의 '일정 추가' 화면을 바로 여는 intent 링크.
 * 캘린더 앱이 없거나 intent를 막는 브라우저면 browser_fallback_url(구글 캘린더 웹)로 이동.
 */
export function androidCalendarIntent() {
  const e = calendarEvent();
  const s = (k: string, v: string) => `S.${k}=${encodeURIComponent(v)}`;
  return [
    'intent:#Intent',
    'action=android.intent.action.INSERT',
    'type=vnd.android.cursor.dir/event',
    s('title', e.title),
    s('eventLocation', e.location),
    s('description', e.details),
    `l.beginTime=${e.startMs}`,
    `l.endTime=${e.endMs}`,
    s('browser_fallback_url', googleCalendarUrl()),
    'end',
  ].join(';');
}
