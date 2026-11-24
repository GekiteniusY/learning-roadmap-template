#!/usr/bin/env python3
"""学習ロードマップ HTML ジェネレーター。

使い方: python3 build.py roadmap.json -o roadmap.html
外部ライブラリ不要（Python 3.8+）。
"""
import argparse, html, json, sys

def e(s): return html.escape(str(s), quote=True)

def refs_html(refs):
    out = []
    for r in refs or []:
        t = ' title="%s"' % e(r["title"]) if r.get("title") else ""
        if r.get("url"):
            out.append('<a href="%s" target="_blank" rel="noopener"%s>%s</a>' % (e(r["url"]), t, e(r["label"])))
        else:
            out.append('<code%s>%s</code>' % (t, e(r["label"])))
    return '<span class="ref">' + " ・ ".join(out) + '</span>' if out else ""

def layout(steps):
    ids = [s["id"] for s in steps]
    after = {s["id"]: s.get("after", []) for s in steps}
    for i, a in after.items():
        for p in a:
            if p not in after: sys.exit("step %r: unknown dependency %r" % (i, p))
    layer = {}
    def depth(i, seen=()):
        if i in seen: sys.exit("dependency cycle at %r" % i)
        if i not in layer:
            layer[i] = 1 + max([depth(p, seen + (i,)) for p in after[i]] or [-1])
        return layer[i]
    for i in ids: depth(i)
    cols = {}
    for i in ids: cols.setdefault(layer[i], []).append(i)
    return layer, cols

