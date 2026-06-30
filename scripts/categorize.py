import os, re, json, time, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
KEY=os.environ["GEMINI_KEY"]
URL=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={KEY}"
W=12; BATCH=40
CATS="Madhyamaka, Yogacara, Abhidharma, Prajnaparamita, Pramana (logic/epistemology), Tathagatagarbha, Mahayana-sutra, Agama-Nikaya (early/mainstream), Vinaya, Tantra, Avadana-Jataka (narrative), Stotra-Kavya (hymn/poetry), Other"
PROMPT=("Assign each Buddhist work to ONE doctrinal/genre category. Allowed categories EXACTLY: "+CATS+".\n"
"Use the standard scholarly classification of the ORIGINAL Indian work (e.g. Mūlamadhyamakakārikā/Prasannapadā→Madhyamaka; "
"Abhidharmakośabhāṣya/Abhidharmasamuccaya→Abhidharma; Mahāyānasūtrālaṃkāra/Yogācārabhūmi/Madhyāntavibhāga→Yogacara; "
"Aṣṭasāhasrikā/Abhisamayālaṃkāra→Prajnaparamita; Pramāṇavārttika/Nyāyabindu→Pramana; Ratnagotravibhāga→Tathagatagarbha; "
"Laṅkāvatāra/Saṃdhinirmocana→Mahayana-sutra; Dhammapada/Suttanipāta→Agama-Nikaya).\n"
"Output ONE line per input: N|CATEGORY  (category must be one of the allowed names, first word is enough e.g. 'Yogacara').\nWORKS:\n")
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
    out=call(PROMPT+"\n".join(f"{i+1}. {w}" for i,w in enumerate(batch))); res={}
    if not out: return res
    for l in out.splitlines():
        if "|" not in l: continue
        mnum=re.match(r"\s*(\d+)",l)
        if not mnum: continue
        i=int(mnum.group(1))-1
        cm=re.search(r"([A-Za-z][A-Za-z-]+)\s*$", l.split("|")[-1].strip())
        if 0<=i<len(batch) and cm: res[batch[i]]=cm.group(1)
    return res
seed={}
import os
if os.path.exists("/tmp/claude-1000/work_categories.tsv"):
    for l in open("/tmp/claude-1000/work_categories.tsv",encoding="utf-8"):
        p=l.rstrip("\n").split("\t")
        if len(p)==2 and p[1]!="Other": seed[p[0]]=p[1]
allworks=[l.rstrip("\n") for l in open("/tmp/claude-1000/all_works.txt") if l.strip()]
works=[w for w in allworks if w not in seed]
batches=[works[i:i+BATCH] for i in range(0,len(works),BATCH)]
cat={}
with ThreadPoolExecutor(max_workers=W) as ex:
    for fu in as_completed([ex.submit(proc,b) for b in batches]):
        cat.update(fu.result())
cat.update(seed)
with open("/tmp/claude-1000/work_categories.tsv","w",encoding="utf-8") as f:
    for w in allworks: f.write(f"{w}\t{cat.get(w,'Other')}\n")
from collections import Counter
print("categorized",len(cat),"/",len(works))
print(Counter(cat.values()).most_common())
