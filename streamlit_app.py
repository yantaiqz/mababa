import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time

# ==========================================
# 1. 基础配置
# ==========================================
st.set_page_config(
    page_title="花光大佬的钱 | Spend Billions",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 数据配置
# ==========================================

# --- A. 多语言文本映射 ---
LANG_TEXT = {
    "zh": {
        "title": "花光{name}的钱",
        "subtitle": "你现在拥有 **{money}**。这钱不花完，别想下班！",
        "receipt_title": "购物清单", # 通用兜底
        "total_spent": "实付金额",
        "balance_zero": "恭喜你！你已经身无分文，可以安心退休了！",
        "toast_no_money": "余额不足！大佬也要精打细算！",
        "coffee_btn": "☕ 请开发者喝咖啡",
        "coffee_title": "☕ 支持作者",
        "coffee_desc": "如果这个小游戏让你摸鱼更快乐，欢迎投喂！",
        "pay_wechat": "微信支付",
        "pay_alipay": "支付宝",
        "pay_paypal": "PayPal",
        "unit_cn": "杯",
        "unit_total": "总计投入",
        "pay_success": "收到！感谢你的 {count} 杯咖啡！代码写得更有劲了！❤️",
        "visitor_today": "今日 UV",
        "visitor_total": "历史 UV",
        "share_prompt": "👇 截图或复制下方文案分享给朋友",
        "share_copy_text": "我在《花光大佬的钱》里挥霍了 {amount}！买了 {item_count} 件离谱商品，你也来试试？👉 https://spend-billions.streamlit.app",
        "scan_to_play": "长按识别二维码挑战"
    },
    "en": {
        "title": "Spend {name}'s Money",
        "subtitle": "You have **{money}**. Spend it all before you can leave!",
        "receipt_title": "Receipt",
        "total_spent": "Total Paid",
        "balance_zero": "Congratulations! You are broke and free!",
        "toast_no_money": "Not enough money!",
        "coffee_btn": "☕ Buy me a coffee",
        "coffee_title": "☕ Support Me",
        "coffee_desc": "If you enjoyed this, consider buying me a coffee!",
        "pay_wechat": "WeChat Pay",
        "pay_alipay": "Alipay",
        "pay_paypal": "PayPal",
        "unit_cn": "Cups",
        "unit_total": "Total",
        "pay_success": "Received! Thanks for {count} cups! ❤️",
        "visitor_today": "Today UV",
        "visitor_total": "Total UV",
        "share_prompt": "👇 Screenshot or Copy text to share",
        "share_copy_text": "I spent {amount} in 'Spend Billions'! Bought {item_count} items. Can you beat me? 👉 https://spend-billions.streamlit.app",
        "scan_to_play": "Scan to Play"
    }
}

# --- B. 人物配置 (含账单类型) ---
CHARACTERS = {
    "jack": {
        "name_zh": "马云",
        "name_en": "Jack Ma",
        "avatar": "👨🏻‍🏫",
        "money": 200_000_000_000,
        "currency": "¥",
        "bill_type": "alipay", # 支付宝
        "theme_color": ["#1677ff", "#4096ff"], # 支付宝蓝
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
        "bill_type": "wechat", # 微信
        "theme_color": ["#2aad67", "#20c06d"], # 微信绿
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
        "money": 250_000_000_000, # 美元
        "currency": "$",
        "bill_type": "paypal", # PayPal
        "theme_color": ["#003087", "#009cde"], # PayPal 蓝
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
# 3. 状态与工具
# ==========================================
if 'lang' not in st.session_state:
    st.session_state.lang = 'zh'
if 'char_key' not in st.session_state:
    st.session_state.char_key = 'jack'
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'visitor_id' not in st.session_state:
    st.session_state["visitor_id"] = str(uuid.uuid4())

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

# ==========================================
# 4. CSS (适配不同账单风格)
# ==========================================
current_char = get_char()
theme_colors = current_char['theme_color']

st.markdown(f"""
<style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background-color: #f1f2f6; }}
    
    /* 顶部导航 */
    .header-container {{
        position: sticky; top: 0; z-index: 999;
        background: linear-gradient(180deg, {theme_colors[0]}, {theme_colors[1]});
        color: white; padding: 10px 0; text-align: center;
        font-weight: 800; font-size: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;
    }}
    
    /* 商品卡片 - 紧凑 */
    .item-card {{
        background: white; padding: 12px 6px; border-radius: 8px;
        text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        height: 100%; display: flex; flex-direction: column; justify-content: space-between;
    }}
    .item-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
    
    /* Emoji 按钮 */
    .emoji-btn-container button {{
        background: transparent !important; border: none !important;
        font-size: 2.8rem !important; padding: 0 !important; line-height: 1.2 !important;
    }}
    .emoji-btn-container button:hover {{ transform: scale(1.1); transition: transform 0.2s; }}
    .emoji-btn-container button:active {{ transform: scale(0.95); }}
    
    .item-name {{ font-size: 0.9rem; font-weight: bold; color: #333; margin: 5px 0; height: 35px; display: flex; align-items: center; justify-content: center; line-height: 1.1; }}
    .item-price {{ color: {theme_colors[1]}; font-weight: bold; font-size: 0.85rem; margin-bottom: 5px; }}
    div.stButton > button {{ padding: 0.2rem 0.5rem; font-size: 0.8rem; }}
    
    /* --- 账单公共样式 --- */
    .bill-container {{
        background: white; margin: 0 auto; max-width: 400px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    .bill-footer {{
        background: #f9f9f9; padding: 15px; text-align: center; border-top: 1px dashed #ddd;
    }}
    
    /* 微信样式 */
    .bill-wechat {{ border-radius: 8px; }}
    .bill-wechat-header {{ background: #2AAD67; color: white; padding: 15px; text-align: center; font-weight: bold; }}
    .bill-wechat-total {{ font-size: 2.2rem; font-weight: bold; text-align: center; margin: 20px 0 5px 0; color: #000; }}
    .bill-wechat-label {{ text-align: center; color: #666; font-size: 0.9rem; margin-bottom: 20px; }}
    
    /* 支付宝样式 */
    .bill-alipay {{ border-radius: 8px; }}
    .bill-alipay-header {{ background: #1677ff; color: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; }}
    .bill-alipay-row {{ display: flex; justify-content: space-between; padding: 12px 15px; border-bottom: 1px solid #f5f5f5; font-size: 0.95rem; }}
    .bill-alipay-total {{ padding: 15px; text-align: right; font-weight: bold; font-size: 1.2rem; border-top: 1px solid #eee; }}
    
    /* PayPal 样式 */
    .bill-paypal {{ border: 1px solid #e0e0e0; border-radius: 4px; }}
    .bill-paypal-header {{ background: #003087; color: white; padding: 20px; }}
    .bill-paypal-logo {{ font-size: 1.5rem; font-weight: 900; font-style: italic; }}
    .bill-paypal-total {{ font-size: 2.5rem; color: #003087; text-align: center; margin: 20px 0; font-weight: 300; }}

    /* 裂变二维码 */
    .qr-box {{ margin-top: 10px; padding: 10px; background: white; border-radius: 8px; display: inline-block; }}
    .share-area {{ margin-top: 20px; padding: 15px; background: #eef2f5; border-radius: 8px; text-align: center; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. 主页面逻辑
# ==========================================

# A. 导航
col_logo, col_chars, col_lang = st.columns([1, 6, 1])
with col_chars:
    c_cols = st.columns(len(CHARACTERS) + 2)
    idx = 1
    for key, data in CHARACTERS.items():
        with c_cols[idx]:
            if st.button(f"{data['avatar']} {data['name_zh' if st.session_state.lang == 'zh' else 'name_en']}", key=f"btn_char_{key}"):
                switch_char(key)
                st.rerun()
        idx += 1
with col_lang:
    if st.button("EN" if st.session_state.lang == 'zh' else "中", use_container_width=True):
        st.session_state.lang = 'en' if st.session_state.lang == 'zh' else 'zh'
        st.rerun()

# B. 余额展示
balance, total_spent = calculate_balance()
c_key = st.session_state.char_key
currency = current_char['currency']
char_name = current_char['name_zh'] if st.session_state.lang == 'zh' else current_char['name_en']

st.markdown(f"<h1 style='text-align: center;'>{get_txt('title').format(name=char_name)}</h1>", unsafe_allow_html=True)
money_str = f"{currency}{current_char['money']:,}"
st.markdown(f"<div style='text-align: center; color: #666; font-size: 0.9rem; margin-bottom: 10px;'>{get_txt('subtitle').format(money=money_str)}</div>", unsafe_allow_html=True)
st.markdown(f"""<div class="header-container">{currency} {balance:,.0f}</div>""", unsafe_allow_html=True)

# C. 商品网格 (4列)
items = current_char['items']
cols_per_row = 4
for i in range(0, len(items), cols_per_row):
    cols = st.columns(cols_per_row)
    for j in range(cols_per_row):
        if i + j < len(items):
            item = items[i + j]
            item_name = item['name_zh'] if st.session_state.lang == 'zh' else item['name_en']
            with cols[j]:
                with st.container():
                    st.markdown('<div class="item-card">', unsafe_allow_html=True)
                    # 点击 Emoji 加购
                    st.markdown('<div class="emoji-btn-container">', unsafe_allow_html=True)
                    if st.button(item['icon'], key=f"add_{c_key}_{item['id']}", help="+1"):
                        update_count(item['id'], 1, item['price'], balance)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown(f"""<div class="item-name">{item_name}</div><div class="item-price">{currency} {item['price']:,}</div></div>""", unsafe_allow_html=True)
                    
                    b1, b2, b3 = st.columns([1.2, 1.5, 1.2])
                    with b1: st.button("－", key=f"dec_{c_key}_{item['id']}", on_click=update_count, args=(item['id'], -1, item['price'], balance), use_container_width=True)
                    with b2:
                        cnt = st.session_state.cart[c_key].get(item['id'], 0)
                        st.markdown(f"<div style='text-align: center; line-height: 2.2rem; font-weight: bold; color:#444;'>{cnt}</div>", unsafe_allow_html=True)
                    with b3: st.button("＋", key=f"inc_{c_key}_{item['id']}", on_click=update_count, args=(item['id'], 1, item['price'], balance), type="primary", use_container_width=True)
                    st.write("")

# D. 账单生成 (皮肤化 + 裂变)
if total_spent > 0:
    st.markdown("---")
    bill_type = current_char['bill_type']
    
    # 准备账单数据
    purchased_items = []
    item_count_total = 0
    for item in items:
        cnt = st.session_state.cart[c_key].get(item['id'], 0)
        if cnt > 0:
            name = item['name_zh'] if st.session_state.lang == 'zh' else item['name_en']
            purchased_items.append((name, cnt, item['price'] * cnt))
            item_count_total += cnt

    # --- 生成 HTML ---
    # 模拟二维码 API
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://spend-billions.streamlit.app"
    
    # 1. 微信风格
    if bill_type == 'wechat':
        bill_html = f"""
        <div class="bill-container bill-wechat">
            <div class="bill-wechat-header">
                <span>{get_txt('pay_wechat')}</span>
            </div>
            <div class="bill-wechat-total">{currency}{total_spent:,.0f}</div>
            <div class="bill-wechat-label">{get_txt('total_spent')}</div>
            <div style="padding: 0 20px;">
                <hr style="border-top: 1px solid #eee; margin: 10px 0;">
                <div style="max-height: 300px; overflow-y: auto;">
        """
        for name, cnt, cost in purchased_items:
            bill_html += f"""
                <div style="display: flex; justify-content: space-between; margin: 8px 0; font-size: 0.9rem; color: #333;">
                    <span>{name} x{cnt}</span>
                    <span style="font-weight: bold;">{currency}{cost:,.0f}</span>
                </div>"""
        bill_html += f"""
                </div>
            </div>
            <div class="bill-footer">
                <div style="color: #999; font-size: 0.8rem; margin-bottom: 5px;">{get_txt('scan_to_play')}</div>
                <img src="{qr_url}" style="width: 80px; height: 80px; mix-blend-mode: multiply;">
            </div>
        </div>
        """

    # 2. 支付宝风格
    elif bill_type == 'alipay':
        bill_html = f"""
        <div class="bill-container bill-alipay">
            <div class="bill-alipay-header">
                <span>{'<'}</span>
                <span>{get_txt('receipt_title')}</span>
                <span>...</span>
            </div>
            <div style="padding: 10px;">
        """
        for name, cnt, cost in purchased_items:
            bill_html += f"""
                <div class="bill-alipay-row">
                    <span style="color: #333;">{name} x{cnt}</span>
                    <span style="font-weight: bold; color: #333;">-{currency}{cost:,.0f}</span>
                </div>"""
        bill_html += f"""
            </div>
            <div class="bill-alipay-total">
                {get_txt('total_spent')}: <span style="font-size: 1.5rem; color: #1677ff;">{currency}{total_spent:,.0f}</span>
            </div>
            <div class="bill-footer">
                <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                    <img src="{qr_url}" style="width: 60px; height: 60px;">
                    <div style="text-align: left; font-size: 0.8rem; color: #999;">
                        <div>{get_txt('scan_to_play')}</div>
                        <div style="color: #1677ff;">PK Billionaires</div>
                    </div>
                </div>
            </div>
        </div>
        """

    # 3. PayPal 风格
    else:
        bill_html = f"""
        <div class="bill-container bill-paypal">
            <div class="bill-paypal-header">
                <div class="bill-paypal-logo">PayPal</div>
                <div style="font-size: 0.8rem; opacity: 0.8;">{datetime.datetime.now().strftime('%Y-%m-%d')}</div>
            </div>
            <div class="bill-paypal-total">
                {currency}{total_spent:,.0f}
            </div>
            <div style="padding: 0 20px;">
                <div style="font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Details</div>
        """
        for name, cnt, cost in purchased_items:
            bill_html += f"""
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0; font-size: 0.9rem;">
                    <span>{name} ({cnt})</span>
                    <span>{currency}{cost:,.0f}</span>
                </div>"""
        bill_html += f"""
            </div>
            <div class="bill-footer" style="margin-top: 20px;">
                <img src="{qr_url}" style="width: 60px; height: 60px;">
                <div style="font-size: 0.7rem; color: #aaa; margin-top: 5px;">Scan to challenge Elon</div>
            </div>
        </div>
        """

    # 渲染账单
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(bill_html, unsafe_allow_html=True)
        
        # 裂变文案复制区
        share_text = get_txt('share_copy_text').format(amount=f"{currency}{total_spent:,.0f}", item_count=item_count_total)
        st.markdown(f"""
        <div class="share-area">
            <div style="font-weight: bold; color: #333; margin-bottom: 8px;">{get_txt('share_prompt')}</div>
            <code style="display: block; padding: 10px; background: white; border: 1px solid #ddd; border-radius: 4px; color: #555;">{share_text}</code>
        </div>
        """, unsafe_allow_html=True)

    if balance == 0:
        st.balloons()
        st.success(get_txt('balance_zero'))

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 6. 底部功能 (数据库 & 咖啡)
# ==========================================
# ... (保留原有的 Coffee 和 Database 逻辑，为节省篇幅此处省略，实际使用请粘贴上个版本代码的最后部分) ...
# 为了完整性，这里补充简化的咖啡入口
c_btn_col1, c_btn_col2, c_btn_col3 = st.columns([1, 2, 1])
with c_btn_col2:
    if st.button(get_txt('coffee_btn'), use_container_width=True):
        st.toast("☕ 感谢支持！(功能代码请参考上一版)", icon="❤️")

# 简单统计显示 (占位)
st.markdown(f"""
<div class="metric-container">
    <div class="metric-box"><div class="metric-sub">{get_txt('visitor_today')}: 1024</div></div>
    <div class="metric-box" style="border-left:1px solid #ddd; padding-left:10px;"><div class="metric-sub">{get_txt('visitor_total')}: 8848</div></div>
</div><br>
""", unsafe_allow_html=True)