def build(d):
    steps = d["steps"]
    W, H, GX, GY, PAD = 130, 78, 34, 22, 8
    layer, cols = layout(steps)
    rows = max(len(v) for v in cols.values())
    vh = rows * H + (rows - 1) * GY + 2 * PAD
    pos = {}
    for c, members in cols.items():
        colh = len(members) * H + (len(members) - 1) * GY
        y0 = (vh - colh) / 2
        for k, i in enumerate(members):
            pos[i] = (PAD + c * (W + GX), y0 + k * (H + GY))
    vw = PAD * 2 + (max(cols) + 1) * W + max(cols) * GX
    num = {s["id"]: n for n, s in enumerate(steps, 1)}

    g = []
    def edge(a, b, cls="edge", label=None):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        if layer[a] == layer[b]:  # 同じ列: 縦につなぐ
            top = y1 < y2
            sx, sy = x1 + W / 2, (y1 + H if top else y1)
            ex, ey = x2 + W / 2, (y2 - 4 if top else y2 + H + 4)
            dd = "M%.0f %.0f L%.0f %.0f" % (sx, sy, ex, ey)
            lx, ly = sx + 6, (sy + ey) / 2 + 4
        else:
            sx, sy, ex, ey = x1 + W, y1 + H / 2, x2 - 4, y2 + H / 2
            mx = (sx + ex) / 2
            dd = "M%.0f %.0f C%.0f %.0f %.0f %.0f %.0f %.0f" % (sx, sy, mx, sy, mx, ey, ex, ey)
            lx, ly = mx + 4, (sy + ey) / 2 - 4
        g.append('<path d="%s" class="%s" marker-end="url(#ar)"/>' % (dd, cls))
        if label: g.append('<text x="%.0f" y="%.0f" class="elab">%s</text>' % (lx, ly, e(label)))
    for s in steps:
        for p in s.get("after", []): edge(p, s["id"])
    for x in d.get("extra_edges", []):
        edge(x["from"], x["to"], "edge dash" if x.get("dashed", True) else "edge", x.get("label"))
    for s in steps:
        n = num[s["id"]]; x, y = pos[s["id"]]
        g.append('<a href="#s%d" class="node" data-node="%d"><rect x="%.0f" y="%.0f" width="%d" height="%d" rx="8"/>'
                 '<text x="%.0f" y="%.0f" class="nno">Step %d</text><text x="%.0f" y="%.0f" class="nt">%s</text>'
                 '<text x="%.0f" y="%.0f" class="ns">%s</text>'
                 '<rect x="%.0f" y="%.0f" width="%d" height="5" rx="2.5" class="pbg"/>'
                 '<rect x="%.0f" y="%.0f" width="0" height="5" rx="2.5" class="pfg" data-bar="%d"/>'
                 '<text x="%.0f" y="%.0f" class="npc" data-pc="%d">0/0</text></a>'
                 % (n, n, x, y, W, H, x + 10, y + 17, n, x + 10, y + 37, e(s.get("short", s["title"])),
                    x + 10, y + 53, e(s.get("node_sub", s.get("sub", ""))), x + 10, y + 63, W - 52,
                    x + 10, y + 63, n, x + W - 10, y + 68, n))
    svg = ('<svg viewBox="0 0 %.0f %.0f" role="img" aria-label="%dステップのロードマップ"><defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#8a94a6"/></marker></defs>%s</svg>'
           % (vw, vh, len(steps), "\n".join(g)))

    sec = []
    for s in steps:
        n = num[s["id"]]
        links = s.get("links") or []
        lk = '<p class="reqs">' + "　".join(
            '<span class="rq">%s%s</span>' % (
                '<a href="%s" target="_blank" rel="noopener">%s</a>' % (e(l["url"]), e(l["label"])) if l.get("url") else e(l["label"]),
                (" " + e(l["note"])) if l.get("note") else "") for l in links) + '</p>' if links else ""
        lis = "\n".join('<li><label><input type="checkbox" data-id="s%d-%d"><span class="t">%s</span></label>%s</li>'
                        % (n, j, e(it["text"]), refs_html(it.get("refs"))) for j, it in enumerate(s["items"], 1))
        questions = s.get("mindmap_questions")
        mindmap = ""
        if questions:
            question_items = "\n".join('<li>%s</li>' % e(q) for q in questions)
            mindmap = ('<div class="mindmap"><h3>このステップのマインドマップ</h3>'
                       '<ul>%s</ul></div>' % question_items)
        sec.append('<section id="s%d"><h2><span class="no">%d</span>%s<span class="sub">%s</span><span class="cnt" data-cnt="%d">0/%d</span></h2>%s<ul>%s</ul>%s</section>'
                   % (n, n, e(s["title"]), e(s.get("sub", "")), n, len(s["items"]), lk, lis, mindmap))
    total = sum(len(s["items"]) for s in steps)
    key = d.get("storage_key") or ("learning-roadmap-" + d["title"])
    return (TEMPLATE.replace("@@TITLE@@", e(d["title"])).replace("@@TOTAL@@", str(total))
            .replace("@@SVG@@", svg).replace("@@SEC@@", "\n".join(sec))
            .replace("@@FOOTER@@", e(d.get("footer", "")) + " チェックはこのブラウザに保存されます。")
            .replace("@@KEY@@", json.dumps(key)).replace("@@N@@", str(len(steps))).replace("@@BW@@", str(W - 52)))

