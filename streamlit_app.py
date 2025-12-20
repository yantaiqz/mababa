import streamlit as st
import pandas as pd

# ==========================================
# 1. 配置与CSS样式 (模拟 Neal.fun 风格)
# ==========================================
st.set_page_config(
    page_title="花光马云的钱 (Spend Jack Ma's Money)",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义 CSS 以优化卡片视觉和顶部粘性栏
st.markdown("""
<style>
    /* 全局背景 */
    .stApp {
        background-color: #f1f2f6;
    }
    
    /* 顶部余额条 */
    .header-container {
        position: sticky;
        top: 0;
        z-index: 999;
        background: linear-gradient(180deg, #2ecc71, #27ae60);
        color: white;
        padding: 20px 0;
        text-align: center;
        font-weight: 800;
        font-size: 2.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* 商品卡片样式 */
    .item-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .item-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .item-emoji {
        font-size: 4rem;
        margin-bottom: 10px;
    }
    .item-name {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
    }
    .item-price {
        color: #27ae60;
        font-weight: bold;
        font-size: 1rem;
        margin-bottom: 15px;
    }
    
    /* 调整按钮样式 */
    div.stButton > button {
        background-color: #f1f2f6;
        border: 1px solid #ccc;
        color: #333;
        font-weight: bold;
    }
    div.stButton > button:hover {
        border-color: #27ae60;
        color: #27ae60;
    }
    
    /* 购物小票 */
    .receipt {
        background: white;
        padding: 30px;
        max-width: 500px;
        margin: 40px auto;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        font-family: 'Courier New', Courier, monospace;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 数据定义 (马云版商品)
# ==========================================
# 初始资金：2000亿人民币 (约合 $27B)
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
    {"id": "twitter", "name": "收购 Twitter (X)", "price": 300000000000, "icon": "🐦"}, # 这是一个陷阱，钱不够
]

# ==========================================
# 3. 状态管理
# ==========================================
# 初始化购物车数量
for item in ITEMS:
    if item['id'] not in st.session_state:
        st.session_state[item['id']] = 0

# 计算当前余额
def calculate_balance():
    spent = 0
    for item in ITEMS:
        spent += st.session_state[item['id']] * item['price']
    return TOTAL_MONEY - spent, spent

balance, total_spent = calculate_balance()

# 回调函数：处理购买/出售
def update_count(item_id, delta, item_price):
    current = st.session_state[item_id]
    # 检查是否没钱了
    if delta > 0 and balance < item_price:
        st.toast("钱不够啦！马老师也要省着花！", icon="⚠️")
        return
    # 检查是否卖完了
    if delta < 0 and current <= 0:
        return
    
    st.session_state[item_id] += delta

# ==========================================
# 4. 页面渲染
# ==========================================

# --- 顶部：马云的头像和标题 ---
c1, c2 = st.columns([1, 6])
with c1:
    # 这里用 Emoji 代替头像，你也可以换成 st.image
    st.markdown("<div style='font-size: 80px; text-align: center;'>👨🏻‍🏫</div>", unsafe_allow_html=True)
with c2:
    st.title("花光马云的钱")
    st.markdown("你现在拥有 **2000亿** 人民币。这钱不花完，别想下班！(996福报)")

# --- 悬浮余额条 ---
# 根据余额变色
bg_color = "#2ecc71" if balance > 0 else "#e74c3c"
st.markdown(f"""
<div class="header-container" style="background: {bg_color};">
    ¥ {balance:,.0f}
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 商品网格 ---
# 每行显示 3 个商品
cols_per_row = 3
for i in range(0, len(ITEMS), cols_per_row):
    cols = st.columns(cols_per_row)
    # 处理每一行的列
    for j in range(cols_per_row):
        if i + j < len(ITEMS):
            item = ITEMS[i + j]
            with cols[j]:
                # 卡片容器
                with st.container():
                    st.markdown(f"""
                    <div class="item-card">
                        <div class="item-emoji">{item['icon']}</div>
                        <div class="item-name">{item['name']}</div>
                        <div class="item-price">¥ {item['price']:,}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 按钮控制区
                    b_col1, b_col2, b_col3 = st.columns([1, 2, 1])
                    
                    with b_col1:
                        st.button(
                            "－", 
                            key=f"sell_{item['id']}", 
                            on_click=update_count, 
                            args=(item['id'], -1, item['price']),
                            use_container_width=True
                        )
                    
                    with b_col2:
                        # 显示当前拥有数量
                        count = st.session_state[item['id']]
                        st.markdown(f"<div style='text-align: center; line-height: 2.5rem; font-weight: bold; font-size: 1.2rem;'>{count}</div>", unsafe_allow_html=True)
                        
                    with b_col3:
                        st.button(
                            "＋", 
                            key=f"buy_{item['id']}", 
                            on_click=update_count, 
                            args=(item['id'], 1, item['price']),
                            type="primary", # 购买按钮高亮
                            use_container_width=True
                        )
                    st.markdown("<br>", unsafe_allow_html=True)
# ==========================================
# 5. 底部：购物小票
# ==========================================
if total_spent > 0:
    st.markdown("---")
    
    # 1. 拼接 HTML 字符串
    # 这里的关键是：所有样式都写在内联 style 里，确保 flex 布局生效
    html_content = f"""
<div style="
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    max-width: 500px;
    margin: 0 auto;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    color: #333;
    font-family: 'Courier New', Courier, monospace;
">
    <h2 style="text-align: center; border-bottom: 2px dashed #333; padding-bottom: 10px; margin-bottom: 20px; font-weight: 800;">
        🧾 支付宝账单
    </h2>
    """
    
    # 2. 循环添加已购商品
    for item in ITEMS:
        count = st.session_state[item['id']]
        if count > 0:
            html_content += f"""
<div style="display: flex; justify-content: space-between; margin: 10px 0; border-bottom: 1px solid #eee; padding-bottom: 5px;">
    <span style="text-align: left; font-weight: bold;">{item['name']} x{count}</span>
    <span style="font-weight: bold; color: #e74c3c;">¥ {item['price'] * count:,.0f}</span>
</div>
            """

    # 3. 添加总计
    html_content += f"""
<div style="
    display: flex; 
    justify-content: space-between; 
    font-size: 1.3rem; 
    font-weight: 900; 
    margin-top: 20px; 
    border-top: 3px solid #333; 
    padding-top: 15px;
">
    <span>总计消费:</span>
    <span>¥ {total_spent:,.0f}</span>
</div>
</div>
    """
    
    # 4. 【核心修复点】渲染 HTML
    # 必须加上 unsafe_allow_html=True，否则就会显示成你看到的那种乱码
    st.markdown(html_content, unsafe_allow_html=True)
    
    # 彻底花光彩蛋
    if balance == 0:
        st.balloons()
        st.success("恭喜你！你已经身无分文，可以安心退休了！")

# 底部留白
st.markdown("<br><br><br>", unsafe_allow_html=True)



import sqlite3
import uuid  # <--- 新增导入
import datetime
import os
# 持久化目录（Streamlit Share 仅~/目录可持久化）
DB_DIR = os.path.expanduser("~/")
DB_FILE = os.path.join(DB_DIR, "visit_stats.db")
# -------------------------- 配置 --------------------------
#DB_FILE = "visit_stats.db"

def init_db():
    """初始化数据库（包含自动修复旧表结构的功能）"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    
    # 1. 确保表存在（这是旧逻辑）
    c.execute('''CREATE TABLE IF NOT EXISTS daily_traffic 
                 (date TEXT PRIMARY KEY, 
                  pv_count INTEGER DEFAULT 0)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS visitors 
                 (visitor_id TEXT PRIMARY KEY, 
                  first_visit_date TEXT)''')
    
    # 2. 【关键修复】手动检查并添加缺失的列 (Schema Migration)
    # 获取 visitors 表的所有列名
    c.execute("PRAGMA table_info(visitors)")
    columns = [info[1] for info in c.fetchall()]
    
    # 如果发现旧数据库里没有 last_visit_date，就动态添加进去
    if "last_visit_date" not in columns:
        try:
            c.execute("ALTER TABLE visitors ADD COLUMN last_visit_date TEXT")
            # 可选：把所有老数据的最后访问时间初始化为他们的首次访问时间，避免空值
            c.execute("UPDATE visitors SET last_visit_date = first_visit_date WHERE last_visit_date IS NULL")
        except Exception as e:
            print(f"数据库升级失败: {e}")

    conn.commit()
    conn.close()

def get_visitor_id():
    """获取或生成访客ID（修复版：使用UUID替代不稳定的内部API）"""
    if "visitor_id" not in st.session_state:
        # 生成一个唯一的随机ID，并保存在当前会话状态中
        st.session_state["visitor_id"] = str(uuid.uuid4())
    return st.session_state["visitor_id"]

def track_and_get_stats():
    """核心统计逻辑"""
    init_db()
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    
    today_str = datetime.datetime.utcnow().date().isoformat()
    visitor_id = get_visitor_id() # 这里调用修改后的函数

    # --- 写操作 (仅当本Session未计数时执行) ---
    if "has_counted" not in st.session_state:
        try:
            # 1. 更新每日PV
            c.execute("INSERT OR IGNORE INTO daily_traffic (date, pv_count) VALUES (?, 0)", (today_str,))
            c.execute("UPDATE daily_traffic SET pv_count = pv_count + 1 WHERE date=?", (today_str,))
            
            # 2. 更新访客UV信息
            c.execute("SELECT visitor_id FROM visitors WHERE visitor_id=?", (visitor_id,))
            exists = c.fetchone()
            
            if exists:
                c.execute("UPDATE visitors SET last_visit_date=? WHERE visitor_id=?", (today_str, visitor_id))
            else:
                c.execute("INSERT INTO visitors (visitor_id, first_visit_date, last_visit_date) VALUES (?, ?, ?)", 
                          (visitor_id, today_str, today_str))
            
            conn.commit()
            st.session_state["has_counted"] = True
            
        except Exception as e:
            st.error(f"数据库写入错误: {e}")

    # --- 读操作 ---
    # 1. 获取今日UV
    c.execute("SELECT COUNT(*) FROM visitors WHERE last_visit_date=?", (today_str,))
    today_uv = c.fetchone()[0]
    
    # 2. 获取历史总UV
    c.execute("SELECT COUNT(*) FROM visitors")
    total_uv = c.fetchone()[0]

    # 3. 获取今日PV
    c.execute("SELECT pv_count FROM daily_traffic WHERE date=?", (today_str,))
    res_pv = c.fetchone()
    today_pv = res_pv[0] if res_pv else 0
    
    conn.close()
    
    return today_uv, total_uv, today_pv

# -------------------------- 页面展示 --------------------------

# 执行统计
try:
    today_uv, total_uv, today_pv = track_and_get_stats()
except Exception as e:
    st.error(f"统计模块出错: {e}")
    today_uv, total_uv, today_pv = 0, 0, 0

# CSS 样式
st.markdown("""
<style>
    .metric-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 20px;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    .metric-box {
        text-align: center;
    }
    .metric-label {
        color: #6c757d;
        font-size: 0.85rem;
        margin-bottom: 2px;
    }
    .metric-value {
        color: #212529;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .metric-sub {
        font-size: 0.7rem;
        color: #adb5bd;
    }
    /* 优化右上角按钮样式 */
    div[data-testid="column"]:nth-child(2) button {
        width: 100%;
        white-space: nowrap;
        font-size: 0.85rem;
        padding: 4px 8px;
    }
    /* 确保HTML按钮和原生按钮样式一致 */
    div[data-testid="column"]:nth-child(3) button:hover {
        background-color: #0284c7;
    }
</style>
""", unsafe_allow_html=True)

# 展示数据
st.markdown(f"""
<div class="metric-container">
    <div class="metric-box">
        <div class="metric-sub">今日 UV: {today_uv} 访客数</div>
    </div>
    <div class="metric-box" style="border-left: 1px solid #dee2e6; border-right: 1px solid #dee2e6; padding-left: 20px; padding-right: 20px;">
        <div class="metric-sub">历史总 UV: {total_uv} 总独立访客</div>
    </div>
</div>
""", unsafe_allow_html=True)
