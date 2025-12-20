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
