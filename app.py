import streamlit as st
import pandas as pd
import gspread
import time
import os
import base64
import glob
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="IPL Fantasy 2026", layout="wide", page_icon="🏏")

# ── Match labels ──────────────────────────────────────────────────────
MATCH_LABELS = {
    'Match1': 'M1: RCB vs SRH',
    'Match2': 'M2: MI vs KKR',
    'Match3': 'M3: CSK vs RR',
    'Match4': 'M4: PBKS vs GT',
    'Match5': 'M5: DC vs LSG',
    'Match6': 'M6: SRH vs KKR',
}

AVATAR_COLORS = [
    ('#E8C84A', '#E8C84A'), ('#4A90D9', '#4A90D9'), ('#7B61FF', '#7B61FF'),
    ('#FF6B9D', '#FF6B9D'), ('#00E5FF', '#00E5FF'), ('#69F0AE', '#69F0AE'),
    ('#FFB74D', '#FFB74D'), ('#FF5252', '#FF5252'), ('#B388FF', '#B388FF'),
    ('#80CBC4', '#80CBC4'), ('#FFCC02', '#FFCC02'), ('#FF8040', '#FF8040'),
    ('#40C4FF', '#40C4FF'),
]

BAR_COLORS = [
    '#E8C84A','#4A90D9','#7B61FF','#FF6B9D','#00E5FF',
    '#69F0AE','#FFB74D','#FF5252','#B388FF','#80CBC4',
    '#FFCC02','#FF8040','#40C4FF',
]

