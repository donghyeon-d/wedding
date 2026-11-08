# 청첩장 BGM 합성: 사장조 80BPM, 피아노 아르페지오 + 오르골 멜로디 + 패드 + 베이스
# 사용: python3 tools/make_bgm.py /tmp/bgm.wav && afconvert -f m4af -d aac -b 128000 -q 127 /tmp/bgm.wav web/public/bgm/calm.m4a
# 버퍼 길이로 감싸서(원형) 렌더링하므로 끝 → 처음이 끊김 없이 반복된다.
import sys
import numpy as np
from scipy.io import wavfile

SR = 44100
BPM = 80
BEAT = 60 / BPM
BAR = 4 * BEAT
BARS = 32
L = int(round(BARS * BAR * SR))
rng = np.random.default_rng(7)

mix = {k: np.zeros((2, L)) for k in ('piano', 'bell', 'pad', 'bass')}

def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)

def place(bus, sig, t0, pan=0.0):
    """t0초에 신호를 원형 버퍼에 더함 (pan -1~1)"""
    i0 = int(round(t0 * SR)) % L
    n = len(sig)
    idx = (np.arange(n) + i0) % L
    lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    np.add.at(mix[bus][0], idx, sig * lg)
    np.add.at(mix[bus][1], idx, sig * rg)

def adsr_tail(n_on, rel, sr=SR):
    nr = int(rel * sr)
    env = np.ones(n_on + nr)
    env[n_on:] = np.linspace(1, 0, nr) ** 2
    return env

def piano(m, dur, vel):
    f = hz(m)
    n_on = int(dur * SR)
    env_r = adsr_tail(n_on, 0.35)
    t = np.arange(len(env_r)) / SR
    tau = 1.3 * (220 / f) ** 0.35
    s = np.zeros_like(t)
    for k, a in enumerate([1, 0.45, 0.2, 0.1, 0.05], start=1):
        fk = f * k * (1 + 0.0004 * k * k)  # 살짝 비조화 → 피아노 느낌
        if fk > SR / 2.2:
            break
        s += a * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t * k ** 0.8 / tau)
    att = np.minimum(1, t / 0.004)
    return vel * s * att * env_r

def bell(m, dur, vel):
    f = hz(m)
    n_on = int(max(dur, 1.2) * SR)
    env_r = adsr_tail(n_on, 0.6)
    t = np.arange(len(env_r)) / SR
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t / 1.6)
         + 0.28 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t / 0.7)
         + 0.08 * np.sin(2 * np.pi * f * 3.0 * t) * np.exp(-t / 0.35)
         + 0.05 * np.sin(2 * np.pi * f * 4.16 * t) * np.exp(-t / 0.2))
    att = np.minimum(1, t / 0.003)
    return vel * s * att * env_r

def pad(m, dur, vel):
    f = hz(m)
    n = int((dur + 1.4) * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for c in (-5, 0, 5):
        fc = f * 2 ** (c / 1200)
        s += np.sin(2 * np.pi * fc * t + rng.uniform(0, 6.28)) + 0.18 * np.sin(4 * np.pi * fc * t)
    env = np.minimum(1, t / 0.9)
    rel_start = dur
    env *= np.where(t > rel_start, np.clip(1 - (t - rel_start) / 1.4, 0, 1) ** 2, 1)
    return vel * s / 3 * env

def bass(m, dur, vel):
    f = hz(m)
    n_on = int(dur * SR)
    env_r = adsr_tail(n_on, 0.4)
    t = np.arange(len(env_r)) / SR
    s = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.4)) * np.exp(-t / 2.2)
    return vel * s * np.minimum(1, t / 0.012) * env_r

# 마디별 코드: (베이스, [화음 3음])
G = (43, [55, 59, 62]); Dfs = (42, [54, 57, 62]); Em = (40, [52, 55, 59]); C = (36, [52, 55, 60])
D = (38, [54, 57, 62]); Am = (45, [52, 57, 60])
prog16 = [G, Dfs, Em, C, G, Dfs, Em, C, G, D, C, D, Em, C, Am, D]
prog = prog16 * 2

