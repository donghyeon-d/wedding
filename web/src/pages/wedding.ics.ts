// '캘린더에 추가하기'용 일정 파일 (빌드 시 dist/wedding.ics 로 생성)
import type { APIRoute } from 'astro';
import { config } from '../config';
import { calendarEvent } from '../lib/calendar';

export const GET: APIRoute = () => {
  const e = calendarEvent();
  // RFC 5545: 쉼표·세미콜론·줄바꿈 이스케이프
  const esc = (s: string) => s.replace(/\\/g, '\\\\').replace(/([,;])/g, '\\$1').replace(/\n/g, '\\n');
  const ics = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//wedding//invitation//KO',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'BEGIN:VEVENT',
    `UID:wedding-${e.start}@${new URL(config.siteUrl).hostname}`,
    `DTSTAMP:${e.start}`,
    `DTSTART:${e.start}`,
    `DTEND:${e.end}`,
    `SUMMARY:${esc(e.title)}`,
    `LOCATION:${esc(e.location)}`,
    `DESCRIPTION:${esc(e.details)}`,
    'BEGIN:VALARM',
    'TRIGGER:-P1D',
    'ACTION:DISPLAY',
    `DESCRIPTION:${esc(e.title)}`,
    'END:VALARM',
    'END:VEVENT',
    'END:VCALENDAR',
  ].join('\r\n');
  return new Response(ics, { headers: { 'Content-Type': 'text/calendar; charset=utf-8' } });
};