# ── Load slideshow images from folder ─────────────────────────────────
def load_slideshow_images():
    """Load all jpg/png from slideshow_images/ folder next to app.py"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(script_dir, 'slideshow_images')
    if not os.path.isdir(folder):
        return []
    patterns = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    files = []
    for pat in patterns:
        files.extend(glob.glob(os.path.join(folder, pat)))
    files = sorted(set(files))
    b64_list = []
    for fpath in files:
        ext = os.path.splitext(fpath)[1].lower()
        mime = 'image/png' if ext == '.png' else 'image/jpeg'
        with open(fpath, 'rb') as fh:
            b64 = base64.b64encode(fh.read()).decode()
        b64_list.append(f'data:{mime};base64,{b64}')
    return b64_list

SLIDESHOW_IMAGES = load_slideshow_images()

# ── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=DM+Sans:wght@400;500&display=swap');

@keyframes floodlight-pulse {
  0%,100% { opacity: 0.06; }
  50%      { opacity: 0.13; }
}
@keyframes star-twinkle {
  0%,100% { opacity: 0.4; }
  50%      { opacity: 0.9; }
}
@keyframes crowd-sway {
  0%,100% { transform: translateY(0px); }
  50%      { transform: translateY(-3px); }
}
@keyframes pulse-gold {
  0%,100% { box-shadow: 0 0 24px rgba(255,213,79,0.18), 0 8px 32px rgba(0,0,0,0.4); }
  50%      { box-shadow: 0 0 44px rgba(255,213,79,0.32), 0 8px 32px rgba(0,0,0,0.4); }
}
@keyframes shimmer {
  0%   { background-position: -600px 0; }
  100% { background-position: 600px 0; }
}
@keyframes float-up {
  0%   { opacity:0; transform:translateY(14px); }
  100% { opacity:1; transform:translateY(0); }
}
@keyframes dot-ping {
  0%   { transform:scale(1.4); opacity:0.8; }
  70%  { transform:scale(2.4); opacity:0; }
  100% { transform:scale(2.4); opacity:0; }
}

/* ── Page base ── */
[data-testid="stAppViewContainer"] {
    background: #050A1E !important;
    position: relative;
    font-family: 'DM Sans', system-ui, sans-serif !important;
}
[data-testid="stHeader"] { background: transparent !important; z-index: 10; }
[data-testid="block-container"] { padding-top: 0 !important; position: relative; z-index: 2; }

/* ── Background layer ── */
.stadium-bg {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
}
.stadium-bg svg { width: 100%; height: 100%; }

.scroll-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(180deg,
        rgba(4,8,26,0.48) 0%,
        rgba(4,8,26,0.65) 42%,
        rgba(4,8,26,0.93) 78%,
        rgba(4,8,26,0.99) 100%);
    z-index: 1;
    pointer-events: none;
}

/* ── Typography ── */
body, p, span, div, label, td, th { color: #C8D4F0 !important; }

/* ── Streamlit tabs — pill style ── */
[data-testid="stTabs"] {
    background: rgba(6,11,35,0.60) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    padding: 4px !important;
}
[data-testid="stTabs"] button {
    color: #7A90BC !important;
    font-weight: 500 !important;
    background: transparent !important;
    border: none !important;
    border-radius: 9px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stTabs"] button:hover {
    color: #A8C0E0 !important;
    background: rgba(255,255,255,0.04) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #FFD54F !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, rgba(255,213,79,0.13), rgba(255,213,79,0.06)) !important;
    box-shadow: inset 0 1px 0 rgba(255,213,79,0.22), 0 1px 8px rgba(0,0,0,0.3) !important;
}
[data-testid="stTabs"] [role="tablist"] { border-bottom: none !important; gap: 2px !important; }

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: linear-gradient(135deg, rgba(10,16,48,0.88), rgba(6,10,32,0.92)) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    color: #C8D4F0 !important;
    border-radius: 10px !important;
    backdrop-filter: blur(14px);
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.07) !important; }
[data-testid="stDataFrame"] thead tr th {
    background: rgba(10,16,48,0.9) !important;
    color: #FFD54F !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stDataFrame"] tbody tr td {
    background: rgba(8,12,38,0.82) !important;
    color: #C8D4F0 !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
    font-size: 13px !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background: rgba(14,22,60,0.92) !important;
}

/* ── Button ── */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, rgba(14,22,60,0.88), rgba(8,14,42,0.92)) !important;
    color: #FFD54F !important;
    border: 1px solid rgba(255,213,79,0.25) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(12px);
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stButton"] button:hover {
    border-color: rgba(255,213,79,0.55) !important;
    box-shadow: 0 0 16px rgba(255,213,79,0.15) !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Header ── */
.stadium-header { padding: 2rem 0 1rem; text-align: center; animation: float-up 0.6s ease both; }
.big-title {
    font-family: 'Sora', sans-serif !important;
    font-size: 34px; font-weight: 800; color: #FFD54F !important;
    text-shadow: 0 0 40px rgba(255,213,79,0.5), 0 2px 12px rgba(0,0,0,0.8);
    letter-spacing: 0.01em; margin-bottom: 4px;
}
.subtitle {
    font-size: 13px; color: #8FA8D0 !important;
    letter-spacing: 0.04em; margin-bottom: 0;
}

/* ── Section label with line ── */
.section-label-wrap {
    display: flex; align-items: center; gap: 10px;
    margin: 1.2rem 0 0.6rem;
}
.section-label {
    font-size: 10px; font-weight: 700; color: #6880AA !important;
    text-transform: uppercase; letter-spacing: 0.12em;
    white-space: nowrap;
}
.section-line {
    flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(104,128,170,0.3), transparent);
}

.divider { border: none; border-top: 1px solid rgba(255,255,255,0.07); margin: 1.2rem 0; }

/* ── Podium ── */
.podium-wrap { display: flex; gap: 12px; margin-bottom: 1.5rem; animation: float-up 0.6s 0.08s ease both; }
.podium-card {
    flex: 1; border-radius: 18px; padding: 20px 14px 16px; text-align: center;
    background: linear-gradient(145deg, rgba(10,16,48,0.84), rgba(6,10,32,0.90));
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    border: 1px solid rgba(255,255,255,0.08);
    position: relative; overflow: hidden;
    transition: transform 0.25s ease;
}
.podium-card:hover { transform: translateY(-3px); }
/* shimmer top-edge line */
.podium-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.22) 50%, transparent 100%);
}

/* Gold card */
.podium-gold {
    border-color: rgba(255,213,79,0.42) !important;
    animation: pulse-gold 3.5s ease-in-out infinite;
}
.podium-gold::before {
    background: linear-gradient(90deg, transparent 0%, rgba(255,213,79,0.55) 50%, transparent 100%) !important;
}
.podium-gold::after {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(105deg, transparent 30%, rgba(255,213,79,0.05) 50%, transparent 70%);
    background-size: 600px 100%;
    animation: shimmer 3.5s linear infinite;
}

/* Silver card */
.podium-silver { border-color: rgba(180,190,220,0.28) !important; }
.podium-silver::before {
    background: linear-gradient(90deg, transparent 0%, rgba(180,190,220,0.35) 50%, transparent 100%) !important;
}

/* Bronze card */
.podium-bronze { border-color: rgba(200,130,60,0.32) !important; }
.podium-bronze::before {
    background: linear-gradient(90deg, transparent 0%, rgba(200,130,60,0.38) 50%, transparent 100%) !important;
}

.podium-medal     { font-size: 28px; margin-bottom: 6px; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.5)); }
.podium-rank-lbl  { font-size: 9px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: rgba(200,212,240,0.38) !important; margin-bottom: 4px; }
.podium-name      { font-family: 'Sora', sans-serif; font-size: 15px; font-weight: 700; color: #D8E4F8 !important; }
.podium-pts       { font-family: 'Sora', sans-serif; font-size: 28px; font-weight: 800; margin-top: 8px; line-height: 1; }
.podium-pts-lbl   { font-size: 9px; color: rgba(200,212,240,0.32) !important; letter-spacing: 0.08em; margin-top: 2px; }
.podium-delta     { font-size: 11px; font-weight: 600; margin-top: 8px; padding: 3px 10px; border-radius: 20px; display: inline-block; }

/* ── Leaderboard rows ── */
.lb-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 14px; border-radius: 12px; margin-bottom: 5px;
    background: linear-gradient(135deg, rgba(8,14,42,0.75), rgba(6,10,34,0.82));
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.06);
    position: relative; overflow: hidden;
    transition: all 0.2s ease;
}
.lb-row:hover {
    background: linear-gradient(135deg, rgba(12,20,56,0.88), rgba(8,14,44,0.94));
    border-color: rgba(255,255,255,0.12);
    transform: translateX(3px);
}
/* left accent bar */
.lb-row::before {
    content: '';
    position: absolute; left: 0; top: 22%; bottom: 22%;
    width: 2px; border-radius: 1px;
    opacity: 0.65;
}
.lb-rank   {
    font-family: 'Sora', sans-serif;
    font-size: 11px; font-weight: 600; color: #6880AA !important;
    width: 20px; text-align: center; flex-shrink: 0;
}
.lb-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Sora', sans-serif;
    font-size: 10px; font-weight: 700; flex-shrink: 0;
}
.lb-name   { font-size: 13px; font-weight: 500; color: #D0DCEE !important; flex: 1; }
.lb-bar-wrap { flex: 2; height: 3px; background: rgba(255,255,255,0.06); border-radius: 2px; overflow: hidden; }
.lb-bar    { height: 3px; border-radius: 2px; }
.lb-pts    { font-family: 'Sora', sans-serif; font-size: 13px; font-weight: 700; min-width: 70px; text-align: right; }

/* ── Match day cards ── */
.mgr-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-bottom: 1rem; }
.mgr-card {
    background: linear-gradient(145deg, rgba(10,16,48,0.84), rgba(6,10,32,0.90));
    backdrop-filter: blur(16px);
    border-radius: 14px; padding: 14px 16px;
    border: 1px solid rgba(255,255,255,0.08);
    position: relative; overflow: hidden;
}
.mgr-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.2) 50%, transparent 100%);
}
.mgr-card-rank { font-size: 10px; color: #6880AA !important; margin-bottom: 4px; letter-spacing: 0.08em; }
.mgr-card-name { font-family: 'Sora', sans-serif; font-size: 13px; font-weight: 700; color: #D0DCEE !important; }
.mgr-card-pts  { font-family: 'Sora', sans-serif; font-size: 22px; font-weight: 800; color: #FFD54F !important; margin-top: 4px; }

/* ── Player table ── */
.player-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.player-table tr { border-bottom: 1px solid rgba(255,255,255,0.05); }
.player-table tr:last-child { border-bottom: none; }
.player-table td { padding: 8px 6px; color: #C8D4F0 !important; }
.role-c     { background: rgba(255,213,79,0.14); color: #FFD54F !important; font-size: 10px; padding: 2px 8px; border-radius: 6px; white-space: nowrap; border: 1px solid rgba(255,213,79,0.25); }
.role-vc    { background: rgba(74,144,217,0.14); color: #7AB8F5 !important; font-size: 10px; padding: 2px 8px; border-radius: 6px; white-space: nowrap; border: 1px solid rgba(74,144,217,0.25); }
.role-bench { background: rgba(255,255,255,0.05); color: #6880AA !important; font-size: 10px; padding: 2px 8px; border-radius: 6px; white-space: nowrap; }
.pts-pos { color: #69F0AE !important; font-weight: 700; }
.pts-neg { color: #FF5252 !important; font-weight: 700; }
.pts-zero{ color: #3A4A7A !important; }

/* ── Trend bars ── */
.trend-row { display: flex; align-items: center; gap: 8px; margin-bottom: 7px; }
.trend-label { font-size: 11px; color: #6880AA !important; width: 58px; flex-shrink: 0; }
.trend-bar-bg { flex: 1; height: 4px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; }
.trend-bar-fg { height: 4px; border-radius: 3px; }
.trend-val { font-family: 'Sora', sans-serif; font-size: 12px; font-weight: 600; width: 50px; text-align: right; flex-shrink: 0; }

/* ── Roster header ── */
.roster-header {
    display:flex; align-items:center; gap:14px; margin-bottom:1.2rem;
    background: linear-gradient(145deg, rgba(10,16,48,0.84), rgba(6,10,32,0.90));
    backdrop-filter: blur(16px);
    border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:18px;
    position: relative; overflow: hidden;
}
.roster-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.2) 50%, transparent 100%);
}
.roster-av   { width:50px; height:50px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-family:'Sora',sans-serif; font-size:16px; font-weight:700; border: 2px solid; }
.roster-name { font-family:'Sora',sans-serif; font-size:19px; font-weight:700; color:#FFD54F !important; }
.roster-sub  { font-size:12px; color:#6880AA !important; margin-top:2px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(4,8,24,0.92) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
    backdrop-filter: blur(20px) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Background: slideshow or SVG stadium ─────────────────────────────
if SLIDESHOW_IMAGES:
    images_js = '[' + ','.join(f'"{img}"' for img in SLIDESHOW_IMAGES) + ']'
    bg_html = f"""
