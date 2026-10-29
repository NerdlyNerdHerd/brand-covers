import sys
src=open('/home/claude/brand-covers/team/generate.py').read().split('ITEMS=[')[0]
exec(src)
ITEMS=[
 ('hq-start-here',list('FAILTE'),GOLD,TEAL,'triskele'),   # Failte = welcome
 ('kpi-scorecard',['B','U','A'],TEAL,GOLD,'rings'),       # Bua = victory
 ('archive-2025',list('CUIMHNE'),'#8E86A8','#5A5078','rings'),  # Cuimhne = memory (muted)
]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    for i,(k,letters,a1,a2,motif) in enumerate(ITEMS):
        svg=cover(k,letters,a1,a2,motif,seed=40+i)
        pg.set_viewport_size({'width':1500,'height':600})
        pg.set_content(f'<html><body style="margin:0">{svg}</body></html>')
        pg.screenshot(path=f'/home/claude/brand-covers/team/covers/{k}.png',clip={'x':0,'y':0,'width':1500,'height':600})
    b.close()
print('ok')
