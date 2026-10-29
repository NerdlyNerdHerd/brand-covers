"""Sector covers for Nerdly OS pages (1500x600, text-free).

Same family as team/generate.py: navy field, plum glow, starfield, neon heartbeat
stem with feather marks, Celtic motif on the right. The left-centre badge holds a
line-art glyph for the sector instead of an Ogham name. Symbols stay inside the
middle band (y 170-430) so Notion's cover crop keeps them.

Run:  python3 sectors/generate.py   ->  covers/sector-<key>.png
"""
import math, random, os
from playwright.sync_api import sync_playwright

NAVY = '#100C33'; PLUM = '#6B2FA0'; PINK = '#E91C8C'; CORAL = '#EF4E4E'
GOLD = '#F0B429'; TEAL = '#1AC3B8'; IVORY = '#F7F3F0'
BLUE = '#5AA9FF'; VIOLET = '#A66BFF'

W, H = 1500, 600
CX, CY = 540, 300          # badge centre
R = 128                    # badge ring radius


def stars(n, seed):
    rnd = random.Random(seed); s = []
    for _ in range(n):
        x = rnd.uniform(0, W); y = rnd.uniform(0, H)
        r = rnd.choice([0.6, 0.8, 1, 1.2, 1.6]); o = rnd.uniform(0.15, 0.7)
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{IVORY}" opacity="{o:.2f}"/>')
    return ''.join(s)


def triquetra_path(cx, cy, Rr):
    d = Rr / math.sqrt(3)
    C = [(cx + d * math.cos(math.radians(-90 + 120 * k)), cy + d * math.sin(math.radians(-90 + 120 * k))) for k in range(3)]
    out = []
    for i in range(3):
        A = C[i]; B = C[(i + 1) % 3]; Cc = C[(i + 2) % 3]
        mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
        X = (2 * mx - Cc[0], 2 * my - Cc[1])
        out.append(f"M{Cc[0]:.1f},{Cc[1]:.1f} A{Rr:.1f},{Rr:.1f} 0 0 1 {X[0]:.1f},{X[1]:.1f} A{Rr:.1f},{Rr:.1f} 0 0 1 {Cc[0]:.1f},{Cc[1]:.1f} Z")
    return out


def triskele_path(cx, cy, Rr):
    out = []
    for k in range(3):
        rot = math.radians(120 * k); pts = []
        for t in range(121):
            th = t / 120 * 2.6 * math.pi; r = Rr * (0.08 + 0.92 * t / 120); a = th + rot
            pts.append((cx + r * math.cos(a) * 0.55, cy + r * math.sin(a) * 0.55))
        out.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts))
    return out


def motif(kind):
    mx, my = 1235, 300
    if kind == 'triquetra':
        m = ''.join(f'<path d="{p}" fill="none" stroke="url(#g2)" stroke-width="7" opacity="0.5"/>' for p in triquetra_path(mx, my, 128))
        m += f'<circle cx="{mx}" cy="{my}" r="80" fill="none" stroke="url(#g2)" stroke-width="5" opacity="0.4"/>'
    elif kind == 'triskele':
        m = ''.join(f'<path d="{p}" fill="none" stroke="url(#g2)" stroke-width="9" stroke-linecap="round" opacity="0.5"/>' for p in triskele_path(mx, my, 250))
        m += f'<circle cx="{mx}" cy="{my}" r="190" fill="none" stroke="url(#g2)" stroke-width="3" opacity="0.28"/>'
    else:  # rings
        m = ''.join(f'<circle cx="{mx}" cy="{my}" r="{r}" fill="none" stroke="url(#g2)" stroke-width="{w}" opacity="{o}"/>'
                    for r, w, o in [(70, 6, 0.45), (130, 4, 0.32), (195, 3, 0.2), (260, 2, 0.12)])
        m += ''.join(f'<path d="{p}" fill="none" stroke="url(#g2)" stroke-width="5" opacity="0.55"/>' for p in triquetra_path(mx, my, 80))
    return m


# ---------- glyphs: drawn in a 200x200 box centred on (CX, CY); stroke = url(#g1) ----------
def G(d):
    return f'<path d="{d}"/>'


def at(x, y):
    return CX + x, CY + y


