# 청첩장 BGM용 간단한 합성 엔진 (numpy/scipy)
# - 곡 길이만큼의 원형 버퍼에 음을 배치 → 끝과 처음이 끊김 없이 반복된다
# - 악기: piano, bell, glock, vibes, rhodes, pluck(Karplus-Strong), upright, flute, pad, bass
#         kick, clap, shaker, hat, ride, brush, rim
import numpy as np
from scipy.signal import butter, lfilter

SR = 44100


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


class Song:
    def __init__(self, seconds, seed=1):
        self.L = int(round(seconds * SR))
        self.rng = np.random.default_rng(seed)
        self.buses = {}

    def place(self, bus, sig, t0, pan=0.0, send=0.3):
        """t0초에 신호를 원형 버퍼에 더한다. send = 리버브로 보낼 양"""
        if bus not in self.buses:
            self.buses[bus] = [np.zeros((2, self.L)), send]
        buf = self.buses[bus][0]
        i0 = int(round(t0 * SR)) % self.L
        n = min(len(sig), self.L)
        sig = sig[:n]
        lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        end = i0 + n
        if end <= self.L:
            buf[0, i0:end] += sig * lg
            buf[1, i0:end] += sig * rg
        else:
            k = self.L - i0
            buf[0, i0:] += sig[:k] * lg
            buf[1, i0:] += sig[:k] * rg
            buf[0, : n - k] += sig[k:] * lg
            buf[1, : n - k] += sig[k:] * rg

    def render(self, reverb_secs=2.0, wet=0.3, rms_db=-20.0, peak_db=-1.5):
        L = self.L
        dry = np.zeros((2, L))
        send = np.zeros((2, L))
        for buf, s in self.buses.values():
            dry += buf
            send += buf * s
        wetsig = np.stack([_reverb(send[0], L, reverb_secs, 11), _reverb(send[1], L, reverb_secs, 12)])
        out = dry + wet * wetsig
        F = np.fft.rfft(out, axis=1)
        fr = np.fft.rfftfreq(L, 1 / SR)
        F *= np.clip(fr / 30, 0, 1)[None, :]  # 30Hz 이하 럼블 제거
        out = np.fft.irfft(F, n=L, axis=1)
        out *= 10 ** (rms_db / 20) / np.sqrt(np.mean(out ** 2))
        # 소프트 리미터 (피크만 살짝 눌러줌)
        lim = 10 ** (peak_db / 20)
        out = np.where(np.abs(out) > lim * 0.8, np.sign(out) * (lim * 0.8 + (lim * 0.2) * np.tanh((np.abs(out) - lim * 0.8) / (lim * 0.2))), out)
        return out


def _reverb(x, L, secs, seed):
    n = int(secs * SR)
    r = np.random.default_rng(seed)
    t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t / (secs / 6.9))
    ir = lfilter(*butter(1, 5000 / (SR / 2)), ir)
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))  # 프리딜레이 느낌
    ir /= np.sqrt(np.sum(ir ** 2))
    h = np.zeros(L)
    h[:n] = ir
    return np.real(np.fft.ifft(np.fft.fft(x) * np.fft.fft(h)))


# ── 공통 엔벨로프 ──
def _t(n):
    return np.arange(n) / SR


def _release(n_on, rel):
    nr = int(rel * SR)
    env = np.ones(n_on + nr)
    env[n_on:] = np.linspace(1, 0, nr) ** 2
    return env


def _att(t, a):
    return np.minimum(1, t / a)


# ── 음정 악기 ──
def piano(m, dur, vel, rng=np.random):
    f = hz(m)
    env = _release(int(dur * SR), 0.3)
    t = _t(len(env))
    tau = 1.3 * (220 / f) ** 0.35
    s = np.zeros_like(t)
    for k, a in enumerate([1, 0.45, 0.2, 0.1, 0.05], start=1):
        fk = f * k * (1 + 0.0004 * k * k)
        if fk > SR / 2.2:
            break
        s += a * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t * k ** 0.8 / tau)
    return vel * s * _att(t, 0.004) * env


