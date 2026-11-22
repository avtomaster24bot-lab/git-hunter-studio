"""Иллюстрации карточек 1200x600 (Pillow): градиент, эмодзи, макеты интерфейса. Без логотипов клиентов."""
import json, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
F_DIR='assets/fonts/'
def font(w,s): return ImageFont.truetype(F_DIR+f'Inter-{w}.ttf',s)
EMO=ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',109)
W,H=1200,600
ACC=(124,92,255);ACC2=(34,211,238);TXT=(235,240,248);MUT=(150,162,182);PANEL=(22,28,42);LINE=(52,62,88)
def bg(seed):
    im=Image.new('RGB',(W,H),(11,15,23)); g=Image.new('RGB',(W,H)); d=ImageDraw.Draw(g)
    cols=[ACC,ACC2,(255,61,154),(52,211,153),(251,191,36)]
    d.ellipse((-200+seed*40,-300,500+seed*40,400),fill=cols[seed%5]); d.ellipse((800-seed*30,250,1500,900),fill=cols[(seed+1)%5])
    im=Image.blend(im,g.filter(ImageFilter.GaussianBlur(150)),.45).convert('RGBA')
    d=ImageDraw.Draw(im)
    for x in range(0,W,40):
        for y in range(0,H,40): d.point((x,y),fill=(255,255,255,40))
    return im
def emoji(im,e,x,y,size):
    t=Image.new('RGBA',(150,150),(0,0,0,0)); ImageDraw.Draw(t).text((75,75),e,font=EMO,embedded_color=True,anchor='mm')
    t=t.resize((size,size),Image.LANCZOS); im.alpha_composite(t,(int(x),int(y)))
