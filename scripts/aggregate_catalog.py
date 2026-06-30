#!/usr/bin/env python3
"""Aggregate translation records by canonical work, cross-ref dharmanexus-sanskrit,
write the Japanese-translation catalog to ~/data/dharmanexus-modern-japanese/."""
import os, re, json, unicodedata
from collections import defaultdict
SA=os.path.expanduser("~/data/dharmanexus-sanskrit")
OUTDIR=os.path.expanduser("~/data/dharmanexus-modern-japanese")
def norm(s):
    s=unicodedata.normalize("NFKD",s); s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]","",s.lower())
# Sanskrit catalog index
cat=json.load(open(os.path.join(SA,"SA_files.json")))
sa_index=[]
for e in cat:
    for k in (e.get("uniformtitle",""),e.get("displayName","")):
        if k: sa_index.append(norm(k))
sa_set=set(x for x in sa_index if x)
def sa_available(worknorm):
    if len(worknorm)<5: return False
    for sk in sa_set:
        if worknorm==sk or (len(worknorm)>=6 and (worknorm in sk or sk in worknorm)): return True
    return False
# aggregate
agg=defaultdict(lambda:{"disp":{},"full":0,"partial":0,"unknown":0,"count":0,"tr":defaultdict(int),"years":set()})
for ln in open("/tmp/claude-1000/jp_trans_records.tsv",encoding="utf-8"):
    p=ln.rstrip("\n").split("\t")
    if len(p)<6: continue
    work,scope,tr,yr,c,line=p[0],p[1],p[2],p[3],int(p[4]) if p[4].isdigit() else 1,p[5]
    if not work or len(work)<3: continue
    k=norm(work)
    if not k: continue
    a=agg[k]; a["disp"][work]=a["disp"].get(work,0)+c; a["count"]+=c
    s=scope.lower()
    if "full" in s: a["full"]+=1
    elif "partial" in s: a["partial"]+=1
    else: a["unknown"]+=1
    if tr.strip(): a["tr"][tr.strip()]+=c
    m=re.search(r"(19|20)\d\d",yr);  a["years"].add(m.group(0)) if m else None
rows=[]
for k,a in agg.items():
    disp=max(a["disp"].items(),key=lambda x:x[1])[0]
    saok=sa_available(k)
    trs=", ".join(t for t,_ in sorted(a["tr"].items(),key=lambda x:-x[1])[:3])
    yrs=sorted(a["years"]); yr=f"{yrs[0]}-{yrs[-1]}" if len(yrs)>1 else (yrs[0] if yrs else "")
    rows.append((a["count"],disp,a["full"],a["partial"],a["unknown"],saok,trs,yr))
rows.sort(key=lambda r:-r[0])
# TSV
with open(os.path.join(OUTDIR,"japanese_translations_catalog.tsv"),"w",encoding="utf-8") as f:
    f.write("work\tcitations\tfull\tpartial\tunknown\tsanskrit_in_repo\ttranslators\tyears\n")
    for c,d,full,part,unk,sa,tr,yr in rows:
        f.write(f"{d}\t{c}\t{full}\t{part}\t{unk}\t{'yes' if sa else 'no'}\t{tr}\t{yr}\n")
# MD (readable) — works WITH a full translation first
full_works=[r for r in rows if r[2]>0]
part_only=[r for r in rows if r[2]==0 and r[3]>0]
with open(os.path.join(OUTDIR,"japanese_translations_catalog.md"),"w",encoding="utf-8") as f:
    f.write("# Japanese translations of Indian Buddhist works\n\n")
    f.write(f"Mined from bibliographies/titles of {os.path.basename(os.path.dirname(OUTDIR+'/'))} scholarship "
            f"(~7,500 files). {len(rows)} distinct works. 'full' = at least one full-text JA translation cited; "
            "'sa' = Sanskrit original present in dharmanexus-sanskrit. Sorted by citation frequency.\n\n")
    f.write(f"## Works WITH a full Japanese translation ({len(full_works)})\n\n")
    f.write("| Work | cites | #full | #partial | Skt? | translators | years |\n|---|--:|--:|--:|:-:|---|---|\n")
    for c,d,full,part,unk,sa,tr,yr in full_works:
        f.write(f"| {d} | {c} | {full} | {part} | {'✓' if sa else ''} | {tr} | {yr} |\n")
    f.write(f"\n## Works with only PARTIAL Japanese translations ({len(part_only)})\n\n")
    f.write("| Work | cites | #partial | Skt? | translators | years |\n|---|--:|--:|:-:|---|---|\n")
    for c,d,full,part,unk,sa,tr,yr in part_only:
        f.write(f"| {d} | {c} | {part} | {'✓' if sa else ''} | {tr} | {yr} |\n")
print(f"works total={len(rows)} full={len(full_works)} partial_only={len(part_only)}")
print("written to", OUTDIR)
