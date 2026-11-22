import json, asyncio, subprocess, sys, os, time
import edge_tts
B=json.load(open('tools/blocks.json'))
async def one(b):
    out=f"audio/{b['id']}.mp3"
    if os.path.exists(out) and os.path.getsize(out)>10000: return
    for i in range(8):
        try:
            c=edge_tts.Communicate(b['text'], b['voice'], rate="+5%")
            subs=edge_tts.SubMaker()
            with open(out,'wb') as f:
                async for ch in c.stream():
                    if ch['type']=='audio': f.write(ch['data'])
                    elif ch['type'] in ('WordBoundary','SentenceBoundary'): subs.feed(ch)
            open(f"tools/{b['id']}.srt",'w').write(subs.get_srt())
            return
        except Exception as e:
            print('retry',b['id'],e); time.sleep(10*(i+1))
    raise SystemExit('fail '+b['id'])
async def main():
    for b in B: await one(b)
asyncio.run(main())
for b in B:
    d=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f"audio/{b['id']}.mp3"]).decode().strip()
    b['dur']=round(float(d),1); print(b['id'],b['dur'])
json.dump(B,open('tools/blocks.json','w'),ensure_ascii=False,indent=1)