def bell(m, dur, vel):
    """오르골/셀레스타"""
    f = hz(m)
    env = _release(int(max(dur, 1.0) * SR), 0.5)
    t = _t(len(env))
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t / 1.5)
         + 0.28 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t / 0.6)
         + 0.08 * np.sin(2 * np.pi * f * 3.0 * t) * np.exp(-t / 0.3)
         + 0.05 * np.sin(2 * np.pi * f * 4.16 * t) * np.exp(-t / 0.18))
    return vel * s * _att(t, 0.003) * env


def glock(m, dur, vel):
    """글로켄슈필: 밝고 맑은 금속음"""
    f = hz(m)
    env = _release(int(max(dur, 0.9) * SR), 0.4)
    t = _t(len(env))
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.9)
         + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.25)
         + 0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.08))
    return vel * s * _att(t, 0.0015) * env


def vibes(m, dur, vel):
    """비브라폰: 부드러운 금속음 + 트레몰로"""
    f = hz(m)
    env = _release(int(max(dur, 0.6) * SR), 0.6)
    t = _t(len(env))
    trem = 1 - 0.22 * (0.5 + 0.5 * np.sin(2 * np.pi * 5.2 * t))
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t / 2.2)
         + 0.18 * np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t / 0.35)
         + 0.06 * np.sin(2 * np.pi * f * 10.0 * t) * np.exp(-t / 0.05))
    return vel * s * trem * _att(t, 0.002) * env


def rhodes(m, dur, vel):
    """일렉트릭 피아노 (FM)"""
    f = hz(m)
    env = _release(int(dur * SR), 0.25)
    t = _t(len(env))
    idx = 1.6 * vel / 0.2 * np.exp(-t / 0.35) + 0.25
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    s += 0.12 * np.sin(2 * np.pi * f * 7.0 * t) * np.exp(-t / 0.03)  # 타인 소리
    return vel * s * np.exp(-t / 1.8) * _att(t, 0.002) * env


def pluck(m, dur, vel, bright=0.5, sustain=0.996, rng=np.random):
    """Karplus-Strong 현 (우쿨렐레·기타·피치카토)"""
    f = hz(m)
    N = int(round(SR / f))
    n = int((dur + 0.25) * SR)
    burst = rng.uniform(-1, 1, N)
    b, a = butter(1, min(0.99, 800 + bright * 9000) / (SR / 2))
    burst = lfilter(b, a, burst)
    x = np.zeros(n)
    x[:N] = burst
    a_coef = np.zeros(N + 2)
    a_coef[0] = 1
    a_coef[N] = -sustain / 2
    a_coef[N + 1] = -sustain / 2
    y = lfilter([1.0], a_coef, x)
    env = _release(int(dur * SR), 0.25)[:n]
    y = y[: len(env)] * env
    y /= np.max(np.abs(y)) + 1e-9
    return vel * y


def upright(m, dur, vel, rng=np.random):
    """콘트라베이스 (워킹)"""
    f = hz(m)
    env = _release(int(dur * SR), 0.12)
    t = _t(len(env))
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.9) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.3)
    thump = pluck(m + 12, dur, 1.0, bright=0.15, sustain=0.985, rng=rng)[: len(s)]
    s[: len(thump)] += 0.25 * thump
    return vel * s * _att(t, 0.006) * env


def flute(m, dur, vel, rng=np.random):
    f = hz(m)
    n_on = int(dur * SR)
    env = _release(n_on, 0.18)
    t = _t(len(env))
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5 * t) * np.clip((t - 0.25) / 0.3, 0, 1)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    s = np.sin(ph) + 0.12 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    noise = rng.standard_normal(len(t))
    b, a = butter(2, [max(100, f * 0.8) / (SR / 2), min(0.95, f * 3 / (SR / 2))], btype='band')
    s += 0.12 * lfilter(b, a, noise)
    a_env = np.minimum(1, t / 0.06)
    return vel * s * a_env * env


