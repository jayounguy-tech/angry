import streamlit as st
import random
import time

# --- 頁面設定 ---
st.set_page_config(
    page_title="家庭生存模擬器",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS 樣式 (暗黑風格 & 聊天氣泡) ---
st.markdown("""
<style>
    /* 全局背景與字體 */
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
    }
    
    /* 標題樣式 */
    h1 {
        color: #FF5252 !important;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        text-shadow: 2px 2px 4px #000000;
        border-bottom: 2px solid #333;
        padding-bottom: 20px;
    }
    
    /* 輸入框樣式 */
    .stTextInput > div > div > input {
        background-color: #2C2C2C;
        color: #FFFFFF;
        border: 1px solid #444;
        border-radius: 10px;
    }
    
    /* 聊天氣泡樣式 - 對方 (憤怒模式) */
    .chat-bubble-ai {
        background-color: #381E1E; /* 深紅色背景 */
        border-left: 4px solid #D32F2F;
        color: #FFD7D7;
        padding: 15px;
        border-radius: 0px 15px 15px 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.5);
        font-size: 16px;
        line-height: 1.6;
    }
    
    /* 聊天氣泡樣式 - 使用者 (弱勢模式) */
    .chat-bubble-user {
        background-color: #263238; /* 深藍灰色 */
        color: #ECEFF1;
        padding: 10px 15px;
        border-radius: 15px 15px 0px 15px;
        margin-bottom: 10px;
        text-align: right;
        float: right;
        clear: both;
        display: inline-block;
        box-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }
    
    /* 分隔線 */
    hr {
        border-color: #333;
    }

    /* 隱藏 Streamlit 預設的 header 和 footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- 模擬人格邏輯 (資料庫) ---
# 這裡儲存語氣片段，用於隨機組合成無限的碎念
intro_phrases = [
    "你與其有空在那邊講這些有的沒的",
    "讚什麼讚",
    "嫌我顧小孩不夠累嗎",
    "比起什麼幽默風趣",
    "我都講過幾次了",
    "你不要以為你在那邊裝傻就沒事了",
    "我看你真的是過太爽",
    "現在都幾點了"
]

topics = [
    "你女鵝的作業",
    "小孩的聯絡簿",
    "補習班的錄音",
    "那個圖書館借的布可星球的書",
    "我叫你領的包裹",
    "小孩明天的便當盒",
    "才藝班的學費",
    "學校發的那些通知單"
]

actions = [
    "她聯絡簿簽名了沒",
    "她作業在那邊拖拖拉拉你不要也在那邊跟著她拖拖拉拉的好不好",
    "檢查了嗎",
    "你去領了沒已經最後一天了喔有一件已經付款了",
    "你記得帶我的證件去不要到時候沒辦法領又要白跑一趟",
    "明天聯絡簿上要帶的東西弄好了嗎",
    "趕快讓她做一做還有八九本過幾天要還了不然要過期了",
    "你快幫她弄好錄完之後傳給我我再傳過補習班",
    "家裡都要我整理什麼都要我用腦袋整天只會想那些沒營養的"
]

conclusions = [
    "都幾點了小孩還不睡覺",
    "如果不是沒空我也不想要叫你弄",
    "我明天白天還有晚上還要上課事情很多",
    "真的會被你們父女氣死",
    "快點去弄不要讓我講第二次",
    "你在那邊滑手機是會幫忙做家事是不是"
]

# --- 核心邏輯函式 ---
def generate_angry_response(user_input):
    """
    根據使用者的輸入，生成一段符合「焦慮碎念」風格的回覆。
    邏輯：隨機組合開頭、主題、動作和結尾，並且極少使用標點符號。
    """
    
    # 1. 偵測關鍵字做特殊回覆
    if "愛你" in user_input or "辛苦" in user_input:
        return "少在那邊跟我灌迷湯現在講這些都沒有用你去把陽台衣服收進來摺好比較實際小孩明天要穿運動服你不要明天早上才在那邊翻箱倒櫃找沒有"
    
    if "等一下" in user_input or "晚點" in user_input:
        return "又要等一下又要晚點每次都這樣講結果最後都是我做你女鵝就是學你這種拖延症明天早上起不來遲到看是你載還是我載反正我沒空"
        
    if "好啦" in user_input or "知道了" in user_input:
        return "知道了就趕快去動啊嘴巴講知道了身體黏在沙發上是有什麼用垃圾車都要走了你還不快點去綁垃圾袋"

    # 2. 生成隨機碎念 (混合模式)
    # 隨機決定句子長度，模擬一口氣講很長
    phrase_intro = random.choice(intro_phrases)
    phrase_topic = random.choice(topics)
    phrase_action = random.choice(actions)
    phrase_conclusion = random.choice(conclusions)
    
    # 80% 機率是長句子，20% 機率是極長句子
    if random.random() > 0.2:
        response = f"{phrase_intro}{phrase_topic}{phrase_action}{phrase_conclusion}"
    else:
        # 雙重打擊模式
        phrase_topic2 = random.choice(topics)
        phrase_action2 = random.choice(actions)
        response = f"{phrase_intro}{phrase_topic}{phrase_action}還有{phrase_topic2}{phrase_action2}{phrase_conclusion}"

    return response

# --- 初始化 Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 初始歡迎語 (也是碎念)
    welcome_msg = "你回來了喔襪子不要亂丟我都講幾次了快去洗手小孩功課還沒看快去幫忙看你是要我一個人忙死嗎"
    st.session_state.messages.append({"role": "ai", "content": welcome_msg})

# --- UI 佈局 ---

st.title("⚡ 家庭生存模擬器")
st.markdown("<p style='text-align: center; color: #888;'>狀態：<span style='color:red;'>極度焦慮</span> | 任務：<span style='color:orange;'>活下去</span></p>", unsafe_allow_html=True)

# 顯示聊天記錄
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
            <div class="chat-bubble-user">
                {msg["content"]}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="chat-bubble-ai">
                <strong>老婆:</strong><br>
                {msg["content"]}
            </div>
        """, unsafe_allow_html=True)

# 輸入區域
st.markdown("<br>", unsafe_allow_html=True) # 間距
if prompt := st.chat_input("輸入你的回覆 (例如: 好啦我現在去、再五分鐘)..."):
    # 1. 顯示使用者訊息
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f"""
        <div class="chat-bubble-user">
            {prompt}
        </div>
    """, unsafe_allow_html=True)

    # 2. 模擬思考/打字延遲 (增加壓力感)
    with st.spinner('對方正在輸入中...'):
        time.sleep(random.uniform(0.5, 1.5)) # 隨機延遲

    # 3. 獲取 AI 回覆
    response_text = generate_angry_response(prompt)
    
    # 4. 顯示 AI 訊息
    st.session_state.messages.append({"role": "ai", "content": response_text})
    st.markdown(f"""
        <div class="chat-bubble-ai">
             <strong>老婆:</strong><br>
            {response_text}
        </div>
    """, unsafe_allow_html=True)
    
    # 強制刷新以確保捲動到底部 (Streamlit 的特性)
    st.rerun()

# --- 底部裝飾 ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: #555; font-size: 12px;'>警告：本模擬器內容可能引起心跳加速、手心冒汗等症狀，請斟酌使用。</div>", unsafe_allow_html=True)