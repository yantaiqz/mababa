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
# 2. 数据配置
# ==========================================

# --- A. 多语言文本映射 ---
LANG_TEXT = {
    "zh": {
        "title": "花光{name}的钱",
        "subtitle": "你现在拥有 **{money}**。这钱不花完，别想下班！",
        "receipt_title": "购物清单",
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
        "scan_to_play": "长按识别二维码挑战",
        "pv_today": "今日 PV"
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
        "scan_to_play": "Scan to Play",
        "pv_today": "Today PV"
    }
}

# --- B. 人物与商品配置 (扩充至14个) ---
CHARACTERS = {
    "jack": {
        "name_zh": "马云",
        "name_en": "Jack Ma",
        "avatar": "👨🏻‍🏫",
        "money": 200_000_000_000,
        "currency": "¥",
        "bill_type": "alipay",
        "theme_color": ["#1677ff", "#4096ff"],
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
if 'coffee_num' not in st.session_state:
    st.session_state.coffee_num = 1

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

# 点击 Emoji 直接购买的辅助函数
def click_item_add(item_id, item_price, current_balance):
    update_count(item_id, 1, item_price, current_balance)

# ==========================================
# 4. CSS (核心样式 - 修复显示问题)
# ==========================================
current_char = get_char()
theme_colors = current_char['theme_color']

st.markdown(f"""
<style>
    /* 基础重置 */
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ 
        background-color: #f1f2f6; 
        padding: 0 10px;
    }}
    
    /* 顶部导航 */
    .header-container {{
        position: sticky; top: 0; z-index: 999;
        background: linear-gradient(180deg, {theme_colors[0]}, {theme_colors[1]});
        color: white; padding: 10px 0; text-align: center;
        font-weight: 800; font-size: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
        border-radius: 8px;
    }}
    
    /* 商品卡片包装器 - 关键修复 */
    .card-wrapper {{
        background: white; 
        border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        padding: 15px;
        height: 220px;  /* 固定高度确保显示完整 */
        display: flex;
        flex-direction: column;
        justify-content: space-around;  /* 均匀分布内容 */
        border: 1px solid transparent;
        transition: all 0.2s;
        margin-bottom: 15px;  /* 增加卡片间距 */
    }}
    .card-wrapper:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        border-color: {theme_colors[0]};
    }}

    /* Emoji 按钮样式 - 完全重构 */
    .emoji-btn {{
        background: transparent !important;
        border: none !important;
        font-size: 3.5rem !important;
        line-height: 1 !important;
        padding: 10px 0 !important;
        margin: 0 auto !important;
        display: block !important;
        width: 100% !important;
        box-shadow: none !important;
        color: inherit !important;
    }}
    .emoji-btn:hover {{ 
        transform: scale(1.1); 
        color: {theme_colors[0]} !important;
    }}
    .emoji-btn:active {{ 
        transform: scale(0.95); 
    }}
    
    /* 文字信息 - 优化排版 */
    .item-info {{ 
        text-align: center; 
        margin: 5px 0;
        flex-grow: 0;
    }}
    .item-name {{ 
        font-size: 1rem; 
        font-weight: bold; 
        color: #333; 
        min-height: 40px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        line-height: 1.2;
        padding: 0 5px;
    }}
    .item-price {{ 
        color: {theme_colors[1]}; 
        font-weight: bold; 
        font-size: 0.95rem; 
        margin: 5px 0;
    }}
    
    /* 操作按钮容器 - 修复布局 */
    .btn-group {{
        display: flex;
        gap: 5px;
        margin-top: 10px;
    }}
    .btn-group button {{
        flex: 1;
        padding: 6px 0 !important;
        font-size: 1rem !important;
        border-radius: 6px !important;
    }}
    .count-display {{
        text-align: center;
        font-weight: bold;
        color: #444;
        font-size: 1.1rem;
        line-height: 2.2rem;
    }}

    /* 全局容器限制 */
    .content-container {{ 
        max-width: 1000px; 
        margin: 0 auto;
        padding: 0 15px;
    }}
    
    /* --- 账单样式 --- */
    .bill-container {{ 
        background: white; 
        margin: 20px auto; 
        max-width: 400px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
        overflow: hidden;
        border-radius: 8px;
    }}
    .bill-footer {{ 
        background: #f9f9f9; 
        padding: 15px; 
        text-align: center; 
        border-top: 1px dashed #ddd;
    }}
    /* 微信 */
    .bill-wechat-header {{ 
        background: #2AAD67; 
        color: white; 
        padding: 15px; 
        text-align: center; 
        font-weight: bold; 
        font-size: 1.1rem;
    }}
    .bill-wechat-total {{ 
        font-size: 2.2rem; 
        font-weight: bold; 
        text-align: center; 
        margin: 20px 0 5px 0; 
        color: #000; 
    }}
    .bill-wechat-label {{ 
        text-align: center; 
        color: #666; 
        font-size: 0.9rem; 
        margin-bottom: 20px; 
    }}
    /* 支付宝 */
    .bill-alipay-header {{ 
        background: #1677ff; 
        color: white; 
        padding: 15px; 
        display: flex; 
        justify-content: space-between; 
        font-size: 1.1rem;
    }}
    .bill-alipay-row {{ 
        display: flex; 
        justify-content: space-between; 
        padding: 12px 15px; 
        border-bottom: 1px solid #f5f5f5; 
        font-size: 0.95rem; 
    }}
    .bill-alipay-total {{ 
        padding: 15px; 
        text-align: right; 
        font-weight: bold; 
        font-size: 1.2rem; 
        border-top: 1px solid #eee; 
    }}
    /* PayPal */
    .bill-paypal {{ 
        border: 1px solid #e0e0e0; 
        border-radius: 4px; 
    }}
    .bill-paypal-header {{ 
        background: #003087; 
        color: white; 
        padding: 20px; 
        display: flex;
        justify-content: space-between;
    }}
    .bill-paypal-total {{ 
        font-size: 2.5rem; 
        color: #003087; 
        text-align: center; 
        margin: 20px 0; 
        font-weight: 300; 
    }}
    
    /* 咖啡打赏 */
    .coffee-card {{
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e5e7eb; 
        border-radius: 12px;
        padding: 15px; 
        text-align: center;
        margin-bottom: 15px;
    }}
    .price-number {{ 
        color: #d9534f; 
        font-weight: 900; 
        font-size: 1.5rem; 
    }}
    
    /* 统计信息 */
    .stats-container {{
        display: flex; 
        justify-content: center; 
        gap: 20px; 
        margin: 20px auto; 
        padding: 12px; 
        background-color: #f8f9fa; 
        border-radius: 8px; 
        border: 1px solid #e9ecef; 
        color: #666; 
        font-size: 0.9rem; 
        max-width: 500px;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. 主页面逻辑
# ==========================================

# 全局居中容器
st.markdown('<div class="content-container">', unsafe_allow_html=True)

# A. 导航栏
col_logo, col_chars, col_lang = st.columns([1, 8, 1])
with col_chars:
    # 人物切换按钮 - 均匀分布
    char_btns = st.columns(len(CHARACTERS))
    for idx, (key, data) in enumerate(CHARACTERS.items()):
        with char_btns[idx]:
            btn_label = f"{data['avatar']} {data['name_zh' if st.session_state.lang == 'zh' else 'name_en']}"
            if st.button(btn_label, key=f"btn_char_{key}", use_container_width=True):
                switch_char(key)
                st.rerun()
with col_lang:
    lang_btn_label = "🇺🇸 EN" if st.session_state.lang == 'zh' else "🇨🇳 中文"
    if st.button(lang_btn_label, use_container_width=True):
        st.session_state.lang = 'en' if st.session_state.lang == 'zh' else 'zh'
        st.rerun()

# B. 余额展示
balance, total_spent = calculate_balance()
c_key = st.session_state.char_key
currency = current_char['currency']
char_name = current_char['name_zh'] if st.session_state.lang == 'zh' else current_char['name_en']

# 标题和副标题
st.markdown(f"<h1 style='text-align: center; margin: 10px 0; font-size:2rem;'>{get_txt('title').format(name=char_name)}</h1>", unsafe_allow_html=True)
money_str = f"{currency}{current_char['money']:,}"
st.markdown(f"""
<div style='text-align: center; color: #666; font-size: 1rem; margin-bottom: 15px;'>
    {get_txt('subtitle').format(money=money_str)}
</div>
""", unsafe_allow_html=True)

# 悬浮余额条
st.markdown(f"""
<div class="header-container">
    {currency} {balance:,.0f}
</div>
""", unsafe_allow_html=True)

# C. 商品网格 (3列布局 - 核心修复)
items = current_char['items']
cols_per_row = 3
# 计算需要多少行
total_rows = (len(items) + cols_per_row - 1) // cols_per_row

# 逐行渲染商品
for row_idx in range(total_rows):
    # 取当前行的商品
    start_idx = row_idx * cols_per_row
    end_idx = min(start_idx + cols_per_row, len(items))
    row_items = items[start_idx:end_idx]
    
    # 创建3列（即使最后一行商品不足3个）
    cols = st.columns([1]*cols_per_row, gap="medium")
    
    # 渲染当前行的商品
    for col_idx, item in enumerate(row_items):
        with cols[col_idx]:
            item_name = item['name_zh'] if st.session_state.lang == 'zh' else item['name_en']
            
            # 商品卡片
            st.markdown('<div class="card-wrapper">', unsafe_allow_html=True)
            
            # 1. Emoji 购买按钮 (核心修复：独立按钮+正确样式)
            emoji_btn_key = f"emoji_{c_key}_{item['id']}"
            if st.button(
                item['icon'],
                key=emoji_btn_key,
                help=get_txt('toast_no_money'),
                use_container_width=True
            ):
                click_item_add(item['id'], item['price'], balance)
            # 为Emoji按钮添加样式类
            st.markdown(f"""
            <style>
                button[data-testid="baseButton-{emoji_btn_key}"] {{
                    class: "emoji-btn";
                    background: transparent !important;
                    border: none !important;
                    font-size: 3.5rem !important;
                    line-height: 1 !important;
                    padding: 10px 0 !important;
                    margin: 0 auto !important;
                    display: block !important;
                    width: 100% !important;
                    box-shadow: none !important;
                    color: inherit !important;
                }}
                button[data-testid="baseButton-{emoji_btn_key}"]:hover {{
                    transform: scale(1.1);
                    color: {theme_colors[0]} !important;
                }}
            </style>
            """, unsafe_allow_html=True)
            
            # 2. 商品信息
            st.markdown(f"""
            <div class="item-info">
                <div class="item-name">{item_name}</div>
                <div class="item-price">{currency} {item['price']:,}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 3. 操作按钮组 (-/数量/+)
            st.markdown('<div class="btn-group">', unsafe_allow_html=True)
            b1, b2, b3 = st.columns([1, 1.5, 1], gap="small")
            
            with b1:
                st.button(
                    "－",
                    key=f"dec_{c_key}_{item['id']}",
                    on_click=update_count,
                    args=(item['id'], -1, item['price'], balance),
                    use_container_width=True
                )
            
            with b2:
                cnt = st.session_state.cart[c_key].get(item['id'], 0)
                st.markdown(f"<div class='count-display'>{cnt}</div>", unsafe_allow_html=True)
            
            with b3:
                st.button(
                    "＋",
                    key=f"inc_{c_key}_{item['id']}",
                    on_click=update_count,
                    args=(item['id'], 1, item['price'], balance),
                    type="primary",
                    use_container_width=True
                )
            st.markdown('</div>', unsafe_allow_html=True)  # 关闭btn-group
            st.markdown('</div>', unsafe_allow_html=True)  # 关闭card-wrapper

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

    # 二维码 URL
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://spend-billions.streamlit.app"
    
    # 1. 微信风格
    if bill_type == 'wechat':
        bill_html = f"""
        <div class="bill-container bill-wechat">
            <div class="bill-wechat-header"><span>{get_txt('pay_wechat')}</span></div>
            <div class="bill-wechat-total">{currency}{total_spent:,.0f}</div>
            <div class="bill-wechat-label">{get_txt('total_spent')}</div>
            <div style="padding: 0 20px;"><hr style="border-top: 1px solid #eee; margin: 10px 0;">
                <div style="max-height: 300px; overflow-y: auto;">
        """
        for name, cnt, cost in purchased_items:
            bill_html += f"""<div style="display: flex; justify-content: space-between; margin: 8px 0; font-size: 0.9rem; color: #333;"><span>{name} x{cnt}</span><span style="font-weight: bold;">{currency}{cost:,.0f}</span></div>"""
        bill_html += f"""</div></div>
            <div class="bill-footer"><div style="color: #999; font-size: 0.8rem; margin-bottom: 5px;">{get_txt('scan_to_play')}</div><img src="{qr_url}" style="width: 80px; height: 80px; mix-blend-mode: multiply;"></div>
        </div>"""

    # 2. 支付宝风格
    elif bill_type == 'alipay':
        bill_html = f"""
        <div class="bill-container bill-alipay">
            <div class="bill-alipay-header"><span>{'<'}</span><span>{get_txt('receipt_title')}</span><span>...</span></div>
            <div style="padding: 10px;">
        """
        for name, cnt, cost in purchased_items:
            bill_html += f"""<div class="bill-alipay-row"><span style="color: #333;">{name} x{cnt}</span><span style="font-weight: bold; color: #333;">-{currency}{cost:,.0f}</span></div>"""
        bill_html += f"""</div>
            <div class="bill-alipay-total">{get_txt('total_spent')}: <span style="font-size: 1.5rem; color: #1677ff;">{currency}{total_spent:,.0f}</span></div>
            <div class="bill-footer"><div style="display: flex; align-items: center; justify-content: center; gap: 10px;"><img src="{qr_url}" style="width: 60px; height: 60px;"><div style="text-align: left; font-size: 0.8rem; color: #999;"><div>{get_txt('scan_to_play')}</div><div style="color: #1677ff;">PK Billionaires</div></div></div></div>
        </div>"""

    # 3. PayPal 风格
    else: 
        bill_html = f"""
        <div class="bill-container bill-paypal">
            <div class="bill-paypal-header"><div style="font-weight: bold; font-size: 1.1rem;">PayPal</div><div style="font-size: 0.8rem; opacity: 0.8;">{datetime.datetime.now().strftime('%Y-%m-%d')}</div></div>
            <div class="bill-paypal-total">{currency}{total_spent:,.0f}</div>
            <div style="padding: 0 20px;"><div style="font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Details</div>
        """
        for name, cnt, cost in purchased_items:
            bill_html += f"""<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0; font-size: 0.9rem;"><span>{name} ({cnt})</span><span>{currency}{cost:,.0f}</span></div>"""
        bill_html += f"""</div>
            <div class="bill-footer" style="margin-top: 20px;"><img src="{qr_url}" style="width: 60px; height: 60px;"><div style="font-size: 0.7rem; color: #aaa; margin-top: 5px;">Scan to challenge Elon</div></div>
        </div>"""

    # 渲染账单与裂变文案
    st.markdown("<div style='display: flex; justify-content: center; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown(bill_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 分享文案
    share_text = get_txt('share_copy_text').format(amount=f"{currency}{total_spent:,.0f}", item_count=item_count_total)
    st.markdown(f"""
    <div style="margin: 20px auto; padding: 15px; background: #eef2f5; border-radius: 8px; text-align: center; max-width: 600px;">
        <div style="font-weight: bold; color: #333; margin-bottom: 8px;">{get_txt('share_prompt')}</div>
        <code style="display: block; padding: 10px; background: white; border: 1px solid #ddd; border-radius: 4px; color: #555; word-break: break-all;">{share_text}</code>
    </div>
    """, unsafe_allow_html=True)

    if balance == 0:
        st.balloons()
        st.success(get_txt('balance_zero'), icon="🎉")

st.markdown('</div>', unsafe_allow_html=True) # End content container

# ==========================================
# 6. 底部咖啡 & 统计 (优化显示)
# ==========================================
@st.dialog("☕ " + get_txt('coffee_title'), width="small")
def show_coffee_window():
    st.markdown(f"""
    <div class="coffee-card">
        <h3 style="margin: 0 0 10px 0; font-size: 1.2rem;">{get_txt('coffee_btn')}</h3>
        <p style="color: #666; margin: 0 0 15px 0;">{get_txt('coffee_desc')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 预设数量
    presets = [("☕", 1), ("🍗", 3), ("🚀", 5)]
    def set_val(n): st.session_state.coffee_num = n
    preset_cols = st.columns(3, gap="small")
    for i, (icon, num) in enumerate(presets):
        with preset_cols[i]:
            if st.button(f"{icon} {num}", use_container_width=True, key=f"p_btn_{i}"):
                set_val(num)
    
    st.write("")
    
    # 数量选择和金额
    coffee_cols = st.columns([1, 1], gap="small")
    with coffee_cols[0]:
        cnt = st.number_input(
            get_txt('unit_cn'), 
            min_value=1, 
            max_value=100, 
            step=1, 
            key='coffee_num', 
            label_visibility="visible"
        )
    total = cnt * 10
    with coffee_cols[1]:
        st.markdown(f"""
        <div style="background:#fff0f0; border:1px dashed #ffcccc; border-radius:8px; padding:10px; text-align:center; height: 100%; display: flex; flex-direction: column; justify-content: center;">
            <div style="color:#888; font-size: 0.8rem; margin-bottom: 5px;">{get_txt('unit_total')} (¥)</div>
            <div class="price-number">{total}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 支付方式
    pay_tabs = st.tabs([get_txt('pay_wechat'), get_txt('pay_alipay')])
    def show_qr(img_path):
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            # 生成捐赠二维码
            st.image(
                f"https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=Donate_{total}_CNY", 
                width=140
            )
    
    with pay_tabs[0]:
        show_qr("wechat_pay.jpg")
    with pay_tabs[1]:
        show_qr("ali_pay.jpg")
    
    st.write("")
    
    # 确认按钮
    if st.button("🎉 " + get_txt('pay_success').split('!')[0], type="primary", use_container_width=True):
        st.balloons()
        st.success(get_txt('pay_success').format(count=cnt))
        time.sleep(2)
        st.rerun()

# 咖啡按钮
coffee_col1, coffee_col2, coffee_col3 = st.columns([2, 3, 2])
with coffee_col2:
    if st.button(get_txt('coffee_btn'), use_container_width=True, type="secondary"):
        show_coffee_window()

# 数据库统计
DB_DIR = os.path.expanduser("~/")
DB_FILE = os.path.join(DB_DIR, "visit_stats.db")
def track_stats():
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        # 创建表
        c.execute('''CREATE TABLE IF NOT EXISTS daily_traffic (date TEXT PRIMARY KEY, pv_count INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS visitors (visitor_id TEXT PRIMARY KEY, last_visit_date TEXT)''')
        
        today = datetime.datetime.utcnow().date().isoformat()
        vid = st.session_state["visitor_id"]
        
        # 统计PV/UV
        if "has_counted" not in st.session_state:
            # 初始化今日PV
            c.execute("INSERT OR IGNORE INTO daily_traffic (date, pv_count) VALUES (?, 0)", (today,))
            # 增加PV
            c.execute("UPDATE daily_traffic SET pv_count = pv_count + 1 WHERE date=?", (today,))
            # 更新访客最后访问时间
            c.execute("INSERT OR REPLACE INTO visitors (visitor_id, last_visit_date) VALUES (?, ?)", (vid, today))
            conn.commit()
            st.session_state["has_counted"] = True
        
        # 查询数据
        t_uv = c.execute("SELECT COUNT(*) FROM visitors WHERE last_visit_date=?", (today,)).fetchone()[0]
        a_uv = c.execute("SELECT COUNT(*) FROM visitors").fetchone()[0]
        t_pv = c.execute("SELECT pv_count FROM daily_traffic WHERE date=?", (today,)).fetchone()[0]
        
        conn.close()
        return t_uv, a_uv, t_pv
    except Exception as e:
        st.error(f"统计数据出错: {e}")
        return 0, 0, 0

today_uv, total_uv, today_pv = track_stats()

# 显示统计信息
st.markdown(f"""
<div class="stats-container">
    <div style="text-align: center;">
        <div style="font-weight: bold; font-size: 1rem;">{today_uv}</div>
        <div style="font-size: 0.8rem;">{get_txt('visitor_today')}</div>
    </div>
    <div style="border-left:1px solid #ddd; padding-left:20px; text-align: center;">
        <div style="font-weight: bold; font-size: 1rem;">{total_uv}</div>
        <div style="font-size: 0.8rem;">{get_txt('visitor_total')}</div>
    </div>
    <div style="border-left:1px solid #ddd; padding-left:20px; text-align: center;">
        <div style="font-weight: bold; font-size: 1rem;">{today_pv}</div>
        <div style="font-size: 0.8rem;">{get_txt('pv_today')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 底部留白
st.markdown("<br><br>", unsafe_allow_html=True)