def glyph(key):
    x0, y0 = CX, CY
    if key == 'ops':  # gear with compass needle
        teeth = []
        for i in range(10):
            a = math.radians(i * 36)
            p1 = (x0 + 70 * math.cos(a - 0.16), y0 + 70 * math.sin(a - 0.16)); p2 = (x0 + 92 * math.cos(a - 0.11), y0 + 92 * math.sin(a - 0.11))
            p3 = (x0 + 92 * math.cos(a + 0.11), y0 + 92 * math.sin(a + 0.11)); p4 = (x0 + 70 * math.cos(a + 0.16), y0 + 70 * math.sin(a + 0.16))
            teeth.append(f'M{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} L{p3[0]:.1f},{p3[1]:.1f} L{p4[0]:.1f},{p4[1]:.1f}')
        s = G(' '.join(teeth)) + f'<circle cx="{x0}" cy="{y0}" r="70"/><circle cx="{x0}" cy="{y0}" r="40"/>'
        s += G(f'M{x0},{y0-30} L{x0+10},{y0} L{x0},{y0+30} L{x0-10},{y0} Z')
        return s
    if key == 'systems':  # hexagon with node network
        hexp = ' '.join(f'{x0+88*math.cos(math.radians(60*i-90)):.1f},{y0+88*math.sin(math.radians(60*i-90)):.1f}' for i in range(6))
        nodes = [(0, -42), (-38, 22), (38, 22), (0, 0)]
        s = f'<polygon points="{hexp}"/>'
        s += G(f'M{x0},{y0-42} L{x0},{y0} M{x0-38},{y0+22} L{x0},{y0} L{x0+38},{y0+22} M{x0-38},{y0+22} L{x0+38},{y0+22}')
        s += ''.join(f'<circle cx="{x0+a}" cy="{y0+b}" r="11" fill="{NAVY}"/>' for a, b in nodes)
        return s
    if key == 'bots':  # friendly robot with nerd glasses
        s = f'<rect x="{x0-78}" y="{y0-52}" width="156" height="118" rx="34"/>'
        s += G(f'M{x0},{y0-52} L{x0},{y0-82}') + f'<circle cx="{x0}" cy="{y0-92}" r="10"/>'
        s += f'<rect x="{x0-58}" y="{y0-22}" width="46" height="38" rx="10"/><rect x="{x0+12}" y="{y0-22}" width="46" height="38" rx="10"/>'
        s += G(f'M{x0-12},{y0-6} L{x0+12},{y0-6} M{x0-30},{y0+40} Q{x0},{y0+56} {x0+30},{y0+40}')
        s += G(f'M{x0-78},{y0} L{x0-96},{y0} M{x0+78},{y0} L{x0+96},{y0}')
        return s
    if key == 'email':  # envelope with check
        s = f'<rect x="{x0-90}" y="{y0-60}" width="180" height="120" rx="14"/>'
        s += G(f'M{x0-86},{y0-54} L{x0},{y0+8} L{x0+86},{y0-54}')
        s += f'<circle cx="{x0+78}" cy="{y0+52}" r="30" fill="{NAVY}"/>' + G(f'M{x0+64},{y0+52} L{x0+75},{y0+63} L{x0+93},{y0+41}')
        return s
    if key == 'onboarding':  # arched doorway, path and star
        s = G(f'M{x0-62},{y0+82} L{x0-62},{y0-18} A62,62 0 0 1 {x0+62},{y0-18} L{x0+62},{y0+82}')
        s += G(f'M{x0-92},{y0+82} L{x0+92},{y0+82}')
        s += G(f'M{x0-16},{y0+82} L{x0-6},{y0+20} M{x0+16},{y0+82} L{x0+6},{y0+20}')
        sx, sy = x0, y0 - 20
        star = ' '.join(f'{sx+(20 if i%2==0 else 8)*math.cos(math.radians(90*i/2-90)):.1f},{sy+(20 if i%2==0 else 8)*math.sin(math.radians(90*i/2-90)):.1f}' for i in range(8))
        return s + f'<polygon points="{star}"/>'
    if key == 'success':  # heart with pulse
        s = G(f'M{x0},{y0+78} C{x0-40},{y0+44} {x0-96},{y0+8} {x0-96},{y0-30} C{x0-96},{y0-70} {x0-46},{y0-86} {x0},{y0-40} '
              f'C{x0+46},{y0-86} {x0+96},{y0-70} {x0+96},{y0-30} C{x0+96},{y0+8} {x0+40},{y0+44} {x0},{y0+78} Z')
        s += G(f'M{x0-62},{y0-6} L{x0-28},{y0-6} L{x0-14},{y0-34} L{x0+4},{y0+24} L{x0+20},{y0-6} L{x0+62},{y0-6}')
        return s
    if key == 'support':  # lifebuoy
        s = f'<circle cx="{x0}" cy="{y0}" r="88"/><circle cx="{x0}" cy="{y0}" r="40"/>'
        for a in (45, 135, 225, 315):
            r1, r2 = 40, 88; t = math.radians(a)
            for off in (-0.28, 0.28):
                s += G(f'M{x0+r1*math.cos(t+off*1.6):.1f},{y0+r1*math.sin(t+off*1.6):.1f} L{x0+r2*math.cos(t+off*0.7):.1f},{y0+r2*math.sin(t+off*0.7):.1f}')
        return s
    if key == 'training':  # open book with spark
        s = G(f'M{x0},{y0-30} C{x0-30},{y0-52} {x0-70},{y0-52} {x0-96},{y0-40} L{x0-96},{y0+66} C{x0-70},{y0+54} {x0-30},{y0+54} {x0},{y0+76} '
              f'C{x0+30},{y0+54} {x0+70},{y0+54} {x0+96},{y0+66} L{x0+96},{y0-40} C{x0+70},{y0-52} {x0+30},{y0-52} {x0},{y0-30} Z')
        s += G(f'M{x0},{y0-30} L{x0},{y0+76}')
        s += G(f'M{x0},{y0-96} L{x0},{y0-66} M{x0-15},{y0-81} L{x0+15},{y0-81} M{x0-30},{y0-60} L{x0-40},{y0-70} M{x0+30},{y0-60} L{x0+40},{y0-70}')
        return s
    if key == 'client-kits':  # toolkit case with star badge
        s = f'<rect x="{x0-92}" y="{y0-34}" width="184" height="112" rx="16"/>'
        s += G(f'M{x0-34},{y0-34} L{x0-34},{y0-62} Q{x0-34},{y0-72} {x0-24},{y0-72} L{x0+24},{y0-72} Q{x0+34},{y0-72} {x0+34},{y0-62} L{x0+34},{y0-34}')
        s += G(f'M{x0-92},{y0+6} L{x0+92},{y0+6}')
        sx, sy = x0, y0 + 34
        star = ' '.join(f'{sx+(22 if i%2==0 else 9)*math.cos(math.radians(36*i-90)):.1f},{sy+(22 if i%2==0 else 9)*math.sin(math.radians(36*i-90)):.1f}' for i in range(10))
        return s + f'<polygon points="{star}"/>'
    if key == 'marketing':  # megaphone with waves
        s = G(f'M{x0-80},{y0-24} L{x0-40},{y0-24} L{x0+40},{y0-70} L{x0+40},{y0+70} L{x0-40},{y0+24} L{x0-80},{y0+24} Z')
        s += G(f'M{x0-58},{y0+24} L{x0-46},{y0+76} L{x0-24},{y0+76} L{x0-30},{y0+28}')
        s += G(f'M{x0+66},{y0-30} Q{x0+84},{y0} {x0+66},{y0+30} M{x0+86},{y0-54} Q{x0+118},{y0} {x0+86},{y0+54}')
        return s
    if key == 'affiliates':  # three interlocking rings
        return ''.join(f'<circle cx="{x0+40*math.cos(math.radians(120*i-90)):.1f}" cy="{y0+8+40*math.sin(math.radians(120*i-90)):.1f}" r="54"/>' for i in range(3))
    if key == 'finance':  # balance scale
        s = G(f'M{x0},{y0-80} L{x0},{y0+70} M{x0-46},{y0+80} L{x0+46},{y0+80} M{x0-82},{y0-52} L{x0+82},{y0-52}')
        s += f'<circle cx="{x0}" cy="{y0-82}" r="9"/>'
        for sx in (-1, 1):
            bx = x0 + 82 * sx
            s += G(f'M{bx},{y0-52} L{bx-30},{y0+16} M{bx},{y0-52} L{bx+30},{y0+16} M{bx-36},{y0+16} Q{bx},{y0+46} {bx+36},{y0+16} Z')
        return s
    if key == 'security':  # shield with keyhole
        s = G(f'M{x0},{y0-92} L{x0+78},{y0-62} L{x0+78},{y0} C{x0+78},{y0+48} {x0+40},{y0+78} {x0},{y0+94} C{x0-40},{y0+78} {x0-78},{y0+48} {x0-78},{y0} L{x0-78},{y0-62} Z')
        s += f'<circle cx="{x0}" cy="{y0-12}" r="18"/>' + G(f'M{x0-8},{y0+4} L{x0-14},{y0+40} L{x0+14},{y0+40} L{x0+8},{y0+4}')
        return s
    if key == 'meetings':  # microphone with waveform
        s = f'<rect x="{x0-30}" y="{y0-88}" width="60" height="110" rx="30"/>'
        s += G(f'M{x0-56},{y0-10} Q{x0-56},{y0+52} {x0},{y0+52} Q{x0+56},{y0+52} {x0+56},{y0-10} M{x0},{y0+52} L{x0},{y0+86} M{x0-34},{y0+86} L{x0+34},{y0+86}')
        for sx in (-1, 1):
            s += G(' '.join(f'M{x0+sx*(78+i*14)},{y0-30+abs(i-1)*0} L{x0+sx*(78+i*14)},{y0-30-(18,32,18)[i]} ' for i in range(3)).replace('  ', ' '))
        return s
    if key == 'partner-kb':  # lighthouse with beams
        s = G(f'M{x0-30},{y0+84} L{x0-20},{y0-34} L{x0+20},{y0-34} L{x0+30},{y0+84} Z')
        s += f'<rect x="{x0-26}" y="{y0-66}" width="52" height="32" rx="6"/>' + G(f'M{x0-30},{y0-66} L{x0},{y0-90} L{x0+30},{y0-66}')
        s += G(f'M{x0-25},{y0+10} L{x0+25},{y0+10} M{x0-28},{y0+48} L{x0+28},{y0+48} M{x0-70},{y0+84} L{x0+70},{y0+84}')
        s += G(f'M{x0-36},{y0-56} L{x0-104},{y0-82} M{x0-36},{y0-44} L{x0-104},{y0-24} M{x0+36},{y0-56} L{x0+104},{y0-82} M{x0+36},{y0-44} L{x0+104},{y0-24}')
        return s
    if key == 'offers':  # gift-wrapped package with bow
        s = f'<rect x="{x0-84}" y="{y0-30}" width="168" height="110" rx="12"/>'
        s += f'<rect x="{x0-96}" y="{y0-62}" width="192" height="32" rx="10"/>'
        s += G(f'M{x0},{y0-62} L{x0},{y0+80}')
        s += G(f'M{x0},{y0-62} C{x0-20},{y0-98} {x0-64},{y0-96} {x0-52},{y0-74} C{x0-44},{y0-62} {x0-18},{y0-62} {x0},{y0-62} '
               f'C{x0+18},{y0-62} {x0+44},{y0-62} {x0+52},{y0-74} C{x0+64},{y0-96} {x0+20},{y0-98} {x0},{y0-62}')
        return s
    raise KeyError(key)


