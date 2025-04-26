import streamlit as st
import db
from components import folder_management, chat_interface

# 페이지 기본 설정
st.set_page_config(
    page_title="My Task AI - 개인 업무 비서",
    page_icon="🧚‍♀️",
    layout="wide",
)

# DB 초기화 (최초 1회)
db.initialize_db()

# 채팅 세션 초기화
chat_interface.initialize_chat()

# 사이드바 렌더링 (폴더/페이지 관리)
folder_management.render_sidebar()

# 페이지 선택 여부에 따라 상세 페이지 혹은 채팅 인터페이스 분기
if 'selected_page_id' in st.session_state:
    folder_management.render_page_detail()
else:
    chat_interface.render_chat_interface()
