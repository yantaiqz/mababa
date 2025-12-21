import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import re

# ==========================================
# 1. 基础配置
# ==========================================
st.set_page_config(
    page_title="花光马爸爸的钱 | Spend Billions",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 自动检测浏览器语言
# ==========================================
def detect_browser_language():
    try:
        headers = st.context.headers
        accept_language = headers.get('Accept-Language', 'zh')
        lang_codes = re.findall(r'([a-z]{2})(?:-[A-Z]{2})?', accept_language.lower())
        if 'zh' in lang_codes: return 'zh'
        elif 'en' in lang_codes: return 'en'
        else: return 'zh'
    except: return 'zh'

if 'lang' not in st.session_state:
    st.session_state.lang = detect_browser_language()

# ==========================================
# 3. 数据配置
# ==========================================
LANG_TEXT = {
    "zh": {
        "title": "花光{name}的钱",
        "subtitle": "你现在拥有 {money}。这钱不花完，别想下班！",
        "receipt_title": "购物清单",
        "total_spent": "实付金额",
        "balance_zero": "恭喜你！你已经身无分文，可以安心退休了！",
        "toast_no_money": "余额不足！大佬也要精打细算！",
        "coffee_btn": "☕ 请开发者喝咖啡",
        "coffee_title": " ",
        "coffee_desc": "如果这个小游戏让你摸鱼更快乐，欢迎投喂！",
        "pay_wechat": "微信支付",
        "pay_alipay": "支付宝",
        "pay_paypal": "PayPal",
        "more_label": "✨ 更多乐子",
        "unit_cn": "杯",
        "unit_total": "总计投入",
        "pay_success": "收到！感谢打赏。代码写得更有劲了！❤️",
        "visitor_today": "今日 UV",
        "visitor_total": "历史 UV",
        "share_btn": "📤 生成分享海报",
        "share_modal_title": "截图凡尔赛一下",
        "share_prompt": "复制下方文案，配合截图发朋友圈👇",
        "share_copy_text": "我在《花光大佬的钱》里挥霍了 {amount}！买了 {item_count} 件离谱商品，你也来试试？👉 https://mababa.streamlit.app",
        "scan_to_play": "长按识别二维码挑战",
        "pv_today": "今日 PV",
        "pay_choose": "选择支付方式",
        "coffee_amount": "请输入打赏杯数"
    },
    "en": {
        "title": "Spend {name}'s Money",
        "subtitle": "You have {money}. Spend it all before you can leave!",
        "receipt_title": "Receipt",
        "total_spent": "Total Paid",
        "balance_zero": "Congratulations! You are broke and free!",
        "toast_no_money": "Not enough money!",
        "coffee_btn": "☕ Buy me a coffee",
        "coffee_title": " ",
        "coffee_desc": "If you enjoyed this, consider buying me a coffee!",
        "pay_wechat": "WeChat Pay",
        "more_label": "✨ More fun",
        "pay_alipay": "Alipay",
        "pay_paypal": "PayPal",
        "unit_cn": "Cups",
        "unit_total": "Total",
        "pay_success": "Received! Thanks for the coffee! ❤️",
        "visitor_today": "Today UV",
        "visitor_total": "Total UV",
        "share_btn": "📤 Share Receipt",
        "share_modal_title": "Share with Friends",
        "share_prompt": "Copy text below & share with screenshot👇",
        "share_copy_text": "I spent {amount} in 'Spend Billions'! Bought {item_count} items. Can you beat me? 👉 https://mababa.streamlit.app",
        "scan_to_play": "Scan to Play",
        "pv_today": "Today PV",
        "pay_choose": "Choose Payment Method",
        "coffee_amount": "Enter Coffee Count"
    }
}

CHARACTERS = {
    "jack": {
        "name_zh": "马云",
        "name_en": "Jack Ma",
        "avatar": "👨🏻‍🏫",
        "money": 200_000_000_000,
        "currency": "¥",
        "bill_type": "alipay",
        "theme_color": ["#1677ff", "#4096ff"],
        "photo_url": "https://www.diydoutu.com/bq/538.gif",
        "items": [
            {"id": "zhacai", "name_zh": "涪陵榨菜", "name_en": "Pickles", "price": 3, "icon": "🥒"},
            {"id": "cola", "name_zh": "肥宅快乐水", "name_en": "Coca Cola", "price": 5, "icon": "🥤"},
            {"id": "book", "name_zh": "《说话之道》", "name_en": "Speech Book", "price": 50, "icon": "📚"},
            {"id": "flower", "name_zh": "花呗还款", "name_en": "Huabei Bill", "price": 5000, "icon": "💳"},
            {"id": "taobao", "name_zh": "清空购物车", "name_en": "Clear Cart", "price": 50000, "icon": "🛒"},
            {"id": "teacher", "name_zh": "乡村教师工资", "name_en": "Teacher Salary", "price": 100000, "icon": "🏫"},
            {"id": "paint", "name_zh": "马云的油画", "name_en": "Painting", "price": 10000000, "icon": "🎨"},
            {"id": "house_hz", "name_zh": "杭州大平层", "name_en": "Hangzhou Flat", "price": 15000000, "icon": "🏙️"},
            {"id": "hema", "name_zh": "盒马鲜生店", "name_en": "Hema Store", "price": 20000000, "icon": "🦞"},
            {"id": "winery", "name_zh": "法国酒庄", "name_en": "French Winery", "price": 50000000, "icon": "🍷"},
            {"id": "film", "name_zh": "《功守道2》", "name_en": "Kung Fu Movie", "price": 200000000, "icon": "🎬"},
            {"id": "jet", "name_zh": "私人湾流飞机", "name_en": "Private Jet", "price": 400000000, "icon": "✈️"},
            {"id": "cainiao", "name_zh": "菜鸟物流园", "name_en": "Logistics Park", "price": 1000000000, "icon": "📦"},
            {"id": "ant", "name_zh": "重组蚂蚁金服", "name_en": "Ant Group", "price": 50000000000, "icon": "🐜"},
        ]
    },
    "pony": {
        "name_zh": "马化腾",
        "name_en": "Pony Ma",
        "avatar": "🐧",
        "money": 300_000_000_000,
        "currency": "¥",
        "bill_type": "wechat",
        "theme_color": ["#2aad67", "#20c06d"],
        "photo_url": "http://n.sinaimg.cn/sinacn20118/704/w352h352/20181218/3b35-hqhtqsq1135213.gif",
        "items": [
            {"id": "sticker", "name_zh": "微信表情包", "name_en": "Sticker Pack", "price": 1, "icon": "🌝"},
            {"id": "music", "name_zh": "QQ音乐绿钻", "name_en": "Music VIP", "price": 18, "icon": "🎵"},
            {"id": "video", "name_zh": "腾讯视频会员", "name_en": "Video VIP", "price": 30, "icon": "📺"},
            {"id": "skin", "name_zh": "王者荣耀皮肤", "name_en": "Game Skin", "price": 168, "icon": "🎮"},
            {"id": "qq_vip", "name_zh": "QQ大会员(年)", "name_en": "QQ VIP", "price": 200, "icon": "💎"},
            {"id": "server", "name_zh": "云服务器(台)", "name_en": "Cloud Server", "price": 50000, "icon": "🖥️"},
            {"id": "coder", "name_zh": "程序员年薪", "name_en": "Coder Salary", "price": 500000, "icon": "👓"},
            {"id": "start_up", "name_zh": "投资初创公司", "name_en": "Invest Startup", "price": 5000000, "icon": "💼"},
            {"id": "meituan", "name_zh": "增持美团", "name_en": "Buy Meituan", "price": 100000000, "icon": "🦘"},
            {"id": "jd", "name_zh": "增持京东", "name_en": "Buy JD", "price": 200000000, "icon": "🐕"},
            {"id": "nba", "name_zh": "NBA转播权", "name_en": "NBA Rights", "price": 1000000000, "icon": "🏀"},
            {"id": "building", "name_zh": "深圳滨海大厦", "name_en": "Tencent HQ", "price": 2000000000, "icon": "🏢"},
            {"id": "epic", "name_zh": "收购Epic Games", "name_en": "Buy Epic", "price": 3000000000, "icon": "🕹️"},
            {"id": "wechat", "name_zh": "微信新功能研发", "name_en": "WeChat R&D", "price": 5000000000, "icon": "💬"},
        ]
    },
    "elon": {
        "name_zh": "马斯克",
        "name_en": "Elon Musk",
        "avatar": "🚀",
        "money": 250_000_000_000, 
        "currency": "$",
        "bill_type": "paypal",
        "theme_color": ["#003087", "#009cde"],
        "photo_url": "https://media1.tenor.com/images/a9d75860a0b379ba69b3e4ca184eba89/tenor.gif",
        "items": [
            {"id": "check", "name_zh": "推特蓝标", "name_en": "Blue Check", "price": 8, "icon": "✅"},
            {"id": "starlink_sub", "name_zh": "星链月费", "name_en": "Starlink Sub", "price": 110, "icon": "📡"},
            {"id": "doge", "name_zh": "狗狗币", "name_en": "Dogecoin", "price": 1000, "icon": "🐕"},
            {"id": "flame", "name_zh": "火焰喷射器", "name_en": "Flamethrower", "price": 5000, "icon": "🔥"},
            {"id": "robot", "name_zh": "擎天柱机器人", "name_en": "Optimus Bot", "price": 20000, "icon": "🤖"},
            {"id": "tesla", "name_zh": "特斯拉 Model S", "name_en": "Tesla Model S", "price": 80000, "icon": "🚗"},
            {"id": "cybertruck", "name_zh": "CyberTruck", "name_en": "CyberTruck", "price": 100000, "icon": "🚙"},
            {"id": "neuralink", "name_zh": "脑机接口手术", "name_en": "Neuralink", "price": 500000, "icon": "🧠"},
            {"id": "boring", "name_zh": "挖一条隧道", "name_en": "Boring Tunnel", "price": 10000000, "icon": "🚇"},
            {"id": "rocket_launch", "name_zh": "猎鹰9号发射", "name_en": "Falcon 9", "price": 67000000, "icon": "🚀"},
            {"id": "giga", "name_zh": "超级工厂", "name_en": "Giga Factory", "price": 1000000000, "icon": "🏭"},
            {"id": "starship", "name_zh": "星舰飞船", "name_en": "Starship", "price": 3000000000, "icon": "🛸"},
            {"id": "twitter", "name_zh": "收购推特(X)", "name_en": "Buy Twitter", "price": 44000000000, "icon": "🐦"},
            {"id": "mars", "name_zh": "火星殖民地", "name_en": "Mars Colony", "price": 100000000000, "icon": "🪐"},
        ]
    }
}

# ==========================================
# 4. 状态与工具
# ==========================================
if 'char_key' not in st.session_state: st.session_state.char_key = 'jack'
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'visitor_id' not in st.session_state: st.session_state["visitor_id"] = str(uuid.uuid4())
if 'coffee_num' not in st.session_state: st.session_state.coffee_num = 1
if 'payment_method' not in st.session_state: st.session_state.payment_method = 'wechat'

def get_txt(key): return LANG_TEXT[st.session_state.lang][key]
def get_char(): return CHARACTERS[st.session_state.char_key]

def switch_char(key):
    st.session_state.char_key = key
    if key not in st.session_state.cart:
        st.session_state.cart[key] = {}
        for item in CHARACTERS[key]['items']:
            st.session_state.cart[key][item['id']] = 0
switch_char(st.session_state.char_key)

def calculate_balance():
    c_key = st.session_state.char_key
    char_data = CHARACTERS[c_key]
    spent = 0
    current_cart = st.session_state.cart[c_key]
    item_map = {item['id']: item['price'] for item in char_data['items']}
    for item_id, count in current_cart.items():
        if item_id in item_map:
            spent += count * item_map[item_id]
    return char_data['money'] - spent, spent

def update_count(item_id, delta, item_price, current_balance):
    c_key = st.session_state.char_key
    current_count = st.session_state.cart[c_key].get(item_id, 0)
    if delta > 0 and current_balance < item_price:
        st.toast(get_txt("toast_no_money"), icon="⚠️")
        return
    if delta < 0 and current_count <= 0: return
    st.session_state.cart[c_key][item_id] = current_count + delta

def click_item_add(item_id, item_price, current_balance):
    update_count(item_id, 1, item_price, current_balance)

# ==========================================
# 5. CSS (CSS 优化)
# ==========================================
current_char = get_char()
theme_colors = current_char['theme_color']

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap');
    .stApp {{ background-color: #f3f4f6; font-family: 'Inter', sans-serif; }}
    
    /* === 响应式核心布局 === */
    .block-container {{ max-width: 900px !important; padding: 1rem 1rem 3rem 1rem !important; }}
    @media (max-width: 768px) {{ .block-container {{ padding: 0.5rem 0.5rem 2rem 0.5rem !important; }} }}
    
    /* === 人物头像样式 (核心优化) === */
    .char-avatar-container {{
        display: flex; justify-content: center; align-items: center;
        margin-bottom: 8px; position: relative;
    }}
    .char-avatar-img {{
        width: 90px; height: 90px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        z-index: 2;
    }}
    .char-avatar-img.active {{
        border-color: {theme_colors[0]};
        transform: scale(1.1);
        box-shadow: 0 0 0 4px {theme_colors[1]}33, 0 8px 20px rgba(0,0,0,0.15);
    }}
    @media (max-width: 768px) {{ .char-avatar-img {{ width: 70px; height: 70px; }} }}
    
    /* === 其他组件样式 === */
    #MainMenu, footer, header {{visibility: hidden;}}
    .header-container {{
        position: sticky; top: 0; z-index: 999;
        background: linear-gradient(180deg, {theme_colors[0]}ee, {theme_colors[1]}dd);
        backdrop-filter: blur(12px); color: white; padding: 12px 0; text-align: center;
        font-weight: 800; font-size: 2.2rem; font-family: 'JetBrains Mono', monospace;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15); margin-bottom: 25px;
        margin-left: -1rem; margin-right: -1rem; border-radius: 0 0 20px 20px;
    }}
    
    /* 商品卡片 */
    [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] {{
        background: white; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid rgba(229, 231, 235, 0.5);
    }}
   
    /* Emoji 按钮 */
    button[kind="tertiary"] {{
        background-color: transparent !important; border: none !important;
        padding: 0 !important; transition: transform 0.1s !important;
    }}
    button[kind="tertiary"]:hover {{ transform: scale(1.1) !important; }}
    button[kind="tertiary"] p {{
        font-size: 4rem !important; margin: 0 !important; padding-top: 5px !important;
        text-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}
    
    /* 文本与数字 */
    .item-name {{ 
        font-size: 1rem; font-weight: 700; color: #1f2937; 
        height: 36px; display: flex; align-items: center; justify-content: center; 
        line-height: 1.2; text-align: center; margin-bottom: 4px;
    }}
    .item-price {{ 
        color: {theme_colors[1]}; font-weight: 600; font-size: 0.9rem; 
        text-align: center; margin-bottom: 12px; font-family: 'JetBrains Mono', monospace;
    }}
    
    .count-display {{
        text-align: center; line-height: 36px; 
        font-weight: 800; color: #374151; font-size: 1.1rem;
        background: #f9fafb; border-radius: 10px; 
        border: 1px solid #e5e7eb; font-family: 'JetBrains Mono', monospace;
    }}

    /* 账单样式 */
    .bill-container {{ 
        background: white; margin: 30px auto; max-width: 420px; 
        box-shadow: 0 15px 40px rgba(0,0,0,0.12); border-radius: 6px; overflow: hidden; position: relative;
    }}
    .bill-container::after {{
        content: ""; position: absolute; bottom: -5px; left: 0; right: 0; height: 10px;
        background: radial-gradient(circle, transparent 70%, white 75%) 0 0 / 10px 10px repeat-x; transform: rotate(180deg);
    }}
    .bill-footer {{ background: #fafafa; padding: 25px; text-align: center; border-top: 2px dashed #eee; }}
    .bill-wechat-header {{ background: #2AAD67; color: white; padding: 25px; text-align: center; font-weight: 600; }}
    .bill-alipay-header {{ background: #1677ff; color: white; padding: 20px; display: flex; justify-content: space-between; }}
    .bill-paypal-header {{ background: #003087; color: white; padding: 30px; }}
    
    /* 统计条 */
    .stats-bar {{
        display: flex; justify-content: center; gap: 25px; margin-top: 40px; 
        padding: 15px 25px; background-color: white; border-radius: 50px; 
        border: 1px solid #eee; color: #6b7280; font-size: 0.85rem; 
        width: fit-content; margin-left: auto; margin-right: auto; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }}

    /* 右上角按钮样式 */
    .top-btn {{
        width: 100%; padding: 0.5rem 0; background-color: white;
        border: 1px solid #e5e7eb; border-radius: 0.75rem; color: #333;
        font-size: 0.9rem; cursor: pointer; transition: all 0.15s ease; font-weight: 600;
        text-align: center; display: inline-block; text-decoration: none;
    }}
    .top-btn:hover {{ background-color: #f9fafb; border-color: #d1d5db; transform: translateY(-1px); }}

    /* =================================================================
       New Styles: Unified Payment Card Layout
       ================================================================= */
    .pay-card {
        background: #fdfdfd;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-top: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .pay-amount-display {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 800;
        margin: 10px 0;
    }
    .pay-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }
    .pay-instruction {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    
    /* Colors for different payment methods */
    .color-wechat { color: #2AAD67; }
    .color-alipay { color: #1677ff; }
    .color-paypal { color: #003087; }
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# 6. 主页面逻辑
# ==========================================
# 顶部操作栏
st.markdown('<div class="top-actions-bar">', unsafe_allow_html=True)
col_lang, col_more = st.columns([1, 1], gap="small")

with col_lang:
    # 1. 语言切换按钮 (逻辑按钮)
    lang_label = "🌐 EN" if st.session_state.lang == 'zh' else "🌐 中"
    if st.button(lang_label, key="btn_lang", use_container_width=True, type="secondary"):
        st.session_state.lang = 'en' if st.session_state.lang == 'zh' else 'zh'
        st.rerun()

with col_more:
    # 2. 更多乐子按钮 (链接按钮)
    st.link_button(
        label=get_txt('more_label'), 
        url="https://laodeng.streamlit.app/", 
        use_container_width=True, 
        type="secondary"
    )

st.markdown('</div>', unsafe_allow_html=True)

# --- 人物切换区域 (优化版) ---
char_cols = st.columns(3, gap="small")
chars_list = list(CHARACTERS.items())

for idx, (key, data) in enumerate(chars_list):
    with char_cols[idx]:
        is_active = (st.session_state.char_key == key)
        char_name = data['name_zh'] if st.session_state.lang == 'zh' else data['name_en']
        
        # 1. 显示头像
        img_class = "char-avatar-img active" if is_active else "char-avatar-img"
        st.markdown(f"""
            <div class="char-avatar-container">
                <img src="{data['photo_url']}" class="{img_class}" 
                     onerror="this.src='https://api.dicebear.com/7.x/avataaars/svg?seed={key}'">
            </div>
        """, unsafe_allow_html=True)
        
        # 2. 显示按钮
        btn_type = "primary" if is_active else "secondary"
        if st.button(char_name, key=f"sel_btn_{key}", type=btn_type, use_container_width=True):
            if not is_active:
                switch_char(key)
                st.rerun()

# 标题与余额
balance, total_spent = calculate_balance()
c_key = st.session_state.char_key
currency = current_char['currency']
char_name = current_char['name_zh'] if st.session_state.lang == 'zh' else current_char['name_en']

st.markdown(f"<br>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center; font-size: clamp(1.8rem, 5vw, 2.8rem); margin-bottom: 0.2rem; letter-spacing: -1px;'>{get_txt('title').format(name=char_name)}</h1>", unsafe_allow_html=True)
money_str = f"{currency}{current_char['money']:,}"
st.markdown(f"<div style='text-align: center; color: #6b7280; font-weight: 500; margin-bottom: 20px;'>{get_txt('subtitle').format(money=money_str)}</div>", unsafe_allow_html=True)
st.markdown(f"""<div class="header-container">{currency} {balance:,.0f}</div>""", unsafe_allow_html=True)

# 商品展示
items = current_char['items']
cols_per_row = 3
for i in range(0, len(items), cols_per_row):
    cols = st.columns(cols_per_row, gap="small")
    for j in range(cols_per_row):
        if i + j < len(items):
            item = items[i + j]
            item_name = item['name_zh'] if st.session_state.lang == 'zh' else item['name_en']
            with cols[j]:
                with st.container(border=True): 
                    if st.button(item['icon'], key=f"emoji_{c_key}_{item['id']}", use_container_width=True, type="tertiary"):
                        click_item_add(item['id'], item['price'], balance)
                    st.markdown(f"""<div class="item-name">{item_name}</div><div class="item-price">{currency} {item['price']:,}</div>""", unsafe_allow_html=True)
                    b1, b2, b3 = st.columns([1, 1.2, 1], gap="small")
                    with b1: st.button("－", key=f"dec_{c_key}_{item['id']}", on_click=update_count, args=(item['id'], -1, item['price'], balance), use_container_width=True)
                    with b2: st.markdown(f'<div class="count-display">{st.session_state.cart[c_key].get(item["id"], 0)}</div>', unsafe_allow_html=True)
                    with b3: st.button("＋", key=f"inc_{c_key}_{item['id']}", on_click=update_count, args=(item['id'], 1, item['price'], balance), type="primary", use_container_width=True)

# E. 账单与分享功能
if total_spent > 0:
    st.markdown("<br><br>", unsafe_allow_html=True)
    bill_type = current_char['bill_type']
    
    purchased_items = []
    item_count_total = 0
    for item in items:
        cnt = st.session_state.cart[c_key].get(item['id'], 0)
        if cnt > 0:
            name = item['name_zh'] if st.session_state.lang == 'zh' else item['name_en']
            purchased_items.append((name, cnt, item['price'] * cnt))
            item_count_total += cnt

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://mababa.streamlit.app"
    
    # 账单 HTML
    bill_html = ""
    if bill_type == 'wechat':
        bill_html = f"""
        <div class="bill-container bill-wechat">
            <div class="bill-wechat-header"><span>{get_txt('pay_wechat')}</span></div>
            <div class="bill-wechat-total">{currency}{total_spent:,.0f}</div>
            <div style="text-align: center; color: #666; margin-bottom: 20px;">{get_txt('total_spent')}</div>
            <div style="padding: 0 25px;"><hr style="border-top: 1px solid #eee; margin: 10px 0;">
                <div style="max-height: 400px; overflow-y: auto;">
        """
        for name, cnt, cost in purchased_items:
            bill_html += f"""<div style="display: flex; justify-content: space-between; margin: 12px 0; font-size: 0.95rem; color: #333;"><span>{name} x{cnt}</span><span style="font-weight: bold;">{currency}{cost:,.0f}</span></div>"""
        bill_html += f"""</div></div>
            <div class="bill-footer"><div style="color: #999; font-size: 0.85rem; margin-bottom: 8px;">{get_txt('scan_to_play')}</div><img src="{qr_url}" style="width: 100px; height: 100px; mix-blend-mode: multiply;"></div>
        </div>"""
    elif bill_type == 'alipay':
        bill_html = f"""
        <div class="bill-container bill-alipay">
            <div class="bill-alipay-header"><span>{'<'}</span><span>{get_txt('receipt_title')}</span><span>...</span></div>
            <div style="padding: 15px;">
        """
        for name, cnt, cost in purchased_items:
            bill_html += f"""<div style="display: flex; justify-content: space-between; padding: 12px 15px; border-bottom: 1px solid #f5f5f5; font-size: 0.95rem;"><span style="color: #333;">{name} x{cnt}</span><span style="font-weight: bold; color: #333;">-{currency}{cost:,.0f}</span></div>"""
        bill_html += f"""</div>
            <div class="bill-alipay-total">{get_txt('total_spent')}: <span style="font-size: 1.6rem; color: #1677ff;">{currency}{total_spent:,.0f}</span></div>
            <div class="bill-footer"><div style="display: flex; align-items: center; justify-content: center; gap: 15px;"><img src="{qr_url}" style="width: 80px; height: 80px;"><div style="text-align: left; font-size: 0.85rem; color: #999;"><div>{get_txt('scan_to_play')}</div><div style="color: #1677ff; font-weight:bold;">PK Billionaires</div></div></div></div>
        </div>"""
    else: # PayPal
        bill_html = f"""
        <div class="bill-container bill-paypal">
            <div class="bill-paypal-header"><div class="bill-paypal-logo" style="font-size: 1.5rem; font-weight: 900; font-style: italic;">PayPal</div><div style="font-size: 0.9rem; opacity: 0.8;">{datetime.datetime.now().strftime('%Y-%m-%d')}</div></div>
            <div class="bill-paypal-total">{currency}{total_spent:,.0f}</div>
            <div style="padding: 0 30px;"><div style="font-size: 0.85rem; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px;">DETAILS</div>
        """
        for name, cnt, cost in purchased_items:
            bill_html += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f0f0; font-size: 0.95rem;"><span>{name} ({cnt})</span><span>{currency}{cost:,.0f}</span></div>"""
        bill_html += f"""</div>
            <div class="bill-footer" style="margin-top: 30px;"><img src="{qr_url}" style="width: 80px; height: 80px;"><div style="font-size: 0.8rem; color: #aaa; margin-top: 8px;">Scan to challenge Elon</div></div>
        </div>"""

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(bill_html, unsafe_allow_html=True)
        
        # 分享弹窗
        st.write("")
        @st.dialog(get_txt("share_modal_title"), width="large")
        def show_share_modal(html, amount, count):
            st.markdown(html, unsafe_allow_html=True)
            share_text = get_txt('share_copy_text').format(amount=amount, item_count=count)
            st.markdown(f"""
                <div style="margin-top: 25px; padding: 20px; background: #f8fafc; border-radius: 12px; text-align: center; border:1px solid #e2e8f0;">
                    <div style="font-weight: 700; color: #333; margin-bottom: 10px;">{get_txt('share_prompt')}</div>
                    <code style="display: block; padding: 12px; background: white; border: 1px solid #cbd5e1; border-radius: 6px; color: #475569; word-break: break-all; font-family: 'JetBrains Mono', monospace;">{share_text}</code>
                </div>
            """, unsafe_allow_html=True)

        if st.button(get_txt("share_btn"), type="primary", use_container_width=True):
            show_share_modal(bill_html, f"{currency}{total_spent:,.0f}", item_count_total)

    if balance == 0:
        st.balloons()
        st.success(get_txt('balance_zero'))
        
# ==========================================
# 7. 底部咖啡 & 统计 (UI 统一优化版)
# ==========================================
st.markdown("<br><br>", unsafe_allow_html=True)
c_btn_col1, c_btn_col2, c_btn_col3 = st.columns([1, 2, 1])
with c_btn_col2:
    @st.dialog(" " + get_txt('coffee_title'), width="small")
    def show_coffee_window():
        st.markdown(f"""<div style="text-align:center; color:#666; margin-bottom:15px;">{get_txt('coffee_desc')}</div>""", unsafe_allow_html=True)
        
        # 快捷按钮
        presets = [("☕", 1), ("🍗", 3), ("🚀", 5)]
        def set_val(n): st.session_state.coffee_num = n
        cols = st.columns(3, gap="small")
        for i, (icon, num) in enumerate(presets):
            with cols[i]:
                if st.button(f"{icon} {num}", use_container_width=True, key=f"p_btn_{i}"): set_val(num)
        st.write("")

        # 输入与计算
        col_amount, col_total = st.columns([1, 1], gap="small")
        with col_amount: 
            cnt = st.number_input(get_txt('coffee_amount'), 1, 100, step=1, key='coffee_num')
        
        cny_total = cnt * 10
        usd_total = cnt * 2
        
        with col_total: 
            st.markdown(f"""<div style="background:#fff1f2; border-radius:8px; padding:8px; text-align:center; color:#e11d48; font-weight:bold; font-size:1.5rem; height: 100%; display: flex; align-items: center; justify-content: center;">¥{cny_total}</div>""", unsafe_allow_html=True)
        
        # 统一支付卡片渲染函数
        def render_pay_tab(title, amount_str, color_class, img_path, qr_data_suffix, link_url=None):
            st.markdown(f"""
                <div class="pay-card">
                    <div class="pay-label {color_class}">{title}</div>
                    <div class="pay-amount-display {color_class}">{amount_str}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # 显示二维码 (或Logo)
            # 使用 container 居中图片
            c1, c2, c3 = st.columns([1, 3, 1])
            with c2:
                if os.path.exists(img_path): 
                    st.image(img_path, use_container_width=True)
                else: 
                    # 备用二维码生成
                    qr_data = f"Donate_{cny_total}_{qr_data_suffix}"
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={qr_data}", use_container_width=True)
            
            # 如果是PayPal等需要外链的，显示按钮
            if link_url:
                st.link_button(f"👉 Pay {amount_str}", link_url, type="primary", use_container_width=True)
            else:
                st.markdown('<div class="pay-instruction">请使用手机扫描上方二维码</div>', unsafe_allow_html=True)

        # 支付方式 Tabs
        st.write("")
        t1, t2, t3 = st.tabs([get_txt('pay_wechat'), get_txt('pay_alipay'), get_txt('pay_paypal')])
        
        with t1:
            render_pay_tab("WeChat Pay", f"¥{cny_total}", "color-wechat", "wechat_pay.jpg", "WeChat")
            
        with t2:
            render_pay_tab("Alipay", f"¥{cny_total}", "color-alipay", "ali_pay.jpg", "Alipay")
            
        with t3:
            # PayPal 特殊处理：使用 paypal.png (如果不存在则用API生成二维码作为占位), 并提供链接
            # 这里的 qr_data_suffix 设为 PayPal 仅用于生成备用图
            render_pay_tab("PayPal", f"${usd_total}", "color-paypal", "paypal.png", "PayPal", "https://paypal.me/yourid")
        
        st.write("")
        if st.button("🎉 " + get_txt('pay_success').split('!')[0], type="primary", use_container_width=True):
            st.balloons()
            st.success(get_txt('pay_success').format(count=cnt))
            time.sleep(1)
            st.rerun()

    if st.button(get_txt('coffee_btn'), use_container_width=True):
        show_coffee_window()

# 数据库统计
DB_DIR = os.path.expanduser("~/")
DB_FILE = os.path.join(DB_DIR, "visit_stats.db")
def track_stats():
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS daily_traffic (date TEXT PRIMARY KEY, pv_count INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS visitors (visitor_id TEXT PRIMARY KEY, last_visit_date TEXT)''')
        today = datetime.datetime.utcnow().date().isoformat()
        vid = st.session_state["visitor_id"]
        if "has_counted" not in st.session_state:
            c.execute("INSERT OR IGNORE INTO daily_traffic (date, pv_count) VALUES (?, 0)", (today,))
            c.execute("UPDATE daily_traffic SET pv_count = pv_count + 1 WHERE date=?", (today,))
            c.execute("INSERT OR REPLACE INTO visitors (visitor_id, last_visit_date) VALUES (?, ?)", (vid, today))
            conn.commit()
            st.session_state["has_counted"] = True
        t_uv = c.execute("SELECT COUNT(*) FROM visitors WHERE last_visit_date=?", (today,)).fetchone()[0]
        a_uv = c.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
        t_pv = c.execute("SELECT pv_count FROM daily_traffic WHERE date=?", (today,)).fetchone()[0]
        conn.close()
        return t_uv, a_uv, t_pv
    except: return 0, 0, 0

today_uv, total_uv, today_pv = track_stats()
st.markdown(f"""
<div class="stats-bar">
    <div style="text-align: center;"><div>{get_txt('visitor_today')}</div><div style="font-weight:700; color:#111;">{today_uv}</div></div>
    <div style="border-left:1px solid #eee; padding-left:25px; text-align: center;"><div>{get_txt('visitor_total')}</div><div style="font-weight:700; color:#111;">{total_uv}</div></div>
</div><br><br>
""", unsafe_allow_html=True)

# 移动端检测
try:
    user_agent = st.context.headers.get('User-Agent', '')
    if any(mobile in user_agent.lower() for mobile in ['mobile', 'android', 'iphone', 'ipad']):
        st.session_state.is_mobile = True
except:
    st.session_state.is_mobile = False
