import streamlit as st
import google.generativeai as genai
import tempfile
from docx import Document
from pptx import Presentation

# 1. 頁面標題與設定
st.set_page_config(page_title="AI 智能摘要工具", layout="centered")
st.title("🚀 多媒體內容摘要與翻譯工具")

# 2. 從後端讀取 API Key (使用者看不到)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.error("❌ 系統尚未配置 API Key，請聯繫管理員設定 Secrets。")
    st.stop()

# 3. 直接顯示上傳介面
uploaded_file = st.file_uploader("📂 請上傳檔案 (PPT, Word, MP3, MP4)", type=["docx", "pptx", "mp3", "mp4"])

if uploaded_file:
    with st.spinner("AI 正在解析並生成摘要中..."):
        try:
            # 處理影音
            if uploaded_file.type in ["audio/mpeg", "video/mp4"]:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as f:
                    f.write(uploaded_file.getbuffer())
                    g_file = genai.upload_file(path=f.name)
                    response = model.generate_content([g_file, "請分析此影音內容，列出重點摘要並翻譯成繁體中文"])
            
            # 處理 Word/PPT
            else:
                text_content = ""
                if "word" in uploaded_file.type:
                    doc = Document(uploaded_file)
                    text_content = "\n".join([p.text for p in doc.paragraphs])
                elif "presentation" in uploaded_file.type:
                    prs = Presentation(uploaded_file)
                    text_content = "\n".join([s.text for slide in prs.slides for s in slide.shapes if hasattr(s, "text")])
                
                response = model.generate_content(f"請條列此內容重點摘要，並譯為繁體中文：\n\n{text_content}")

            st.success("✅ 分析完成")
            st.subheader("📝 摘要結果")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"❌ 處理失敗: {e}")

st.divider()
st.caption("支援格式：.docx, .pptx, .mp3, .mp4")
