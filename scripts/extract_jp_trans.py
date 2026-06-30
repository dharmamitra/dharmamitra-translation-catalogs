#!/usr/bin/env python3
"""Normalize harvested Japanese citation lines -> structured translation records via Gemini.
For each line: canonical Sanskrit/Pali work, scope (full/partial), translator, year.
In: /tmp/claude-1000/jp_cites.json ([[line,count],...])  Out: jp_trans_records.tsv"""
import os, re, json, time, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
KEY=os.environ["GEMINI_KEY"]
URL=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={KEY}"
W=int(os.environ.get("W","32")); BATCH=30
PROMPT=("Each numbered line is a Japanese bibliographic citation or scholarly article title. "
"For EACH line, decide if it refers to a Japanese translation (和訳/和譯/訳註/訳注/全訳/現代語訳/訳出) of a classical "
"INDIAN Buddhist text whose original is Sanskrit, Pali, Prakrit, or a reconstructed Indian work (incl. works surviving only in "
"Tibetan/Chinese but of Indian origin, e.g. Prasannapadā, Bodhicaryāvatārapañjikā, Abhidharmakośa, Madhyamakāvatāra).\n"
"Output ONE line per input, format: N|WORK|SCOPE|TRANSLATOR|YEAR\n"
" WORK = standard romanized Sanskrit/Pali title of the ORIGINAL work, normalized (中論→Mūlamadhyamakakārikā; 倶舎論/俱舍論→Abhidharmakośabhāṣya; "
"入菩提行論→Bodhicaryāvatāra; 入中論→Madhyamakāvatāra; 大乗荘厳経論→Mahāyānasūtrālaṃkāra; 菩薩地→Bodhisattvabhūmi; 中辺分別論→Madhyāntavibhāga; etc.)\n"
" SCOPE = full (whole work) | partial (a chapter/section/fascicle/selection — note things like 第N章, (1),(2), 章, 品, fragments) | unknown\n"
" TRANSLATOR = Japanese surname(s) if present, else empty.  YEAR = 4-digit if present, else empty.\n"
"If the line is NOT a Japanese translation of an Indian Buddhist work (e.g. study/article about a text, a Chinese/Japanese indigenous "
"work, a sutra known only in Chinese with no Indian original, or unclear), output: N|SKIP\n"
"No commentary, exactly one output line per input line.\nLINES:\n")
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
    body="\n".join(f"{i+1}. {ln}" for i,(ln,c) in enumerate(batch))
    out=call(PROMPT+body); recs=[]
    if not out: return recs
    for l in out.splitlines():
        m=re.match(r"\s*(\d+)\s*\|\s*(.*)",l)
        if not m: continue
        i=int(m.group(1))-1; rest=m.group(2).strip()
        if i<0 or i>=len(batch): continue
        if rest.upper().startswith("SKIP"): continue
        parts=[p.strip() for p in rest.split("|")]
        work=parts[0] if parts else ""
        if not work or work.upper()=="SKIP": continue
        scope=parts[1] if len(parts)>1 else ""
        tr=parts[2] if len(parts)>2 else ""
        yr=parts[3] if len(parts)>3 else ""
        recs.append((work,scope,tr,yr,batch[i][1],batch[i][0]))  # work,scope,tr,yr,count,line
    return recs
if __name__=="__main__":
    data=json.load(open("/tmp/claude-1000/jp_cites.json"))
    batches=[data[i:i+BATCH] for i in range(0,len(data),BATCH)]
    res=[None]*len(batches); done=0; t0=time.time(); lock=threading.Lock()
    with ThreadPoolExecutor(max_workers=W) as ex:
        fut={ex.submit(proc,b):i for i,b in enumerate(batches)}
        for fu in as_completed(fut):
            res[fut[fu]]=fu.result()
            with lock:
                done+=1
                if done%50==0: print(f"  {done}/{len(batches)} {time.time()-t0:.0f}s",flush=True)
    with open("/tmp/claude-1000/jp_trans_records.tsv","w",encoding="utf-8") as f:
        for b in res:
            for work,scope,tr,yr,c,line in (b or []):
                f.write(f"{work}\t{scope}\t{tr}\t{yr}\t{c}\t{line}\n")
    print("done",sum(len(b or []) for b in res),"records",flush=True)
