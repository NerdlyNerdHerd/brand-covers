import math, random, json
from playwright.sync_api import sync_playwright
NAVY='#100C33'; PLUM='#6B2FA0'; PINK='#E91C8C'; CORAL='#EF4E4E'; GOLD='#F0B429'; TEAL='#1AC3B8'; IVORY='#F7F3F0'
# Ogham: letter -> (group, count)
OG={'B':('b',1),'L':('b',2),'F':('b',3),'S':('b',4),'N':('b',5),
    'H':('h',1),'D':('h',2),'T':('h',3),'C':('h',4),'Q':('h',5),
    'M':('m',1),'G':('m',2),'NG':('m',3),'Z':('m',4),'R':('m',5),
    'A':('v',1),'O':('v',2),'U':('v',3),'E':('v',4),'I':('v',5)}
def ogham_strokes(letters, cx, cy, L=110, sp=30, gap=62, sw=14):
    """Return list of line segments (x1,y1,x2,y2) and stem extent for horizontal Ogham centered at cx."""
    widths=[(OG[l][1]-1)*sp for l in letters]
    total=sum(widths)+gap*(len(letters)-1)
    x=cx-total/2; segs=[]
    for l,w in zip(letters,widths):
        g,n=OG[l]
        for i in range(n):
            xi=x+i*sp
            if g=='b': segs.append((xi,cy,xi,cy+L))
            elif g=='h': segs.append((xi,cy-L,xi,cy))
            elif g=='v': segs.append((xi,cy-L*0.42,xi,cy+L*0.42))
            elif g=='m': segs.append((xi-L*0.38,cy+L*0.62,xi+L*0.38,cy-L*0.62))
        x+=w+gap
    return segs, cx-total/2, cx+total/2
def arcpts(cx,cy,r,a0,a1,n=40):
    return [(cx+r*math.cos(a0+(a1-a0)*t/n), cy+r*math.sin(a0+(a1-a0)*t/n)) for t in range(n+1)]
def triquetra_path(cx,cy,R):
    d=R/math.sqrt(3)
    C=[(cx+d*math.cos(math.radians(-90+120*k)), cy+d*math.sin(math.radians(-90+120*k))) for k in range(3)]
    paths=[]
    for i in range(3):
        A=C[i]; B=C[(i+1)%3]; Cc=C[(i+2)%3]
        mx,my=(A[0]+B[0])/2,(A[1]+B[1])/2
        X=(2*mx-Cc[0],2*my-Cc[1])
        paths.append(f"M{Cc[0]:.1f},{Cc[1]:.1f} A{R:.1f},{R:.1f} 0 0 1 {X[0]:.1f},{X[1]:.1f} A{R:.1f},{R:.1f} 0 0 1 {Cc[0]:.1f},{Cc[1]:.1f} Z")
    return paths
