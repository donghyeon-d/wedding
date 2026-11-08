import { config } from '../config';

/** 예식 일정 (시작·끝은 UTC 'YYYYMMDDTHHMMSSZ') — .ics 파일과 구글 캘린더 링크가 같이 쓴다 */
export function calendarEvent() {
  const { groom, bride, venue } = config;
  const start = new Date(config.date);
  const end = new Date(start.getTime() + 2 * 60 * 60 * 1000); // 예식 + 식사 약 2시간
  const fmt = (d: Date) => d.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
  return {
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