def panel(im,box,r=24,fill=PANEL,outline=LINE):
    sh=Image.new('RGBA',im.size,(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((box[0]+8,box[1]+16,box[2]+8,box[3]+16),r,fill=(0,0,0,140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); ImageDraw.Draw(im).rounded_rectangle(box,r,fill=fill,outline=outline,width=2)
def bubble(im,x,y,text,me=False,w=None):
    d=ImageDraw.Draw(im); f=font('SemiBold',24); tw=d.textlength(text,font=f); w=w or tw+40
    fill=(124,92,255) if me else (38,46,66); d.rounded_rectangle((x,y,x+w,y+52),22,fill=fill); d.text((x+20,y+12),text,font=f,fill=TXT)
def gradbox(im,box,r=20):
    w,h=box[2]-box[0],box[3]-box[1]; g=Image.new('RGBA',(w,h)); gd=ImageDraw.Draw(g)
    for i in range(w): t=i/w; gd.line([(i,0),(i,h)],fill=tuple(int(ACC[k]*(1-t)+ACC2[k]*t) for k in range(3))+(255,))
    m=Image.new('L',(w,h)); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),r,fill=255); im.paste(g,(box[0],box[1]),m)
def label(im,text,x,y,size=54,col=TXT,w='ExtraBold'): ImageDraw.Draw(im).text((x,y),text,font=font(w,size),fill=col)
def scene(sc,c,seed):
    im=bg(seed); d=ImageDraw.Draw(im)
    if sc=='hero':
        emoji(im,'🤖',90,120,200); label(im,'ИИ работает',90,350,64); label(im,'на вас 24/7',90,425,64,ACC2)
        panel(im,(640,70,1120,530)); 
        for i,(t,me) in enumerate([("Почта разобрана ✓",False),("Клиент записан на 15:00",False),("Пост опубликован",True),("Заявка с сайта",False),("КП отправлено ✓",True)]):
            bubble(im,670 if not me else 800,100+i*82,t,me)
    elif sc=='trust':
        panel(im,(80,90,620,510)); label(im,'Git Hunter',120,120,50); label(im,'подборка дня',120,180,30,MUT,'SemiBold')
        for i in range(4):
            y=245+i*62; d.rounded_rectangle((120,y,180,y+44),10,fill=(ACC,ACC2,(52,211,153),(251,191,36))[i]); d.rounded_rectangle((200,y+6,560-i*50,y+20),6,fill=(70,80,105)); d.rounded_rectangle((200,y+28,470-i*30,y+38),5,fill=(48,56,78))
        emoji(im,'🔎',720,90,170); label(im,'Сотни ИИ-проектов',700,300,46); label(im,'разбираем каждый день',700,360,34,ACC2,'SemiBold'); label(im,'t.me/githunter77',700,430,30,MUT,'SemiBold')
    elif sc=='chat':
        panel(im,(70,60,560,540)); 
        msgs=[("Сколько стоит замена масла?",False),("От 8 000 ₸. Записать вас?",True),("Да, на завтра",False),("Готово: завтра 11:00 ✓",True)]
        for i,(t,me) in enumerate(msgs): bubble(im,95 if not me else 160,90+i*100,t,me)
        emoji(im,'🤖',640,70,150)
        for i,(e,t) in enumerate([('📧','Почта'),('📅','Запись'),('🎬','Контент'),('📊','Отчёты и КП')]):
            emoji(im,e,640+(i%2)*250,260+(i//2)*130,64); label(im,t,715+(i%2)*250,272+(i//2)*130,30,TXT,'SemiBold')
        label(im,'Данные остаются у вас',640,520,28,ACC2,'SemiBold')
    elif sc=='browser':
        panel(im,(60,50,820,550),20,(18,23,35))
        for i,c_ in enumerate([(255,95,87),(255,189,46),(40,201,64)]): d.ellipse((85+i*30,72,103+i*30,90),fill=c_)
        d.rounded_rectangle((190,66,780,96),14,fill=(34,41,58)); label(im,'вашбизнес.kz',210,68,20,MUT,'SemiBold')
        gradbox(im,(90,125,790,300),16); label(im,'Ваш бизнес',120,160,52,(11,15,23)); label(im,'Запишитесь онлайн за 30 секунд',120,230,28,(11,15,23),'SemiBold')
        for i in range(3): d.rounded_rectangle((90+i*237,320,310+i*237,520),16,fill=(30,37,54))
        panel(im,(760,250,1140,560)); emoji(im,'🤖',785,270,64); label(im,'ИИ-консультант',860,285,28)
        bubble(im,785,355,"Есть время в субботу?"); bubble(im,815,425,"Да, 12:00 и 15:00",True); label(im,'Готов за 3–7 дней',860,512,26,ACC2,'SemiBold')
    elif sc=='flow':
        nodes=[('💬','Сообщение'),('🤖','Бот'),('📇','CRM'),('📲','Вам')]
        for i,(e,t) in enumerate(nodes):
            x=70+i*285; panel(im,(x,90,x+220,300)); emoji(im,e,x+65,115,90); label(im,t,x+110-d.textlength(t,font=font('ExtraBold',30))/2,225,30)
            if i<3: d.line((x+225,195,x+280,195),fill=ACC2,width=6); d.polygon([(x+282,195),(x+268,185),(x+268,205)],fill=ACC2)
        panel(im,(70,360,1130,540)); emoji(im,'🏭',100,385,120); label(im,'Контент-завод',250,390,46); label(im,'видео и посты сами → YouTube · TikTok · Instagram',250,455,28,ACC2,'SemiBold')
    elif sc=='niches':
        items=[('🚗','Автосервис'),('💅','Салон'),('🦷','Стоматология'),('🎓','Эксперт'),('🛍','Магазин'),('🏠','Недвижимость')]
        for i,(e,t) in enumerate(items):
            x=70+(i%3)*360; y=60+(i//3)*265; panel(im,(x,y,x+330,y+235)); emoji(im,e,x+115,y+25,100); f=font('ExtraBold',34); d.text((x+165-d.textlength(t,font=f)/2,y+160),t,font=f,fill=TXT)
    elif sc=='prices':
        P=[('Старт','49 000 ₸'),('Бизнес','149 000 ₸'),('Под ключ','299 000 ₸'),('Поддержка','15 000 ₸/мес')]
        for i,(n,p) in enumerate(P):
            x=50+i*285; y=110 if i!=1 else 80
            if i==1: gradbox(im,(x-4,y-4,x+264,y+414),26)
            panel(im,(x,y,x+260,y+410),24,(26,32,48) if i!=1 else (34,30,64))
            label(im,n,x+28,y+40,34); label(im,'от',x+28,y+120,26,MUT,'SemiBold'); label(im,p.split(' ₸')[0]+' ₸',x+28,y+155,40,ACC2 if i!=1 else TXT)
            if '/мес' in p: label(im,'в месяц',x+28,y+210,24,MUT,'SemiBold')
            for k in range(3): d.rounded_rectangle((x+28,y+270+k*36,x+230-k*40,y+284+k*36),6,fill=(60,70,96))
    elif sc=='steps':
        S=['Консультация','Демо','Настройка','Обучение','Поддержка']
        d.line((140,300,1060,300),fill=(60,70,96),width=8)
        for i,t in enumerate(S):
            x=140+i*230; gradbox(im,(x-60,240,x+60,360),60); f=font('ExtraBold',56); d.text((x,300),str(i+1),font=f,fill=(11,15,23),anchor='mm')
            f=font('ExtraBold',28); d.text((x,410),t,font=f,fill=TXT,anchor='mm')
        label(im,'15 минут от вас — остальное делаем мы',140,110,40,TXT); 
    elif sc=='faq':
        Q=[('🔒','Безопасно?','Данные у вас'),('🙂','Сложно?','Обычными словами'),('⏱','Долго?','От пары дней'),('💻','Нужен мощный ПК?','Обычно — нет')]
        for i,(e,q,a) in enumerate(Q):
            x=70+(i%2)*540; y=60+(i//2)*265; panel(im,(x,y,x+510,y+235)); emoji(im,e,x+30,y+30,90); label(im,q,x+140,y+50,36); label(im,a,x+140,y+110,30,ACC2,'SemiBold')
    elif sc=='gift':
        emoji(im,'🎁',100,110,240); label(im,'Бесплатная',420,150,72); label(im,'консультация',420,235,72); 
        gradbox(im,(420,360,1010,450),45); f=font('ExtraBold',34); d.text((715,405),'@Git_Hunter_bot',font=f,fill=(11,15,23),anchor='mm'); label(im,'15 минут · без обязательств',420,480,32,MUT,'SemiBold')
    # бейдж
    return im.convert('RGB')
if __name__=='__main__':
    C=json.load(open('tools/cards.json'))
    for i,(k,c) in enumerate(C.items()):
        scene(c['scene'],c,i).save(f'img/{k}.jpg',quality=88); print(k)