# 멜로디 (마디 0-기준, 박, 음, 길이) — 한 패스(16마디) 중 5~16마디
mel16 = [
    (4, 0, 71, 1.5), (4, 1.5, 69, 0.5), (4, 2, 67, 1), (4, 3, 74, 1),
    (5, 0, 74, 1.5), (5, 1.5, 76, 0.5), (5, 2, 78, 1), (5, 3, 74, 1),
    (6, 0, 76, 2), (6, 2, 79, 1), (6, 3, 78, 1),
    (7, 0, 76, 1.5), (7, 1.5, 74, 0.5), (7, 2, 72, 1), (7, 3, 71, 1),
    (8, 0, 71, 1), (8, 1, 74, 1), (8, 2, 79, 1.5), (8, 3.5, 78, 0.5),
    (9, 0, 76, 1), (9, 1, 74, 1), (9, 2, 69, 2),
    (10, 0, 72, 1), (10, 1, 76, 1), (10, 2, 79, 1), (10, 3, 76, 1),
    (11, 0, 78, 2), (11, 2, 81, 1), (11, 3, 78, 1),
    (12, 0, 79, 1.5), (12, 1.5, 78, 0.5), (12, 2, 76, 1), (12, 3, 71, 1),
    (13, 0, 72, 1), (13, 1, 76, 1), (13, 2, 79, 2),
    (14, 0, 81, 1.5), (14, 1.5, 79, 0.5), (14, 2, 76, 1), (14, 3, 72, 1),
    (15, 0, 74, 3),
]

arp_pat = [0, 1, 2, 3, 2, 1, 2, 1]
E8 = BEAT / 2
for b, (bn, tones) in enumerate(prog):
    t0 = b * BAR
    tt = tones + [tones[0] + 12]
    intro = b < 4
    for i, p in enumerate(arp_pat):
        human = rng.normal(0, 0.006)
        vel = (0.16 if intro else 0.13) * (1.0 if i % 2 == 0 else 0.78) * rng.uniform(0.92, 1.05)
        place('piano', piano(tt[p], E8 * 1.6, vel), t0 + i * E8 + human, pan=(-0.35 + 0.1 * p))
    for m in tones:
        place('pad', pad(m, BAR, 0.035), t0, pan=rng.uniform(-0.5, 0.5))
    if b >= 2:
        place('bass', bass(bn, BEAT * 1.9, 0.30), t0)
        place('bass', bass(bn, BEAT * 1.4, 0.18), t0 + 2.5 * BEAT)

for pas in range(2):
    off = pas * 16
    for bar, beat, m, dur in mel16:
        t = (off + bar) * BAR + beat * BEAT + rng.normal(0, 0.004)
        if pas == 1 and bar < 8:
            # 2번째 패스 앞부분은 피아노가 한 옥타브 아래로 부드럽게
            place('piano', piano(m - 12, dur * BEAT, 0.20), t, pan=0.15)
        else:
            place('bell', bell(m, dur * BEAT, 0.16), t, pan=0.2)
            if pas == 1:
                place('bell', bell(m + 12, dur * BEAT, 0.035), t + 0.01, pan=-0.3)

# 리버브: 지수감쇠 노이즈 IR을 원형 컨볼루션 (반복 지점에서도 잔향이 이어짐)
def reverb(x, secs=2.4, seed=0):
    n = int(secs * SR)
    r = np.random.default_rng(seed)
    t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t / (secs / 6.9))
    # 고역 감쇠 (부드러운 잔향)
    k = 12
    ir = np.convolve(ir, np.ones(k) / k, mode='same')
    ir /= np.sqrt(np.sum(ir ** 2))
    h = np.zeros(L); h[:n] = ir
    return np.real(np.fft.ifft(np.fft.fft(x) * np.fft.fft(h)))

dry = 1.0 * mix['piano'] + 1.0 * mix['bell'] + 1.0 * mix['pad'] + 1.0 * mix['bass']
send = 0.9 * mix['piano'] + 1.3 * mix['bell'] + 0.8 * mix['pad'] + 0.1 * mix['bass']
wet = np.stack([reverb(send[0], seed=1), reverb(send[1], seed=2)])
out = dry + 0.32 * wet

# 아주 부드러운 저역 컷(럼블 제거): 원형 FFT로 30Hz 이하 감쇠
F = np.fft.rfft(out, axis=1)
fr = np.fft.rfftfreq(L, 1 / SR)
F *= np.clip(fr / 30, 0, 1)[None, :]
out = np.fft.irfft(F, n=L, axis=1)

# 음량: RMS -21 dBFS 목표, 피크는 -1.5 dBFS 이하
rms = np.sqrt(np.mean(out ** 2))
out *= 10 ** (-21 / 20) / rms
peak = np.max(np.abs(out))
if peak > 10 ** (-1.5 / 20):
    out *= 10 ** (-1.5 / 20) / peak
print('len %.1fs  rms %.1f dBFS  peak %.1f dBFS' % (L / SR, 20 * np.log10(np.sqrt(np.mean(out ** 2))), 20 * np.log10(np.max(np.abs(out)))))
wavfile.write(sys.argv[1], SR, (out.T * 32767).astype(np.int16))
