import base64, hashlib, math
from datetime import datetime

import cv2
import numpy as np
import streamlit as st

from src.recognizer import load_gallery, identify

st.set_page_config(page_title="FaceID Console", page_icon="🧬", layout="wide")

USER = "Admin"                     # greeting name, change it
OK, BAD = "#2fbf71", "#ef5350"
PAL = ["#4a78c8", "#8e6fe0", "#e0708a", "#2fa98c", "#e0a040"]
H = lambda s: "\n".join(l.strip() for l in s.splitlines())   # avoids markdown code-block bug

# ───────────────────────────── styling ─────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
:root{--ink:#1d2b4f;--mut:#7d8cae}
.stApp{background:radial-gradient(900px 520px at 8% 0%,#dae7fc,transparent 70%),radial-gradient(800px 600px at 100% 100%,#d4e0f9,transparent 70%),#f3f6fc}
.stApp,.stApp [data-testid=stMarkdownContainer],.stApp label,.stApp button{font-family:'Poppins',sans-serif!important}
header[data-testid=stHeader]{background:transparent}
[data-testid=stToolbar],[data-testid=stDecoration],footer{display:none!important}
.block-container{padding:1.8rem 2.2rem;max-width:1320px}

/* sidebar */
section[data-testid=stSidebar]{background:linear-gradient(180deg,#fff,#edf3fd);border:0;box-shadow:10px 0 36px -14px rgba(40,70,140,.28)}
section[data-testid=stSidebar] *{color:#26345a}
.brand{display:flex;gap:12px;align-items:center;margin:2px 0 8px}
.logo{width:46px;height:46px;border-radius:15px;display:grid;place-items:center;font-size:22px;background:linear-gradient(145deg,#6ea0f0,#3b66b3);box-shadow:0 10px 18px -6px rgba(59,102,179,.65),inset 0 1px 0 rgba(255,255,255,.45)}
.bt{font-weight:700;font-size:16px;color:var(--ink)!important}.bs{font-size:12px;color:var(--mut)!important}
.sl{font-size:13px;font-weight:600;color:var(--ink)!important;margin:22px 0 8px}
.sh{font-size:12px;color:var(--mut)!important;margin:-4px 0 10px;line-height:1.4}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:26px}
.chips span{font-size:11px;font-weight:500;padding:5px 11px;border-radius:20px;background:#fff;color:#4a78c8!important;box-shadow:0 3px 8px -2px rgba(60,90,170,.2)}
[data-testid=stFileUploader]>div,[data-testid=stFileUploader] section,[data-testid=stFileUploaderDropzone]{background:#f4f8ff!important;border:1.5px dashed #aebfe0!important;border-radius:16px!important}
[data-testid=stFileUploaderFile]{background:#fff!important;border-radius:12px!important;box-shadow:0 4px 10px -4px rgba(60,90,170,.25)}
[data-testid=stFileUploader] small{color:var(--mut)!important}
[data-testid=stFileUploader] button{background:#fff!important;border:1px solid #d3def3!important;border-radius:10px!important}
[data-testid=stSlider] [role=slider]{background:#4a78c8!important;box-shadow:0 4px 10px rgba(74,120,200,.5)!important}
[data-testid=stSliderThumbValue]{color:#4a78c8!important;font-weight:600}

/* cards */
.card,.st-key-scan{background:linear-gradient(180deg,#fff,#f5f8ff);border-radius:28px;padding:22px;box-shadow:0 1px 2px rgba(30,60,120,.06),0 14px 28px -10px rgba(30,60,120,.16),0 36px 64px -24px rgba(30,60,120,.26),inset 0 1px 0 #fff}
.st-key-scan{min-height:640px;padding:24px 22px;justify-content:space-between}
.cardt{font-weight:600;color:#26345a;font-size:15px;margin-bottom:8px}
.card.low{min-height:240px}

/* hero */
.hero{min-height:640px;display:flex;flex-direction:column;border-radius:28px;padding:26px;position:relative;overflow:hidden;
background:radial-gradient(260px 260px at 100% 0,rgba(255,255,255,.8),transparent 70%),linear-gradient(165deg,#bad2f7,#dde9fc 62%,#eef4fe);
box-shadow:0 1px 2px rgba(30,60,120,.06),0 14px 28px -10px rgba(30,60,120,.2),0 36px 64px -24px rgba(30,60,120,.3),inset 0 1px 0 rgba(255,255,255,.8)}
.hero:after{content:"";position:absolute;left:-60px;bottom:-80px;width:320px;height:240px;border-radius:50%;background:radial-gradient(closest-side,rgba(74,120,200,.25),transparent)}
.hero>*{position:relative;z-index:1}
.hi{font-size:28px;font-weight:700;color:var(--ink);line-height:1.2}
.sub{color:#4d7cc7;font-size:13px;font-weight:600;margin-top:6px}
.when{color:var(--mut);font-size:12px;margin-top:2px}
.tiles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:24px 0 18px}
.tile{border-radius:18px;padding:14px 16px;font-size:12px;font-weight:500;color:#51607f;display:flex;flex-direction:column;gap:2px;box-shadow:0 10px 18px -8px rgba(40,70,140,.32),inset 0 1px 0 rgba(255,255,255,.75)}
.tile b{font-size:26px;line-height:1.1;color:var(--ink);font-weight:700}
.t1{background:linear-gradient(120deg,#d1eefe,#d6f6e3)}.t2{background:linear-gradient(120deg,#dedaff,#efdaff)}
.t3{background:linear-gradient(120deg,#ffdfdf,#ffe9d9)}.t4{background:linear-gradient(120deg,#d3e2fb,#c1d6f6)}
.big{margin-top:auto;border-radius:22px;padding:20px 22px;background:linear-gradient(135deg,#8db5f1,#cfe0fb);color:#17305f;font-size:13px;font-weight:500;box-shadow:0 16px 28px -12px rgba(42,79,154,.55),inset 0 1px 0 rgba(255,255,255,.6)}
.big b{display:block;font-size:48px;line-height:1.1;color:#2a4f9a}

/* scan card */
.modal{text-align:center}
.modal .t{font-weight:600;color:#26345a;font-size:15px}
.frame{--c:#2fbf71;--g:rgba(47,191,113,.2);box-sizing:border-box;width:min(232px,100%);aspect-ratio:1;margin:24px auto 18px;border-radius:26px;border:6px solid var(--c);padding:6px;position:relative;overflow:hidden;box-shadow:0 0 0 8px var(--g),0 20px 36px -10px rgba(0,0,0,.3)}
.frame.bad{--c:#ef5350;--g:rgba(239,83,80,.18)}
.frame img{width:100%;height:100%;object-fit:cover;border-radius:16px;display:block}
.frame:after{content:"";position:absolute;left:6px;right:6px;height:3px;background:linear-gradient(90deg,transparent,var(--c),transparent);animation:scan 2.4s ease-in-out infinite}
.frame.empty{--c:#b9c8e6;--g:rgba(185,200,230,.2);border-style:dashed;display:flex;align-items:center;justify-content:center;color:#8b9bc0;font-size:13px;padding:24px;box-shadow:none}
.frame.empty:after{display:none}
@keyframes scan{0%,100%{top:8%}50%{top:90%}}
@media (prefers-reduced-motion:reduce){.frame:after{animation:none}}
.pct{font-size:50px;font-weight:700;color:var(--ink);line-height:1.1}
.done{font-size:13px;color:#51607f;margin:2px 0 10px}
.badge{display:inline-block;padding:6px 18px;border-radius:20px;font-weight:600;font-size:15px}
div.stButton>button{width:100%;border:0;border-radius:14px;padding:.75rem;font-weight:600;background:linear-gradient(180deg,#5b8bdc,#3f6cbc);box-shadow:0 12px 22px -8px rgba(63,108,188,.7),inset 0 1px 0 rgba(255,255,255,.3);transition:transform .15s}
div.stButton>button p{color:#fff!important}
div.stButton>button:hover,div.stButton>button:focus:not(:active){border:0;transform:translateY(-1px)}
div.stButton>button:disabled{background:#cdd8ee;box-shadow:none}

/* detection panel */
.dark{min-height:640px;display:flex;flex-direction:column;border-radius:28px;padding:20px;color:#fff;
background:radial-gradient(420px 320px at 20% 0,#3a84ea,transparent 70%),linear-gradient(170deg,#1b4fa8,#0a2760 70%,#071c47);
box-shadow:0 1px 2px rgba(5,20,60,.2),0 18px 32px -10px rgba(8,34,90,.45),0 40px 70px -26px rgba(8,34,90,.55),inset 0 1px 0 rgba(255,255,255,.18)}
.dh{display:flex;justify-content:space-between;align-items:center;font-weight:600;font-size:15px;margin-bottom:14px}
.dh span{font-size:12px;font-weight:500;padding:4px 12px;border-radius:20px;background:rgba(255,255,255,.14);color:#cfe1ff}
.stage{height:360px;border-radius:20px;display:flex;align-items:center;justify-content:center;overflow:hidden;background:rgba(4,18,52,.5);box-shadow:inset 0 0 40px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.08);color:#b8d2ff;font-size:13px}
.stage img{max-width:100%;max-height:100%;object-fit:contain;display:block}
.dfoot{display:flex;align-items:center;gap:16px;margin-top:auto;padding-top:18px}
.bars{display:flex;align-items:flex-end;gap:3px;height:60px}
.bars i{flex:1;background:linear-gradient(#8fd8ff,#2f78e0);border-radius:3px;box-shadow:0 0 8px rgba(110,190,255,.35)}
.cap{font-size:12px;color:#b8d2ff;margin-top:6px}

/* lists */
.row{display:flex;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid #eaf0fa;font-size:14px;color:#26345a}
.row:last-child{border:0}.row small{color:var(--mut)}
.av{width:36px;height:36px;flex:none;border-radius:50%;display:grid;place-items:center;color:#fff;font-weight:600;box-shadow:0 6px 12px -4px rgba(40,70,140,.4)}
.pill{margin-left:auto;padding:3px 12px;border-radius:20px;font-size:12px;font-weight:600;white-space:nowrap}
.meter{position:relative;height:8px;flex:1;border-radius:8px;background:#e8eefa;box-shadow:inset 0 1px 2px rgba(40,70,140,.18)}
.meter i{display:block;height:100%;border-radius:8px}
.meter u{position:absolute;top:-4px;width:2px;height:16px;border-radius:2px;background:#26345a;opacity:.5}
</style>""", unsafe_allow_html=True)


# ───────────────────────────── helpers ─────────────────────────────
def b64(img, w=900):
    s = w / img.shape[1]
    if s < 1:
        img = cv2.resize(img, None, fx=s, fy=s)
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 88])
    return base64.b64encode(buf).decode()


def crop(img, box, pad=0.3):
    x, y, w, h = box
    px, py = int(w * pad), int(h * pad)
    return img[max(0, y - py): y + h + py, max(0, x - px): x + w + px]


def hud(img, results):
    """Corner-bracket boxes + label pills instead of a plain rectangle."""
    out = img.copy()
    for r in results:
        x, y, w, h = r["box"]
        c = (113, 191, 47) if r["name"] != "Unknown" else (80, 82, 239)   # BGR
        t = max(2, img.shape[1] // 400)
        l = max(14, int(min(w, h) * .22))
        cv2.rectangle(out, (x, y), (x + w, y + h), c, 1, cv2.LINE_AA)
        for px, py, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
            cv2.line(out, (px, py), (px + dx * l, py), c, t + 1, cv2.LINE_AA)
            cv2.line(out, (px, py), (px, py + dy * l), c, t + 1, cv2.LINE_AA)
        label = f'{r["name"]}  {pct(r["score"])}%'
        fs = max(.5, w / 260)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, fs, 2)
        top = max(0, y - th - 14)
        cv2.rectangle(out, (x, top), (x + tw + 14, top + th + 12), c, -1)
        cv2.putText(out, label, (x + 7, top + th + 4), cv2.FONT_HERSHEY_SIMPLEX, fs, (255, 255, 255), 2, cv2.LINE_AA)
    return out


def ring(p, color, size=96):
    r = 44
    c = 2 * math.pi * r
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 120 120" style="flex:none;filter:drop-shadow(0 6px 10px rgba(0,0,0,.35))">'
            f'<circle cx="60" cy="60" r="{r}" stroke="rgba(255,255,255,.18)" stroke-width="9" fill="none"/>'
            f'<circle cx="60" cy="60" r="{r}" stroke="{color}" stroke-width="9" fill="none" stroke-linecap="round" '
            f'stroke-dasharray="{c:.1f}" stroke-dashoffset="{c * (1 - p / 100):.1f}" transform="rotate(-90 60 60)"/>'
            f'<text x="60" y="68" text-anchor="middle" fill="#fff" font-size="24" font-weight="700">{p}%</text></svg>')


def pct(score):
    return int(round(max(0.0, min(1.0, score)) * 100))


def av(name, ok):
    bg = PAL[sum(map(ord, name)) % 5] if ok else "#9aa7c4"
    return f'<div class="av" style="background:{bg}">{name[:1].upper()}</div>'


# ───────────────────────────── state & sidebar ─────────────────────────────
S = st.session_state
for k, v in (("scans", 0), ("rec", 0), ("unk", 0), ("log", []), ("last", None)):
    S.setdefault(k, v)

try:
    gallery = st.cache_resource(load_gallery)()
except FileNotFoundError:
    st.error("gallery.npz not found. Run build_gallery('dataset') first.")
    st.stop()
enrolled = len(set(map(str, gallery[1])))

with st.sidebar:
    st.markdown(H("""<div class="brand"><div class="logo">🧬</div>
        <div><div class="bt">FaceID Console</div><div class="bs">Face access control</div></div></div>"""),
                unsafe_allow_html=True)
    st.markdown('<div class="sl">Input</div>', unsafe_allow_html=True)
    source = st.radio("Source", ["Upload", "Camera"], horizontal=True, label_visibility="collapsed")
    file = (st.file_uploader("Photo", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            if source == "Upload" else st.camera_input("Photo", label_visibility="collapsed"))
    st.markdown('<div class="sl">Match threshold</div>'
                '<div class="sh">Higher is stricter: fewer wrong matches, more missed ones.</div>',
                unsafe_allow_html=True)
    thr = st.slider("Threshold", 0.30, 0.95, 0.342, 0.001, format="%.3f", label_visibility="collapsed")
    st.markdown(f'<div class="chips"><span>Facenet512</span><span>Cosine</span><span>{enrolled} identities</span></div>',
                unsafe_allow_html=True)

img, res = None, []
if file:
    data = file.getvalue()
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    res = identify(img, gallery, thr)
    key = hashlib.md5(data).hexdigest()
    if S.last != key:                      # log once per new photo, not on every slider move
        S.last = key
        S.scans += 1
        for r in res:
            ok = r["name"] != "Unknown"
            S.rec += ok
            S.unk += not ok
            S.log.insert(0, dict(t=datetime.now().strftime("%H:%M:%S"), name=r["name"], p=pct(r["score"]), ok=ok))
        S.log = S.log[:8]

best = max(res, key=lambda r: r["score"]) if res else None
known = bool(best and best["name"] != "Unknown")
color = OK if known else BAD

# ───────────────────────────── layout ─────────────────────────────
c1, c2, c3 = st.columns([1.05, 1, 1.1], gap="large")

with c1:
    now = datetime.now().strftime("%I:%M %p  •  %a, %b %d")
    st.markdown(H(f"""
    <div class="hero">
      <div class="hi">Hi! {USER}</div>
      <div class="sub">Face access control</div>
      <div class="when">{now}</div>
      <div class="tiles">
        <div class="tile t1">Recognized<b>{S.rec}</b></div>
        <div class="tile t2">Unknown<b>{S.unk}</b></div>
        <div class="tile t3">Scans<b>{S.scans}</b></div>
        <div class="tile t4">In frame<b>{len(res)}</b></div>
      </div>
      <div class="big">Enrolled identities<b>{enrolled}</b></div>
    </div>"""), unsafe_allow_html=True)

with c2:
    with st.container(key="scan"):
        if best:
            p = pct(best["score"])
            frame = (f'<div class="frame {"" if known else "bad"}">'
                     f'<img src="data:image/jpeg;base64,{b64(crop(img, best["box"]), 400)}"></div>')
            msg, who = ("Scan is complete!", best["name"]) if known else ("No match found", "Unknown")
            bg = "#dff6e9" if known else "#ffe3e2"
        else:
            frame = '<div class="frame empty">Upload a photo to start a scan</div>'
            p, msg, who, bg = 0, "Waiting for a photo", "Ready", "#e8eefa"
            color = "#7d8cae"
        st.markdown(H(f"""
        <div class="modal">
          <div class="t">Face Recognition</div>
          {frame}
          <div class="pct">{p}%</div>
          <div class="done">{msg}</div>
          <div class="badge" style="background:{bg};color:{color}">{who}</div>
        </div>"""), unsafe_allow_html=True)
        if st.button("Confirm", disabled=not known):
            st.toast(f"Identity confirmed: {best['name']}", icon="✅")

with c3:
    if img is not None:
        stage = f'<img src="data:image/jpeg;base64,{b64(hud(img, res))}">'
    else:
        stage = "Awaiting scan…"
    amp = (pct(best["score"]) / 100) if best else .3
    bars = "".join(f'<i style="height:{14 + 86 * abs(math.sin(i * .7 + 1)) * amp:.0f}%"></i>' for i in range(24))
    st.markdown(H(f"""
    <div class="dark">
      <div class="dh">Detection view<span>{len(res)} face(s)</span></div>
      <div class="stage">{stage}</div>
      <div class="dfoot">
        {ring(pct(best["score"]) if best else 0, color if best else "#7d8cae")}
        <div style="flex:1;min-width:0"><div class="bars">{bars}</div>
        <div class="cap">Best match confidence  •  threshold {thr:.3f}</div></div>
      </div>
    </div>"""), unsafe_allow_html=True)

# ───────────────────────────── bottom row ─────────────────────────────
b1, b2 = st.columns(2, gap="large")

with b1:
    rows = "".join(H(f"""
    <div class="row">{av(e['name'], e['ok'])}
      <div>{e['name']}<br><small>{e['t']}</small></div>
      <div class="pill" style="background:{'#dff6e9' if e['ok'] else '#ffe3e2'};color:{OK if e['ok'] else BAD}">
      {'Recognized' if e['ok'] else 'Unknown'} · {e['p']}%</div></div>""") for e in S.log) \
        or '<div class="row"><small>No scans yet. Results will appear here.</small></div>'
    st.markdown(f'<div class="card low"><div class="cardt">Recent scans</div>{rows}</div>', unsafe_allow_html=True)

with b2:
    rows = "".join(H(f"""
    <div class="row">{av(r['name'], r['name'] != 'Unknown')}
      <div style="min-width:84px">{r['name']}</div>
      <div class="meter"><i style="width:{pct(r['score'])}%;background:{OK if r['name'] != 'Unknown' else BAD}"></i>
      <u style="left:{thr * 100:.1f}%"></u></div>
      <div style="width:42px;text-align:right;font-weight:600">{pct(r['score'])}%</div></div>""")
        for r in sorted(res, key=lambda r: -r["score"])) \
        or '<div class="row"><small>Upload a photo to see each face and its score.</small></div>'
    st.markdown(f'<div class="card low"><div class="cardt">Faces in this photo</div>{rows}'
                f'<div class="cap" style="color:#7d8cae">The dark tick marks the match threshold.</div></div>',
                unsafe_allow_html=True)

# run with:  streamlit run app.py