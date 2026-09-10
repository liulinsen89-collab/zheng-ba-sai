from pathlib import Path
import re
p=Path('index.html'); s=p.read_text(encoding='utf-8')
marker='V2_4_2_ANTI_DODGE'
if marker in s:
 print('V2.4.2 already applied'); raise SystemExit(0)
old="const realDecide=decide;decide=function(f,e){if(performance.now()<openingLockUntil){f.vx=0;return}return realDecide(f,e)}"
new="const realDecide=decide;decide=function(f,e){if(performance.now()<openingLockUntil){f.vx=0;return}if(f.dodgeStreak==null)f.dodgeStreak=0;const before=f.state;realDecide(f,e);if(f.state==='dodge'){f.dodgeStreak++;if(f.dodgeStreak>=2){f.dodge=0;f.cool=0;f.state='idle';visual(f);const arr=cfg[f.kind].atk;begin(f,'attack',arr[0]);f.dodgeStreak=0}}else if(f.state==='attack'||f.state==='heavy'||f.state==='kick'||f.state==='lightkick'||f.state==='special'){f.dodgeStreak=0}else if(before!=='dodge'){f.dodgeStreak=0}}"
if old not in s: raise SystemExit('V2.4.2 patch failed: decision wrapper not found')
s=s.replace(old,new,1)
s=s.replace('function resetF(f,x){f.x=x;','function resetF(f,x){f.dodgeStreak=0;f.x=x;',1)
s=s.replace('<!-- V2_4_1_ANTI_PASSIVITY -->','<!-- V2_4_1_ANTI_PASSIVITY -->\n<!-- V2_4_2_ANTI_DODGE -->',1)
p.write_text(s,encoding='utf-8'); print('V2.4.2 anti-dodge applied')
