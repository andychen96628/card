import streamlit as st

# 設定網頁標題與風格
st.set_page_config(page_title="排七：絕對不輸助手", layout="wide", initial_sidebar_state="expanded")

# 自定義 CSS 讓 UI 更像遊戲介面
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stNumberInput { font-size: 20px; }
    .stSelectbox { font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🃏 排七 (Sevens) 戰術分析儀表板")
st.subheader("目標：確保你不是最後一名 (斷路、卡牌、最小化蓋牌點數)")

# --- 側邊欄：手牌輸入 ---
st.sidebar.header("📥 輸入你的 8 張手牌")
suits = {'♠️ 黑桃': 'S', '♥️ 紅心': 'H', '♦️ 方塊': 'D', '♣️ 梅花': 'C'}
ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

my_hand = []
for i in range(8):
    cols = st.sidebar.columns(2)
    s = cols[0].selectbox(f"花色 {i+1}", list(suits.keys()), key=f"s_{i}")
    r = cols[1].selectbox(f"數字 {i+1}", ranks, index=6, key=f"r_{i}")
    my_hand.append({'suit': s, 'rank': r, 'val': ranks.index(r) + 1})

# --- 主畫面：桌面局勢 ---
st.header("📍 當前桌面數字 (兩端)")
col1, col2, col3, col4 = st.columns(4)
table_status = {}

with col1:
    st.write("♠️ 黑桃")
    s_min = st.slider("Min", 1, 7, 7, key="sm")
    s_max = st.slider("Max", 7, 13, 7, key="sx")
    table_status['♠️ 黑桃'] = (s_min, s_max)

with col2:
    st.write("♥️ 紅心")
    h_min = st.slider("Min ", 1, 7, 7, key="hm")
    h_max = st.slider("Max ", 7, 13, 7, key="hx")
    table_status['♥️ 紅心'] = (h_min, h_max)

with col3:
    st.write("♦️ 方塊")
    d_min = st.slider("Min  ", 1, 7, 7, key="dm")
    d_max = st.slider("Max  ", 7, 13, 7, key="dx")
    table_status['♦️ 方塊'] = (d_min, d_max)

with col4:
    st.write("♣️ 梅花")
    c_min = st.slider("Min   ", 1, 7, 7, key="cm")
    c_max = st.slider("Max   ", 7, 13, 7, key="cx")
    table_status['♣️ 梅花'] = (c_min, c_max)

# --- 戰略引擎邏輯 ---
st.divider()
st.header("🧠 AI 戰略分析報告")

playable = []
blocking_cards = []  # 關鍵斷路牌 (5, 6, 8, 9)

for card in my_hand:
    curr_min, curr_max = table_status[card['suit']]
    # 檢查是否可出
    if card['val'] == curr_min - 1 or card['val'] == curr_max + 1 or card['val'] == 7:
        playable.append(card)
    # 檢查是否為戰略斷路牌
    if card['val'] in [5, 6, 8, 9]:
        blocking_cards.append(card)

res_col1, res_col2 = st.columns(2)

with res_col1:
    st.success("✅ 目前可出的牌")
    if playable:
        for p in playable:
            st.write(f"👉 **{p['suit']} {p['rank']}**")
            # 提示長龍
            same_suit_count = len([c for c in my_hand if c['suit'] == p['suit']])
            if same_suit_count >= 3:
                st.caption(f"💡 建議出這張，你還有 {same_suit_count-1} 張同花色牌等著出。")
    else:
        st.warning("⚠️ 沒牌可接！必須選擇一張蓋牌。")

with res_col2:
    st.error("💀 關鍵斷路器 (卡牌建議)")
    if blocking_cards:
        for b in blocking_cards:
            is_stuck = "已上桌" if (table_status[b['suit']][0] < b['val'] < table_status[b['suit']][1]) else "在手中"
            st.write(f"🛑 **{b['suit']} {b['rank']}** ({is_stuck})")
            st.caption("這張是通往 A 或 K 的必經之路。若你不出，別人後面整排都會爆掉。")
    else:
        st.write("目前手中無關鍵斷路牌。")

# --- 蓋牌策略 ---
st.divider()
if st.button("🚨 點擊獲取：被迫蓋牌時的優先順序"):
    # 排序邏輯：點數由小到大 (A=1 最優先蓋)
    st.info("若真的要蓋牌，請依照以下順序（從點數最小的開始，保護你的總分）：")
    sorted_hand = sorted(my_hand, key=lambda x: x['val'])
    suggestion = " -> ".join([f"{c['suit']}{c['rank']}" for c in sorted_hand])
    st.write(suggestion)
