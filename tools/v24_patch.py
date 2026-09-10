from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='V2_4_1_ANTI_PASSIVITY'
if marker in s:
    print('V2.4.1 already applied')
    raise SystemExit(0)

m=re.search(r'function\s+decide\s*\([^)]*\)\s*\{',s)
if not m:
    raise SystemExit('V2.4.1 patch failed: decide() not found')
brace=s.find('{',m.start()); depth=0; end=None
for j in range(brace,len(s)):
    if s[j]=='{': depth+=1
    elif s[j]=='}':
        depth-=1
        if depth==0:
            end=j+1; break
if end is None: raise SystemExit('V2.4.1 patch failed: decide() end not found')

new=r'''function utilityScore(f,e,a,q,c,low,enemyLow,incoming){const s=c.style;let v=Math.random()*1.2;if(a==='attack'){v+=q<24?6:1;v+=s==='aggressive'?4:2;if(enemyLow)v+=4}if(a==='heavy'){v+=q<18?6:1;v+=s==='aggressive'?4:1;if(enemyLow)v+=4;v-=q>30?3:0}if(a==='lightkick'){v+=q<25?4:1;v+=s==='evasive'?2:0}if(a==='kick'){v+=q<30?3:0;v+=enemyLow?4:0}if(a==='guard'){v+=incoming?(s==='evasive'?5:3):0;v+=low?2:0;v-=f.passive>2?8:0}if(a==='dodge'){v+=incoming?(s==='evasive'?8:3):0;v+=low?3:0;v+=q<18?2:0;v-=f.passive>2?10:0}if(a==='jump'){v+=(s==='evasive'&&low)?6:1;v+=incoming?3:0;v-=f.passive>2?7:0}if(a==='special'){v+=f.en>=100?6:0;v+=enemyLow?8:0;v+=q<22?5:0;v+=s==='aggressive'?4:2}return v}
function chooseUtility(f,e,actions,q,c,low,enemyLow,incoming){let best=actions[0],score=-1e9;for(const a of actions){let v=utilityScore(f,e,a,q,c,low,enemyLow,incoming);if(f.passive>=4&&['attack','heavy','lightkick','kick','special'].includes(a))v+=10;if(f.passive>=7&&a==='attack')v+=8;if(f.passive>=7&&a==='dodge')v-=18;if(f.passive>=7&&a==='guard')v-=15;if(e.hp<220&&['attack','heavy','kick','special'].includes(a))v+=5;if(v>score){score=v;best=a}}return best}
function decide(f,e){if(f.action||f.stun>0||f.cool>0||f.hp<=0)return;const q=gap(),c=cfg[f.kind],style=c.style,low=f.hp<240,enemyLow=e.hp<220,incoming=!!e.action&&e.action.t<e.action.max;if(f.passive==null)f.passive=0;f.passive=Math.min(10,f.passive+.45);const desperation=f.passive>=5||timer<=15;if(desperation){if(f.en>=100&&q<c.special[2]){f.en=0;begin(f,'special',c.special);f.passive=0;return}if(q<=c.reach+5){const arr=c.atk;const type=style==='aggressive'&&Math.random()<.55?'heavy':Math.random()<.65?'attack':'kick';const mm=type==='attack'?arr[0]:type==='heavy'?arr[1]:arr[3];begin(f,type,mm);f.passive=0;return}f.state='approach';f.x+=f.face*(style==='evasive'?1.55:1.25);return}if(style==='evasive'&&q<12){const a=chooseUtility(f,e,['dodge','guard','attack'],q,c,low,enemyLow,incoming);if(a==='dodge'){f.dodge=.3;f.state='dodge';visual(f,'dodge');f.cool=.42;return}if(a==='guard'){f.guard=.35;f.state='guard';visual(f,'guard');f.cool=.3;return}}if(incoming&&q<27){const a=chooseUtility(f,e,['guard','dodge','attack'],q,c,low,enemyLow,incoming);if(a==='dodge'&&style==='evasive'){f.dodge=.3;f.state='dodge';visual(f,'dodge');f.cool=.44;return}if(a==='guard'){f.guard=style==='aggressive'?.24:.38;f.state='guard';visual(f,'guard');f.cool=.3;return}}if(q>c.reach+1){f.state='approach';f.x+=f.face*(low?c.speed*.95:c.speed*1.08);return}if(f.en>=100&&q<c.special[2]){const a=chooseUtility(f,e,['special','attack','heavy'],q,c,low,enemyLow,incoming);if(a==='special'){f.en=0;begin(f,'special',c.special);f.passive=0;return}}if(style==='evasive'&&low){const a=chooseUtility(f,e,['dodge','jump','guard','attack'],q,c,low,enemyLow,incoming);if(a==='dodge'){f.dodge=.3;f.state='dodge';visual(f,'dodge');f.cool=.5;return}if(a==='jump'){f.jump=.42;f.state='jump';visual(f,'jump');f.cool=.52;return}}if(f.combo>0&&f.comboT>0){const arr=c.atk,chain=[arr[0],arr[0],arr[1],arr[2],arr[3]],mm=chain[Math.min(f.combo,chain.length-1)],type=mm===arr[0]?'attack':mm===arr[1]?'heavy':mm===arr[2]?'lightkick':'kick';if(Math.random()<(style==='aggressive'?.9:.76)){begin(f,type,mm);f.passive=0;return}}const arr=c.atk,type=chooseUtility(f,e,['attack','heavy','lightkick','kick'],q,c,low,enemyLow,incoming),mm=type==='attack'?arr[0]:type==='heavy'?arr[1]:type==='lightkick'?arr[2]:arr[3];begin(f,type,mm);f.passive=0}'''
s=s[:m.start()]+new+s[end:]
s=s.replace('<!-- V2_4_UTILITY_AI -->','<!-- V2_4_UTILITY_AI -->\n<!-- V2_4_1_ANTI_PASSIVITY -->',1)
p.write_text(s,encoding='utf-8')
print('V2.4.1 anti-passivity applied')