SECTORS = [
    # key, accent1, accent2, celtic motif, spike x
    ('ops', GOLD, TEAL, 'rings', 900),
    ('systems', TEAL, BLUE, 'triquetra', 930),
    ('bots', PINK, TEAL, 'triskele', 900),
    ('email', CORAL, GOLD, 'rings', 920),
    ('onboarding', GOLD, PINK, 'triskele', 900),
    ('success', PINK, CORAL, 'triquetra', 910),
    ('support', TEAL, GOLD, 'rings', 900),
    ('training', BLUE, GOLD, 'triskele', 930),
    ('client-kits', CORAL, TEAL, 'triquetra', 900),
    ('marketing', PINK, GOLD, 'triskele', 920),
    ('affiliates', TEAL, PINK, 'rings', 900),
    ('finance', GOLD, BLUE, 'triquetra', 910),
    ('security', VIOLET, CORAL, 'rings', 900),
    ('meetings', VIOLET, TEAL, 'triskele', 930),
    ('partner-kb', BLUE, PINK, 'triquetra', 900),
    ('offers', GOLD, PINK, 'rings', 920),
]


def cover(key, a1, a2, mot, hb, seed):
    left = CX - R - 18; right = CX + R + 18
    stem = (f'M60,{CY} L{left},{CY} M{right},{CY} L{hb},{CY} L{hb+22},{CY-46} L{hb+44},{CY+58} '
            f'L{hb+70},{CY-96} L{hb+96},{CY+30} L{hb+116},{CY} L1440,{CY}')
    feathers = (f'M{left-26},{CY-26} L{left},{CY} L{left-26},{CY+26} '
                f'M{right+26},{CY-26} L{right},{CY} L{right+26},{CY+26}')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
 <radialGradient id="bg1" cx="24%" cy="55%" r="70%"><stop offset="0" stop-color="{PLUM}" stop-opacity="0.85"/><stop offset="1" stop-color="{NAVY}" stop-opacity="0"/></radialGradient>
 <radialGradient id="bg2" cx="85%" cy="40%" r="55%"><stop offset="0" stop-color="{a2}" stop-opacity="0.34"/><stop offset="1" stop-color="{NAVY}" stop-opacity="0"/></radialGradient>
 <radialGradient id="bg3" cx="50%" cy="110%" r="60%"><stop offset="0" stop-color="{a1}" stop-opacity="0.2"/><stop offset="1" stop-color="{NAVY}" stop-opacity="0"/></radialGradient>
 <linearGradient id="g1" gradientUnits="userSpaceOnUse" x1="{CX-110}" y1="{CY-110}" x2="{CX+110}" y2="{CY+110}"><stop offset="0" stop-color="{a1}"/><stop offset="1" stop-color="{a2}"/></linearGradient>
 <linearGradient id="g2" gradientUnits="userSpaceOnUse" x1="1060" y1="140" x2="1420" y2="460"><stop offset="0" stop-color="{a2}"/><stop offset="1" stop-color="{a1}"/></linearGradient>
 <linearGradient id="stemg" gradientUnits="userSpaceOnUse" x1="40" y1="0" x2="1460" y2="0"><stop offset="0" stop-color="{a1}" stop-opacity="0"/><stop offset="0.15" stop-color="{a1}"/><stop offset="0.85" stop-color="{a2}"/><stop offset="1" stop-color="{a2}" stop-opacity="0"/></linearGradient>
 <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" fill="{NAVY}"/>
