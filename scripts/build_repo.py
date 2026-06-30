#!/usr/bin/env python3
"""Assemble the dharmamitra-translation-catalogs repo: JA + EN catalogs (TSV+JSON)
with categories, and a category-stratified Plotly visualization for each."""
import os, re, json, unicodedata
REPO=os.path.expanduser("~/data/dharmamitra-translation-catalogs")
os.makedirs(REPO+"/catalogs",exist_ok=True); os.makedirs(REPO+"/viz",exist_ok=True)
MJ=os.path.expanduser("~/data/dharmanexus-modern-japanese")
def norm(s):
    s=unicodedata.normalize("NFKD",s); s="".join(c for c in s if not unicodedata.combining(c)); return re.sub(r"[^a-z]","",s.lower())
catmap={}
for l in open("/tmp/claude-1000/work_categories.tsv",encoding="utf-8"):
    p=l.rstrip("\n").split("\t")
    if len(p)==2: catmap[p[0]]=p[1]
def category(w): return catmap.get(w,"Other")

# --- Japanese catalog (citation-based + on-drive files) ---
ja=[]
hdr=None
for i,l in enumerate(open(os.path.join(MJ,"japanese_translations_catalog.tsv"),encoding="utf-8")):
    c=l.rstrip("\n").split("\t")
    if i==0: hdr=c; continue
    work=c[0]; full=int(c[2]); part=int(c[3]); sa=c[5]=="yes"
    nfiles=int(c[8]) if len(c)>8 and c[8].isdigit() else 0
    files=c[9] if len(c)>9 else ""
    ja.append({"w":work,"c":category(work),"f":full,"p":part,"s":sa,"nf":nfiles,
               "tr":c[6] if len(c)>6 else "","files":files})
# --- English catalog (file-based) ---
en=[]
for i,l in enumerate(open("/tmp/claude-1000/en_catalog_raw.tsv",encoding="utf-8")):
    c=l.rstrip("\n").split("\t")
    if i==0: continue
    work=c[0]; full=int(c[1]); part=int(c[2]); sa=c[3]=="yes"
    en.append({"w":work,"c":category(work),"f":full,"p":part,"s":sa,"nf":full+part,
               "tr":"","files":c[4] if len(c)>4 else ""})

def write_tsv(rows,path,lang):
    with open(path,"w",encoding="utf-8") as o:
        o.write("work\tcategory\tfull\tpartial\tsanskrit_in_repo\tfiles_on_drive\tpaths\n")
        for r in rows:
            o.write(f"{r['w']}\t{r['c']}\t{r['f']}\t{r['p']}\t{'yes' if r['s'] else 'no'}\t{r['nf']}\t{r['files']}\n")
write_tsv(ja,REPO+"/catalogs/japanese.tsv","ja")
write_tsv(en,REPO+"/catalogs/english.tsv","en")
# slim json for viz (no big path strings)
def slim(rows): return [{"w":r["w"],"c":r["c"],"f":r["f"],"p":r["p"],"s":r["s"]} for r in rows]
json.dump(slim(ja),open(REPO+"/catalogs/japanese.json","w"),ensure_ascii=False)
json.dump(slim(en),open(REPO+"/catalogs/english.json","w"),ensure_ascii=False)

