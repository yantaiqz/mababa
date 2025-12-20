import streamlit as st
import pandas as pd
import sqlite3
import uuid
import datetime
import os
import time

# ==========================================
# 1. 基础配置 (必须位于最前)
# ==========================================
st.set_page_config(
    page_title="花光马云的钱 (Spend Jack Ma's Money)",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. CSS 样式 (合并了 Neal.fun 风格与咖啡打赏样式)
# ==========================================
st.markdown("""
<style>
    /* --- 基础清理 --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {display: none;}
    .stApp { background-color: #f1f2f6; }
    
    /* --- 右上角按钮 --- */
    .neal-btn {
        font-family: 'Inter', sans-serif; background: #fff;
        border: 1px solid #e5e7eb; color: #111; font-weight: 600;
        font-size: 14px; padding: 8px 16px; border-radius: 8px;
        cursor: pointer; transition: all 0.2s; display: inline-flex;
        align-items: center; justify-content: center; white-space: nowrap;
        text-decoration: none !important; width: 100%; height: 38px;
    }
    .neal-btn:hover { background: #f9fafb; border-color: #111; transform: translateY(-1px); }
    .neal-btn-link { text-decoration: none; width: 100%; display: block; }

    /* --- 顶部余额条 --- */
    .header-container {
        position: sticky; top: 0; z-index: 999;
        background: linear-gradient(180deg, #2ecc71, #27ae60);
        color: white; padding: 20px 0; text-align: center;
        font-weight: 800; font-size: 2.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    
    /* --- 商品卡片 --- */
    .item-card {
        background: white; padding: 20px; border-radius: 10px;
        text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s; height: 100%;
    }
    .item-card:hover { transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    .item-emoji { font-size: 4rem; margin-bottom: 10px; }
    .item-name { font-size: 1.2rem; font-weight: bold; color: #333; }
    .item-price { color: #27ae60; font-weight: bold; font-size: 1rem; margin-bottom: 15px; }
    
    /* --- 按钮样式微调 --- */
    div.stButton > button {
        background-color: #f1f2f6; border: 1px solid #ccc;
        color: #333; font-weight: bold;
    }
    div.stButton > button:hover { border-color: #27ae60; color: #27ae60; }
    
    /* --- 统计模块 --- */
    .metric-container {
        display: flex; justify-content: center; gap: 20px;
        margin-top: 20px; padding: 10px; background-color: #f8f9fa;
        border-radius: 10px; border: 1px solid #e9ecef;
    }
    .metric-box { text-align: center; }
    .metric-sub { font-size: 0.7rem; color: #adb5bd; }

    /* --- ☕ 咖啡打赏专用样式 --- */
    .coffee-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e5e7eb; border-radius: 16px;
        padding: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 10px; text-align: center;
    }
    .price-tag-container {
        background: #fff0f0; border: 1px dashed #ffcccc;
        border-radius: 12px; padding: 10px; text-align: center;
        margin-top: 5px; transition: all 0.3s;
    }
    .price-tag-container:hover { transform: scale(1.02); }
    .price-label { color: #888; font-size: 0.8rem; margin-bottom: 2px; }
    .price-number { color: #d9534f; font-weight: 900; font-size: 1.8rem; }
    /* 调整 Tab 居中 */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 状态与数据初始化
# ==========================================
if 'coffee_num' not in st.session_state:
    st.session_state.coffee_num = 1
if 'visitor_id' not in st.session_state:
    st.session_state["visitor_id"] = str(uuid.uuid4())

# 商品数据
TOTAL_MONEY = 200_000_000_000 
ITEMS = [
    {"id": "zhacai", "name": "涪陵榨菜", "price": 3, "icon": "🥒"},
    {"id": "cola", "name": "肥宅快乐水", "price": 5, "icon": "🥤"},
    {"id": "milktea", "name": "喜茶", "price": 30, "icon": "🧋"},
    {"id": "book", "name": "《马云说话之道》", "price": 50, "icon": "📚"},
    {"id": "sneakers", "name": "AJ 倒钩", "price": 8000, "icon": "👟"},
    {"id": "iphone", "name": "iPhone 16 Pro Max", "price": 10000, "icon": "📱"},
    {"id": "lv", "name": "LV 包包", "price": 25000, "icon": "👜"},
    {"id": "tesla", "name": "特斯拉 Model X", "price": 800000, "icon": "🚗"},
    {"id": "house_hz", "name": "杭州大平层", "price": 15000000, "icon": "🏙️"},
    {"id": "ferrari", "name": "法拉利 LaFerrari", "price": 25000000, "icon": "🏎️"},
    {"id": "siheyuan", "name": "北京四合院", "price": 100000000, "icon": "⛩️"},
    {"id": "film", "name": "拍一部《功守道2》", "price": 200000000, "icon": "🎬"},
    {"id": "jet", "name": "私人湾流飞机", "price": 400000000, "icon": "✈️"},
    {"id": "island", "name": "加勒比私人岛屿", "price": 800000000, "icon": "🏝️"},
    {"id": "nba", "name": "NBA 篮球队", "price": 15000000000, "icon": "🏀"},
    {"id": "rocket", "name": "SpaceX 火箭发射", "price": 40000000000, "icon": "🚀"},
    {"id": "twitter", "name": "收购 Twitter (X)", "price": 300000000000, "icon": "🐦"},
]

# 初始化购物车
for item in ITEMS:
    if item['id'] not in st.session_state:
        st.session_state[item['id']] = 0

# 计算逻辑
def calculate_balance():
    spent = 0
    for item in ITEMS:
        spent += st.session_state[item['id']] * item['price']
    return TOTAL_MONEY - spent, spent

balance, total_spent = calculate_balance()

def update_count(item_id, delta, item_price):
    current = st.session_state[item_id]
    if delta > 0 and balance < item_price:
        st.toast("钱不够啦！马老师也要省着花！", icon="⚠️")
        return
    if delta < 0 and current <= 0:
        return
    st.session_state[item_id] += delta

# ==========================================
# 4. 核心功能：咖啡打赏弹窗 (新增逻辑)
# ==========================================
@st.dialog("☕ 支持作者", width="small")
def show_coffee_window():
    # 头部文案
    st.markdown("""
    <div class="coffee-card">
        <h3 style="margin:0; font-size:1.2rem;">请开发者喝杯咖啡</h3>
        <p style="color:#666; font-size:0.8rem; margin-top:5px;">如果这个小游戏让你摸鱼更快乐，欢迎投喂！</p>
    </div>""", unsafe_allow_html=True)

    # 1. 预设选项 (Emoji, 数量, 文案)
    presets = [("☕ 提神", 1, "由衷感谢"), ("🍗 鸡腿", 3, "动力加倍"), ("🚀 续命", 5, "老登不朽")]
    
    def set_val(n): st.session_state.coffee_num = n
    
    cols = st.columns(3)
    for i, (label, num, tip) in enumerate(presets):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"p_btn_{i}"): set_val(num)
            st.markdown(f"<div style='text-align:center; font-size:0.7rem; color:#aaa; margin-top:-5px;'>{tip}</div>", unsafe_allow_html=True)

    st.write("")
    
    # 2. 数量与金额
    c1, c2 = st.columns([1, 1])
    with c1:
        cnt = st.number_input("自定义数量 (杯)", 1, 100, step=1, key='coffee_num')
    total = cnt * 10
    with c2:
        st.markdown(f"""
        <div class="price-tag-container">
            <div class="price-label">总计投入 (¥)</div>
            <div class="price-number">{total}</div>
        </div>""", unsafe_allow_html=True)

    # 3. 支付Tab
    t1, t2 = st.tabs(["💬 微信支付", "💙 支付宝"])
    
    def show_qr(img_path):
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            # 占位符逻辑
            st.warning("未找到本地收款码图片")
            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Pay_{total}_RMB", width=150)

    with t1: show_qr("wechat_pay.jpg")
    with t2: show_qr("ali_pay.jpg")

    # 4. 反馈
    st.write("")
    if st.button("🎉 我已支付，给作者打气！", type="primary", use_container_width=True):
        st.balloons()
        st.success(f"收到！感谢你的 {cnt} 杯咖啡！代码写得更有劲了！❤️")
        time.sleep(2)
        st.rerun()

# ==========================================
# 5. 页面布局渲染
# ==========================================

# --- 右上角导航 ---
col_empty, col_lang, col_more = st.columns([0.7, 0.1, 0.2])
with col_lang:
    st.button("中/En", key="lang_switch", help="语言切换（暂无实际功能）")
with col_more:
    st.markdown(f"""
        <a href="https://haowan.streamlit.app/" target="_blank" class="neal-btn-link">
            <button class="neal-btn">✨ 更多好玩应用</button>
        </a>""", unsafe_allow_html=True)

# --- 头部区域 ---
c1, c2 = st.columns([1, 6])
with c1:
    st.markdown("<div style='font-size: 80px; text-align: center;'>👨🏻‍🏫</div>", unsafe_allow_html=True)
with c2:
    st.title("花光马云的钱")
    st.markdown("你现在拥有 **2000亿** 人民币。这钱不花完，别想下班！(996福报)")

# --- 悬浮余额条 ---
bg_color = "#2ecc71" if balance > 0 else "#e74c3c"
st.markdown(f"""
<div class="header-container" style="background: {bg_color};">
    ¥ {balance:,.0f}
</div><br>
""", unsafe_allow_html=True)

# --- 商品网格 ---
cols_per_row = 3
for i in range(0, len(ITEMS), cols_per_row):
    cols = st.columns(cols_per_row)
    for j in range(cols_per_row):
        if i + j < len(ITEMS):
            item = ITEMS[i + j]
            with cols[j]:
                with st.container():
                    st.markdown(f"""
                    <div class="item-card">
                        <div class="item-emoji">{item['icon']}</div>
                        <div class="item-name">{item['name']}</div>
                        <div class="item-price">¥ {item['price']:,}</div>
                    </div>""", unsafe_allow_html=True)
                    
                    b_col1, b_col2, b_col3 = st.columns([1, 2, 1])
                    with b_col1:
                        st.button("－", key=f"sell_{item['id']}", on_click=update_count, args=(item['id'], -1, item['price']), use_container_width=True)
                    with b_col2:
                        count = st.session_state[item['id']]
                        st.markdown(f"<div style='text-align: center; line-height: 2.5rem; font-weight: bold; font-size: 1.2rem;'>{count}</div>", unsafe_allow_html=True)
                    with b_col3:
                        st.button("＋", key=f"buy_{item['id']}", on_click=update_count, args=(item['id'], 1, item['price']), type="primary", use_container_width=True)
                    st.markdown("<br>", unsafe_allow_html=True)

# --- 底部：购物小票 ---
if total_spent > 0:
    st.markdown("---")
    html_content = f"""
    <div style="background-color: white; padding: 20px; border-radius: 10px; max-width: 500px; margin: 0 auto; box-shadow: 0 4px 10px rgba(0,0,0,0.1); color: #333; font-family: 'Courier New', Courier, monospace;">
        <h2 style="text-align: center; border-bottom: 2px dashed #333; padding-bottom: 10px; margin-bottom: 20px; font-weight: 800;">🧾 支付宝账单</h2>
    """
    for item in ITEMS:
        count = st.session_state[item['id']]
        if count > 0:
            html_content += f"""
            <div style="display: flex; justify-content: space-between; margin: 10px 0; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                <span style="text-align: left; font-weight: bold;">{item['name']} x{count}</span>
                <span style="font-weight: bold; color: #e74c3c;">¥ {item['price'] * count:,.0f}</span>
            </div>"""
    html_content += f"""
        <div style="display: flex; justify-content: space-between; font-size: 1.3rem; font-weight: 900; margin-top: 20px; border-top: 3px solid #333; padding-top: 15px;">
            <span>总计消费:</span><span>¥ {total_spent:,.0f}</span>
        </div>
    </div>"""
    st.markdown(html_content, unsafe_allow_html=True)
    if balance == 0:
        st.balloons()
        st.success("恭喜你！你已经身无分文，可以安心退休了！")

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# 6. 底部：咖啡打赏入口与统计
# ==========================================
c_btn_col1, c_btn_col2, c_btn_col3 = st.columns([1, 2, 1])
with c_btn_col2:
    # 咖啡打赏按钮
    if st.button("☕ 请作者喝杯咖啡", use_container_width=True):
        show_coffee_window()

# --- 数据库统计逻辑 ---
DB_DIR = os.path.expanduser("~/")
DB_FILE = os.path.join(DB_DIR, "visit_stats.db")

def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS daily_traffic (date TEXT PRIMARY KEY, pv_count INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS visitors (visitor_id TEXT PRIMARY KEY, first_visit_date TEXT)''')
    try:
        c.execute("ALTER TABLE visitors ADD COLUMN last_visit_date TEXT")
        c.execute("UPDATE visitors SET last_visit_date = first_visit_date WHERE last_visit_date IS NULL")
    except: pass
    conn.commit()
    conn.close()

def track_and_get_stats():
    init_db()
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    today = datetime.datetime.utcnow().date().isoformat()
    vid = st.session_state["visitor_id"]
    
    if "has_counted" not in st.session_state:
        try:
            c.execute("INSERT OR IGNORE INTO daily_traffic (date, pv_count) VALUES (?, 0)", (today,))
            c.execute("UPDATE daily_traffic SET pv_count = pv_count + 1 WHERE date=?", (today,))
            c.execute("SELECT visitor_id FROM visitors WHERE visitor_id=?", (vid,))
            if c.fetchone():
                c.execute("UPDATE visitors SET last_visit_date=? WHERE visitor_id=?", (today, vid))
            else:
                c.execute("INSERT INTO visitors (visitor_id, first_visit_date, last_visit_date) VALUES (?, ?, ?)", (vid, today, today))
            conn.commit()
            st.session_state["has_counted"] = True
        except: pass

    try:
        t_uv = c.execute("SELECT COUNT(*) FROM visitors WHERE last_visit_date=?", (today,)).fetchone()[0]
        a_uv = c.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
        t_pv = c.execute("SELECT pv_count FROM daily_traffic WHERE date=?", (today,)).fetchone()[0]
    except: t_uv, a_uv, t_pv = 0, 0, 0
    conn.close()
    return t_uv, a_uv, t_pv

try:
    today_uv, total_uv, today_pv = track_and_get_stats()
except:
    today_uv, total_uv, today_pv = 0, 0, 0

st.markdown(f"""
<div class="metric-container">
    <div class="metric-box"><div class="metric-sub">今日 UV: {today_uv}</div></div>
    <div class="metric-box" style="border-left:1px solid #ddd; padding-left:20px;"><div class="metric-sub">历史 UV: {total_uv}</div></div>
    <div class="metric-box" style="border-left:1px solid #ddd; padding-left:20px;"><div class="metric-sub">今日 PV: {today_pv}</div></div>
</div><br>
""", unsafe_allow_html=True)
