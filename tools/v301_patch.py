from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='<!-- V3_0_1_CLOSE_RANGE_DODGE_FIX -->'
if marker in s:
    print('already patched')
    raise SystemExit(0)
patch=r'''<!-- V3_0_1_CLOSE_RANGE_DODGE_FIX -->
<script>
(()=>{
  const started=performance.now();
  const timer=setInterval(()=>{
    if(!window.decide||window.decide.__v301)return;
    const previous=window.decide;
    const w=function(f,e){
      e=e||(f===window.A?window.B:window.A);
      previous(f,e);
      if(!f||!e||f.hp<=0||e.hp<=0)return;
      const dist=Math.abs((f.x||0)-(e.x||0));
      const isSpeed=f===window.B;
      if(isSpeed && dist<155 && f.state==='dodge'){
        f.dodge=0; f.cool=0; f.vx=0;
        if(typeof begin==='function') begin(f,'attack','jab'); else f.state='attack';
      }
      if(isSpeed && dist<125 && f.state==='idle' && Math.random()<0.72){
        f.vx=0;
        if(typeof begin==='function') begin(f,'attack','jab'); else f.state='attack';
      }
    };
    w.__v301=true;
    window.decide=w;
    clearInterval(timer);
  },50);
  setTimeout(()=>clearInterval(timer),5000);
})();
</script>
'''
s=s.replace('</body></html>',patch+'</body></html>')
p.write_text(s,encoding='utf-8')
print('patched V3.0.1')
