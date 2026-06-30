#!/usr/bin/env python3
"""Classify each modern-japanese corpus FILE (by filename) -> is it itself a Japanese
translation of an Indian Buddhist work? which canonical work? full/partial. Gemini fleet."""
import os, re, json, time, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
KEY=os.environ["GEMINI_KEY"]
URL=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={KEY}"
W=int(os.environ.get("W","32")); BATCH=40
PROMPT=("Each numbered line is the FILENAME of a Japanese Buddhist-studies file (author_year@title). "
"Decide whether the FILE ITSELF is a English translation of a classical INDIAN Buddhist text "
"(Sanskrit/Pali/Prakrit original, incl. works surviving only in Tibetan/Chinese but of Indian origin).\n"
"Output ONE line per input: N|WORK|SCOPE\n"
" WORK = standard romanized Sanskrit/Pali title of the original, normalized (中論→Mūlamadhyamakakārikā; 倶舎論/俱舍論→Abhidharmakośabhāṣya; "
"入菩提行論→Bodhicaryāvatāra; 大乗荘厳経論→Mahāyānasūtrālaṃkāra; 摂大乗論→Mahāyānasaṃgraha; 菩薩地→Bodhisattvabhūmi; etc.)\n"
" SCOPE = full (whole work) | partial (a chapter/section/installment e.g. 第N章/(1)/（2）/章/品/fragment) | unknown\n"
"If the file is NOT itself such a translation (a study/article ABOUT a text, a modern work, a Chinese/Japanese/Tibetan indigenous text, "
"a grammar, an index, or unclear), output: N|SKIP\n"
"Exactly one output line per input, no commentary.\nFILES:\n")
def call(p):
    body={"contents":[{"parts":[{"text":p}]}],"generationConfig":{"temperature":0,"thinkingConfig":{"thinkingBudget":0}}}
    data=json.dumps(body).encode()
    for k in range(6):
        try:
            r=json.load(urllib.request.urlopen(urllib.request.Request(URL,data=data,headers={"Content-Type":"application/json"}),timeout=120))
            return "".join(x.get("text","") for x in r.get("candidates",[{}])[0].get("content",{}).get("parts",[]))
        except Exception:
            if k<5: time.sleep(min(2*(k+1),20)); continue
            return None
def proc(batch):
    body="\n".join(f"{i+1}. {fn}" for i,fn in enumerate(batch))
    out=call(PROMPT+body); recs=[]
    if not out: return recs
    for l in out.splitlines():
        m=re.match(r"\s*(\d+)\s*\|\s*(.*)",l)
        if not m: continue
        i=int(m.group(1))-1
        if i<0 or i>=len(batch): continue
        rest=m.group(2).strip()
        if rest.upper().startswith("SKIP"): continue
        parts=[p.strip() for p in rest.split("|")]
        work=parts[0] if parts else ""
        if not work or work.upper()=="SKIP": continue
        scope=parts[1] if len(parts)>1 else "unknown"
        recs.append((batch[i],work,scope))
    return recs
if __name__=="__main__":
    files=[l.rstrip("\n") for l in open("/tmp/claude-1000/en_filenames.txt") if l.strip()]
    batches=[files[i:i+BATCH] for i in range(0,len(files),BATCH)]
    res=[None]*len(batches); done=0; t0=time.time(); lock=threading.Lock()
    with ThreadPoolExecutor(max_workers=W) as ex:
        fut={ex.submit(proc,b):i for i,b in enumerate(batches)}
        for fu in as_completed(fut):
            res[fut[fu]]=fu.result()
            with lock:
                done+=1
                if done%30==0: print(f"  {done}/{len(batches)} {time.time()-t0:.0f}s",flush=True)
    with open("/tmp/claude-1000/en_file_works.tsv","w",encoding="utf-8") as f:
        for b in res:
            for fn,work,scope in (b or []):
                f.write(f"{work}\t{scope}\t{fn}\n")
    print("done",sum(len(b or []) for b in res),"translation files identified",flush=True)
