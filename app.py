import streamlit as st
import random
import time

# 嘗試匯入 Gemini 套件，若失敗則設定旗標，避免程式崩潰
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# --- 設定 API Key ---
# ⚠️ 注意：請勿將含有 API Key 的程式碼上傳至公開儲存庫
API_KEY = "AIzaSyDA5kveo53vq0wPIYnvFVMnJcub3RkiEQ4"

# 1. 頁面基本設定
st.set_page_config(
    page_title="家庭生存模擬器 (AI 加強版)",
    page_icon="💀",
    layout="centered"
)

# 2. 自定義 CSS (黑暗風格 + 聊天氣泡樣式 + 文字增亮)
st.markdown("""
<style>
    /* 全域背景設為深灰黑 */
    .stApp {
        background-color: #121212;
        color: #ffffff; /* 調整為全白，更亮 */
    }
    
    /* 強制所有 Markdown 文字更亮 */
    div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 500; /* 稍微加粗增加對比 */
    }
    
    /* 調整標題顏色 */
    h1, h2, h3 {
        color: #ff5252 !important; /* 帶點紅色的警告感 */
        font-family: 'Helvetica', sans-serif;
    }
    
    /* 輸入框樣式 */
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444;
    }
    
    /* 隱藏 Streamlit 預設的漢堡選單和 footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 自定義聊天氣泡的 CSS (輔助 Streamlit 原生 chat) */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.08); /* 背景稍微亮一點點 */
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* 使用者氣泡微調 */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: rgba(64, 224, 208, 0.15); /* 增加一點不透明度 */
    }
    
    /* 機器人(老婆/媽媽)氣泡微調 */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: rgba(255, 82, 82, 0.15); 
        border-left: 3px solid #ff5252;
    }
</style>
""", unsafe_allow_html=True)

# 3. 側邊欄設定 (已移除 Key 輸入，僅顯示狀態)
with st.sidebar:
    st.header("⚙️ 系統狀態")
    if HAS_GENAI:
        st.success("✅ AI 模組已載入")
        st.caption("目前模式：AI 智慧碎念")
    else:
        st.error("⚠️ 未偵測到 `google-generativeai` 套件")
        st.caption("目前模式：隨機語錄 (Fallback)")