def pad(m, dur, vel, rng=np.random, attack=0.8, rel=1.3):
    f = hz(m)
    n = int((dur + rel) * SR)
    t = _t(n)
    s = np.zeros(n)
    for c in (-6, 0, 6):
        fc = f * 2 ** (c / 1200)
        s += np.sin(2 * np.pi * fc * t + rng.uniform(0, 6.28)) + 0.15 * np.sin(4 * np.pi * fc * t)
    env = np.minimum(1, t / attack) * np.where(t > dur, np.clip(1 - (t - dur) / rel, 0, 1) ** 2, 1)
    return vel * s / 3 * env


def bass(m, dur, vel):
    f = hz(m)
    env = _release(int(dur * SR), 0.15)
    t = _t(len(env))
    s = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.3)) * np.exp(-t / 1.5)
    return vel * s * _att(t, 0.008) * env


# ── 타악기 ──
def _noise(n, rng):
    return rng.standard_normal(n)


def _filt(x, lo=None, hi=None, order=2):
    if lo and hi:
        b, a = butter(order, [lo / (SR / 2), hi / (SR / 2)], btype='band')
    elif lo:
        b, a = butter(order, lo / (SR / 2), btype='high')
    else:
        b, a = butter(order, hi / (SR / 2))
    return lfilter(b, a, x)


def kick(vel):
    n = int(0.35 * SR)
    t = _t(n)
    f = 48 + 70 * np.exp(-t / 0.03)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)
    return vel * s


def clap(vel, rng):
    n = int(0.25 * SR)
    t = _t(n)
    env = np.zeros(n)
    for d in (0, 0.009, 0.018):
        env += np.where(t >= d, np.exp(-(t - d) / 0.006), 0) * 0.6
    env += np.where(t >= 0.025, np.exp(-(t - 0.025) / 0.07), 0) * 0.5
    return vel * _filt(_noise(n, rng), 900, 2600) * env


def shaker(vel, rng):
    n = int(0.09 * SR)
    t = _t(n)
    env = np.minimum(1, t / 0.012) * np.exp(-t / 0.03)
    return vel * _filt(_noise(n, rng), 5000, None) * env


def hat(vel, rng, open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    t = _t(n)
    env = np.exp(-t / (0.08 if open_ else 0.018))
    return vel * _filt(_noise(n, rng), 7000, None) * env


def ride(vel, rng):
    n = int(0.9 * SR)
    t = _t(n)
    metal = sum(np.sin(2 * np.pi * fr * t + rng.uniform(0, 6)) for fr in (3150, 4210, 5380, 6920)) / 4
    s = (0.6 * _filt(_noise(n, rng), 6000, None) + 0.4 * metal) * np.exp(-t / 0.35)
    s[: int(0.004 * SR)] *= 2.0
    return vel * s


def brush(vel, rng):
    """브러시 스네어 (짧은 '츠' 소리)"""
    n = int(0.18 * SR)
    t = _t(n)
    env = np.minimum(1, t / 0.01) * np.exp(-t / 0.06)
    return vel * _filt(_noise(n, rng), 1500, 7000) * env


def rim(vel, rng):
    n = int(0.06 * SR)
    t = _t(n)
    s = 0.6 * np.sin(2 * np.pi * 1750 * t) * np.exp(-t / 0.008) + 0.4 * _filt(_noise(n, rng), 1500, 4000) * np.exp(-t / 0.006)
    return vel * s


def felt(m, dur, vel, rng=np.random):
    """펠트 피아노: 해머에 천을 댄 듯 부드럽고 먹먹한 피아노"""
    s = piano(m, dur, vel, rng=rng)
    cut = min(3200, hz(m) * 5)
    b, a = butter(2, cut / (SR / 2))
    s = lfilter(b, a, s)
    # 건반 누르는 작은 소리
    n = int(0.03 * SR)
    t = _t(n)
    s[:n] += vel * 0.05 * _filt(rng.standard_normal(n), 300, 1500) * np.exp(-t / 0.008)
    return s
