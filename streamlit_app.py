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