# 4. 定義「崩潰碎碎念」資料庫 (Fallback 用，或是作為 AI 的 Few-shot 範例)
NAGGING_DATABASE = [
    # 原有範例
    "你與其有空在那邊看這些有的沒的為什麼不看一下你女鵝的作業她聯絡簿簽名了沒她作業在那邊拖拖拉拉你不要也在那邊跟著她拖拖拉拉的好不好然後我叫你領的包裹你去領了沒已經最後一天了喔有一件已經付款了你記得帶我的證件去不要到時候沒辦法領又要白跑一趟",
    "讚什麼讚 小孩的作業檢查了嗎？明天聯絡簿上要帶的東西弄好了嗎？都幾點了 小孩還不睡覺",
    "嫌我顧小孩不夠累嗎？家裡都要我整理，什麼都要我用，腦袋整天只會想那些沒營養的......",
    "比起什麼幽默風趣你女鵝英文補習的作業要錄音你錄了沒你不要以為她大考昨天剛考完就沒事了你快幫她弄好錄完之後傳給我我再傳過補習班然後圖書館借的布可星球的書趕快讓她做一做還有八九本過幾天要還了不然要過期了我明天白天還有晚上還要上課事情很多如果不是沒空我也不想要叫你弄",
    "你現在是在滑手機嗎？垃圾倒了沒？碗洗了沒？你要不要看一下現在幾點了？",
    "我講過幾次了襪子不要亂丟，你是不是聽不懂人話？跟你女兒一樣講都講不聽，我真的是上輩子欠你們的。",
    "不要跟我嬉皮笑臉，明天要繳的學費單在桌上你看到了沒有？還有那個安親班老師說她最近上課很不專心，你有空不會關心一下嗎？",
    "去洗澡！不要再拖了！全家都在等你一個人！",
    "你那個包裹到底是買什麼？家裡已經堆不下了你知不知道？錢是這樣花的嗎？",
    "我看你倒是很閒嘛，還有空在那邊打字聊天，去把陽台衣服收進來折一折好不好？",
    "嘆什麼氣？我才想嘆氣吧？每天像個陀螺一樣轉，你幫過什麼忙？",
    # 新增語錄 (小孩作業與學校篇)
    "你女鵝那個數學評量寫了沒？明天要考試了你知不知道？",
    "聯絡簿簽名沒？老師寫說明天要帶水彩用具，家裡到底有沒有？沒有現在要去買嗎？現在幾點了？",
    "她英文單字背了沒？上次考那個什麼分數？你都不會覺得丟臉嗎？",
    "不要只會問『吃飽沒』，你有看過她功課嗎？字寫得像鬼畫符一樣你也不管？",
    "學校明天要交的照片洗了沒？我上禮拜就跟你講了，現在才在問？",
    "安親班老師打電話來說她今天又沒帶課本，是你整理書包還是她整理書包？",
    "才藝班的學費袋放在桌上三天了，你是沒看到還是裝作沒看到？",
    "她明天戶外教學要帶便當，你能不能幫忙想一下要弄什麼？不要什麼都丟給我！",
    "聯絡簿上寫說要帶保特瓶，家裡有嗎？沒有你去樓下超商買個飲料喝掉把瓶子留下來！",
    "你女鵝說她直笛不見了，是不是你上次打掃亂塞？",
    "她作文寫不出來在那邊哭，你是不會過去教一下嗎？滑手機會讓作文變出來嗎？",
    "明天要穿制服還是運動服？你不知道？你到底是不是這個家的人？",
    "老師說她最近上課都在發呆，跟你在家一樣，遺傳真的很可怕。",
    "那個什麼線上學習單，截止日期是什麼時候？你不要等到最後一刻才在那邊弄網路。",
    "家長會你要去還是我去？反正你去了也是在那邊發呆，算了還是我去吧。",
    # 新增語錄 (家事與衛生篇)
    "浴室排水孔都是頭髮，你洗完澡是不會順手清一下嗎？",
    "馬桶蓋可以稍微掀起來嗎？還是你有瞄準障礙？",
    "洗碗精沒了是不會講喔？要等到我要洗碗發現擠不出來才甘願？",
    "衣服洗好了在洗衣機裡面悶多久了？是要讓它發霉重洗一次嗎？",
    "地上那團衛生紙是誰的？你的？還是你女鵝的？垃圾桶就在旁邊很難嗎？",
    "桌上喝完的飲料杯是不會拿去丟喔？要長螞蟻了你知不知道！",
    "你那是洗碗還是沖水？油都還在上面，你是要我再洗一次是不是？",
    "冰箱那個牛奶過期三天了，你是眼睛有問題還是鼻子有問題？",
    "鞋子脫下來擺好很難嗎？門口亂得跟戰場一樣。",
    "陽台的植物都快枯死了，你不是說你要顧？顧到哪裡去？",
    "冷氣濾網多久沒洗了？難怪我最近一直過敏，你都不會主動看一下嗎？",
    "垃圾車音樂響了你還坐著？是要我穿著睡衣衝出去倒嗎？",
    "地板黏黏的你沒感覺嗎？拖地是很委屈你嗎？",
    "那件襯衫你要穿就早點拿出來燙，不要明天早上才在那邊叫。",
    "浴室鏡子上的水漬是你噴的吧？刷牙一定要噴得到處都是嗎？",
    # 新增語錄 (生活習慣與態度篇)
    "你現在是怎樣？不講話是怎樣？",
    "我在跟你講話你眼睛看著電視是什麼意思？",
    "又在打電動？小孩在旁邊看你打電動，真是好榜樣。",
    "幾點了還不睡？明天早上叫不起來不要怪我掀被子。",
    "你那個手機是黏在手上是不是？去哪裡都要帶著？",
    "假日一定要睡到中午嗎？家裡多少事情要做你知不知道？",
    "你肥皂用完不要直接丟在洗手台上，軟爛在那邊很噁心耶。",
    "講一件事要講八百遍，我真的覺得我會高血壓。",
    "你剛剛有沒有在聽？那我剛剛說什麼？你看，你根本沒在聽。",
    "笑？你還笑得出來？",
    "你那什麼態度？我欠你的嗎？",
    "每次叫你做個事就像要你的命一樣，我自己做還比較快。",
    "去把頭髮吹乾！滴得到處都是水，踩到滑倒算誰的？",
    "你內褲破洞了是不會丟掉喔？還穿？",
    "坐有坐相好不好，癱在那邊像一團肉。",
    # 新增語錄 (購物與金錢篇)
    "這個月電費怎麼這麼貴？你是不是冷氣都沒在關？",
    "又買？這個家裡已經有三個了你還要買？",
    "你去全聯買東西有看價錢嗎？這個貴了二十塊你也買得下去？",
    "那個包裹又是你的？你這個月花多少錢在網拍上了？",
    "小孩補習費要轉帳了，薪水進來了沒？",
    "不要每次去超商都買那些垃圾食物給小孩吃，很難教耶。",
    "我叫你買醬油你買成醬油膏？眼睛是裝飾品嗎？",
    "發票記得存載具，不要每次都拿一堆廢紙回來塞口袋。",
    "我們要不要省一點？下個月保險費要繳了你知不知道？",
    "你那張信用卡年費繳了沒？不要到時候又在那邊哇哇叫。",
    # 新增語錄 (情緒勒索與崩潰篇)
    "我覺得我真的很失敗，怎麼會教出這種老公跟小孩。",
    "是不是我死了你們才會知道我的重要？",
    "大家都說我很幸福，誰知道我回到家像個女傭一樣。",
    "如果不是為了小孩，我早就......算了，講了你也不懂。",
    "你以前不是這樣的，為什麼現在變這麼懶？",
    "好啊，都不要做啊，反正家裡髒死算了，大家都不要動。",
    "我頭很痛，你能不能讓我安靜一下？",
    "不要碰我，我現在很火大。",
    "你去照照鏡子看看你現在這副德性。",
    "我當初真的是瞎了眼。",
    "你跟你媽真的一個樣，碎碎念的功力是遺傳的是不是？（反諷）",
    "有沒有人跟你說過跟你講話很累？",
    "我真的心很累，你懂那種感覺嗎？不，你不懂，你只在乎你自己。",
    "現在是怎樣？要吵架是不是？來啊！",
    "去睡客廳！我不想看到你！",
    # 更多生活瑣事
    "遙控器電池沒電了是不會換喔？拍一拍就會有電嗎？",
    "你洗澡洗了一個小時是在裡面幹嘛？",
    "小孩水壺漏水了，你能不能幫忙修一下？還是又要買新的？",
    "明天早餐吃什麼？你不要又要我想要我買要我弄。",
    "你那個朋友又要來借錢？你敢借試試看。",
    "這週末回娘家你表現好一點，不要一直滑手機。",
    "車子該保養了吧？那個燈亮很久了，你是要等到顧路才甘願？",
    "你刮鬍刀清一下好不好，洗手台都是鬍渣。",
    "不要在床上吃餅乾！會有屑屑！",
    "你女鵝說她要買哀鳳，你不要在那邊亂答應，沒錢！",
    "去把窗戶關起來，要下雨了。",
    "你襯衫領子都黃了，是沒洗乾淨還是你流汗太誇張？",
    "那個誰誰誰的老公都會帶她去吃大餐，阿你勒？滷肉飯？",
    "我生理期來不舒服，你是不會倒杯熱水喔？直男癌末期耶。",
    "不要一直在那邊抖腳，看得很煩。",
    "你那什麼表情？不爽講出來啊！",
    "手機聲音關小聲一點！吵死人了！",
    "去幫小孩吹頭髮！手斷掉了是不是？",
    "晚餐想吃什麼？隨便？隨便最難煮你知不知道！",
    "你看看人家隔壁老王，週末都帶全家出去玩，我們勒？在家大眼瞪小眼。",
    "衣服不要掛得密密麻麻，這樣怎麼會乾？",
    "你鼻毛跑出來了，修一下好不好，能看嗎？",
    "我真的很想離家出走，讓你們知道沒有我這個家會變怎樣。",
    "好了啦，閉嘴啦，去做事啦。",
    "不要再問我鑰匙在哪裡，門口櫃子上！眼睛長頭頂喔！"
]

