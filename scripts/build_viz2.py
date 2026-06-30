#!/usr/bin/env python3
"""Rebuild the visualizations: X=year, Y=category band, one dot per individual
translation, coloured full vs partial. Writes viz/{japanese,english}.html."""
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
<div class="sub">each dot = one individual translation · X = year published · Y = doctrinal category · <b style="color:#278063">green</b> = full · <b style="color:#c0852b">orange</b> = partial · dot size ≈ text length · hover for full title & author · drag to zoom
<a class="nav" href="__OTHER__">↔ switch to __OTHERNAME__</a> <a class="nav" href="../index.html">home</a></div>
<input id="search" placeholder="highlight a work, e.g. kośa, prasannapada, laṅkā…"><span id="count"></span></div>
<div id="plot"></div>
<script>
const DATA=__DATA__;
const MAXZ=Math.max(1,...DATA.map(d=>d.z||0));
const dotsize=d=>5+28*Math.sqrt((d.z||0)/MAXZ);
const order={};{let c={};DATA.forEach(d=>c[d.c]=(c[d.c]||0)+1);
 Object.keys(c).sort((a,b)=>c[a]-c[b]).forEach((k,i)=>order[k]=i);}
const CATS=Object.keys(order).sort((a,b)=>order[a]-order[b]);
function rng(s){let x=Math.sin(s*12.9898)*43758.5453;return x-Math.floor(x);}
DATA.forEach((d,i)=>{d.yy=order[d.c]+(rng(i+1)-0.5)*0.7; d.xx=d.y+(rng(i+7)-0.5)*0.6;});
function traces(filter){
 return [["full","rgba(39,128,99,.80)"],["partial","rgba(192,133,43,.70)"]].map(([sc,col])=>{
  const pts=DATA.filter(d=>d.s===sc);
  return {name:sc+" ("+pts.length+")",x:pts.map(d=>d.xx),y:pts.map(d=>d.yy),mode:"markers",type:"scattergl",
   text:pts.map(d=>`<b>${d.w}</b> · ${d.s}<br>${d.c} · ${d.y}`+(d.t?`<br>${d.t}`:"")+(d.a?`<br><i>${d.a}</i>`:"")+(d.z?`<br>~${Math.round(d.z/1000)}k chars`:"")),hoverinfo:"text",
   marker:{size:pts.map(dotsize),sizemode:"diameter",
    color:pts.map(d=>(filter&&!d.w.toLowerCase().includes(filter))?"rgba(210,210,210,.18)":col),
    line:{width:0.5,color:"#fff"},opacity:0.78}};
 });
}
const lay={hovermode:"closest",margin:{l:140,r:20,t:10,b:40},
 xaxis:{title:"year",zeroline:false,gridcolor:"#eee",dtick:20},
 yaxis:{tickmode:"array",tickvals:CATS.map(c=>order[c]),ticktext:CATS,zeroline:false,gridcolor:"#f0f0f0",range:[-0.6,CATS.length-0.4]},
 legend:{orientation:"h",y:1.04},paper_bgcolor:"#fafafa",plot_bgcolor:"#fff"};
Plotly.newPlot("plot",traces(""),lay,{responsive:true});
const n=DATA.length,f=DATA.filter(d=>d.s==="full").length;
document.getElementById("count").textContent=`${n} translations · ${f} full · ${n-f} partial`;
document.getElementById("search").addEventListener("input",e=>{
 const q=e.target.value.trim().toLowerCase();
 Plotly.react("plot",traces(q),lay,{responsive:true});
 document.getElementById("count").textContent=q?`${DATA.filter(d=>d.w.toLowerCase().includes(q)).length} match "${q}"`:`${n} translations · ${f} full · ${n-f} partial`;
});
</script></body></html>"""
def gen(pts,lang,title,other,othername):
    h=(HTML.replace("__TITLE__",title).replace("__DATA__",json.dumps(pts,ensure_ascii=False))
         .replace("__OTHER__",other).replace("__OTHERNAME__",othername))
    open(f"{REPO}/viz/{lang}.html","w",encoding="utf-8").write(h)
gen(ja,"japanese",f"Japanese Translations of Buddhist Works — {len(ja)} translations, 1867–2019","english.html","English")
gen(en,"english",f"English Translations of Buddhist Works — {len(en)} translations, 1867–2019","japanese.html","Japanese")
print(f"JA viz: {len(ja)} dots | EN viz: {len(en)} dots")
