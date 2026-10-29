import os
# Former-team desk covers: same style as the active desks (name in Ogham + a Celtic motif), no bitmoji.
# Ogham has no K or Y, so Kate uses C (Coll) and Tatyana uses I (Idad), as Irish spelling would.
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'generate.py')).read().split('ITEMS=[')[0]
exec(src)
ITEMS = [
 ('former-kate',    list('CATE'),    GOLD, PLUM, 'triquetra'),
 ('former-tatyana', list('TATIANA'), PINK, TEAL, 'triskele'),
 ('former-genesis', list('GENESIS'), TEAL, CORAL, 'rings'),
 ('former-lisa',    list('LISA'),    CORAL, GOLD, 'triskele'),
]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    for i, (k, letters, a1, a2, motif) in enumerate(ITEMS):
        svg = cover(k, letters, a1, a2, motif, seed=60 + i)
        pg.set_viewport_size({'width': 1500, 'height': 600})
        pg.set_content(f'<html><body style="margin:0">{svg}</body></html>')
        pg.screenshot(path=os.path.join(here, 'covers', f'{k}.png'), clip={'x': 0, 'y': 0, 'width': 1500, 'height': 600})
    b.close()
print('ok')
