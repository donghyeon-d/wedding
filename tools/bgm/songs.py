# 청첩장 BGM 곡들. 사용: python3 tools/bgm/songs.py [곡이름...]  (생략하면 전부)
# 결과: web/public/bgm/<이름>.m4a  (macOS afconvert 로 AAC 변환)
import os
import subprocess
import sys
import tempfile

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, os.path.dirname(__file__))
from synth import (SR, Song, bell, felt, brush, clap, flute, glock, hat, kick, pad, piano, pluck, rhodes,  # noqa: E402
                   rim, ride, shaker, upright, vibes, bass)

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'web', 'public', 'bgm')


# ─────────────────────────────────────────────────────────────
# 1. 써니 팝 — 라장조 112BPM, 우쿨렐레 스트럼 + 글로켄슈필 + 박수·셰이커
# ─────────────────────────────────────────────────────────────
def sunny():
    BPM = 112
    B = 60 / BPM
    BAR = 4 * B
    bars = 32
    s = Song(bars * BAR, seed=3)
    r = s.rng
    D = (38, [62, 66, 69, 74]); A = (45, [61, 64, 69, 73]); Bm = (47, [62, 66, 71, 74]); G = (43, [62, 67, 71, 74])
    prog = [D, A, Bm, G, D, A, G, A, G, A, Bm, G, G, A, D, A] * 2
    mel = {
        4: [(0, 78, .5), (.5, 81, .5), (1, 81, 1), (2, 78, .5), (2.5, 76, .5), (3, 74, 1)],
        5: [(0, 76, .5), (.5, 78, .5), (1, 76, .5), (1.5, 73, .5), (2, 69, 2)],
        6: [(0, 71, .5), (.5, 74, .5), (1, 79, 1), (2, 78, .5), (2.5, 79, .5), (3, 81, 1)],
        7: [(0, 81, 1.5), (1.5, 78, .5), (2, 76, 2)],
        8: [(0, 79, .5), (.5, 79, .5), (1, 79, .5), (1.5, 81, .5), (2, 83, 1), (3, 81, 1)],
        9: [(0, 78, .5), (.5, 76, .5), (1, 73, 1), (2, 76, 1), (3, 78, 1)],
        10: [(0, 78, .5), (.5, 81, .5), (1, 86, 1), (2, 83, .5), (2.5, 81, .5), (3, 78, 1)],
        11: [(0, 79, 1), (1, 78, .5), (1.5, 76, .5), (2, 74, 2)],
        12: [(0, 71, .5), (.5, 74, .5), (1, 79, .5), (1.5, 78, .5), (2, 79, 1), (3, 83, 1)],
        13: [(0, 81, 1), (1, 85, 1), (2, 88, 1), (3, 85, 1)],
        14: [(0, 86, 2), (2, 81, .5), (2.5, 78, .5), (3, 74, 1)],
        15: [(0, 76, 1), (1, 73, 1), (2, 69, 1), (3, 73, 1)],
    }
    strum = [(0, 'D', 1.0), (2, 'D', .8), (3, 'U', .6), (5, 'U', .6), (6, 'D', .8), (7, 'U', .65)]
    for b, (root, tones) in enumerate(prog):
        t0 = b * BAR
        for e8, d, v in strum:
            order = tones if d == 'D' else tones[::-1]
            for k, m in enumerate(order):
                tt = t0 + e8 * B / 2 + k * 0.011 + r.normal(0, 0.003)
                s.place('uke', pluck(m, B * 0.9, 0.13 * v * (1 if d == 'D' else 0.8), bright=0.55, sustain=0.993, rng=r),
                        tt, pan=-0.25 + 0.12 * k, send=0.25)
        if True:  # 베이스는 처음부터 (반복 시 갑자기 비지 않게)
            s.place('bass', bass(root, B * 0.8, 0.32), t0, send=0.05)
            s.place('bass', bass(root, B * 0.45, 0.22), t0 + 1.5 * B, send=0.05)
            s.place('bass', bass(root + 7, B * 0.8, 0.24), t0 + 2 * B, send=0.05)
            s.place('bass', bass(root + 12, B * 0.45, 0.18), t0 + 3.5 * B, send=0.05)
        for e in range(8):
            s.place('shk', shaker(0.05 if e % 2 else 0.03, r), t0 + e * B / 2 + r.normal(0, 0.004), pan=0.35, send=0.1)
        if b % 16 >= 4:
            s.place('kick', kick(0.35), t0, send=0.02)
            s.place('kick', kick(0.25), t0 + 2 * B, send=0.02)
            s.place('kick', kick(0.15), t0 + 2.5 * B, send=0.02)
            for bt in (1, 3):
                s.place('clap', clap(0.13, r), t0 + bt * B, pan=-0.1, send=0.35)
        p = b // 16
        for (bt, m, dur) in mel.get(b % 16, []):
            tt = t0 + bt * B + r.normal(0, 0.003)
            s.place('glock', glock(m, dur * B, 0.13), tt, pan=0.15, send=0.35)
            if p == 1:
                s.place('glock2', glock(m - 12, dur * B, 0.06), tt + 0.005, pan=-0.2, send=0.3)
    return s.render(reverb_secs=1.6, wet=0.22, rms_db=-19.5)