<div class="stadium-bg" id="stadium-bg-container">
  <div id="slide-a" style="position:absolute;inset:0;background-size:cover;background-position:center;transition:opacity 1.6s ease;"></div>
  <div id="slide-b" style="position:absolute;inset:0;background-size:cover;background-position:center;opacity:0;transition:opacity 1.6s ease;"></div>
</div>
<div class="scroll-overlay"></div>
<script>
(function(){{
  var images = {images_js};
  var INTERVAL = 5000;
  var slideA = document.getElementById('slide-a');
  var slideB = document.getElementById('slide-b');
  if (!slideA || images.length === 0) return;
  var current = 0, showingA = true;
  slideA.style.backgroundImage = 'url(' + images[0] + ')';
  slideA.style.opacity = '1';
  setInterval(function() {{
    var next = (current + 1) % images.length;
    var inc = showingA ? slideB : slideA;
    var out = showingA ? slideA : slideB;
    inc.style.backgroundImage = 'url(' + images[next] + ')';
    inc.style.opacity = '1';
    out.style.opacity = '0';
    showingA = !showingA;
    current = next;
  }}, INTERVAL);
}})();
</script>"""
else:
    bg_html = """
<div class="stadium-bg" id="stadium-bg-container">
<svg id="cricket-svg" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="sky-grad" cx="50%" cy="0%" r="80%">
      <stop offset="0%" stop-color="#0D1E5A"/><stop offset="100%" stop-color="#020714"/>
    </radialGradient>
    <radialGradient id="field-glow" cx="50%" cy="85%" r="70%">
      <stop offset="0%" stop-color="#2ECC40" stop-opacity="0.28"/>
      <stop offset="50%" stop-color="#1A7A1A" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#051008" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="field-centre" cx="50%" cy="100%" r="40%">
      <stop offset="0%" stop-color="#3DDB50" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#3DDB50" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="fl-left" cx="2%" cy="0%" r="90%">
      <stop offset="0%" stop-color="#FFFDE7" stop-opacity="0.28"/><stop offset="100%" stop-color="#FFFDE7" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="fl-right" cx="98%" cy="0%" r="90%">
      <stop offset="0%" stop-color="#FFFDE7" stop-opacity="0.28"/><stop offset="100%" stop-color="#FFFDE7" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1440" height="900" fill="url(#sky-grad)"/>
  <circle cx="72" cy="38" r="1.8" fill="white" opacity="0.7" style="animation:star-twinkle 2.1s infinite"/>
  <circle cx="280" cy="55" r="2.2" fill="white" opacity="0.8" style="animation:star-twinkle 2.7s infinite 1.2s"/>
  <circle cx="640" cy="12" r="2" fill="white" opacity="0.9" style="animation:star-twinkle 3.1s infinite 0.9s"/>
  <circle cx="990" cy="15" r="2.2" fill="white" opacity="0.8" style="animation:star-twinkle 2.9s infinite 1.5s"/>
  <circle cx="1220" cy="32" r="1.8" fill="white" opacity="0.7" style="animation:star-twinkle 3.5s infinite 1.1s"/>
  <path d="M0 340 Q90 270 200 285 Q310 255 420 272 Q490 248 545 265 L545 900 L0 900 Z" fill="#060C1C"/>
  <circle cx="90" cy="307" r="3" fill="#4488FF" opacity="0.8" style="animation:crowd-sway 3.3s infinite 0.3s"/>
  <circle cx="165" cy="293" r="3" fill="#FF6B9D" opacity="0.8" style="animation:crowd-sway 3.5s infinite 0.9s"/>
  <circle cx="240" cy="277" r="3" fill="#69F0AE" opacity="0.8" style="animation:crowd-sway 3.8s infinite 0.5s"/>
  <circle cx="315" cy="260" r="3" fill="#B388FF" opacity="0.8" style="animation:crowd-sway 3.2s infinite 0.1s"/>
  <circle cx="390" cy="244" r="3" fill="#4488FF" opacity="0.8" style="animation:crowd-sway 3.1s infinite 0.7s"/>
  <path d="M895 265 Q960 248 1050 255 Q1160 248 1270 272 Q1370 285 1440 340 L1440 900 L895 900 Z" fill="#060C1C"/>
  <circle cx="978" cy="246" r="3" fill="#FF4444" opacity="0.8" style="animation:crowd-sway 2.7s infinite 0.7s"/>
  <circle cx="1054" cy="246" r="3" fill="#B388FF" opacity="0.8" style="animation:crowd-sway 3.9s infinite 0.6s"/>
  <circle cx="1130" cy="259" r="3" fill="#69F0AE" opacity="0.8" style="animation:crowd-sway 3.3s infinite 0.8s"/>
  <circle cx="1206" cy="271" r="3" fill="#00E5FF" opacity="0.8" style="animation:crowd-sway 3.7s infinite 0.5s"/>
  <rect x="20" y="70" width="16" height="220" fill="#0E1830" rx="3"/>
  <rect x="4" y="60" width="48" height="22" fill="#1C2D55" rx="4"/>
  <circle cx="13" cy="68" r="7" fill="white" opacity="0.95"/>
  <circle cx="28" cy="68" r="7" fill="white" opacity="0.95"/>
  <circle cx="43" cy="68" r="7" fill="white" opacity="0.95"/>
  <rect x="1404" y="70" width="16" height="220" fill="#0E1830" rx="3"/>
  <rect x="1388" y="60" width="48" height="22" fill="#1C2D55" rx="4"/>
  <circle cx="1397" cy="68" r="7" fill="white" opacity="0.95"/>
  <circle cx="1412" cy="68" r="7" fill="white" opacity="0.95"/>
  <circle cx="1427" cy="68" r="7" fill="white" opacity="0.95"/>
  <path d="M28 90 L480 900 L0 900 Z" fill="url(#fl-left)" style="animation:floodlight-pulse 4s ease-in-out infinite"/>
  <path d="M1412 90 L960 900 L1440 900 Z" fill="url(#fl-right)" style="animation:floodlight-pulse 4s ease-in-out infinite 1s"/>
  <rect x="0" y="500" width="1440" height="400" fill="#0D2E0D"/>
  <rect x="0" y="500" width="103" height="400" fill="#12400F" opacity="0.95"/>
  <rect x="103" y="500" width="103" height="400" fill="#0F3A0C" opacity="0.95"/>
  <rect x="206" y="500" width="103" height="400" fill="#164A12" opacity="0.95"/>
  <rect x="309" y="500" width="103" height="400" fill="#0F3A0C" opacity="0.95"/>
  <rect x="412" y="500" width="103" height="400" fill="#164A12" opacity="0.95"/>
  <rect x="515" y="500" width="103" height="400" fill="#0F3A0C" opacity="0.95"/>
  <rect x="618" y="500" width="103" height="400" fill="#164A12" opacity="0.95"/>
  <rect x="721" y="500" width="103" height="400" fill="#0F3A0C" opacity="0.95"/>
  <rect x="824" y="500" width="103" height="400" fill="#164A12" opacity="0.95"/>
  <rect x="927" y="500" width="103" height="400" fill="#0F3A0C" opacity="0.95"/>
  <rect x="1030" y="500" width="103" height="400" fill="#164A12" opacity="0.95"/>
  <rect x="1133" y="500" width="103" height="400" fill="#0F3A0C" opacity="0.95"/>
  <rect x="1236" y="500" width="103" height="400" fill="#164A12" opacity="0.95"/>
  <rect x="1339" y="500" width="101" height="400" fill="#0F3A0C" opacity="0.95"/>
  <rect x="0" y="500" width="1440" height="400" fill="url(#field-glow)"/>
  <rect x="0" y="500" width="1440" height="400" fill="url(#field-centre)"/>
  <line x1="0" y1="503" x2="1440" y2="503" stroke="white" stroke-width="3" stroke-dasharray="18 12" opacity="0.55"/>
  <rect x="648" y="520" width="144" height="72" rx="5" fill="#B8926A" opacity="0.55"/>
  <line x1="648" y1="535" x2="792" y2="535" stroke="white" stroke-width="1.5" opacity="0.35"/>
  <line x1="648" y1="577" x2="792" y2="577" stroke="white" stroke-width="1.5" opacity="0.35"/>
</svg>
</div>
<div class="scroll-overlay"></div>"""

st.markdown(bg_html, unsafe_allow_html=True)


# ── Data loading ──────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_data():
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        if os.path.exists('service_account.json'):
            creds = Credentials.from_service_account_file('service_account.json', scopes=scopes)
        elif os.path.exists('fantasy-ipl/service_account.json'):
            creds = Credentials.from_service_account_file('fantasy-ipl/service_account.json', scopes=scopes)
        else:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sh = client.open_by_key('138qxoRKnz3Aw7LKnxO3_ZiwXPq4qQLnXe2VkavUqPyM')
        all_data = []
        for ws in sh.worksheets():
            if ws.title == 'Master_Roster':
                continue
            time.sleep(1.5)
            records = ws.get_all_records()
            for row in records:
                if not row.get('PlayerName'):
                    continue
                entry = {
                    'Owner':         ws.title.strip(),
                    'PlayerName':    row.get('PlayerName', ''),
                    'Multiplier':    row.get('Multiplier', 1.0),
                    'CurrentPoints': row.get('CurrentPoints', 0.0),
                }
                for mk in MATCH_LABELS:
                    entry[mk] = row.get(mk, 0.0)
                all_data.append(entry)
        return pd.DataFrame(all_data)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


def initials(name):
    parts = name.strip().split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else name[:2].upper()

def role_badge(mult):
    if mult == 2.0: return '<span class="role-c">⚡ C</span>'
    if mult == 1.5: return '<span class="role-vc">🔵 VC</span>'
    if mult == 0.5: return '<span class="role-bench">🪑 Bench</span>'
    return '<span style="color:#3A4A7A;font-size:11px">—</span>'

def pts_cls(v):
    if v > 0: return 'pts-pos'
    if v < 0: return 'pts-neg'
    return 'pts-zero'

def hex_to_rgba(hex_col, alpha):
    h = hex_col.lstrip('#')
    r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f'rgba({r},{g},{b},{alpha})'

def sec_label(text):
    return f'<div class="section-label-wrap"><span class="section-label">{text}</span><div class="section-line"></div></div>'


# ── Load data ─────────────────────────────────────────────────────────
df = get_data()
if df.empty:
    st.warning("No data found.")
    st.stop()

for col in ['CurrentPoints', 'Multiplier'] + list(MATCH_LABELS.keys()):
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

active_matches = [mk for mk in MATCH_LABELS if mk in df.columns and df[mk].abs().sum() > 0]
latest_match   = active_matches[-1] if active_matches else None

lb = df.groupby('Owner')['CurrentPoints'].sum().sort_values(ascending=False).reset_index()
lb.columns = ['Manager', 'Total']
max_pts        = lb['Total'].max()
owners_ordered = lb['Manager'].tolist()

# ── Header ────────────────────────────────────────────────────────────
n = len(active_matches)
st.markdown(f"""
<div class="stadium-header">
  <div class="big-title">🏏 IPL Fantasy 2026</div>
  <div class="subtitle">{n} match{"es" if n!=1 else ""} played &nbsp;·&nbsp; Season standings</div>
</div>
""", unsafe_allow_html=True)

medals      = ['🥇', '🥈', '🥉']
place_label = ['1st place', '2nd place', '3rd place']

tab1, tab2, tab3 = st.tabs(["🏆  Leaderboard", "📅  Match Day", "📋  Rosters"])

# ══════════════════════════════════════════════════════════════════════
# TAB 1 — LEADERBOARD
# ══════════════════════════════════════════════════════════════════════
with tab1:
    top3 = lb.head(3)

    def last_delta(manager):
        if not latest_match: return 0.0
        return round(df[df['Owner'] == manager][latest_match].sum(), 2)

    # Podium: silver(1) · gold(0) · bronze(2)
    order = [1, 0, 2] if len(top3) >= 3 else list(range(len(top3)))
    podium_html = '<div class="podium-wrap">'
    for pos in order:
        if pos >= len(top3): continue
        row   = top3.iloc[pos]
        delta = last_delta(row['Manager'])
        d_str = f'+{delta:.1f}' if delta >= 0 else f'{delta:.1f}'

        if pos == 0:   # gold
            card_cls  = 'podium-gold'
            name_col  = '#FFD54F'
            pts_col   = '#FFD54F'
            delta_cls = 'pod-delta-g'
            delta_sty = 'background:rgba(105,240,174,0.12);color:#69F0AE;border:1px solid rgba(105,240,174,0.22)'
            pts_lbl_col = 'rgba(255,213,79,0.38)'
        elif pos == 1: # silver
            card_cls  = 'podium-silver'
            name_col  = '#D0DCEE'
            pts_col   = '#C8D4EC'
            delta_sty = 'background:rgba(160,180,220,0.10);color:#9AAAC0;border:1px solid rgba(160,180,220,0.18)'
            pts_lbl_col = 'rgba(200,212,240,0.32)'
        else:          # bronze
            card_cls  = 'podium-bronze'
            name_col  = '#D0DCEE'
            pts_col   = '#D4894A'
            delta_sty = 'background:rgba(200,120,60,0.10);color:#C07040;border:1px solid rgba(200,120,60,0.20)'
            pts_lbl_col = 'rgba(200,212,240,0.32)'

        podium_html += f"""
        <div class="podium-card {card_cls}">
          <div class="podium-medal">{medals[pos]}</div>
          <div class="podium-rank-lbl">{place_label[pos]}</div>
          <div class="podium-name" style="color:{name_col}">{row['Manager']}</div>
          <div class="podium-pts" style="color:{pts_col}">{row['Total']:.1f}</div>
          <div class="podium-pts-lbl" style="color:{pts_lbl_col}">points</div>
          <div class="podium-delta" style="{delta_sty}">{d_str} last match</div>
        </div>"""
    podium_html += '</div>'
    st.markdown(podium_html, unsafe_allow_html=True)

    st.markdown(sec_label('All managers'), unsafe_allow_html=True)

    lb_html = ''
    for i, row in lb.iterrows():
        col_hex = BAR_COLORS[i % len(BAR_COLORS)]
        av_rgba_bg  = hex_to_rgba(col_hex, 0.16)
        av_rgba_bdr = hex_to_rgba(col_hex, 0.42)
        bar_pct = round((row['Total'] / max_pts) * 100) if max_pts > 0 else 0
        lb_html += f"""
        <div class="lb-row" style="--accent:{col_hex}">
          <style>.lb-row:nth-child({i+1})::before{{background:{col_hex};}}</style>
          <span class="lb-rank">{i+1}</span>
          <div class="lb-avatar" style="background:{av_rgba_bg};color:{col_hex};border:1px solid {av_rgba_bdr}">{initials(row['Manager'])}</div>
          <span class="lb-name">{row['Manager']}</span>
          <div class="lb-bar-wrap"><div class="lb-bar" style="width:{bar_pct}%;background:linear-gradient(90deg,{col_hex}88,{col_hex})"></div></div>
          <span class="lb-pts" style="color:{col_hex}">{row['Total']:.2f}</span>
        </div>"""
    st.markdown(lb_html, unsafe_allow_html=True)

    if active_matches:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(sec_label('Per-match breakdown'), unsafe_allow_html=True)
        breakdown = lb.copy()
        for mk in active_matches:
            breakdown[MATCH_LABELS[mk]] = breakdown['Manager'].map(
                df.groupby('Owner')[mk].sum()).round(2)
        fmt = {'Total': '{:.2f}'}
        fmt.update({MATCH_LABELS[mk]: '{:.2f}' for mk in active_matches})
        st.dataframe(breakdown.style.format(fmt), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 2 — MATCH DAY
# ══════════════════════════════════════════════════════════════════════
with tab2:
    if not active_matches:
        st.info("No match data yet.")
    else:
        selected = st.selectbox(
            "Select match", active_matches,
            index=len(active_matches)-1,
            format_func=lambda x: MATCH_LABELS[x]
        )
        mgr_match = df.groupby('Owner')[selected].sum().sort_values(ascending=False).reset_index()
        mgr_match.columns = ['Manager', 'Points']

        st.markdown(f'<div style="font-family:Sora,sans-serif;font-size:17px;font-weight:700;color:#FFD54F;margin-bottom:1rem;text-shadow:0 0 20px rgba(255,213,79,0.35)">{MATCH_LABELS[selected]}</div>',
                    unsafe_allow_html=True)

        mgr_html = '<div class="mgr-grid">'
        for i, row in mgr_match.head(3).iterrows():
            mgr_html += f"""
            <div class="mgr-card">
              <div class="mgr-card-rank">{medals[i]} {place_label[i]}</div>
              <div class="mgr-card-name">{row['Manager']}</div>
              <div class="mgr-card-pts">{row['Points']:.1f}</div>
            </div>"""
        mgr_html += '</div>'
        st.markdown(mgr_html, unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown(sec_label('Player scores'), unsafe_allow_html=True)
            chosen = st.selectbox("Manager", mgr_match['Manager'].tolist(), key='match_mgr')
            pdf = df[df['Owner'] == chosen].copy().sort_values(selected, ascending=False)
            table_html = '<table class="player-table">'
            for _, prow in pdf.iterrows():
                v = prow[selected]
                if v == 0 and prow['Multiplier'] not in [2.0, 1.5]:
                    continue
                pc = pts_cls(v)
                ps = f'+{v:.2f}' if v > 0 else f'{v:.2f}'
                table_html += f"""<tr>
                  <td>{prow['PlayerName']}</td>
                  <td style="text-align:center">{role_badge(prow['Multiplier'])}</td>
                  <td style="text-align:right" class="{pc}">{ps}</td>
                </tr>"""
            table_html += '</table>'
            st.markdown(table_html, unsafe_allow_html=True)

        with col_right:
            st.markdown(sec_label('All managers this match'), unsafe_allow_html=True)
            all_mgr_html = ''
            for _, row in mgr_match.iterrows():
                idx = owners_ordered.index(row['Manager']) if row['Manager'] in owners_ordered else 0
                col_hex     = BAR_COLORS[idx % len(BAR_COLORS)]
                av_rgba_bg  = hex_to_rgba(col_hex, 0.16)
                av_rgba_bdr = hex_to_rgba(col_hex, 0.42)
                ps = f"+{row['Points']:.2f}" if row['Points'] > 0 else f"{row['Points']:.2f}"
                pts_col = col_hex if row['Points'] > 0 else ('#FF5252' if row['Points'] < 0 else '#3A4A7A')
                all_mgr_html += f"""
                <div class="lb-row" style="margin-bottom:4px">
                  <div class="lb-avatar" style="background:{av_rgba_bg};color:{col_hex};border:1px solid {av_rgba_bdr}">{initials(row['Manager'])}</div>
                  <span class="lb-name">{row['Manager']}</span>
                  <span style="font-family:Sora,sans-serif;font-size:13px;font-weight:700;color:{pts_col}">{ps}</span>
                </div>"""
            st.markdown(all_mgr_html, unsafe_allow_html=True)

            st.markdown(sec_label('Match-by-match trend'), unsafe_allow_html=True)
            trend_data = [
                (MATCH_LABELS[mk].split(':')[0], round(df[df['Owner'] == chosen][mk].sum(), 2))
                for mk in active_matches
            ]
            max_trend = max(abs(v) for _, v in trend_data) if trend_data else 1
            sel_label = MATCH_LABELS[selected].split(':')[0]
            trend_html = ''
            for label, val in trend_data:
                pct   = round((abs(val) / max_trend) * 100) if max_trend > 0 else 0
                bar_c = '#FFD54F' if label == sel_label else ('#2A3A7A' if val >= 0 else '#7A2A2A')
                t_c   = '#FFD54F' if label == sel_label else ('#69F0AE' if val > 0 else ('#FF5252' if val < 0 else '#3A4A7A'))
                ps    = f'+{val:.1f}' if val > 0 else f'{val:.1f}'
                trend_html += f"""
                <div class="trend-row">
                  <span class="trend-label">{label}</span>
                  <div class="trend-bar-bg"><div class="trend-bar-fg" style="width:{pct}%;background:{bar_c}"></div></div>
                  <span class="trend-val" style="color:{t_c}">{ps}</span>
                </div>"""
            st.markdown(trend_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# TAB 3 — ROSTERS
# ══════════════════════════════════════════════════════════════════════
with tab3:
    owner = st.selectbox("Select manager", owners_ordered, key='roster_owner')
    idx   = owners_ordered.index(owner)
    col_hex     = BAR_COLORS[idx % len(BAR_COLORS)]
    av_rgba_bg  = hex_to_rgba(col_hex, 0.18)
    av_rgba_bdr = hex_to_rgba(col_hex, 0.55)
    total = round(df[df['Owner'] == owner]['CurrentPoints'].sum(), 2)
    rank  = idx + 1

    st.markdown(f"""
    <div class="roster-header">
      <div class="roster-av" style="background:{av_rgba_bg};color:{col_hex};border-color:{av_rgba_bdr}">{initials(owner)}</div>
      <div>
        <div class="roster-name">{owner}</div>
        <div class="roster-sub">Rank #{rank} &nbsp;·&nbsp; {total:.2f} pts total</div>
      </div>
    </div>""", unsafe_allow_html=True)

    rdf = df[df['Owner'] == owner].sort_values('CurrentPoints', ascending=False)
    st.markdown(sec_label('Squad'), unsafe_allow_html=True)

    th_style = 'color:#6880AA;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;padding-bottom:6px'
    table_html = f'<table class="player-table"><tr style="border-bottom:1px solid rgba(255,255,255,0.08)">'
    table_html += f'<td style="{th_style}">Player</td>'
    table_html += f'<td style="{th_style};text-align:center">Role</td>'
    table_html += f'<td style="{th_style};text-align:right">Total</td>'
    for mk in active_matches:
        table_html += f'<td style="{th_style};text-align:right">{MATCH_LABELS[mk].split(":")[0]}</td>'
    table_html += '</tr>'

    for _, row in rdf.iterrows():
        tp = row['CurrentPoints']
        pc = pts_cls(tp)
        table_html += f'<tr><td>{row["PlayerName"]}</td>'
        table_html += f'<td style="text-align:center">{role_badge(row["Multiplier"])}</td>'
        table_html += f'<td style="text-align:right" class="{pc}">{tp:.2f}</td>'
        for mk in active_matches:
            v  = row.get(mk, 0.0)
            mc = pts_cls(v)
            vs = f'{v:.1f}' if v != 0 else '—'
            table_html += f'<td style="text-align:right" class="{mc}">{vs}</td>'
        table_html += '</tr>'
    table_html += '</table>'
    st.markdown(table_html, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
if SLIDESHOW_IMAGES:
    st.markdown(f'<div style="text-align:center;font-size:11px;color:#3A4A7A;margin-bottom:8px">{len(SLIDESHOW_IMAGES)} slideshow image(s) loaded from slideshow_images/</div>', unsafe_allow_html=True)
if st.button("🔄 Force Refresh (use sparingly)"):
    st.cache_data.clear()
    st.rerun()
