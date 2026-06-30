#!/usr/bin/env python3
"""Extract the translator(s) for each English translation file (from its filename),
so multi-volume sets by the same translator can be collapsed into one translation."""
import os, re, json, time, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
KEY=os.environ["GEMINI_KEY"]
URL=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={KEY}"
W=24; BATCH=40
PROMPT=("Each numbered line is the FILENAME of an English translation/edition of a Buddhist text "
"(it usually contains author/translator, title, volume, year). Output the TRANSLATOR/EDITOR surname(s) only.\n"
"Output ONE line per input: N|SURNAMES  (e.g. 'Poussin & Pruden', 'Takasaki', 'Conze', 'Lamotte'). "
"Give the SAME normalized surname string for the same person across volumes (ignore 'vol', 'tr.', initials, year). "
"If no translator is identifiable, output: N|?\nFILES:\n")
def call(p):
    body={"contents":[{"parts":[{"text":p}]}],"generationConfig":{"temperature":0,"thinkingConfig":{"thinkingBudget":0}}}
    for k in range(6):
        try:
            r=json.load(urllib.request.urlopen(urllib.request.Request(URL,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"}),timeout=120))
            return "".join(x.get("text","") for x in r["candidates"][0]["content"]["parts"])
        except Exception:
            if k<5: time.sleep(min(2*(k+1),20)); continue
            return None
def proc(batch):
    out=call(PROMPT+"\n".join(f"{i+1}. {fn}" for i,fn in enumerate(batch))); res={}
    if not out: return res
    for l in out.splitlines():
        m=re.match(r"\s*(\d+)\s*\|\s*(.+)$",l)
        if m:
            i=int(m.group(1))-1
            if 0<=i<len(batch): res[batch[i]]=m.group(2).strip()
    return res
fns=[l.rstrip("\n").split("\t")[2] for l in open("/tmp/claude-1000/en_file_works.tsv",encoding="utf-8")]
fns=list(dict.fromkeys(fns))
batches=[fns[i:i+BATCH] for i in range(0,len(fns),BATCH)]
m={}
with ThreadPoolExecutor(max_workers=W) as ex:
    for fu in as_completed([ex.submit(proc,b) for b in batches]):
        m.update(fu.result())
for fn in fns: m.setdefault(fn,"?")
json.dump(m,open("/tmp/claude-1000/en_translators.json","w"),ensure_ascii=False)
print("translators extracted for",len(m),"files")
PY
