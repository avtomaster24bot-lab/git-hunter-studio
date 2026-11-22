import json, asyncio, time, sys, os, subprocess
import edge_tts
B=json.load(open('tools/blocks.json'))
async def go(text, voice, mp3):
    words, buf = [], bytearray()
    c=edge_tts.Communicate(text, voice, rate="+5%", boundary="WordBoundary")
    async for ch in c.stream():
        if ch['type']=='audio': buf.extend(ch['data'])
        elif ch['type']=='WordBoundary': words.append((ch['offset']/1e7,(ch['offset']+ch['duration'])/1e7,ch['text']))
    if len(buf)<5000 or not words: raise RuntimeError('empty')
    open(mp3,'wb').write(bytes(buf)); return words
for b in B:
    wp=f"tools/words/{b['id']}.json"
    if os.path.exists(wp): continue
    os.makedirs('tools/words',exist_ok=True)
    voices=[b['voice']]+(["ru-RU-SvetlanaNeural"] if b['voice']!="ru-RU-SvetlanaNeural" else [])
    ok=False
    for i in range(10):
        v=voices[0] if i<3 else voices[-1]
        try:
            w=asyncio.run(go(b['text'],v,f"audio/{b['id']}.mp3")); b['voice']=v; ok=True; break
        except Exception as e: print('retry',b['id'],v,e,flush=True); time.sleep(6*(i+1))
    if not ok: print('FAIL',b['id']); continue
    json.dump(w,open(wp,'w'),ensure_ascii=False)
    b['dur']=round(float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f"audio/{b['id']}.mp3"])),1)
    print(b['id'],v,b['dur'],len(w),flush=True)
    json.dump(B,open('tools/blocks.json','w'),ensure_ascii=False,indent=1)