# 5. 初始化 Session State (儲存對話紀錄)
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 開場白
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "你還知道要回來？都幾點了？"
    })

# 6. 設定 AI Model 邏輯
def get_ai_response(user_text, api_key):
    if not HAS_GENAI:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # 使用輕量快速的模型
        
        # 建立崩潰家長的 System Prompt
        system_prompt = f"""
        你現在要扮演一位情緒非常不穩定、壓力很大、講話速度很快、非常愛碎碎念的配偶（老婆/媽媽）。
        你的對話對象是你的另一半（老公），他很懶惰、常常忘東忘西、只會滑手機。
        
        請遵守以下說話風格：
        1. **極度碎碎念**：一口氣講很長，不要換行，很少用標點符號，像機關槍一樣。
        2. **主題**：圍繞在小孩作業、家事沒做、包裹沒領、錢亂花、生活習慣差。
        3. **語氣**：憤怒、無奈、諷刺、質問。不要給出有建設性的建議，只要抱怨。
        4. **禁止**：不要出現「親愛的」、「老公」這種親暱稱呼，直接用「你」或者「喂」。
        5. **長度**：回覆要長一點，可以把好幾件不相關的舊帳翻出來一起講。
        
        以下是你的說話範例（請模仿這種語氣）：
        {random.sample(NAGGING_DATABASE, 3)}
        
        現在，老公對你說：「{user_text}」
        請用崩潰碎碎念的風格回覆他：
        """
        
        response = model.generate_content(system_prompt)
        return response.text
    except Exception as e:
        return None

