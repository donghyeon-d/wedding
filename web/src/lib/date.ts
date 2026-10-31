import { config } from '../config';

const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토'];
const WEEKDAYS_EN = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];

// 빌드 서버의 시간대와 무관하도록 문자열에서 직접 파싱
const m = config.date.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);
if (!m) throw new Error(`config.date 형식이 올바르지 않습니다: ${config.date}`);

export const wedding = {
  year: Number(m[1]),
  month: Number(m[2]),
  day: Number(m[3]),
  hour: Number(m[4]),
  minute: Number(m[5]),
  get weekday() {
    return new Date(Date.UTC(this.year, this.month - 1, this.day)).getUTCDay();
  },
};

export const weekdayKo = WEEKDAYS[wedding.weekday];
export const weekdayEn = WEEKDAYS_EN[wedding.weekday];

export const dateKo = `${wedding.year}년 ${wedding.month}월 ${wedding.day}일 ${weekdayKo}요일`;

export const dateDot = [wedding.year, wedding.month, wedding.day]
  .map((n) => String(n).padStart(2, '0'))
  .join('. ');

export const timeKo = (() => {
  const { hour, minute } = wedding;
  const label = hour < 12 ? '오전' : hour === 12 ? '낮' : '오후';
  const h = hour > 12 ? hour - 12 : hour;
  return `${label} ${h}시${minute ? ` ${minute}분` : ''}`;
})();

/** 해당 월 달력 (주 단위 배열, 빈 칸은 null) */
export function monthGrid(): (number | null)[][] {
  const first = new Date(Date.UTC(wedding.year, wedding.month - 1, 1)).getUTCDay();
  const days = new Date(Date.UTC(wedding.year, wedding.month, 0)).getUTCDate();
  const cells: (number | null)[] = [...Array(first).fill(null), ...Array.from({ length: days }, (_, i) => i + 1)];
  while (cells.length % 7) cells.push(null);
  return Array.from({ length: cells.length / 7 }, (_, i) => cells.slice(i * 7, i * 7 + 7));
}
