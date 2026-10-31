let toastTimer: number | undefined;

export function toast(message: string) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = message;
  el.classList.add('is-shown');
  clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => el.classList.remove('is-shown'), 2000);
}

export async function copyText(text: string, done = '복사되었습니다') {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    // 일부 인앱 브라우저는 Clipboard API 미지원
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:fixed;opacity:0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    ta.remove();
  }
  toast(done);
}
