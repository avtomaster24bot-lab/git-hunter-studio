import json, asyncio, os, time, edge_tts
P=json.load(open('promo/src/promos.json'))
async def one(p):
    out=f"promo/src/{p['id']}.mp3"
    if os.path.exists(out) and os.path.getsize(out)>10000: return
    for i in range(8):
        try:
            c=edge_tts.Communicate(p['text'],"ru-RU-SvetlanaNeural",rate="+8%"); s=edge_tts.SubMaker()
            with open(out,'wb') as f:
                async for ch in c.stream():
                    if ch['type']=='audio': f.write(ch['data'])
                    elif ch['type'] in ('WordBoundary','SentenceBoundary'): s.feed(ch)
            open(f"promo/src/{p['id']}.srt",'w').write(s.get_srt()); return
        except Exception as e: print('retry',e); time.sleep(10*(i+1))
    raise SystemExit('fail')
async def m():
    for p in P: await one(p)
asyncio.run(m())
