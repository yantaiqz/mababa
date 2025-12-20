import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time

# ==========================================
# 1. 基础配置 (必须位于最前)
# ==========================================
st.set_page_config(
    page_title="花光大佬的钱 | Spend Billions",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 数据配置 (多语言 & 多人物)
# ==========================================

# --- A. 多语言文本映射 ---
LANG_TEXT = {
    "zh": {
        "title": "花光{name}的钱",
        "subtitle": "你现在拥有 **{money}**。这钱不花完，别想下班！",
        "btn_more": "✨ 更多好玩应用",
        "receipt_title": "🧾 购物清单",
        "total_spent": "总计消费",
        "balance_zero": "恭喜你！你已经身无分文，可以安心退休了！",
        "toast_no_money": "钱不够啦！大佬也要省着花！",
        "coffee_btn": "☕ 请开发者喝咖啡",
        "coffee_title": "☕ 支持作者",
        "coffee_desc": "如果这个小游戏让你摸鱼更快乐，欢迎投喂！",
        "pay_wechat": "💬 微信支付",
        "pay_alipay": "💙 支付宝",
        "unit_cn": "杯",
        "unit_total": "总计投入",
        "pay_success": "收到！感谢你的 {count} 杯咖啡！代码写得更有劲了！❤️",
        "visitor_today": "今日 UV",
        "visitor_total": "历史 UV",
        "pv_today": "今日 PV"
    },
    "en": {
        "title": "Spend {name}'s Money",
        "subtitle": "You have **{money}**. Spend it all before you can leave!",
        "btn_more": "✨ More Apps",
        "receipt_title": "🧾 Receipt",
        "total_spent": "Total Spent",
        "balance_zero": "Congratulations! You are broke and free!",
        "toast_no_money": "Not enough money! Even billionaires have limits!",
        "coffee_btn": "☕ Buy me a coffee",
        "coffee_title": "☕ Support Me",
        "coffee_desc": "If you enjoyed this, consider buying me a coffee!",
        "pay_wechat": "💬 WeChat Pay",
        "pay_alipay": "💙 Alipay",
        "unit_cn": "Cups",
        "unit_total": "Total",
        "pay_success": "Received! Thanks for {count} cups! Coding with power! ❤️",
        "visitor_today": "Today UV",
        "visitor_total": "Total UV",
        "pv_today": "Today PV"
    }
}

# --- B. 人物与商品配置 ---
# 汇率估算：1 USD ≈ 7.2 CNY (为了简化游戏体验，马斯克直接用美元结算)
CHARACTERS = {
    "jack": {
        "name_zh": "马云",
        "name_en": "Jack Ma",
        "avatar": "👨🏻‍🏫",
        "money": 200_000_000_000,
        "currency": "¥",
        "theme_color": ["#2ecc71", "#27ae60"], # 绿色系
        "items": [
            {"id": "zhacai", "name_zh": "涪陵榨菜", "name_en": "Pickles", "price": 3, "icon": "🥒"},
            {"id": "cola", "name_zh": "肥宅快乐水", "name_en": "Coca Cola", "price": 5, "icon": "🥤"},
            {"id": "book", "name_zh": "《说话之道》", "name_en": "Speech Book", "price": 50, "icon": "📚"},
            {"id": "taobao", "name_zh": "清空购物车", "name_en": "Clear Cart", "price": 50000, "icon": "🛒"},
            {"id": "house_hz", "name_zh": "杭州大平层", "name_en": "Hangzhou Flat", "price": 15000000, "icon": "🏙️"},
            {"id": "film", "name_zh": "《功守道2》", "name_en": "Kung Fu Movie", "price": 200000000, "icon": "🎬"},
            {"id": "ant", "name_zh": "成立蚂蚁金服", "name_en": "Ant Group", "price": 50000000000, "icon": "🐜"},
        ]
    },
    "pony": {
        "name_zh": "马化腾",
        "name_en": "Pony Ma",
        "avatar": "🐧",
        "money": 300_000_000_000,
        "currency": "¥",
        "theme_color": ["#3498db", "#2980b9"], # 蓝色系
        "items": [
            {"id": "skin", "name_zh": "王者荣耀皮肤", "name_en": "Game Skin", "price": 168, "icon": "🎮"},
            {"id": "qq_vip", "name_zh": "QQ大会员(年)", "name_en": "QQ VIP", "price": 200, "icon": "💎"},
            {"id": "server", "name_zh": "扩容服务器", "name_en": "Server", "price": 50000, "icon": "🖥️"},
            {"id": "start_up", "name_zh": "投资初创公司", "name_en": "Invest Startup", "price": 5000000, "icon": "💼"},
            {"id": "building", "name_zh": "深圳滨海大厦", "name_en": "Tencent HQ", "price": 2000000000, "icon": "🏢"},
            {"id": "wechat", "name_zh": "微信新功能研发", "name_en": "WeChat R&D", "price": 5000000000, "icon": "💬"},
        ]
    },
    "elon": {
        "name_zh": "马斯克",
        "name_en": "Elon Musk",
        "avatar": "🚀",
        "money": 250_000_000_000, # 美元
        "currency": "$",
        "theme_color": ["#9b59b6", "#8e44ad"], # 紫色系
        "items": [
            {"id": "check", "name_zh": "推特蓝标", "name_en": "Blue Check", "price": 8, "icon": "✅"},
            {"id": "doge", "name_zh": "狗狗币", "name_en": "Dogecoin", "price": 1000, "icon": "🐕"},
            {"id": "flame", "name_zh": "火焰喷射器", "name_en": "Flamethrower", "price": 5000, "icon": "🔥"},
            {"id": "tesla", "name_zh": "特斯拉 Model S", "name_en": "Tesla Model S", "price": 80000, "icon": "🚗"},
            {"id": "twitter", "name_zh": "收购推特(X)", "name_en": "Buy Twitter", "price": 44000000000, "icon": "🐦"},
            {"id": "mars", "name_zh": "火星殖民地", "name_en": "Mars Colony", "price": 100000000000, "icon": "🪐"},
        ]
    }
}

# ==========================================
# 3. 状态初始化与工具函数
# ==========================================
if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'
if 'char_key' not in st.session_state:
    st.session_state.char_key = 'jack' # 默认马云
if 'cart' not in st.session_state:
    st.session_state.cart = {} # 购物车结构: {char_key: {item_id: count}}
if 'coffee_num' not in st.session_state:
    st.session_state.coffee_num = 1
if 'visitor_id' not in st.session_state:
    st.session_state["visitor_id"] = str(uuid.uuid4())

# 获取当前文本
def get_txt(key):
    return LANG_TEXT[st.session_state.lang][key]

# 获取当前人物数据
def get_char():
    return CHARACTERS[st.session_state.char_key]

# 切换人物（需重置购物车显示，或保留不同人物的独立购物车）
def switch_char(key):
    st.session_state.char_key = key
    # 不重置所有购物车，只是切换视图，数据隔离在 st.session_state.cart[key] 中
    if key not in st.session_state.cart:
        st.session_state.cart[key] = {}
        # 初始化该人物的所有商品数量为0
        for item in CHARACTERS[key]['items']:
            st.session_state.cart[key][item['id']] = 0

# 确保当前人物购物车已初始化
switch_char(st.session_state.char_key)

# 计算余额
def calculate_balance():
    c_key = st.session_state.char_key
    char_data = CHARACTERS[c_key]
    spent = 0
    
    # 遍历当前人物的购物车
    current_cart = st.session_state.cart[c_key]
    
    # 需要根据 item list 来匹配价格，因为 cart 只存了 id 和数量
    item_map = {item['id']: item['price'] for item in char_data['items']}
    
    for item_id, count in current_cart.items():
        if item_id in item_map:
            spent += count * item_map[item_id]
            
    return char_data['money'] - spent, spent

# 更新购买数量
def update_count(item_id, delta, item_price, current_balance):
    c_key = st.session_state.char_key
    current_count = st.session_state.cart[c_key].get(item_id, 0)
    
    if delta > 0 and current_balance < item_price:
        st.toast(get_txt("toast_no_money"), icon="⚠️")
        return
    if delta < 0 and current_count <= 0:
        return
        
    st.session_state.cart[c_key][item_id] = current_count + delta

# ==========================================
# 4. CSS 样式 (动态颜色)
# ==========================================
current_char = get_char()
theme_colors = current_char['theme_color']

st.markdown(f"""
<style>
    /* --- 基础清理 --- */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{display: none;}}
    .stApp {{ background-color: #f1f2f6; }}
    
    /* --- 顶部余额条 (动态颜色) --- */
    .header-container {{
        position: sticky; top: 0; z-index: 999;
        background: linear-gradient(180deg, {theme_colors[0]}, {theme_colors[1]});
        color: white; padding: 20px 0; text-align: center;
        font-weight: 800; font-size: 2.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
    }}
    
    /* --- 人物切换按钮 --- */
    .char-btn {{
        border: 2px solid transparent; border-radius: 50%; padding: 2px;
        cursor: pointer; transition: all 0.3s; opacity: 0.6;
    }}
    .char-btn:hover {{ opacity: 1; transform: scale(1.1); }}
    .char-btn.active {{ border-color: {theme_colors[0]}; opacity: 1; transform: scale(1.1); }}
    
    /* --- 商品卡片 --- */
    .item-card {{
        background: white; padding: 20px; border-radius: 10px;
        text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s; height: 100%; display: flex; flex-direction: column; justify-content: space-between;
    }}
    .item-card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
    .item-emoji {{ font-size: 3.5rem; margin-bottom: 10px; }}
    .item-name {{ font-size: 1.1rem; font-weight: bold; color: #333; height: 40px; display: flex; align-items: center; justify-content: center; }}
    .item-price {{ color: {theme_colors[1]}; font-weight: bold; font-size: 1rem; margin: 10px 0; }}
    
    /* --- 按钮样式 --- */
    div.stButton > button {{
        background-color: #f8f9fa; border: 1px solid #ddd;
        color: #333; font-weight: bold; width: 100%;
    }}
    div.stButton > button:hover {{ border-color: {theme_colors[0]}; color: {theme_colors[0]}; }}
    /* 购买按钮高亮 */
    div.stButton > button:active {{ background-color: {theme_colors[0]} !important; color: white !important; }}

    /* --- 咖啡 & 统计 --- */
    .metric-container {{
        display: flex; justify-content: center; gap: 20px;
        margin-top: 20px; padding: 10px; background-color: #f8f9fa;
        border-radius: 10px; border: 1px solid #e9ecef; color: #666;
    }}
    .coffee-card {{
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e5e7eb; border-radius: 16px;
        padding: 10px; text-align: center;
    }}
    .price-number {{ color: #d9534f; font-weight: 900; font-size: 1.8rem; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. 核心逻辑：渲染与交互
# ==========================================

# --- A. 顶部导航 (语言 & 人物) ---
col_logo, col_chars, col_lang = st.columns([1, 4, 1])

with col_chars:
    # 居中显示人物切换
    c_cols = st.columns(len(CHARACTERS) + 2) # 左右留白
    idx = 1
    for key, data in CHARACTERS.items():
        with c_cols[idx]:
            # 判断是否选中
            is_active = "active" if st.session_state.char_key == key else ""
            if st.button(f"{data['avatar']} {data['name_zh' if st.session_state.lang == 'zh' else 'name_en']}", key=f"btn_char_{key}"):
                switch_char(key)
                st.rerun()
        idx += 1

with col_lang:
    lang_label = "🇺🇸 English" if st.session_state.lang == 'zh' else "🇨🇳 中文"
    if st.button(lang_label, use_container_width=True):
        st.session_state.lang = 'en' if st.session_state.lang == 'zh' else 'zh'
        st.rerun()

# --- B. 标题与余额 ---
# 重新获取数据（防止切换后未更新）
current_char = get_char()
balance, total_spent = calculate_balance()
c_key = st.session_state.char_key
currency = current_char['currency']

# 标题
char_name = current_char['name_zh'] if st.session_state.lang == 'zh' else current_char['name_en']
st.markdown(f"<h1 style='text-align: center; margin-top:-10px;'>{get_txt('title').format(name=char_name)}</h1>", unsafe_allow_html=True)

# 【修复点】将复杂的格式化拆分为两步，避免引号冲突
money_str = f"{currency}{current_char['money']:,}" 
subtitle_text = get_txt('subtitle').format(money=money_str)

st.markdown(f"<div style='text-align: center; color: #666; margin-bottom: 20px;'>{subtitle_text}</div>", unsafe_allow_html=True)

# 悬浮余额条
st.markdown(f"""
<div class="header-container">
    {currency} {balance:,.0f}
</div>
""", unsafe_allow_html=True)

# --- C. 商品网格 ---
items = current_char['items']
cols_per_row = 3 # 依然保持3列，或者宽屏可以4列

# 使用 Streamlit 原生 Grid 布局无法完美自定义 CSS，继续用 columns 循环
for i in range(0, len(items), cols_per_row):
    cols = st.columns(cols_per_row)
    for j in range(cols_per_row):
        if i + j < len(items):
            item = items[i + j]
            item_name = item['name_zh'] if st.session_state.lang == 'zh' else item['name_en']
            
            with cols[j]:
                with st.container():
                    st.markdown(f"""
                    <div class="item-card">
                        <div class="item-emoji">{item['icon']}</div>
                        <div class="item-name">{item_name}</div>
                        <div class="item-price">{currency} {item['price']:,}</div>
                    </div>""", unsafe_allow_html=True)
                    
                    # 操作区
                    b_col1, b_col2, b_col3 = st.columns([1, 2, 1])
                    with b_col1:
                        st.button("－", key=f"sell_{c_key}_{item['id']}", 
                                  on_click=update_count, args=(item['id'], -1, item['price'], balance), use_container_width=True)
                    with b_col2:
                        count = st.session_state.cart[c_key].get(item['id'], 0)
                        st.markdown(f"<div style='text-align: center; line-height: 2.3rem; font-weight: bold; font-size: 1.2rem;'>{count}</div>", unsafe_allow_html=True)
                    with b_col3:
                        st.button("＋", key=f"buy_{c_key}_{item['id']}", 
                                  on_click=update_count, args=(item['id'], 1, item['price'], balance), type="primary", use_container_width=True)
                    st.markdown("<br>", unsafe_allow_html=True)

# --- D. 购物小票 ---
if total_spent > 0:
    st.markdown("---")
    
    receipt_title = get_txt('receipt_title')
    total_label = get_txt('total_spent')
    
    html_content = f"""
    <div style="background-color: white; padding: 20px; border-radius: 10px; max-width: 500px; margin: 0 auto; box-shadow: 0 4px 10px rgba(0,0,0,0.1); color: #333; font-family: 'Courier New', Courier, monospace;">
        <h2 style="text-align: center; border-bottom: 2px dashed #333; padding-bottom: 10px; margin-bottom: 20px; font-weight: 800;">{receipt_title}</h2>
    """
    
    for item in items:
        count = st.session_state.cart[c_key].get(item['id'], 0)
        item_name = item['name_zh'] if st.session_state.lang == 'zh' else item['name_en']
        if count > 0:
            html_content += f"""
            <div style="display: flex; justify-content: space-between; margin: 10px 0; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                <span style="text-align: left; font-weight: bold;">{item_name} x{count}</span>
                <span style="font-weight: bold; color: {current_char['theme_color'][1]};">{currency} {item['price'] * count:,.0f}</span>
            </div>"""
            
    html_content += f"""
        <div style="display: flex; justify-content: space-between; font-size: 1.3rem; font-weight: 900; margin-top: 20px; border-top: 3px solid #333; padding-top: 15px;">
            <span>{total_label}:</span><span>{currency} {total_spent:,.0f}</span>
        </div>
    </div>"""
    
    st.markdown(html_content, unsafe_allow_html=True)
    
    if balance == 0:
        st.balloons()
        st.success(get_txt('balance_zero'))

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# 6. 底部功能：咖啡打赏 & 统计
# ==========================================

# --- 咖啡弹窗逻辑 ---
@st.dialog("☕ " + get_txt('coffee_title'), width="small")
def show_coffee_window():
    st.markdown(f"""
    <div class="coffee-card">
        <h3 style="margin:0; font-size:1.2rem;">{get_txt('coffee_btn')}</h3>
        <p style="color:#666; font-size:0.8rem; margin-top:5px;">{get_txt('coffee_desc')}</p>
    </div>""", unsafe_allow_html=True)

    # 选项
    presets = [("☕", 1), ("🍗", 3), ("🚀", 5)]
    def set_val(n): st.session_state.coffee_num = n
    cols = st.columns(3)
    for i, (icon, num) in enumerate(presets):
        with cols[i]:
            if st.button(f"{icon} {num}", use_container_width=True, key=f"p_btn_{i}"): set_val(num)

    st.write("")
    c1, c2 = st.columns([1, 1])
    with c1:
        cnt = st.number_input(get_txt('unit_cn'), 1, 100, step=1, key='coffee_num')
    total = cnt * 10
    with c2:
        st.markdown(f"""
        <div style="background: #fff0f0; border: 1px dashed #ffcccc; border-radius: 12px; padding: 5px; text-align: center;">
            <div style="color:#888; font-size: 0.8rem;">{get_txt('unit_total')} (¥)</div>
            <div class="price-number">{total}</div>
        </div>""", unsafe_allow_html=True)

    t1, t2 = st.tabs([get_txt('pay_wechat'), get_txt('pay_alipay')])
    
    def show_qr(img_path):
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            # 模拟二维码
            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Donate_{total}", width=150)

    with t1: show_qr("wechat_pay.jpg")
    with t2: show_qr("ali_pay.jpg")

    st.write("")
    if st.button("🎉 " + get_txt('pay_success').split('!')[0], type="primary", use_container_width=True):
        st.balloons()
        st.success(get_txt('pay_success').format(count=cnt))
        time.sleep(2)
        st.rerun()

# --- 底部按钮 ---
c_btn_col1, c_btn_col2, c_btn_col3 = st.columns([1, 2, 1])
with c_btn_col2:
    if st.button(get_txt('coffee_btn'), use_container_width=True):
        show_coffee_window()

# --- 数据库统计 (精简版) ---
DB_DIR = os.path.expanduser("~/")
DB_FILE = os.path.join(DB_DIR, "visit_stats.db")

def track_stats():
    # 简单的统计逻辑，不阻塞主线程
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS daily_traffic (date TEXT PRIMARY KEY, pv_count INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS visitors (visitor_id TEXT PRIMARY KEY, last_visit_date TEXT)''')
        
        today = datetime.datetime.utcnow().date().isoformat()
        vid = st.session_state["visitor_id"]
        
        # 写入
        if "has_counted" not in st.session_state:
            c.execute("INSERT OR IGNORE INTO daily_traffic (date, pv_count) VALUES (?, 0)", (today,))
            c.execute("UPDATE daily_traffic SET pv_count = pv_count + 1 WHERE date=?", (today,))
            c.execute("INSERT OR REPLACE INTO visitors (visitor_id, last_visit_date) VALUES (?, ?)", (vid, today))
            conn.commit()
            st.session_state["has_counted"] = True
            
        # 读取
        t_uv = c.execute("SELECT COUNT(*) FROM visitors WHERE last_visit_date=?", (today,)).fetchone()[0]
        a_uv = c.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
        t_pv = c.execute("SELECT pv_count FROM daily_traffic WHERE date=?", (today,)).fetchone()[0]
        conn.close()
        return t_uv, a_uv, t_pv
    except:
        return 0, 0, 0

today_uv, total_uv, today_pv = track_stats()

# 显示统计
st.markdown(f"""
<div class="metric-container">
    <div class="metric-box"><div class="metric-sub">{get_txt('visitor_today')}: {today_uv}</div></div>
    <div class="metric-box" style="border-left:1px solid #ddd; padding-left:20px;"><div class="metric-sub">{get_txt('visitor_total')}: {total_uv}</div></div>
    <div class="metric-box" style="border-left:1px solid #ddd; padding-left:20px;"><div class="metric-sub">{get_txt('pv_today')}: {today_pv}</div></div>
</div><br>
""", unsafe_allow_html=True)
