#!/usr/bin/env python3
"""Visualizations: X=year, Y=doctrinal category band, one dot per individual
translation (volumes/installments collapsed by translator), COLOUR = collection
(text-type), filled=full / open=partial, dot size = total text length."""
import os, json
REPO=os.path.expanduser("~/data/dharmamitra-translation-catalogs")
ja=json.load(open("/tmp/claude-1000/ja_points.json"))
en=json.load(open("/tmp/claude-1000/en_points.json"))

HTML=r"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>__TITLE__</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
 body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#fafafa;color:#1d1d1f}
 #bar{position:sticky;top:0;background:#fff;border-bottom:1px solid #ddd;padding:12px 18px;z-index:10;box-shadow:0 1px 4px rgba(0,0,0,.06)}
 h1{margin:0 0 2px;font-size:19px} .sub{color:#777;font-size:12.5px}
 #search{font-size:15px;padding:8px 12px;width:320px;border:2px solid #2471A3;border-radius:7px;margin-top:8px}
 #count{margin-left:12px;color:#2471A3;font-weight:600}
 a.nav{margin-left:14px;font-size:13px;color:#2471A3;text-decoration:none}
 #plot{width:100%;height:80vh}
</style></head><body>
<div id="bar"><h1>__TITLE__</h1>
<div class="sub">each dot = one translation (volumes/installments merged by translator) · X = year · Y = doctrinal category · <b>colour = collection</b> · <b>●</b> full / <b>○</b> partial · dot size ≈ text length · hover for translator &amp; title
<a class="nav" href="__OTHER__">↔ __OTHERNAME__</a> <a class="nav" href="../index.html">home</a></div>
<input id="search" placeholder="highlight a work, e.g. madhyamaka, kośa, laṅkā…"><span id="count"></span></div>
<div id="plot"></div>
<script>
const DATA=__DATA__;
const MAXZ=Math.max(1,...DATA.map(d=>d.z||0));
const dotsize=d=>6+30*Math.sqrt((d.z||0)/MAXZ);
// Y bands = categories (ordered by count)
const cc={};DATA.forEach(d=>cc[d.c]=(cc[d.c]||0)+1);
const CATS=Object.keys(cc).sort((a,b)=>cc[a]-cc[b]);const order={};CATS.forEach((c,i)=>order[c]=i);
// colours = collections
const COLS=[...new Set(DATA.map(d=>d.k))];
const PAL={"Treatise (śāstra)":"#2471A3","Scripture (sūtra)":"#C0392B","Scripture (āgama/nikāya)":"#E67E22",
 "Poetry / hymn":"#8E44AD","Narrative (avadāna/jātaka)":"#16A085","Tantra":"#B7950B","Vinaya":"#27AE60","Other":"#95A5A6"};
function rng(s){let x=Math.sin(s*12.9898)*43758.5453;return x-Math.floor(x);}
DATA.forEach((d,i)=>{d.yy=order[d.c]+(rng(i+1)-0.5)*0.72; d.xx=d.y+(rng(i+7)-0.5)*0.7;});
function traces(filter){
 return COLS.map(col=>{
  const pts=DATA.filter(d=>d.k===col);
  const dim=d=>filter&&!d.w.toLowerCase().includes(filter);
  return {name:col+" ("+pts.length+")",x:pts.map(d=>d.xx),y:pts.map(d=>d.yy),mode:"markers",type:"scattergl",
   text:pts.map(d=>`<b>${d.w}</b><br>${d.a||"?"} · ${d.y}${d.v>1?" · "+d.v+" vols/parts":""}<br>${d.c} · ${d.k} · ${d.s}${d.sk?" · Skt✦":""}<br>~${Math.round(d.z/1000)}k chars`),
   hoverinfo:"text",
   marker:{size:pts.map(dotsize),sizemode:"diameter",
    symbol:pts.map(d=>d.s==="full"?"circle":"circle-open"),
    color:pts.map(d=>dim(d)?"rgba(210,210,210,.13)":(PAL[col]||"#888")),
    line:{width:pts.map(d=>d.s==="full"?0.5:1.6),color:pts.map(d=>dim(d)?"rgba(210,210,210,.2)":(PAL[col]||"#888"))},
    opacity:0.85}};
 });
}
const lay={hovermode:"closest",margin:{l:150,r:20,t:10,b:40},
 xaxis:{title:"year",zeroline:false,gridcolor:"#eee",dtick:20},
 yaxis:{tickmode:"array",tickvals:CATS.map(c=>order[c]),ticktext:CATS,zeroline:false,gridcolor:"#f0f0f0",range:[-0.6,CATS.length-0.4]},
 legend:{orientation:"h",y:1.05,font:{size:11}},paper_bgcolor:"#fafafa",plot_bgcolor:"#fff"};
Plotly.newPlot("plot",traces(""),lay,{responsive:true});
const n=DATA.length,f=DATA.filter(d=>d.s==="full").length;
const setc=q=>document.getElementById("count").textContent=q?`${DATA.filter(d=>d.w.toLowerCase().includes(q)).length} match "${q}"`:`${n} translations · ${f} full · ${n-f} partial`;
setc("");
document.getElementById("search").addEventListener("input",e=>{const q=e.target.value.trim().toLowerCase();Plotly.react("plot",traces(q),lay,{responsive:true});setc(q);});
</script></body></html>"""
def gen(pts,lang,title,other,othername):
    h=(HTML.replace("__TITLE__",title).replace("__DATA__",json.dumps(pts,ensure_ascii=False))
         .replace("__OTHER__",other).replace("__OTHERNAME__",othername))
    open(f"{REPO}/viz/{lang}.html","w",encoding="utf-8").write(h)
yrs=[p["y"] for p in ja+en]; span=f"{min(yrs)}–{max(yrs)}"
gen(ja,"japanese",f"Japanese Translations of Buddhist Works — {len(ja)} translations, {span}","english.html","English")
gen(en,"english",f"English Translations of Buddhist Works — {len(en)} translations, {span}","japanese.html","Japanese")
print(f"JA viz: {len(ja)} | EN viz: {len(en)} | span {span}")
