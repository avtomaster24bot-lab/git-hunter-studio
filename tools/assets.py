import sys; sys.path.insert(0,'tools')
from fonts import F
from PIL import Image, ImageDraw, ImageFilter
def bg(w,h):
    im=Image.new('RGB',(w,h),(7,7,12)); o=Image.new('RGB',(w,h),(0,0,0)); d=ImageDraw.Draw(o)
    d.ellipse((-w*.3,-h*.6,w*.6,h*.7),fill=(124,92,255)); d.ellipse((w*.55,h*.3,w*1.4,h*1.6),fill=(0,224,198))
    o=o.filter(ImageFilter.GaussianBlur(min(w,h)//4)); return Image.blend(im,o,.35)
def grad(w,h):
    g=Image.new('RGB',(w,h)); d=ImageDraw.Draw(g)
    for x in range(w):
        t=x/max(1,w-1); d.line([(x,0),(x,h)],fill=(int(124+(0-124)*t),int(92+(224-92)*t),int(255+(198-255)*t)))
    return g
im=bg(1200,630); d=ImageDraw.Draw(im)
logo=grad(64,64); m=Image.new('L',(64,64)); ImageDraw.Draw(m).rounded_rectangle((0,0,63,63),16,fill=255); im.paste(logo,(70,64),m)
d.text((102,96),"GH",font=F(26),fill=(7,7,12),anchor="mm")
d.text((152,96),"Git Hunter Studio",font=F(34,"ExtraBold"),fill=(243,243,247),anchor="lm")
y=190
for line in ["ИИ работает на вас,","пока вы занимаетесь","бизнесом"]:
    d.text((70,y),line,font=F(78),fill=(243,243,247)); y+=90
d.text((70,500),"Ассистент · Сайты · Автоматизация · Казахстан",font=F(30,"SemiBold"),fill=(162,163,181))
g=grad(380,64); m=Image.new('L',(380,64)); ImageDraw.Draw(m).rounded_rectangle((0,0,379,63),32,fill=255); im.paste(g,(750,60),m)
d.text((940,92),"🎧 Слушайте, не читайте".replace("🎧 ",""),font=F(26,"ExtraBold"),fill=(7,7,12),anchor="mm")
im.save('assets/og.png',optimize=True)
for s,n in [(32,'favicon-32.png'),(180,'apple-touch-icon.png'),(512,'icon-512.png')]:
    g=grad(s,s); m=Image.new('L',(s,s)); ImageDraw.Draw(m).rounded_rectangle((0,0,s-1,s-1),s//4,fill=255)
    out=Image.new('RGBA',(s,s),(0,0,0,0)); out.paste(g,(0,0),m); ImageDraw.Draw(out).text((s/2,s/2),"GH",font=F(int(s*.42)),fill=(7,7,12),anchor="mm"); out.save('assets/'+n)
open('assets/favicon.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#7c5cff"/><stop offset="1" stop-color="#00e0c6"/></linearGradient></defs><rect width="64" height="64" rx="16" fill="url(#g)"/><text x="32" y="42" font-family="Inter,Arial,sans-serif" font-weight="900" font-size="27" text-anchor="middle" fill="#07070c">GH</text></svg>')
