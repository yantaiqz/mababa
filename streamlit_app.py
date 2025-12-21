import streamlit as st
import sqlite3
import uuid
import datetime
import os
import time
import json
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
    """自动检测浏览器语言，优先使用中文，否则英文"""
    try:
        headers = st.context.headers
        accept_language = headers.get('Accept-Language', 'zh')
        lang_codes = re.findall(r'([a-z]{2})(?:-[A-Z]{2})?', accept_language.lower())
        if 'zh' in lang_codes:
            return 'zh'
        elif 'en' in lang_codes:
            return 'en'
        else:
            return 'zh'
    except:
        return 'zh'

# 初始化语言设置
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
        "photo_url": "https://ichef.bbci.co.uk/news/800/cpsprodpb/7727/production/_103330503_musk3.jpg",
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
        "photo_url": "https://ichef.bbci.co.uk/news/800/cpsprodpb/7727/production/_103330503_musk3.jpg",
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
        "photo_url": "https://ichef.bbci.co.uk/news/800/cpsprodpb/7727/production/_103330503_musk3.jpg",
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
# 5. CSS (重点优化人物选择区域)
# ==========================================
current_char = get_char()
theme_colors = current_char['theme_color']

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap');
    
    /* 全局重置 */
    .stApp {{ 
        background-color: #f3f4f6; 
        font-family: 'Inter', sans-serif;
    }}
    
    /* 响应式布局 - 移动端适配 */
    @media (max-width: 768px) {{
        .block-container {{
            max-width: 100% !important;
            padding-top: 0.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }}
        
        /* 移动端商品网格改为2列 */
        .item-grid {{
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 10px !important;
        }}
        
        /* 移动端标题字体缩小 */
        .header-container {{
            font-size: 1.8rem !important;
            padding: 8px 0 !important;
        }}
        
        /* 移动端人物选择区域优化 */
        .char-select-container {{
            padding: 0 15px !important;
            margin: 10px 0 25px 0 !important;
        }}
        
        .char-card {{
            max-width: 100px !important;
        }}
        
        .char-photo {{
            width: 70px !important;
            height: 70px !important;
        }}
        
        .char-name {{
            font-size: 0.85rem !important;
            padding: 3px 6px !important;
        }}
        
        /* 移动端统计条调整 */
        .stats-bar {{
            flex-direction: column !important;
            gap: 10px !important;
            padding: 15px !important;
            width: 100% !important;
        }}
        
        .stats-bar > div {{
            border-left: none !important;
            padding-left: 0 !important;
            padding-top: 10px !important;
            border-top: 1px solid #eee !important;
        }}
        
        .stats-bar > div:first-child {{
            border-top: none !important;
            padding-top: 0 !important;
        }}
    }}
    
    /* 桌面端样式 */
    @media (min-width: 769px) {{
        .block-container {{
            max-width: 900px !important;
            padding-top: 1rem !important;
            padding-bottom: 3rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        
        .item-grid {{
            display: grid !important;
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 15px !important;
        }}
        
        /* 桌面端人物选择区域 */
        .char-select-container {{
            padding: 0 20px !important;
            margin: 15px 0 35px 0 !important;
        }}
    }}
    
    /* 隐藏 Streamlit 默认组件 */
    #MainMenu, footer, header {{visibility: hidden;}}
    
    /* 磨砂玻璃粘性头部 */
    .header-container {{
        position: sticky; top: 0; z-index: 999;
        background: linear-gradient(180deg, {theme_colors[0]}ee, {theme_colors[1]}dd);
        backdrop-filter: blur(12px);
        color: white; 
        padding: 12px 0; 
        text-align: center;
        font-weight: 800; 
        font-size: 2.2rem;
        font-family: 'JetBrains Mono', monospace;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        margin-bottom: 25px;
        margin-left: -1rem; margin-right: -1rem;
        border-radius: 0 0 20px 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* 商品卡片优化 */
    [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] {{
        background-color: white;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        border: 1px solid rgba(229, 231, 235, 0.5);
        height: 100%;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
        border-color: {theme_colors[0]};
    }}
    
    /* Emoji 按钮优化 */
    button[kind="tertiary"] {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        transition: transform 0.1s !important;
    }}
    button[kind="tertiary"]:hover {{ transform: scale(1.1) !important; }}
    button[kind="tertiary"]:active {{ transform: scale(0.9) !important; }}
    button[kind="tertiary"] p {{
        font-size: 3rem !important; 
        margin: 0 !important;
        padding-top: 5px !important;
        text-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}
    
    /* 文本与数字优化 */
    .item-name {{ 
        font-size: 1rem; font-weight: 700; color: #1f2937; 
        height: 36px; display: flex; align-items: center; justify-content: center; 
        line-height: 1.2; text-align: center; margin-bottom: 4px;
    }}
    .item-price {{ 
        color: {theme_colors[1]}; font-weight: 600; font-size: 0.9rem; 
        text-align: center; margin-bottom: 12px; font-family: 'JetBrains Mono', monospace;
    }}
    
    /* 操作按钮美化 */
    button[kind="secondary"], button[kind="primary"] {{ 
        min-height: 36px; border-radius: 10px; font-weight: 700; border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    
    /* 数量显示框 */
    .count-display {{
        text-align: center; line-height: 36px; 
        font-weight: 800; color: #374151; font-size: 1.1rem;
        background: #f9fafb; border-radius: 10px; 
        border: 1px solid #e5e7eb; font-family: 'JetBrains Mono', monospace;
    }}

    /* 账单拟物化 */
    .bill-container {{ 
        background: white; margin: 30px auto; max-width: 420px; 
        box-shadow: 0 15px 40px rgba(0,0,0,0.12); border-radius: 6px; overflow: hidden; 
        position: relative;
    }}
    /* 锯齿边缘效果 */
    .bill-container::after {{
        content: ""; position: absolute; bottom: -5px; left: 0; right: 0; height: 10px;
        background: radial-gradient(circle, transparent 70%, white 75%) 0 0 / 10px 10px repeat-x;
        transform: rotate(180deg);
    }}
    
    .bill-footer {{ background: #fafafa; padding: 25px; text-align: center; border-top: 2px dashed #eee; }}
    
    /* 账单样式 */
    .bill-wechat-header {{ background: #2AAD67; color: white; padding: 25px; text-align: center; font-weight: 600; }}
    .bill-wechat-total {{ font-size: 1.8rem; font-weight: 800; text-align: center; margin: 15px 0; color: #111; font-family: 'JetBrains Mono'; }}
    
    .bill-alipay-header {{ background: #1677ff; color: white; padding: 20px; display: flex; justify-content: space-between; }}
    .bill-alipay-total {{ padding: 20px; text-align: right; font-weight: 800; font-size: 1.8rem; border-top: 1px solid #f0f0f0; color: #1677ff; font-family: 'JetBrains Mono'; }}
    
    .bill-paypal-header {{ background: #003087; color: white; padding: 30px; }}
    .bill-paypal-total {{ font-size: 1.8rem; color: #003087; text-align: center; margin: 20px 0; font-weight: 300; font-family: 'JetBrains Mono'; }}
    
    /* 统计条 */
    .stats-bar {{
        display: flex; justify-content: center; gap: 25px; margin-top: 40px; 
        padding: 15px 25px; background-color: white; border-radius: 50px; 
        border: 1px solid #eee; color: #6b7280; font-size: 0.85rem; 
        width: fit-content; margin-left: auto; margin-right: auto; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }}

    /* 右上角按钮样式 */
    .neal-btn {{
        width: 100%;
        padding: 0.5rem 0;
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 0.75rem;
        color: #333;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.15s ease;
        font-weight: 600;
    }}
    .neal-btn:hover {{
        background-color: #f9fafb;
        border-color: #d1d5db;
        transform: translateY(-1px);
    }}
    .neal-btn-link {{
        text-decoration: none;
    }}

    /* ========== 人物选择区域核心优化 ========== */
    /* 人物选择容器 */
    .char-select-container {{
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px; /* 增加间距，提升呼吸感 */
        padding: 0 20px;
        margin: 15px 0 35px 0;
        flex-wrap: wrap;
    }}
    
    /* 人物卡片 - 独立容器 */
    .char-card {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        max-width: 120px;
        width: 100%;
        position: relative;
        cursor: pointer;
    }}
    
    /* 人物照片容器 - 新增外层容器，优化居中 */
    .char-photo-wrapper {{
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 12px;
    }}
    
    /* 人物照片样式 - 优化尺寸和阴影 */
    .char-photo {{
        width: 90px;
        height: 90px;
        border-radius: 50%;
        object-fit: cover;
        object-position: center;
        border: 4px solid #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        background-color: #f8f9fa;
        z-index: 2;
        position: relative;
    }}
    
    /* 照片悬停效果 */
    .char-card:hover .char-photo {{
        transform: scale(1.05);
        box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    }}
    
    /* 选中状态 - 照片边框和背景光环 */
    .char-photo.active {{
        border-color: {theme_colors[0]};
        box-shadow: 0 0 0 2px {theme_colors[1]}30, 0 4px 12px rgba(0,0,0,0.12);
    }}
    
    .char-photo-wrapper::after {{
        content: "";
        position: absolute;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, {theme_colors[1]}20 0%, transparent 70%);
        border-radius: 50%;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 1;
    }}
    
    .char-card.active .char-photo-wrapper::after {{
        opacity: 1;
    }}
    
    /* 人物名称样式 - 优化字体和间距 */
    .char-name {{
        font-weight: 700;
        font-size: 0.95rem;
        color: #333;
        text-align: center;
        padding: 4px 10px;
        border-radius: 12px;
        transition: all 0.2s ease;
        z-index: 2;
        position: relative;
        white-space: nowrap;
    }}
    
    /* 选中状态的名称 */
    .char-card.active .char-name {{
        color: {theme_colors[0]};
        font-weight: 800;
        background-color: {theme_colors[1]}10;
    }}
    
    /* 隐藏的选择按钮 */
    .char-select-btn {{
        display: none !important;
    }}
    
    /* 照片加载失败占位符 */
    .char-photo-placeholder {{
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        color: #999;
    }}
    
    /* 顶部操作栏样式 */
    .top-actions-bar {{
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin: 10px 0 5px 0;
    }}
    
    /* 支付方式选择器 */
    .payment-tabs {{
        margin: 15px 0;
    }}
    
    /* 移动端适配的QR码 */
    .qr-code {{
        max-width: 120px;
        height: auto;
        margin: 0 auto;
    }}
    
    /* 平滑滚动 */
    html {{
        scroll-behavior: smooth;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 6. 主页面逻辑 (优化人物选择区域)
# ==========================================

# A. 第一层：语言切换 + more fun (右对齐)
st.markdown('<div class="top-actions-bar">', unsafe_allow_html=True)
col_lang, col_more = st.columns([1, 1.2], gap="small")

with col_lang:
    # 语言切换按钮
    if st.button("🌐 " + ("EN" if st.session_state.lang == 'zh' else "中"), 
                key="btn_lang", 
                use_container_width=True,
                type="secondary"):
        st.session_state.lang = 'en' if st.session_state.lang == 'zh' else 'zh'
        st.rerun()

with col_more:
    # More Fun按钮
    st.markdown(f"""
        <a href="https://laodeng.streamlit.app/" target="_blank" class="neal-btn-link">
            <button class="neal-btn">{get_txt('more_label')}</button>
        </a>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# B. 第二层：人物选择区域 (核心优化)
st.markdown('<div class="char-select-container">', unsafe_allow_html=True)
chars_list = list(CHARACTERS.items())

# 遍历创建人物卡片
for key, data in chars_list:
    is_active = st.session_state.char_key == key
    char_name = data['name_zh'] if st.session_state.lang == 'zh' else data['name_en']
    
    # 创建隐藏的选择按钮（核心交互）
    btn_clicked = st.button(
        label="",
        key=f"char_btn_{key}",
        use_container_width=True,
        class_="char-select-btn"
    )
    
    if btn_clicked:
        switch_char(key)
        st.rerun()
    
    # 人物卡片HTML（纯静态，无内联事件）
    card_class = "char-card" + (" active" if is_active else "")
    photo_class = "char-photo" + (" active" if is_active else "")
    
    st.markdown(f"""
    <div class="{card_class}">
        <div class="char-photo-wrapper">
            <img src="{data['photo_url']}" class="{photo_class}" alt="{char_name}"
                 onerror="this.classList.add('char-photo-placeholder'); this.innerHTML='{data['avatar']}'; this.src='';">
        </div>
        <div class="char-name">{char_name}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# D. 标题与余额
balance, total_spent = calculate_balance()
c_key = st.session_state.char_key
currency = current_char['currency']
char_name = current_char['name_zh'] if st.session_state.lang == 'zh' else current_char['name_en']

st.markdown(f"<br>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center; font-size: clamp(1.8rem, 5vw, 2.8rem); margin-bottom: 0.2rem; letter-spacing: -1px;'>{get_txt('title').format(name=char_name)}</h1>", unsafe_allow_html=True)
money_str = f"{currency}{current_char['money']:,}"
st.markdown(f"<div style='text-align: center; color: #6b7280; font-weight: 500; margin-bottom: 20px;'>{get_txt('subtitle').format(money=money_str)}</div>", unsafe_allow_html=True)

# 粘性余额条
st.markdown(f"""<div class="header-container">{currency} {balance:,.0f}</div>""", unsafe_allow_html=True)

# E. 商品网格 (响应式布局)
items = current_char['items']
st.markdown('<div class="item-grid">', unsafe_allow_html=True)

# 动态计算每行列数（移动端2列，桌面端3列）
cols_per_row = 2 if st.session_state.get('is_mobile', False) or st.query_params.get('mobile') else 3

# 渲染商品网格
for i in range(0, len(items), cols_per_row):
    cols = st.columns(cols_per_row, gap="medium")
    for j in range(cols_per_row):
        if i + j < len(items):
            item = items[i + j]
            item_name = item['name_zh'] if st.session_state.lang == 'zh' else item['name_en']
            
            with cols[j]:
                with st.container(border=True): 
                    # Emoji 按钮
                    if st.button(item['icon'], key=f"emoji_{c_key}_{item['id']}", use_container_width=True, type="tertiary"):
                        click_item_add(item['id'], item['price'], balance)
                    
                    # 信息区
                    st.markdown(f"""
                        <div class="item-name">{item_name}</div>
                        <div class="item-price">{currency} {item['price']:,}</div>
                    """, unsafe_allow_html=True)
                    
                    # 底部操作区
                    b1, b2, b3 = st.columns([1, 1.2, 1], gap="small")
                    with b1: 
                        st.button("－", key=f"dec_{c_key}_{item['id']}", on_click=update_count, args=(item['id'], -1, item['price'], balance), use_container_width=True)
                    with b2:
                        cnt = st.session_state.cart[c_key].get(item['id'], 0)
                        st.markdown(f'<div class="count-display">{cnt}</div>', unsafe_allow_html=True)
                    with b3: 
                        st.button("＋", key=f"inc_{c_key}_{item['id']}", on_click=update_count, args=(item['id'], 1, item['price'], balance), type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# F. 账单与分享功能
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
            <div class="bill-footer"><div style="color: #999; font-size: 0.85rem; margin-bottom: 8px;">{get_txt('scan_to_play')}</div><img src="{qr_url}" class="qr-code"></div>
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
            <div class="bill-footer"><div style="display: flex; align-items: center; justify-content: center; gap: 15px;"><img src="{qr_url}" class="qr-code"><div style="text-align: left; font-size: 0.85rem; color: #999;"><div>{get_txt('scan_to_play')}</div><div style="color: #1677ff; font-weight:bold;">PK Billionaires</div></div></div></div>
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
            <div class="bill-footer" style="margin-top: 30px;"><img src="{qr_url}" class="qr-code"><div style="font-size: 0.8rem; color: #aaa; margin-top: 8px;">Scan to challenge Elon</div></div>
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
# 7. 底部咖啡 & 统计 (PayPal 每单位 2 美元)
# ==========================================
st.markdown("<br><br>", unsafe_allow_html=True)
c_btn_col1, c_btn_col2, c_btn_col3 = st.columns([1, 2, 1])
with c_btn_col2:
    @st.dialog(" " + get_txt('coffee_title'), width="small")
    def show_coffee_window():
        st.markdown(f"""<div style="background:white; border:1px solid #eee; border-radius:12px; padding:15px; text-align:center; box-shadow:0 4px 10px rgba(0,0,0,0.05); margin-bottom:20px;"><p style="margin:0; color:#555;">{get_txt('coffee_desc')}</p></div>""", unsafe_allow_html=True)
        presets = [("☕", 1), ("🍗", 3), ("🚀", 5)]
        def set_val(n): st.session_state.coffee_num = n
        cols = st.columns(3, gap="small")
        for i, (icon, num) in enumerate(presets):
            with cols[i]:
                if st.button(f"{icon} {num}", use_container_width=True, key=f"p_btn_{i}"): set_val(num)
        st.write("")
        
        # 金额输入 - 统一按杯数计算
        col_amount, col_total = st.columns([1, 1], gap="small")
        with col_amount: 
            cnt = st.number_input(get_txt('coffee_amount'), 1, 100, step=1, key='coffee_num', label_visibility="visible")
        
        # 微信/支付宝：每杯10元
        cny_total = cnt * 10
        # PayPal：每杯2美元
        usd_total = cnt * 2
        
        with col_total: 
            st.markdown(f"""<div style="background:#fff1f2; border:1px dashed #fecdd3; border-radius:8px; padding:8px; text-align:center; height:100%; display:flex; align-items:center; justify-content:center;"><div style="color:#e11d48; font-weight:900; font-size:1.6rem; font-family:'JetBrains Mono';">¥{cny_total}</div></div>""", unsafe_allow_html=True)
        
        # 支付方式选择（新增PayPal）
        st.markdown(f"<div style='text-align:center; font-weight:bold; margin:15px 0;'>{get_txt('pay_choose')}</div>", unsafe_allow_html=True)
        payment_tabs = st.tabs([get_txt('pay_wechat'), get_txt('pay_alipay'), get_txt('pay_paypal')])
        
        def show_qr(img_path, alt_text):
            if os.path.exists(img_path): 
                st.image(img_path, use_container_width=True)
            else: 
                # 生成对应支付方式的二维码
                qr_data = f"Donate_{cny_total}_{alt_text}"
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={qr_data}", width=180)
        
        with payment_tabs[0]: 
            show_qr("wechat_pay.jpg", "WeChat")
        with payment_tabs[1]: 
            show_qr("ali_pay.jpg", "Alipay")
        with payment_tabs[2]: 
            # PayPal支付展示 - 每单位2美元
            st.markdown("""
                <div style="background:#003087; color:white; padding:15px; border-radius:8px; text-align:center; margin-bottom:15px;">
                    <div style="font-size:1.2rem; font-weight:bold; font-style:italic;">PayPal</div>
                    <div style="font-size:0.9rem; opacity:0.9;">{cnt} Cups × $2 = ${usd_total}</div>
                </div>
            """.format(cnt=cnt, usd_total=usd_total), unsafe_allow_html=True)
            # 这里替换为你的PayPal收款链接
            paypal_link = "https://paypal.me/ytqz"
            st.markdown(f"""
                <a href="{paypal_link}" target="_blank" style="display:block; text-align:center; margin:10px 0;">
                    <button style="background:#009cde; color:white; border:none; padding:10px 20px; border-radius:8px; font-weight:bold; cursor:pointer;">
                        🛒 Pay ${usd_total} with PayPal
                    </button>
                </a>
            """, unsafe_allow_html=True)
            show_qr("paypal.png", "Paypal")
        
        st.write("")
        if st.button("🎉 " + get_txt('pay_success').split('!')[0], type="primary", use_container_width=True):
            st.balloons()
            st.success(get_txt('pay_success').format(count=cnt))
            time.sleep(2)
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
