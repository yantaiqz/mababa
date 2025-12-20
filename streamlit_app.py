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
LANG_TEXT = {
    "zh": {
        "title": "花光{name}的钱",
        "subtitle": "你现在拥有 {money}。这钱不花完，别想下班！",
        "receipt_title": "购物清单",
        "total_spent": "实付金额",
        "balance_zero": "恭喜你！你已经身无分文，可以安心退休了！",
        "toast_no_money": "余额不足！大佬也要精打细算！",
        "coffee_btn": "☕ 请开发者喝咖啡",
        "coffee_title": "支持作者",
        "coffee_desc": "如果这个小游戏让你摸鱼更快乐，欢迎投喂！",
        "pay_wechat": "微信支付",
        "pay_alipay": "支付宝",
        "pay_paypal": "PayPal",
        "more_label": "✨ 更多乐子",
        "unit_cn": "杯",
        "unit_total": "总计投入",
        "pay_success": "收到！感谢打赏！代码写得更有劲了！❤️",
        "visitor_today": "今日 UV",
        "visitor_total": "历史 UV",
        "share_btn": "📤 生成分享海报",
        "share_modal_title": "截图凡尔赛一下",
        "share_prompt": "复制下方文案，配合截图发朋友圈👇",
        "share_copy_text": "我在《花光大佬的钱》里挥霍了 {amount}！买了 {item_count} 件离谱商品，你也来试试？👉 https://mababa.streamlit.app",
        "scan_to_play": "长按识别二维码挑战",
        "pv_today": "今日 PV"
    },
    "en": {
        "title": "Spend {name}'s Money",
        "subtitle": "You have {money}. Spend it all before you can leave!",
        "receipt_title": "Receipt",
        "total_spent": "Total Paid",
        "balance_zero": "Congratulations! You are broke and free!",
        "toast_no_money": "Not enough money!",
        "coffee_btn": "☕ Buy me a coffee",
        "coffee_title": "Support Me",
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
        "pv_today": "Today PV"
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
if 'lang' not in st.session_state: st.session_state.lang = 'zh'
if 'char_key' not in st.session_state: st.session_state.char_key = 'jack'
if 'cart' not in st.session_state: st.session_state.cart = {}
if 'visitor_id' not in st.session_state: st.session_state["visitor_id"] = str(uuid.uuid4())
if 'coffee_num' not in st.session_state: st.session_state.coffee_num = 1

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
# 4. CSS (全面视觉优化)
# ==========================================
current_char = get_char()
theme_colors = current_char['theme_color']

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    /* 全局重置 - 更干净的基础样式 */
    .stApp {{ 
        background-color: #f8fafc; 
        font-family: 'Inter', sans-serif;
        overflow-x: hidden;
    }}
    
    /* 核心布局容器 - 更精准的间距控制 */
    .block-container {{
        max-width: 950px !important;
        padding-top: 0.8rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        margin: 0 auto !important;
    }}
    
    /* 隐藏 Streamlit 默认组件 */
    #MainMenu, footer, header {{visibility: hidden;}}
    
    /* 1. 顶部导航区 - 右上角按钮容器 */
    .top-nav-container {{
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        padding: 8px 0;
        margin-bottom: 8px;
    }}
    
    /* 2. 磨砂玻璃粘性余额条 - 优化版 */
    .header-container {{
        position: sticky; 
        top: 0; 
        z-index: 999;
        background: linear-gradient(135deg, {theme_colors[0]}dd, {theme_colors[1]}dd);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        color: white; 
        padding: 14px 0; 
        text-align: center;
        font-weight: 800; 
        font-size: clamp(1.8rem, 4vw, 2.3rem);
        font-family: 'JetBrains Mono', monospace;
        box-shadow: 0 6px 24px rgba(31, 38, 135, 0.12);
        margin: 15px -1.2rem 25px -1.2rem;
        border-radius: 0 0 24px 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    }}
    
    /* 3. 人物选择按钮容器 */
    .char-select-container {{
        display: flex;
        justify-content: center;
        gap: 16px;
        margin: 10px 0 20px 0;
        flex-wrap: wrap;
    }}
    
    /* 4. 人物按钮样式 - 统一视觉 */
    .char-btn {{
        flex: 1;
        min-width: 120px;
        max-width: 180px;
        padding: 10px 16px;
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .char-btn:hover {{
        border-color: {theme_colors[0]};
        background: #f8fafc;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    .char-btn.active {{
        border-color: {theme_colors[0]};
        background: rgba({int(theme_colors[0][1:3],16)}, {int(theme_colors[0][3:5],16)}, {int(theme_colors[0][5:7],16)}, 0.08);
    }}
    
    /* 5. 商品卡片 - 增强视觉层次 */
    [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] {{
        background-color: white;
        border-radius: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        border: 1px solid #f0f0f0;
        padding: 12px !important;
        margin-bottom: 16px;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"]:hover {{
        transform: translateY(-6px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
        border-color: {theme_colors[0]}33;
    }}
    
    /* 6. Emoji 按钮 - 更精致的交互 */
    button[kind="tertiary"] {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 8px 0 !important;
        transition: all 0.2s ease !important;
        border-radius: 16px !important;
    }}
    button[kind="tertiary"]:hover {{ 
        transform: scale(1.08) !important; 
        background-color: rgba(0,0,0,0.02) !important;
    }}
    button[kind="tertiary"]:active {{ 
        transform: scale(0.95) !important; 
    }}
    button[kind="tertiary"] p {{
        font-size: clamp(3rem, 8vw, 4rem) !important; 
        margin: 0 !important;
        text-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    
    /* 7. 商品信息文本 - 优化排版 */
    .item-name {{ 
        font-size: 1rem; 
        font-weight: 700; 
        color: #1e293b; 
        height: 40px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        line-height: 1.3; 
        text-align: center; 
        margin: 8px 0 4px 0;
        padding: 0 4px;
    }}
    .item-price {{ 
        color: {theme_colors[1]}; 
        font-weight: 700; 
        font-size: 0.95rem; 
        text-align: center; 
        margin-bottom: 12px; 
        font-family: 'JetBrains Mono', monospace;
    }}
    
    /* 8. 操作按钮 - 统一样式 */
    button[kind="secondary"], button[kind="primary"] {{ 
        min-height: 40px; 
        border-radius: 12px; 
        font-weight: 700; 
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }}
    button[kind="primary"] {{
        background: linear-gradient(135deg, {theme_colors[0]}, {theme_colors[1]}) !important;
    }}
    button[kind="primary"]:hover {{
        box-shadow: 0 4px 12px rgba({int(theme_colors[0][1:3],16)}, {int(theme_colors[0][3:5],16)}, {int(theme_colors[0][5:7],16)}, 0.3);
    }}
    
    /* 9. 数量显示框 - 更精致 */
    .count-display {{
        text-align: center; 
        line-height: 40px; 
        font-weight: 800; 
        color: #1e293b; 
        font-size: 1.15rem;
        background: #f8fafc; 
        border-radius: 12px; 
        border: 1px solid #e2e8f0; 
        font-family: 'JetBrains Mono', monospace;
        margin: 0 4px;
    }}

    /* 10. 账单容器 - 优化阴影和圆角 */
    .bill-container {{ 
        background: white; 
        margin: 25px auto; 
        max-width: 450px; 
        box-shadow: 0 8px 32px rgba(0,0,0,0.08); 
        border-radius: 12px; 
        overflow: hidden; 
        position: relative;
        border: 1px solid #f0f0f0;
    }}
    .bill-container::after {{
        content: ""; 
        position: absolute; 
        bottom: -6px; 
        left: 0; 
        right: 0; 
        height: 12px;
        background: radial-gradient(circle, transparent 65%, white 70%) 0 0 / 12px 12px repeat-x;
        transform: rotate(180deg);
    }}
    
    /* 11. 账单内部样式优化 */
    .bill-footer {{ 
        background: #fafafa; 
        padding: 20px 25px; 
        text-align: center; 
        border-top: 2px dashed #f0f0f0; 
    }}
    .bill-wechat-header {{ 
        background: #2AAD67; 
        color: white; 
        padding: 20px 25px; 
        text-align: center; 
        font-weight: 600; 
        font-size: 1.1rem;
    }}
    .bill-wechat-total {{ 
        font-size: 2rem; 
        font-weight: 800; 
        text-align: center; 
        margin: 15px 0; 
        color: #111; 
        font-family: 'JetBrains Mono'; 
    }}
    .bill-alipay-header {{ 
        background: #1677ff; 
        color: white; 
        padding: 20px; 
        display: flex; 
        justify-content: space-between; 
        font-size: 1.1rem;
    }}
    .bill-alipay-total {{ 
        padding: 20px; 
        text-align: right; 
        font-weight: 800; 
        font-size: 2rem; 
        border-top: 1px solid #f5f5f5; 
        color: #1677ff; 
        font-family: 'JetBrains Mono'; 
    }}
    .bill-paypal-header {{ 
        background: #003087; 
        color: white; 
        padding: 25px 30px; 
    }}
    .bill-paypal-total {{ 
        font-size: 2rem; 
        color: #003087; 
        text-align: center; 
        margin: 20px 0; 
        font-weight: 700; 
        font-family: 'JetBrains Mono'; 
    }}
    
    /* 12. 统计条 - 更精致 */
    .stats-bar {{
        display: flex; 
        justify-content: center; 
        gap: 30px; 
        margin: 30px auto 15px auto; 
        padding: 16px 30px; 
        background-color: white; 
        border-radius: 50px; 
        border: 1px solid #f0f0f0; 
        color: #64748b; 
        font-size: 0.9rem; 
        width: fit-content; 
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
    }}
    .stats-bar > div {{
        text-align: center;
    }}
    .stats-bar .stat-value {{
        font-weight: 800; 
        color: #1e293b; 
        font-size: 1.1rem;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 4px;
    }}
    
    /* 13. 右上角按钮样式优化 */
    .top-right-btn {{
        width: 100%;
        padding: 8px 16px;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        color: #1e293b;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 600;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }}
    .top-right-btn:hover {{
        background-color: #f8fafc;
        border-color: #cbd5e1;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }}
    .top-right-link {{
        text-decoration: none;
    }}
    
    /* 14. 标题样式优化 */
    .main-title {{
        font-size: clamp(2rem, 5vw, 2.8rem);
        font-weight: 800;
        color: #1e293b;
        text-align: center;
        margin: 10px 0 6px 0;
        letter-spacing: -0.5px;
    }}
    .subtitle {{
        text-align: center;
        color: #64748b;
        font-weight: 500;
        margin-bottom: 10px;
        font-size: 1rem;
    }}
    
    /* 15. 响应式适配 */
    @media (max-width: 768px) {{
        .char-select-container {{
            gap: 10px;
            padding: 0 8px;
        }}
        .char-btn {{
            min-width: 100px;
            padding: 8px 12px;
            font-size: 0.85rem;
        }}
        .stats-bar {{
            gap: 20px;
            padding: 12px 20px;
            font-size: 0.8rem;
        }}
        .block-container {{
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }}
        .header-container {{
            margin-left: -0.8rem !important;
            margin-right: -0.8rem !important;
            padding: 12px 0;
        }}
    }}
    
    @media (max-width: 480px) {{
        .top-nav-container {{
            gap: 8px;
        }}
        .char-btn {{
            min-width: 80px;
        }}
        .stats-bar {{
            flex-direction: column;
            gap: 12px;
            padding: 15px;
            border-radius: 20px;
        }}
        .stats-bar > div {{
            padding: 4px 0;
        }}
        .stats-bar > div:not(:last-child) {{
            border-bottom: 1px solid #f0f0f0;
            padding-bottom: 8px;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. 主页面逻辑 (优化版布局)
# ==========================================

# A. 右上角按钮区域 (优化版)
st.markdown('<div class="top-nav-container">', unsafe_allow_html=True)
col_lang, col_more = st.columns([1, 1.3], gap="small")

with col_lang:
    # 语言切换按钮
    lang_label = "🌐 " + ("EN" if st.session_state.lang == 'zh' else "中")
    if st.button(lang_label, key="btn_lang", use_container_width=True, type="secondary"):
        st.session_state.lang = 'en' if st.session_state.lang == 'zh' else 'zh'
        st.rerun()

with col_more:
    # More Fun按钮
    st.markdown(f"""
        <a href="https://laodeng.streamlit.app/" target="_blank" class="top-right-link">
            <button class="top-right-btn">{get_txt('more_label')}</button>
        </a>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# B. 人物切换按钮区域 (居中优化版)
st.markdown('<div class="char-select-container">', unsafe_allow_html=True)
chars_list = list(CHARACTERS.items())
for key, data in chars_list:
    label = f"{data['avatar']} {data['name_zh' if st.session_state.lang == 'zh' else 'name_en']}"
    # 为当前选中的人物按钮添加激活样式
    btn_class = "char-btn active" if key == st.session_state.char_key else "char-btn"
    st.markdown(f"""
        <button class="{btn_class}" onclick="parent.document.querySelector('[data-testid=btn_char_{key}]').click()">
            {label}
        </button>
    """, unsafe_allow_html=True)
    # 隐藏的实际按钮（用于触发逻辑）
    if st.button(label, key=f"btn_char_{key}", use_container_width=True, visible=False):
        switch_char(key)
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# C. 标题与余额 (优化版样式)
balance, total_spent = calculate_balance()
c_key = st.session_state.char_key
currency = current_char['currency']
char_name = current_char['name_zh'] if st.session_state.lang == 'zh' else current_char['name_en']

# 主标题
st.markdown(f"<h1 class='main-title'>{get_txt('title').format(name=char_name)}</h1>", unsafe_allow_html=True)
# 副标题
money_str = f"{currency}{current_char['money']:,}"
st.markdown(f"<div class='subtitle'>{get_txt('subtitle').format(money=money_str)}</div>", unsafe_allow_html=True)

# 粘性余额条
st.markdown(f"""<div class="header-container">{currency} {balance:,.0f}</div>""", unsafe_allow_html=True)

# D. 商品网格 (优化版间距)
items = current_char['items']
cols_per_row = 3
# 适配移动端 - 小屏幕显示2列
if st.session_state.get('is_mobile') or st.query_params.get('mobile'):
    cols_per_row = 2

for i in range(0, len(items), cols_per_row):
    cols = st.columns(cols_per_row, gap="large")
    for j in range(cols_per_row):
        if i + j < len(items):
            item = items[i + j]
            item_name = item['name_zh'] if st.session_state.lang == 'zh' else item['name_en']
            
            with cols[j]:
                with st.container(border=True): 
                    # 1. Emoji 按钮
                    if st.button(item['icon'], key=f"emoji_{c_key}_{item['id']}", use_container_width=True, type="tertiary"):
                        click_item_add(item['id'], item['price'], balance)
                    
                    # 2. 信息区
                    st.markdown(f"""
                        <div class="item-name">{item_name}</div>
                        <div class="item-price">{currency} {item['price']:,}</div>
                    """, unsafe_allow_html=True)
                    
                    # 3. 底部操作区
                    b1, b2, b3 = st.columns([1, 1.4, 1], gap="small")
                    with b1: 
                        st.button("－", key=f"dec_{c_key}_{item['id']}", on_click=update_count, 
                                 args=(item['id'], -1, item['price'], balance), use_container_width=True)
                    with b2:
                        cnt = st.session_state.cart[c_key].get(item['id'], 0)
                        st.markdown(f'<div class="count-display">{cnt}</div>', unsafe_allow_html=True)
                    with b3: 
                        st.button("＋", key=f"inc_{c_key}_{item['id']}", on_click=update_count, 
                                 args=(item['id'], 1, item['price'], balance), type="primary", use_container_width=True)

# E. 账单与分享功能 (优化版样式)
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
    
    # 账单 HTML (优化版)
    bill_html = ""
    if bill_type == 'wechat':
        bill_html = f"""
        <div class="bill-container bill-wechat">
            <div class="bill-wechat-header"><span>{get_txt('pay_wechat')}</span></div>
            <div class="bill-wechat-total">{currency}{total_spent:,.0f}</div>
            <div style="text-align: center; color: #64748b; margin-bottom: 20px; font-size: 0.95rem;">{get_txt('total_spent')}</div>
            <div style="padding: 0 25px;"><hr style="border-top: 1px solid #f0f0f0; margin: 10px 0;">
                <div style="max-height: 400px; overflow-y: auto; padding-right: 8px;">
        """
        for name, cnt, cost in purchased_items:
            bill_html += f"""<div style="display: flex; justify-content: space-between; margin: 12px 0; font-size: 0.95rem; color: #1e293b;"><span>{name} x{cnt}</span><span style="font-weight: bold;">{currency}{cost:,.0f}</span></div>"""
        bill_html += f"""</div></div>
            <div class="bill-footer"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;">{get_txt('scan_to_play')}</div><img src="{qr_url}" style="width: 100px; height: 100px; mix-blend-mode: multiply; border-radius: 8px;"></div>
        </div>"""
    elif bill_type == 'alipay':
        bill_html = f"""
        <div class="bill-container bill-alipay">
            <div class="bill-alipay-header"><span>{'<'}</span><span style="font-weight: 700;">{get_txt('receipt_title')}</span><span>...</span></div>
            <div style="padding: 15px 20px;">
        """
        for name, cnt, cost in purchased_items:
            bill_html += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f5f5f5; font-size: 0.95rem;"><span style="color: #1e293b;">{name} x{cnt}</span><span style="font-weight: bold; color: #1e293b;">-{currency}{cost:,.0f}</span></div>"""
        bill_html += f"""</div>
            <div class="bill-alipay-total">{get_txt('total_spent')}: <span style="font-size: 1.8rem; color: #1677ff;">{currency}{total_spent:,.0f}</span></div>
            <div class="bill-footer"><div style="display: flex; align-items: center; justify-content: center; gap: 15px;"><img src="{qr_url}" style="width: 80px; height: 80px; border-radius: 8px;"><div style="text-align: left; font-size: 0.85rem; color: #94a3b8;"><div>{get_txt('scan_to_play')}</div><div style="color: #1677ff; font-weight:bold; margin-top: 4px;">PK Billionaires</div></div></div></div>
        </div>"""
    else: # PayPal
        bill_html = f"""
        <div class="bill-container bill-paypal">
            <div class="bill-paypal-header"><div class="bill-paypal-logo" style="font-size: 1.6rem; font-weight: 900; font-style: italic;">PayPal</div><div style="font-size: 0.9rem; opacity: 0.9; margin-top: 4px;">{datetime.datetime.now().strftime('%Y-%m-%d')}</div></div>
            <div class="bill-paypal-total">{currency}{total_spent:,.0f}</div>
            <div style="padding: 0 30px;"><div style="font-size: 0.85rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px;">DETAILS</div>
        """
        for name, cnt, cost in purchased_items:
            bill_html += f"""<div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f0f0; font-size: 0.95rem;"><span>{name} ({cnt})</span><span style="font-weight: 600;">{currency}{cost:,.0f}</span></div>"""
        bill_html += f"""</div>
            <div class="bill-footer" style="margin-top: 30px;"><img src="{qr_url}" style="width: 80px; height: 80px; border-radius: 8px;"><div style="font-size: 0.8rem; color: #94a3b8; margin-top: 8px;">Scan to challenge Elon</div></div>
        </div>"""

    # 账单居中显示
    c1, c2, c3 = st.columns([0.5, 2, 0.5])
    with c2:
        st.markdown(bill_html, unsafe_allow_html=True)
        
        # 分享弹窗 (优化版)
        st.write("")
        @st.dialog(get_txt("share_modal_title"), width="large")
        def show_share_modal(html, amount, count):
            st.markdown(html, unsafe_allow_html=True)
            share_text = get_txt('share_copy_text').format(amount=amount, item_count=count)
            st.markdown(f"""
                <div style="margin-top: 25px; padding: 20px; background: #f8fafc; border-radius: 16px; text-align: center; border:1px solid #e2e8f0;">
                    <div style="font-weight: 700; color: #1e293b; margin-bottom: 12px; font-size: 1.05rem;">{get_txt('share_prompt')}</div>
                    <code style="display: block; padding: 14px; background: white; border: 1px solid #cbd5e1; border-radius: 10px; color: #334155; word-break: break-all; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem;">{share_text}</code>
                </div>
            """, unsafe_allow_html=True)

        if st.button(get_txt('share_btn'), type="primary", use_container_width=True):
            show_share_modal(bill_html, f"{currency}{total_spent:,.0f}", item_count_total)

    if balance == 0:
        st.balloons()
        st.success(get_txt('balance_zero'), icon="🎉")

# ==========================================
# 6. 底部咖啡 & 统计 (优化版)
# ==========================================
st.markdown("<br><br>", unsafe_allow_html=True)
# 咖啡按钮居中
coffee_col1, coffee_col2, coffee_col3 = st.columns([1, 2, 1])
with coffee_col2:
    @st.dialog("☕ " + get_txt('coffee_title'), width="small")
    def show_coffee_window():
        st.markdown(f"""<div style="background:white; border:1px solid #e2e8f0; border-radius:16px; padding:20px; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.05); margin-bottom:20px;"><p style="margin:0; color:#475569; font-size: 1rem;">{get_txt('coffee_desc')}</p></div>""", unsafe_allow_html=True)
        presets = [("☕", 1), ("🍗", 3), ("🚀", 5)]
        def set_val(n): st.session_state.coffee_num = n
        cols = st.columns(3, gap="small")
        for i, (icon, num) in enumerate(presets):
            with cols[i]:
                if st.button(f"{icon} {num}", use_container_width=True, key=f"p_btn_{i}", type="secondary"): 
                    set_val(num)
        st.write("")
        c1, c2 = st.columns([1, 1], gap="small")
        with c1: 
            cnt = st.number_input(get_txt('unit_cn'), 1, 100, step=1, key='coffee_num', 
                                label_visibility="collapsed", use_container_width=True)
        total = cnt * 10
        with c2: 
            st.markdown(f"""<div style="background:#fff1f2; border:1px dashed #fecdd3; border-radius:12px; padding:12px; text-align:center; height: 100%; display: flex; align-items: center; justify-content: center;"><div style="color:#e11d48; font-weight:900; font-size:1.7rem; font-family:'JetBrains Mono';">¥{total}</div></div>""", unsafe_allow_html=True)
        
        # 支付方式 tabs
        t1, t2 = st.tabs([get_txt('pay_wechat'), get_txt('pay_alipay')])
        def show_qr(img_path):
            if os.path.exists(img_path): 
                st.image(img_path, use_container_width=True, caption=get_txt('pay_wechat') if t1 else get_txt('pay_alipay'))
            else: 
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=Donate_{total}", 
                        width=160, caption=get_txt('scan_to_play'))
        
        with t1: show_qr("wechat_pay.jpg")
        with t2: show_qr("ali_pay.jpg")
        
        st.write("")
        if st.button("🎉 " + get_txt('pay_success').split('!')[0], type="primary", use_container_width=True):
            st.balloons()
            st.success(get_txt('pay_success').format(count=cnt), icon="❤️")
            time.sleep(2)
            st.rerun()

    if st.button(get_txt('coffee_btn'), use_container_width=True, type="secondary"):
        show_coffee_window()

# 数据库统计 (优化版显示)
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
    except: 
        return 0, 0, 0

today_uv, total_uv, today_pv = track_stats()
st.markdown(f"""
<div class="stats-bar">
    <div>
        <div>{get_txt('visitor_today')}</div>
        <div class="stat-value">{today_uv}</div>
    </div>
    <div>
        <div>{get_txt('visitor_total')}</div>
        <div class="stat-value">{total_uv}</div>
    </div>
    <div>
        <div>{get_txt('pv_today')}</div>
        <div class="stat-value">{today_pv}</div>
    </div>
</div><br><br>
""", unsafe_allow_html=True)