HTML=r"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>__TITLE__</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
 body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#fafafa;color:#1d1d1f}
 #bar{position:sticky;top:0;background:#fff;border-bottom:1px solid #ddd;padding:12px 18px;z-index:10;box-shadow:0 1px 4px rgba(0,0,0,.06)}
 h1{margin:0 0 2px;font-size:19px} .sub{color:#777;font-size:12.5px}
 #search{font-size:15px;padding:8px 12px;width:320px;border:2px solid #2471A3;border-radius:7px;margin-top:8px}
 #count{margin-left:12px;color:#2471A3;font-weight:600}
 #plot{width:100%;height:78vh}
 footer{margin:8px 18px 30px;padding:14px 20px;background:#fff;border:1px solid #e5e5e5;border-radius:10px;color:#555;font-size:13px;line-height:1.6;max-width:1000px}
 footer b{color:#2471A3}
</style></head><body>
<div id="bar"><h1>__TITLE__</h1>
<div class="sub">__SUB__ · hover a dot for details · click a legend category to toggle · larger dot = more translations · <b>green</b> = a full translation exists, <b>grey</b> = partial only · ✦ = Sanskrit original in dharmanexus-sanskrit</div>
<input id="search" placeholder="search a work, e.g. prasannapada, kośa, laṅkā…"><span id="count"></span></div>
<div id="plot"></div>
<footer><b>__TITLE__.</b> Each dot is a Buddhist work, placed in its doctrinal/genre category (Madhyamaka, Yogācāra, Abhidharma, …) and jittered within that column. Mined by Gemini from __SOURCE__. Dot size ∝ number of translations cited/held; colour shows whether a <b>full</b> translation exists. Data: <code>catalogs/__LANG__.tsv</code>.</footer>
<script>
const DATA=__DATA__;
const CATS=[...new Set(DATA.map(d=>d.c))];
// order categories by size desc
const csize={}; DATA.forEach(d=>csize[d.c]=(csize[d.c]||0)+1);
CATS.sort((a,b)=>csize[b]-csize[a]);
const cx={}; CATS.forEach((c,i)=>cx[c]=i);
function rng(seed){let x=Math.sin(seed)*10000;return x-Math.floor(x);}
DATA.forEach((d,i)=>{d.x=cx[d.c]+(rng(i*1.7)-0.5)*0.7; d.y=rng(i*3.1+1);});
function build(filter){
  const traces=CATS.map(cat=>{
    const pts=DATA.filter(d=>d.c===cat);
    return {
      name:cat+" ("+pts.length+")", x:pts.map(d=>d.x), y:pts.map(d=>d.y),
      mode:"markers", type:"scattergl",
      text:pts.map(d=>`<b>${d.w}</b>${d.s?" ✦":""}<br>${d.c}<br>full: ${d.f} · partial: ${d.p}`),
      hoverinfo:"text",
      marker:{
        size:pts.map(d=>Math.max(6,Math.min(34,6+3*Math.sqrt(d.f+d.p)))),
        color:pts.map(d=>{
          if(filter&&!d.w.toLowerCase().includes(filter)) return "rgba(200,200,200,.15)";
          return d.f>0?"rgba(39,128,99,.78)":"rgba(150,150,150,.55)";}),
        line:{width:pts.map(d=>d.s?1.4:0),color:"#2471A3"}
      }
    };
  });
  const lay={hovermode:"closest",showlegend:true,margin:{l:10,r:10,t:10,b:90},
    xaxis:{tickmode:"array",tickvals:CATS.map((c,i)=>i),ticktext:CATS,tickangle:-35,zeroline:false,showgrid:true,gridcolor:"#eee"},
    yaxis:{visible:false,range:[-0.1,1.1]},legend:{orientation:"h",y:-0.18},paper_bgcolor:"#fafafa",plot_bgcolor:"#fff"};
  Plotly.react("plot",traces,lay,{responsive:true,displmodeBar:false});
}
build("");
const tot=DATA.length, full=DATA.filter(d=>d.f>0).length, sa=DATA.filter(d=>d.s).length;
document.getElementById("count").textContent=`${tot} works · ${full} with a full translation · ${sa} with Sanskrit original`;
document.getElementById("search").addEventListener("input",e=>{
  const q=e.target.value.trim().toLowerCase(); build(q);
  if(q){const m=DATA.filter(d=>d.w.toLowerCase().includes(q)).length;
    document.getElementById("count").textContent=`${m} match "${q}"`;}
  else document.getElementById("count").textContent=`${tot} works · ${full} with a full translation · ${sa} with Sanskrit original`;
});
</script></body></html>"""
def gen(rows,lang,title,sub,source):
    h=HTML.replace("__TITLE__",title).replace("__SUB__",sub).replace("__SOURCE__",source).replace("__LANG__",lang).replace("__DATA__",json.dumps(slim(rows),ensure_ascii=False))
    open(f"{REPO}/viz/{lang}.html","w",encoding="utf-8").write(h)
gen(ja,"japanese","Japanese Translations of Buddhist Works",
    f"{len(ja)} works mined from ~7,500 Japanese scholarship files",
    "the bibliographies & titles of the dharmanexus modern-Japanese scholarship corpus (~7,500 files)")
gen(en,"english","English Translations of Buddhist Works",
    f"{len(en)} works mined from ~8,200 English publication files",
    "the buddhist-english-cleaned corpus (~8,200 files)")
print(f"JA catalog: {len(ja)} works | EN catalog: {len(en)} works")
print("repo built at",REPO)