# ─────────────────────────────────────────────────────────────
# 2. 스윙 재즈 — 바장조 138BPM, 로즈 컴핑 + 워킹 베이스 + 브러시·라이드 + 비브라폰
# ─────────────────────────────────────────────────────────────
def jazz():
    BPM = 138
    B = 60 / BPM
    BAR = 4 * B
    SW = 2 / 3  # 스윙 뒷박 위치
    bars = 32
    s = Song(bars * BAR, seed=5)
    r = s.rng
    # (베이스 근음, 코드톤 반음 오프셋[3,5,7], 로즈 보이싱)
    C = {
        'Fmaj7': (41, [4, 7, 11], [57, 60, 64, 67]),
        'Dm7': (38, [3, 7, 10], [53, 57, 60, 64]),
        'Gm7': (43, [3, 7, 10], [58, 62, 65, 69]),
        'C7': (36, [4, 7, 10], [58, 62, 64, 69]),
        'Am7': (45, [3, 7, 10], [55, 60, 64, 67]),
        'D7': (38, [4, 7, 10], [54, 57, 60, 64]),
        'F7': (41, [4, 7, 10], [57, 63, 67]),
        'Bbmaj7': (46, [4, 7, 11], [57, 62, 65, 69]),
        'Eb7': (39, [4, 7, 10], [55, 61, 65, 67]),
    }
    form = [['Fmaj7'], ['Dm7'], ['Gm7'], ['C7'], ['Am7'], ['D7'], ['Gm7'], ['C7'],
            ['Fmaj7'], ['F7'], ['Bbmaj7'], ['Eb7'], ['Am7'], ['D7'], ['Gm7', 'C7'], ['Fmaj7', 'C7']] * 2
    mel = {
        0: [(0, 69, .67), (.67, 72, .33), (1, 76, 1), (2, 74, .67), (2.67, 72, 1.33)],
        1: [(0, 69, 1), (1, 65, .67), (1.67, 69, .33), (2, 72, 2)],
        2: [(0, 70, .67), (.67, 74, .33), (1, 77, 1), (2, 76, .67), (2.67, 74, 1.33)],
        3: [(0, 72, 1), (1, 70, .67), (1.67, 67, .33), (2, 64, 2)],
        4: [(0, 67, .67), (.67, 69, .33), (1, 72, 1), (2, 76, .67), (2.67, 79, 1.33)],
        5: [(0, 78, 1), (1, 76, .67), (1.67, 74, .33), (2, 72, 1), (3, 69, 1)],
        6: [(0, 70, .67), (.67, 74, .33), (1, 77, 1.67), (2.67, 76, .33), (3, 74, 1)],
        7: [(0, 72, 2), (2.67, 64, .33), (3, 67, 1)],
        8: [(0, 69, .67), (.67, 72, .33), (1, 77, 1), (2, 81, .67), (2.67, 79, 1.33)],
        9: [(0, 77, 1), (1, 75, .67), (1.67, 72, .33), (2, 69, 2)],
        10: [(0, 70, .67), (.67, 74, .33), (1, 77, .67), (1.67, 81, .33), (2, 79, 1), (3, 77, 1)],
        11: [(0, 79, 1), (1, 77, .67), (1.67, 73, .33), (2, 70, 2)],
        12: [(0, 72, .67), (.67, 76, .33), (1, 79, 1), (2, 76, .67), (2.67, 72, 1.33)],
        13: [(0, 74, .67), (.67, 78, .33), (1, 81, 1), (2, 78, 1), (3, 74, 1)],
        14: [(0, 77, .67), (.67, 74, .33), (1, 70, 1), (2, 76, .67), (2.67, 72, 1.33)],
        15: [(0, 77, 2.5), (3, 72, 1)],
    }
    comps = [[(0, .5), (1 + SW, .6)], [(1 + SW, .5), (3, .5)], [(0, .9), (2 + SW, .5)], [(SW, .4), (2, .6), (3 + SW, .3)]]

    # 워킹 베이스 음 만들기: 박마다 근음 → 코드톤 → 코드톤 → 다음 근음 반음 접근
    def fit(m):
        while m < 36:
            m += 12
        while m > 55:
            m -= 12
        return m

    beats = []  # (박 번호, 코드 이름)
    for b, chords in enumerate(form):
        per = 4 // len(chords)
        for i, c in enumerate(chords):
            for k in range(per):
                beats.append((b * 4 + i * per + k, c, k, per))
    for idx, (bn, c, k, per) in enumerate(beats):
        root, ct, _ = C[c]
        nxt_root = C[beats[(idx + 1) % len(beats)][1]][0]
        if k == 0:
            m = root
        elif k == per - 1:
            m = nxt_root + (1 if r.random() < 0.5 else -1)
        else:
            m = root + ct[(k - 1 + (bn // 4) % 2) % 3]
        tt = bn * B + r.normal(0, 0.004)
        s.place('bass', upright(fit(m), B * 0.92, 0.42, rng=r), tt, pan=-0.05, send=0.08)

    for b, chords in enumerate(form):
        t0 = b * BAR
        # 로즈 컴핑
        pat = comps[(b + (b // 8)) % len(comps)]
        for (bt, dur) in pat:
            c = chords[0] if bt < 2 or len(chords) == 1 else chords[1]
            for m in C[c][2]:
                s.place('rhodes', rhodes(m, dur * B, 0.07 * r.uniform(0.85, 1.05)), t0 + bt * B + r.normal(0, 0.005), pan=-0.3, send=0.3)
        # 라이드 + 하이햇 페달 + 브러시
        for bt, v in ((0, .9), (1, 1), (1 + SW, .6), (2, .9), (3, 1), (3 + SW, .6)):
            s.place('ride', ride(0.05 * v, r), t0 + bt * B + r.normal(0, 0.003), pan=0.35, send=0.2)
        for bt in (1, 3):
            s.place('hat', hat(0.06, r), t0 + bt * B, pan=0.25, send=0.1)
            s.place('brush', brush(0.07, r), t0 + bt * B + 0.01, pan=0.1, send=0.25)
        if b % 4 == 3:
            s.place('brush', brush(0.05, r), t0 + (2 + SW) * B, pan=0.1, send=0.25)
        # 멜로디 (비브라폰). 2코러스는 한 옥타브 위 + 아래 옥타브 피아노
        p = b // 16
        for (bt, m, dur) in mel.get(b % 16, []):
            tt = t0 + bt * B + r.normal(0, 0.004)
            if p == 0:
                s.place('vibes', vibes(m, dur * B, 0.17), tt, pan=0.2, send=0.35)
            else:
                s.place('vibes', vibes(m + 12, dur * B, 0.11), tt, pan=0.2, send=0.4)
                s.place('pno', piano(m, dur * B, 0.10, rng=r), tt + 0.004, pan=-0.1, send=0.3)
    return s.render(reverb_secs=1.8, wet=0.2, rms_db=-20)


# ─────────────────────────────────────────────────────────────
# 3. 왈츠 — 사장조 3/4 160BPM, 쿵짝짝 피아노 + 오르골 + 피치카토 + 현악 패드
# ─────────────────────────────────────────────────────────────
def waltz():
    BPM = 160
    B = 60 / BPM
    BAR = 3 * B
    G = (43, [59, 62, 67]); Cc = (48, [60, 64, 67]); D7 = (38, [60, 62, 66]); Em = (40, [59, 64, 67]); Am = (45, [60, 64, 69])
    phrase = [G, G, Cc, G, D7, D7, G, G, Em, Am, D7, G, Cc, G, D7, G]
    intro = [G, G, D7, D7]
    prog = intro + phrase * 3
    bars = len(prog)
    s = Song(bars * BAR, seed=9)
    r = s.rng
    mel = [
        [(0, 71, 2), (2, 74, 1)], [(0, 79, 2), (2, 78, 1)], [(0, 76, 1), (1, 79, 1), (2, 76, 1)], [(0, 74, 3)],
        [(0, 72, 2), (2, 74, 1)], [(0, 78, 2), (2, 76, 1)], [(0, 74, 1), (1, 71, 1), (2, 67, 1)], [(0, 71, 3)],
        [(0, 71, 2), (2, 76, 1)], [(0, 81, 2), (2, 79, 1)], [(0, 78, 1), (1, 74, 1), (2, 78, 1)], [(0, 79, 2), (2, 74, 1)],
        [(0, 76, 1), (1, 79, 1), (2, 84, 1)], [(0, 83, 2), (2, 79, 1)], [(0, 81, 1), (1, 78, 1), (2, 74, 1)], [(0, 79, 3)],
    ]
    for b, (root, tones) in enumerate(prog):
        t0 = b * BAR
        # 쿵(베이스) 짝 짝(화음)
        s.place('pno', piano(root, B * 0.9, 0.26, rng=r), t0 + r.normal(0, 0.003), pan=-0.1, send=0.25)
        s.place('pno', piano(root + 12, B * 0.9, 0.10, rng=r), t0 + 0.004, pan=-0.1, send=0.25)
        for bt in (1, 2):
            for m in tones:
                s.place('pno', piano(m, B * 0.45, 0.075 * (1 if bt == 1 else 0.85), rng=r), t0 + bt * B + r.normal(0, 0.004), pan=0.05, send=0.25)
        pidx = (b - 4) // 16 if b >= 4 else -1
        if pidx >= 1:  # 피치카토 짝짝
            for bt in (1, 2):
                s.place('pizz', pluck(tones[-1] + 12, B * 0.3, 0.05, bright=0.4, sustain=0.98, rng=r), t0 + bt * B + 0.01, pan=0.45, send=0.4)
        if pidx == 2:  # 마지막 패스는 현악 패드
            for m in tones:
                s.place('pad', pad(m + 12, BAR, 0.022, rng=r, attack=0.5, rel=0.8), t0, pan=r.uniform(-0.4, 0.4), send=0.6)
        if pidx >= 0:
            for (bt, m, dur) in mel[(b - 4) % 16]:
                tt = t0 + bt * B + r.normal(0, 0.003)
                if pidx == 1:
                    s.place('mel', piano(m, dur * B, 0.17, rng=r), tt, pan=0.15, send=0.3)
                    s.place('mel2', bell(m + 12, dur * B, 0.05), tt + 0.006, pan=-0.2, send=0.4)
                else:
                    s.place('mel', bell(m, dur * B, 0.17), tt, pan=0.15, send=0.4)
                    if pidx == 2:
                        s.place('mel2', bell(m + 12, dur * B, 0.05), tt + 0.006, pan=-0.2, send=0.4)
    return s.render(reverb_secs=2.2, wet=0.28, rms_db=-20.5)


# ─────────────────────────────────────────────────────────────
# 4. 보사노바 — 다장조 140BPM, 나일론 기타 + 림·셰이커 + 플루트
# ─────────────────────────────────────────────────────────────
def bossa():
    BPM = 140
    B = 60 / BPM
    BAR = 4 * B
    bars = 32
    s = Song(bars * BAR, seed=13)
    r = s.rng
    Ch = {
        'Cmaj7': (48, [52, 55, 59, 62]), 'Dm7': (50, [53, 57, 60, 64]), 'G7': (43, [53, 59, 62, 65]),
        'Em7': (40, [55, 59, 62, 64]), 'A7': (45, [55, 61, 64, 67]), 'Fmaj7': (41, [53, 57, 60, 64]), 'Fm6': (41, [53, 56, 60, 62]),
    }
    form = ['Cmaj7', 'Cmaj7', 'Dm7', 'G7', 'Em7', 'A7', 'Dm7', 'G7', 'Fmaj7', 'Fm6', 'Em7', 'A7', 'Dm7', 'G7', 'Cmaj7', 'G7'] * 2
    mel = {
        0: [(0, 76, 1.5), (1.5, 74, .5), (2, 76, 1), (3, 79, 1)], 1: [(0, 76, 3)],
        2: [(0, 77, 1.5), (1.5, 76, .5), (2, 74, 1), (3, 72, 1)], 3: [(0, 71, 2), (2, 74, 1), (3, 77, 1)],
        4: [(0, 79, 1.5), (1.5, 77, .5), (2, 76, 1), (3, 74, 1)], 5: [(0, 73, 2), (2, 76, 1), (3, 79, 1)],
        6: [(0, 77, 1.5), (1.5, 76, .5), (2, 74, 1), (3, 72, 1)], 7: [(0, 74, 3)],
        8: [(0, 72, 1.5), (1.5, 74, .5), (2, 76, 1), (3, 77, 1)], 9: [(0, 80, 2), (2, 77, 1), (3, 74, 1)],
        10: [(0, 76, 1.5), (1.5, 74, .5), (2, 71, 1), (3, 67, 1)], 11: [(0, 69, 2), (2, 73, 1), (3, 76, 1)],
        12: [(0, 77, 1.5), (1.5, 76, .5), (2, 74, 1), (3, 77, 1)], 13: [(0, 79, 1), (1, 77, 1), (2, 74, 1), (3, 71, 1)],
        14: [(0, 72, 3)], 15: [(2, 71, 1), (3, 74, 1)],
    }
    guitar_pat = [[1, 3, 4, 6], [1, 3, 5, 6]]
    clave = [0, 3, 6, 10, 13]  # 2마디(16개 8분음) 기준
    for b, c in enumerate(form):
        t0 = b * BAR
        root, tones = Ch[c]
        # 엄지 베이스: 근음(1박) · 5도(3박)
        s.place('gbass', pluck(root, B * 1.6, 0.22, bright=0.25, sustain=0.995, rng=r), t0, pan=-0.15, send=0.15)
        s.place('gbass', pluck(root + 7 if root + 7 <= 55 else root - 5, B * 1.6, 0.18, bright=0.25, sustain=0.995, rng=r), t0 + 2 * B, pan=-0.15, send=0.15)
        for e8 in guitar_pat[b % 2]:
            for k, m in enumerate(tones):
                s.place('gtr', pluck(m, B * 0.8, 0.085, bright=0.35, sustain=0.994, rng=r), t0 + e8 * B / 2 + k * 0.006 + r.normal(0, 0.003), pan=-0.2 + 0.05 * k, send=0.25)
        # 림 클라베 + 셰이커 + 킥
        for e in clave:
            if e // 8 == b % 2:
                s.place('rim', rim(0.10, r), t0 + (e % 8) * B / 2, pan=0.3, send=0.2)
        for e in range(8):
            s.place('shk', shaker(0.045 if e % 2 else 0.025, r), t0 + e * B / 2 + r.normal(0, 0.004), pan=0.4, send=0.1)
        for bt, v in ((0, .28), (1.5, .14), (2, .24), (3.5, .14)):
            s.place('kick', kick(v), t0 + bt * B, send=0.02)
        p = b // 16
        for (bt, m, dur) in mel.get(b % 16, []):
            tt = t0 + bt * B + r.normal(0, 0.004)
            s.place('flute', flute(m, dur * B, 0.10, rng=r), tt, pan=0.15, send=0.4)
            if p == 1:
                s.place('vib', vibes(m - 12, dur * B, 0.06), tt + 0.004, pan=-0.25, send=0.35)
    return s.render(reverb_secs=1.8, wet=0.22, rms_db=-20.5)


# ─────────────────────────────────────────────────────────────
# 5. 웜 어쿠스틱 — 마장조 92BPM, 펠트 피아노 멜로디 + 핑거피킹 기타 + 현악 패드 + 후반 가벼운 드럼
#    (모바일 청첩장용 '감성' BGM 스타일)
# ─────────────────────────────────────────────────────────────
def warm():
    BPM = 92
    B = 60 / BPM
    BAR = 4 * B
    Ch = {
        'E': (40, [59, 64, 68, 71]), 'B/D#': (39, [59, 63, 66, 71]), 'C#m7': (37, [59, 64, 68, 73]),
        'A': (45, [61, 64, 69, 71]), 'E/G#': (44, [59, 64, 68, 71]), 'F#m7': (42, [57, 61, 64, 69]),
        'Bsus4': (47, [59, 64, 66, 71]), 'B': (47, [59, 63, 66, 71]),
    }
    phrase = [['E'], ['B/D#'], ['C#m7'], ['A'], ['E/G#'], ['A'], ['F#m7'], ['Bsus4', 'B'],
              ['C#m7'], ['B'], ['A'], ['E/G#'], ['F#m7'], ['A'], ['Bsus4'], ['B']]
    intro = [['E'], ['B/D#'], ['C#m7'], ['A']]
    prog = intro + phrase * 2
    bars = len(prog)
    s = Song(bars * BAR, seed=21)
    r = s.rng
    mel = [
        [(0, 68, 1), (1, 71, 1), (2, 76, 1.5), (3.5, 75, .5)], [(0, 75, 1.5), (1.5, 73, .5), (2, 71, 2)],
        [(0, 68, 1), (1, 71, 1), (2, 73, 1), (3, 76, 1)], [(0, 76, 1.5), (1.5, 75, .5), (2, 73, 1), (3, 71, 1)],
        [(0, 71, 1.5), (1.5, 68, .5), (2, 71, 1), (3, 73, 1)], [(0, 76, 2), (2, 78, 1), (3, 76, 1)],
        [(0, 73, 1.5), (1.5, 71, .5), (2, 69, 1), (3, 68, 1)], [(0, 66, 3), (3, 71, 1)],
        [(0, 76, 1), (1, 80, 1), (2, 78, 1), (3, 76, 1)], [(0, 75, 1.5), (1.5, 73, .5), (2, 71, 2)],
        [(0, 73, 1), (1, 76, 1), (2, 81, 1.5), (3.5, 80, .5)], [(0, 80, 1.5), (1.5, 78, .5), (2, 76, 2)],
        [(0, 78, 1), (1, 76, 1), (2, 73, 1), (3, 69, 1)], [(0, 73, 1), (1, 76, 1), (2, 78, 1), (3, 80, 1)],
        [(0, 78, 2), (2, 76, 1), (3, 75, 1)], [(0, 75, 3.5)],
    ]
    pick = [0, 2, 1, 3, 2, 1, 3, 2]  # 핑거피킹 순서 (코드톤 인덱스)
    for b, chords in enumerate(prog):
        t0 = b * BAR
        sec = -1 if b < 4 else (b - 4) // 16  # -1 인트로, 0 첫 패스, 1 두 번째 패스
        for i, p in enumerate(pick):
            c = chords[0] if i < 4 or len(chords) == 1 else chords[1]
            root, tones = Ch[c]
            m = root + 12 if i == 0 else tones[p]
            v = (0.12 if i == 0 else 0.085) * r.uniform(0.9, 1.05)
            s.place('gtr', pluck(m, B * 0.9, v, bright=0.32, sustain=0.995, rng=r), t0 + i * B / 2 + r.normal(0, 0.004),
                    pan=-0.3, send=0.25)
        root, tones = Ch[chords[0]]
        # 피아노 화음 (마디 첫 박, 부드럽게)
        for k, m in enumerate(tones):
            s.place('pchord', felt(m - 12 if k == 0 else m, BAR * 0.95, 0.05, rng=r), t0 + k * 0.012, pan=0.1, send=0.35)
        s.place('bass', bass(root, BAR * 0.6, 0.26), t0, send=0.05)
        s.place('bass', bass(root, B * 0.9, 0.16), t0 + 2.5 * B, send=0.05)
        if sec >= 0 and (b - 4) % 16 >= 8 or sec == 1:
            for m in tones[1:]:
                s.place('str', pad(m + 12, BAR, 0.018, rng=r, attack=1.0, rel=1.2), t0, pan=r.uniform(-0.5, 0.5), send=0.6)
        if sec == 1:
            for bt, v in ((0, .30), (2, .24), (2.5, .12)):
                s.place('kick', kick(v), t0 + bt * B, send=0.02)
            for bt in (1, 3):
                s.place('brush', brush(0.09, r), t0 + bt * B, pan=0.1, send=0.3)
            for e in range(8):
                s.place('shk', shaker(0.035 if e % 2 else 0.02, r), t0 + e * B / 2 + r.normal(0, 0.004), pan=0.4, send=0.1)
        if sec >= 0:
            for (bt, m, dur) in mel[(b - 4) % 16]:
                tt = t0 + bt * B + r.normal(0, 0.004)
                s.place('lead', felt(m, dur * B, 0.20, rng=r), tt, pan=0.12, send=0.4)
                if sec == 1:
                    s.place('lead2', bell(m + 12, dur * B, 0.035), tt + 0.008, pan=-0.2, send=0.45)
    return s.render(reverb_secs=2.4, wet=0.3, rms_db=-20.5)


SONGS = {'warm': warm, 'sunny': sunny, 'jazz': jazz, 'waltz': waltz, 'bossa': bossa}


def main():
    names = sys.argv[1:] or list(SONGS)
    os.makedirs(OUT, exist_ok=True)
    for name in names:
        out = SONGS[name]()
        print(f'{name}: {out.shape[1] / SR:.1f}s  rms {20 * np.log10(np.sqrt(np.mean(out ** 2))):.1f} dBFS  peak {20 * np.log10(np.max(np.abs(out))):.1f} dBFS')
        with tempfile.TemporaryDirectory() as d:
            wav = os.path.join(d, f'{name}.wav')
            wavfile.write(wav, SR, (out.T * 32767).astype(np.int16))
            subprocess.run(['afconvert', '-f', 'm4af', '-d', 'aac', '-b', '128000', '-q', '127', wav,
                            os.path.join(OUT, f'{name}.m4a')], check=True)


if __name__ == '__main__':
    main()