# 7. 介面標題
st.title("☠️ 家庭生存模擬器")
st.caption("請謹慎輸入，對方情緒很不穩定...")

# 8. 顯示歷史訊息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 9. 處理輸入與回應
if user_input := st.chat_input("說點話來辯解 (或討罵)..."):
    # 顯示使用者輸入
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 模擬思考停頓 (增加壓迫感)
    time.sleep(random.uniform(0.5, 1.5))

    response_text = ""
    
    # --- 優先層：關鍵字檢測 (Rule-based) ---
    # 這些特定的關鍵字會觸發預設好的強烈反應
    if "對不起" in user_input or "抱歉" in user_input:
        response_text = "道歉有用的話要警察幹嘛？你自己看看現在家裡亂成什麼樣子？講一百次了有改過嗎？"
    elif "累" in user_input:
        response_text = "你累？我比你更累好不好！我白天要上班晚上還要顧小孩，回到家還要看你這張臉，你到底在累什麼？"
    elif "愛你" in user_input:
        response_text = "少在那邊花言巧語，去把地拖一拖比較實際啦，愛我？愛我就去洗碗啊！"
    elif "做愛" in user_input or "愛愛" in user_input:
        response_text = "都幾點了你還在想這個？小孩還沒睡你是不會去哄喔？整天只想爽，家事怎麼沒看你這麼積極？去把衣服洗一洗冷靜一下啦！"
    else:
        # --- 次要層：AI 生成 或 隨機資料庫 ---
        if HAS_GENAI:
            # 嘗試使用 AI 生成
            ai_reply = get_ai_response(user_input, API_KEY)
            if ai_reply:
                response_text = ai_reply
            else:
                # API 失敗 (例如 Key 錯誤)，Fallback 到資料庫
                selected_sentences = random.sample(NAGGING_DATABASE, k=random.randint(4, 6))
                response_text = "[系統: AI連線不穩，切換回隨機碎念模式] " + " ".join(selected_sentences)
        else:
            # 沒有 Key 或沒有套件，使用資料庫隨機組合
            selected_sentences = random.sample(NAGGING_DATABASE, k=random.randint(4, 6))
            response_text = " ".join(selected_sentences)

    # 顯示機器人回應 (帶有打字機效果)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        # 模擬快速碎念的打字速度 (稍快)
        for chunk in response_text:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.02) 
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})