<rect width="{W}" height="{H}" fill="url(#bg1)"/><rect width="{W}" height="{H}" fill="url(#bg2)"/><rect width="{W}" height="{H}" fill="url(#bg3)"/>
{stars(170, seed)}
<g filter="url(#glow)">{motif(mot)}</g>
<g filter="url(#glow)" fill="none" stroke-linecap="round" stroke-linejoin="round">
 <path d="{stem}" stroke="url(#stemg)" stroke-width="5"/>
 <path d="{feathers}" stroke="{a1}" stroke-width="5" opacity="0.9"/>
 <circle cx="{CX}" cy="{CY}" r="{R}" stroke="url(#g1)" stroke-width="5" opacity="0.75"/>
 <circle cx="{CX}" cy="{CY}" r="{R+14}" stroke="url(#g1)" stroke-width="2" opacity="0.35"/>
 <g stroke="url(#g1)" stroke-width="11">{glyph(key)}</g>
</g>
</svg>'''


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, '..', 'covers')
    only = os.environ.get('ONLY')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(device_scale_factor=1)
        pg.set_viewport_size({'width': W, 'height': H})
        for i, (k, a1, a2, mot, hb) in enumerate(SECTORS):
            if only and k not in only.split(','):
                continue
            pg.set_content(f'<html><body style="margin:0">{cover(k, a1, a2, mot, hb, seed=101 + i)}</body></html>')
            pg.screenshot(path=os.path.join(out, f'sector-{k}.png'), clip={'x': 0, 'y': 0, 'width': W, 'height': H})
        b.close()
    print('done')
