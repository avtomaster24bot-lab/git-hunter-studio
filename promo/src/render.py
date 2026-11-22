import json, re, subprocess, sys, math
sys.path.insert(0,'tools'); from fonts import F
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W,H,FPS=1080,1920,30
EMO=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',109)
def ts(t):
    h,m,s=t.split(':'); s,ms=s.split(','); return int(h)*3600+int(m)*60+int(s)+int(ms)/1000
def subs(path):
    out=[]
    for blk in open(path).read().strip().split('\n\n'):
        L=blk.strip().split('\n'); a,b=[ts(x.strip()) for x in L[1].split('-->')]; txt=' '.join(L[2:])
        words=txt.split(); n=max(1,math.ceil(len(words)/6)); per=math.ceil(len(words)/n)
        chunks=[' '.join(words[i:i+per]) for i in range(0,len(words),per)]
        tot=sum(len(c) for c in chunks); t=a
        for c in chunks:
            d=(b-a)*len(c)/tot; out.append((t,t+d,c)); t+=d
    return out
def grad(w,h):
    g=Image.new('RGB',(w,h)); d=ImageDraw.Draw(g)
    for x in range(w):
        t=x/max(1,w-1); d.line([(x,0),(x,h)],fill=(int(124-124*t),int(92+132*t),int(255-57*t)))
    return g
def bg():
    im=Image.new('RGB',(W,H),(7,7,12)); o=Image.new('RGB',(W,H)); d=ImageDraw.Draw(o)
    d.ellipse((-500,-600,800,700),fill=(124,92,255)); d.ellipse((400,1200,1600,2500),fill=(0,224,198))
    return Image.blend(im,o.filter(ImageFilter.GaussianBlur(260)),.4)
def wrap(d,text,font,maxw):
    lines=[];cur=''
    for w in text.split():
        t=(cur+' '+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
def slide(base,emo,title,idx,total):
    im=base.copy(); d=ImageDraw.Draw(im)
    # brand
    lg=grad(80,80); m=Image.new('L',(80,80)); ImageDraw.Draw(m).rounded_rectangle((0,0,79,79),20,fill=255); im.paste(lg,(80,110),m)
    d.text((120,150),"GH",font=F(32),fill=(7,7,12),anchor="mm")
    d.text((185,150),"Git Hunter Studio",font=F(44,"ExtraBold"),fill=(243,243,247),anchor="lm")
    # emoji
    e=Image.new('RGBA',(140,140),(0,0,0,0)); ImageDraw.Draw(e).text((70,70),emo,font=EMO,embedded_color=True,anchor="mm")
    e=e.resize((220,220),Image.LANCZOS); im.paste(e,(80,430),e)
    f=F(104); lines=wrap(d,title,f,W-160); y=700
    for l in lines: d.text((80,y),l,font=f,fill=(243,243,247)); y+=122
    # dots
    for i in range(total):
        x=80+i*46; d.rounded_rectangle((x,1780,x+(34 if i==idx else 14),1794),7,fill=(0,224,198) if i==idx else (70,70,90))
    return im
def sub_layer(text):
    L=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L); f=F(58,"ExtraBold")
    lines=wrap(d,text,f,W-200); lh=74; h=len(lines)*lh+44; y0=1500-h//2
    d.rounded_rectangle((70,y0,W-70,y0+h),28,fill=(0,0,0,175))
    for i,l in enumerate(lines): d.text((W/2,y0+22+i*lh+lh/2),l,font=f,fill=(255,255,255),anchor="mm")
    return L
def render(p):
    mp3=f"promo/src/{p['id']}.mp3"; dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',mp3]))+0.8
    base=bg(); S=p['slides']; sl=[slide(base,e,t,i,len(S)).convert('RGBA') for i,(e,t) in enumerate(S)]
    sb=subs(f"promo/src/{p['id']}.srt"); cache={}
    cta=Image.new('RGBA',(W,H),(0,0,0,0)); g=grad(W-160,120); m=Image.new('L',g.size); ImageDraw.Draw(m).rounded_rectangle((0,0,g.size[0]-1,119),60,fill=255)
    cta.paste(g,(80,1620),m); ImageDraw.Draw(cta).text((W/2,1680),"Бесплатная консультация → @Git_Hunter_bot",font=F(34,"ExtraBold"),fill=(7,7,12),anchor="mm")
    seg=dur/len(S); n=int(dur*FPS)
    ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',mp3,
        '-c:v','libx264','-preset','medium','-crf','22','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',f"promo/{p['id']}.mp4"],stdin=subprocess.PIPE)
    for k in range(n):
        t=k/FPS; i=min(int(t/seg),len(S)-1); lt=t-i*seg
        fr=sl[i]
        if lt<0.35 and i>0: fr=Image.blend(sl[i-1],sl[i],lt/0.35)
        fr=fr.copy()
        cur=[c for a,b,c in sb if a<=t<b]
        if cur:
            if cur[0] not in cache: cache[cur[0]]=sub_layer(cur[0])
            fr.alpha_composite(cache[cur[0]])
        if i==len(S)-1: fr.alpha_composite(cta)
        d=ImageDraw.Draw(fr); d.rectangle((0,0,int(W*t/dur),10),fill=(0,224,198))
        ff.stdin.write(fr.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait(); print(p['id'],round(dur,1))
for p in json.load(open('promo/src/promos.json')): render(p)
