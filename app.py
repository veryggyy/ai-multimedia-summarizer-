import streamlit as st
import google.generativeai as genai
import tempfile
from docx import Document
from pptx import Presentation

# 介面標題
st.set_page_config(page_title="AI 萬能摘要器", layout="wide")
st.title("📑 多媒體內容摘要與翻譯工具")

# 側邊欄輸入 API Key
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("請輸入 Google API Key", type="password")
    st.info("支援格式：.docx, .pptx, .mp3, .mp4")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    uploaded_file = st.file_uploader("拖曳檔案上傳", type=["docx", "pptx", "mp3", "mp4"])

    if uploaded_file:
        with st.spinner("AI 正在深度解析並翻譯中..."):
            try:
                # 處理音訊或影片
                if uploaded_file.type in ["audio/mpeg", "video/mp4"]:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as f:
                        f.write(uploaded_file.getbuffer())
                        g_file = genai.upload_file(path=f.name)
                        response = model.generate_content([g_file, "請詳細列出此內容重點，並翻譯成台灣繁體中文"])
                
                # 處理 Word 或 PPT
                else:
                    text = ""
                    if "word" in uploaded_file.type:
                        doc = Document(uploaded_file)
                        text = "\n".join([p.text for p in doc.paragraphs])
                    elif "presentation" in uploaded_file.type:
                        prs = Presentation(uploaded_file)
                        text = "\n".join([s.text for slide in prs.slides for s in slide.shapes if hasattr(s, "text")])
                    
                    response = model.generate_content(f"請將以下內容整理成條列式重點摘要，並翻譯為台灣繁體中文：\n\n{text}")

                st.success("分析完成！")
                st.markdown("### ✨ 重點摘要與翻譯")
                st.write(response.text)
            except Exception as e:
                st.error(f"發生錯誤：{e}")
else:
    st.warning("👈 請先在左側選單輸入 API Key 以開始使用")