TEMPLATE = '''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>@@TITLE@@</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif;color:#1f2937;background:#fff;line-height:1.6}
main{max-width:1060px;margin:0 auto;padding:24px 20px 60px}
h1{font-size:20px;margin:0 0 10px}
.overall{display:flex;align-items:center;gap:12px;margin:0 0 14px;font-size:13px;color:#4b5563}
.bar{flex:1;height:8px;background:#e5e7eb;border-radius:4px;overflow:hidden}
.bar>i{display:block;height:100%;width:0;background:#2563eb;transition:width .2s}
#reset{border:0;background:none;color:#9ca3af;font-size:12px;cursor:pointer;padding:0}
svg{display:block;width:100%;height:auto;margin:0 0 8px}
.node rect:first-child{fill:#f8fafc;stroke:#cbd5e1;stroke-width:1.2}
.node:hover rect:first-child{stroke:#2563eb}
.node.done rect:first-child{fill:#eff6ff;stroke:#2563eb}
.nno{font-size:11px;fill:#6b7280}.nt{font-size:15px;font-weight:700;fill:#111827}.ns{font-size:10.5px;fill:#6b7280}
.npc{font-size:10.5px;fill:#374151;text-anchor:end}
.pbg{fill:#e5e7eb}.pfg{fill:#2563eb}
.edge{fill:none;stroke:#8a94a6;stroke-width:1.5}.dash{stroke-dasharray:4 3}
.elab{font-size:10px;fill:#6b7280}
section{margin-top:26px;scroll-margin-top:12px}
h2{font-size:16px;margin:0 0 4px;display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;border-bottom:1px solid #e5e7eb;padding-bottom:4px}
h2 .no{display:inline-block;min-width:22px;height:22px;line-height:22px;text-align:center;border-radius:11px;background:#1f2937;color:#fff;font-size:12px}
h2 .sub{font-weight:400;font-size:13px;color:#6b7280}
h2 .cnt{margin-left:auto;font-weight:400;font-size:13px;color:#374151}
.rq{white-space:nowrap}.reqs{margin:4px 0 6px;font-size:12.5px;color:#4b5563}
ul{list-style:none;margin:0;padding:0}
li{padding:5px 0;border-bottom:1px dotted #eef0f3;font-size:14px}
li label{cursor:pointer;display:inline}
li input{margin:0 8px 0 0;vertical-align:-2px;width:15px;height:15px;cursor:pointer}
li input:checked+.t{color:#9ca3af;text-decoration:line-through}
.mindmap{margin-top:12px}
.mindmap h3{font-size:14px;margin:0 0 4px}
.mindmap ul{list-style:disc;padding-left:1.5em;color:#4b5563}
.mindmap li{padding:2px 0;border:0}
.ref{margin-left:8px;font-size:11.5px;color:#6b7280}.ref a,.ref code{white-space:nowrap}
.ref a{color:#2563eb;text-decoration:none}.ref a:hover{text-decoration:underline}
.ref code{font-size:11px;background:#f3f4f6;padding:0 3px;border-radius:3px}
a{color:#2563eb}
footer{margin-top:30px;font-size:11.5px;color:#9ca3af}
</style></head><body><main>
<h1>@@TITLE@@</h1>
<div class="overall"><span>全体</span><div class="bar"><i id="ob"></i></div><span id="oc">0/@@TOTAL@@</span><button id="reset" type="button">リセット</button></div>
@@SVG@@
@@SEC@@
<footer>@@FOOTER@@</footer>
</main>
<script>
(function(){
var KEY=@@KEY@@,N=@@N@@,st={};
try{st=JSON.parse(localStorage.getItem(KEY)||"{}")||{}}catch(e){st={}}
var boxes=[].slice.call(document.querySelectorAll('input[type=checkbox][data-id]'));
function save(){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}}
function render(){
 var all=0,on=0;
 for(var n=1;n<=N;n++){
  var bs=boxes.filter(function(b){return b.dataset.id.indexOf("s"+n+"-")===0});
  var c=bs.filter(function(b){return b.checked}).length;all+=bs.length;on+=c;
  document.querySelector('[data-cnt="'+n+'"]').textContent=c+"/"+bs.length;
  document.querySelector('[data-pc="'+n+'"]').textContent=c+"/"+bs.length;
  document.querySelector('[data-bar="'+n+'"]').setAttribute("width",(bs.length?@@BW@@*c/bs.length:0).toFixed(1));
  document.querySelector('[data-node="'+n+'"]').classList.toggle("done",bs.length>0&&c===bs.length);
 }
 document.getElementById("oc").textContent=on+"/"+all;
 document.getElementById("ob").style.width=(all?100*on/all:0)+"%";
}
boxes.forEach(function(b){b.checked=!!st[b.dataset.id];b.addEventListener("change",function(){if(b.checked)st[b.dataset.id]=1;else delete st[b.dataset.id];save();render()})});
document.getElementById("reset").addEventListener("click",function(){if(confirm("チェックをすべて外します。よろしいですか？")){st={};boxes.forEach(function(b){b.checked=false});save();render()}});
render();
})();
</script></body></html>'''

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="学習ロードマップ HTML を生成する")
    ap.add_argument("data", help="ロードマップのデータファイル（JSON）")
    ap.add_argument("-o", "--out", default="roadmap.html")
    a = ap.parse_args()
    d = json.load(open(a.data, encoding="utf-8"))
    open(a.out, "w", encoding="utf-8").write(build(d))
    print("%s: %d steps, %d items" % (a.out, len(d["steps"]), sum(len(s["items"]) for s in d["steps"])))
