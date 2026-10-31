// ─────────────────────────────────────────────────────────────
// 청첩장의 모든 문구·정보는 이 파일 하나에서 수정합니다.
// 사진: src/assets/cover.jpg (메인), src/assets/gallery/* (갤러리, 파일명 순 정렬)
// 카카오톡 미리보기 이미지: public/og.jpg (1200×630 권장)
// ─────────────────────────────────────────────────────────────

export const config = {
  /** 실제 서비스 주소 (카카오 공유·미리보기에 사용) */
  siteUrl: 'https://wedding.example.com',

  groom: {
    lastName: '최',
    firstName: '동환',
    father: '김철수',
    mother: '박영희',
    relation: '아들',
  },
  bride: {
    lastName: '김',
    firstName: '해리',
    father: '이영호',
    mother: '최미경',
    relation: '딸',
  },

  /** 예식 일시 (반드시 +09:00 형식 유지) */
  date: '2026-12-19T12:30:00+09:00',

  venue: {
    name: '더 베니르',
    hall: '', // 홀 이름 (예: '5층 ○○홀')
    address: '경기 안산시 단원구 광덕4로 256',
    tel: '031-484-8300',
    lat: 37.3143769,
    lng: 126.8408643,
    naverMapUrl: 'https://naver.me/G1wSzknb',
    kakaoMapUrl: 'https://kko.to/bUUPQGg4lE',
  },

  greeting: {
    title: '소중한 분들을 초대합니다',
    // 빈 문자열('')은 문단 사이 여백
    body: [
      '서로 다른 길을 걸어온 두 사람이',
      '이제 같은 곳을 바라보며 걸어가려 합니다.',
      '',
      '첫눈이 내리는 계절,',
      '저희의 새로운 시작을 축복해 주시면',
      '더없는 기쁨으로 간직하겠습니다.',
    ],
  },

  transport: [
    { label: '지하철', lines: ['2호선 ○○역 1번 출구 도보 5분'] },
    { label: '버스', lines: ['간선 000, 000 / 지선 0000', '○○역 정류장 하차'] },
    { label: '주차', lines: ['건물 내 지하 주차장 2시간 무료', '안내데스크에서 주차 등록해 주세요'] },
  ],

  accounts: {
    groom: [
      { role: '신랑', name: '최동환', bank: '○○은행', number: '000-0000-0000-00' },
      { role: '아버지', name: '김철수', bank: '○○은행', number: '000-0000-0000-00' },
      { role: '어머니', name: '박영희', bank: '○○은행', number: '000-0000-0000-00' },
    ],
    bride: [
      { role: '신부', name: '김해리', bank: '○○은행', number: '000-0000-0000-00' },
      { role: '아버지', name: '이영호', bank: '○○은행', number: '000-0000-0000-00' },
      { role: '어머니', name: '최미경', bank: '○○은행', number: '000-0000-0000-00' },
    ],
  },

  /** 갤러리에 처음 보여줄 사진 수 (나머지는 '더보기') */
  galleryInitialCount: 9,

  share: {
    /** 카카오 디벨로퍼스 → 내 애플리케이션 → 앱 키 → JavaScript 키 (비워두면 카카오 공유 버튼 숨김) */
    kakaoJsKey: '',
    title: '최동환 ♥ 김해리 결혼합니다',
    description: '2026년 12월 19일 토요일 낮 12시 30분\n더 베니르',
  },

  /** 네이버 클라우드 플랫폼 → Maps → Application의 Client ID (비워두면 지도 대신 안내 박스) */
  naverMapKeyId: '',

  /** 배경음악 파일 경로 (예: '/bgm.mp3' 를 public/ 에 넣기). 비워두면 버튼 숨김 */
  bgm: '',
};