def triskele_path(cx,cy,R):
    out=[]
    for k in range(3):
        rot=math.radians(120*k)
        pts=[]
        for t in range(0,121):
            th=t/120*2.6*math.pi
            r=R*(0.08+0.92*t/120)
            a=th+rot
            pts.append((cx+r*math.cos(a)*0.55, cy+r*math.sin(a)*0.55))
        out.append('M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts))
    return out
def stars(w,h,n,seed):
    rnd=random.Random(seed); s=[]
    for _ in range(n):
        x=rnd.uniform(0,w); y=rnd.uniform(0,h); r=rnd.choice([0.6,0.8,1,1.2,1.6]); o=rnd.uniform(0.15,0.7)
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{IVORY}" opacity="{o:.2f}"/>')
    return ''.join(s)
def cover(name, letters, a1, a2, motif, seed, glyph_cx=560):
    W,H=1500,600; cy=300
    segs,x0,x1=ogham_strokes(letters, glyph_cx, cy, L=118 if len(letters)<=2 else 92, sp=30 if len(letters)<=2 else 22, gap=64 if len(letters)<=2 else 40, sw=14)
    sw=16 if len(letters)<=2 else 11
    # stem with heartbeat
    hb_x=max(x1+120, 980)
    stem=f'M60,{cy} L{x0-70:.0f},{cy} M{x0-70:.0f},{cy} L{x1+70:.0f},{cy} L{hb_x:.0f},{cy} L{hb_x+22:.0f},{cy-46} L{hb_x+44:.0f},{cy+58} L{hb_x+70:.0f},{cy-96} L{hb_x+96:.0f},{cy+30} L{hb_x+116:.0f},{cy} L1440,{cy}'
    # feather marks
    fx0=x0-70; fx1=x1+70
    feathers=f'M{fx0-26:.0f},{cy-26} L{fx0:.0f},{cy} L{fx0-26:.0f},{cy+26} M{fx1+26:.0f},{cy-26} L{fx1:.0f},{cy} L{fx1+26:.0f},{cy+26}'
    mot=''
    mx,my=1235,300
    if motif=='triquetra':
        ps=triquetra_path(mx,my,128)
        mot=''.join(f'<path d="{p}" fill="none" stroke="url(#g2)" stroke-width="7" opacity="0.55"/>' for p in ps)
        mot+=f'<circle cx="{mx}" cy="{my}" r="80" fill="none" stroke="url(#g2)" stroke-width="5" opacity="0.45"/>'
    elif motif=='triskele':
        ps=triskele_path(mx,my,250)
        mot=''.join(f'<path d="{p}" fill="none" stroke="url(#g2)" stroke-width="9" stroke-linecap="round" opacity="0.55"/>' for p in ps)
        mot+=f'<circle cx="{mx}" cy="{my}" r="190" fill="none" stroke="url(#g2)" stroke-width="3" opacity="0.3"/>'
    elif motif=='rings':
        mot=''.join(f'<circle cx="{mx}" cy="{my}" r="{r}" fill="none" stroke="url(#g2)" stroke-width="{w}" opacity="{o}"/>' for r,w,o in [(70,6,0.5),(130,4,0.35),(195,3,0.22),(260,2,0.14)])
        ps=triquetra_path(mx,my,80)
        mot+=''.join(f'<path d="{p}" fill="none" stroke="url(#g2)" stroke-width="5" opacity="0.6"/>' for p in ps)
    lines=''.join(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" />' for a,b,c,d in segs)
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
 <radialGradient id="bg1" cx="22%" cy="55%" r="70%"><stop offset="0" stop-color="{PLUM}" stop-opacity="0.85"/><stop offset="1" stop-color="{NAVY}" stop-opacity="0"/></radialGradient>
 <radialGradient id="bg2" cx="85%" cy="40%" r="55%"><stop offset="0" stop-color="{a2}" stop-opacity="0.38"/><stop offset="1" stop-color="{NAVY}" stop-opacity="0"/></radialGradient>
 <radialGradient id="bg3" cx="50%" cy="110%" r="60%"><stop offset="0" stop-color="{a1}" stop-opacity="0.22"/><stop offset="1" stop-color="{NAVY}" stop-opacity="0"/></radialGradient>
 <linearGradient id="g1" gradientUnits="userSpaceOnUse" x1="{x0-60:.0f}" y1="170" x2="{x1+60:.0f}" y2="430"><stop offset="0" stop-color="{a1}"/><stop offset="1" stop-color="{a2}"/></linearGradient>
 <linearGradient id="g2" gradientUnits="userSpaceOnUse" x1="1060" y1="140" x2="1420" y2="460"><stop offset="0" stop-color="{a2}"/><stop offset="1" stop-color="{a1}"/></linearGradient>
 <linearGradient id="stemg" gradientUnits="userSpaceOnUse" x1="40" y1="0" x2="1460" y2="0"><stop offset="0" stop-color="{a1}" stop-opacity="0"/><stop offset="0.15" stop-color="{a1}"/><stop offset="0.85" stop-color="{a2}"/><stop offset="1" stop-color="{a2}" stop-opacity="0"/></linearGradient>
 <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="{NAVY}"/>
<rect width="{W}" height="{H}" fill="url(#bg1)"/><rect width="{W}" height="{H}" fill="url(#bg2)"/><rect width="{W}" height="{H}" fill="url(#bg3)"/>
{stars(W,H,170,seed)}
<g filter="url(#glow)">{mot}</g>
<g filter="url(#glow)" fill="none" stroke-linecap="round" stroke-linejoin="round">
 <path d="{stem}" stroke="url(#stemg)" stroke-width="5"/>
 <path d="{feathers}" stroke="{a1}" stroke-width="5" opacity="0.9"/>
 <g stroke="url(#g1)" stroke-width="{sw}">{lines}</g>
</g>
</svg>'''
    return svg
def icon(letters, a1, a2, motif=None, seed=1):
    S=512; c=256
    if motif=='triquetra':
        ps=triquetra_path(c,c+14,170)
        inner=''.join(f'<path d="{p}" fill="none" stroke="url(#g1)" stroke-width="20" stroke-linejoin="round"/>' for p in ps)
        inner+=f'<circle cx="{c}" cy="{c+6}" r="106" fill="none" stroke="url(#g2)" stroke-width="14"/>'
    else:
        segs,x0,x1=ogham_strokes(letters,c,c,L=118,sp=34,gap=60)
        lines=''.join(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{cc:.1f}" y2="{d:.1f}"/>' for a,b,cc,d in segs)
        inner=f'<path d="M70,{c} L442,{c}" stroke="url(#g2)" stroke-width="14" stroke-linecap="round"/><g stroke="url(#g1)" stroke-width="26" stroke-linecap="round">{lines}</g>'
        inner+=f'<path d="M52,{c-22} L74,{c} L52,{c+22} M460,{c-22} L438,{c} L460,{c+22}" stroke="{a1}" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">
<defs>
 <radialGradient id="bg" cx="35%" cy="30%" r="85%"><stop offset="0" stop-color="{PLUM}"/><stop offset="1" stop-color="{NAVY}"/></radialGradient>
 <linearGradient id="g1" gradientUnits="userSpaceOnUse" x1="100" y1="100" x2="412" y2="412"><stop offset="0" stop-color="{a1}"/><stop offset="1" stop-color="{a2}"/></linearGradient>
 <linearGradient id="g2" gradientUnits="userSpaceOnUse" x1="412" y1="100" x2="100" y2="412"><stop offset="0" stop-color="{a2}"/><stop offset="1" stop-color="{a1}"/></linearGradient>
 <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect x="8" y="8" width="496" height="496" rx="112" fill="url(#bg)"/>
<rect x="8" y="8" width="496" height="496" rx="112" fill="none" stroke="url(#g2)" stroke-width="6" opacity="0.6"/>
{stars(S,S,40,seed).replace('r="1.6"','r="1.4"')}
<g filter="url(#glow)" fill="none">{inner}</g>
</svg>'''
    return svg

ITEMS=[
 # key, kind, letters, a1, a2, motif
 ('desk-colleen','cover',list('COLLEEN'),GOLD,PINK,'triquetra'),
 ('desk-cass','cover',list('CASS'),TEAL,GOLD,'triskele'),
 ('desk-elizabeth','cover',['E','L','I','Z','A','B','E','T','H'],CORAL,PLUM,'rings'),
 ('role-founder','cover',['D'],GOLD,CORAL,'triquetra'),
 ('role-csl','cover',['G'],TEAL,PINK,'triskele'),
 ('role-supervisor','cover',['C'],GOLD,TEAL,'rings'),
 ('role-support','cover',['L'],TEAL,GOLD,'rings'),
 ('role-onboarding','cover',['B'],PINK,TEAL,'triskele'),
 ('role-office-hours','cover',['M'],CORAL,GOLD,'rings'),
 ('role-build','cover',['T'],CORAL,TEAL,'triquetra'),
 ('role-contractor','cover',['F'],TEAL,PLUM,'rings'),
 ('role-every','cover',[],PINK,TEAL,'triquetra'),
 ('icon-elizabeth','icon',['E'],CORAL,GOLD,None),
 ('icon-founder','icon',['D'],GOLD,PINK,None),
 ('icon-csl','icon',['G'],TEAL,GOLD,None),
 ('icon-supervisor','icon',['C'],GOLD,TEAL,None),
 ('icon-support','icon',['L'],TEAL,PINK,None),
 ('icon-onboarding','icon',['B'],PINK,GOLD,None),
 ('icon-office-hours','icon',['M'],CORAL,GOLD,None),
 ('icon-build','icon',['T'],CORAL,TEAL,None),
 ('icon-contractor','icon',['F'],TEAL,GOLD,None),
 ('icon-every','icon',[],PINK,TEAL,'triquetra'),
]
import os
os.makedirs('out',exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page(device_scale_factor=1)
    for i,(k,kind,letters,a1,a2,motif) in enumerate(ITEMS):
        if kind=='cover':
            if not letters:
                svg=cover(k,['A'],a1,a2,'rings',seed=i+7)
                tq=''.join(f'<path d="{pp}" fill="none" stroke="url(#g1)" stroke-width="10"/>' for pp in triquetra_path(560,312,150))
                tq+='<circle cx="560" cy="312" r="94" fill="none" stroke="url(#g1)" stroke-width="7"/>'
                svg=svg.replace('<g stroke="url(#g1)" stroke-width="16">','<g stroke="url(#g1)" stroke-width="16" opacity="0">').replace('</svg>',f'<g filter="url(#glow)">{tq}</g></svg>')
            else:
                svg=cover(k,letters,a1,a2,motif,seed=i+7)
            W,H=1500,600
        else:
            svg=icon(letters,a1,a2,motif,seed=i+3); W,H=512,512
        html=f'<html><body style="margin:0;background:transparent">{svg}</body></html>'
        pg.set_viewport_size({'width':W,'height':H})
        pg.set_content(html)
        pg.screenshot(path=f'out/{k}.png',clip={'x':0,'y':0,'width':W,'height':H},omit_background=(kind=='icon'))
    b.close()
print('done')
