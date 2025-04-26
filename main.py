import streamlit as st
import db
from components import folder_management, chat_interface

# 페이지 기본 설정
st.set_page_config(
    page_title="My Task AI - 개인 업무 비서",
    page_icon="🧚‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 적용 (전체 앱 레이아웃)
st.markdown("""
<style>
    /* 좌우 여백 조정 - 상단 패딩 제거 */
    .block-container {
        padding-top: 0rem !important;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    
    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #FAFAFA;
        border-right: 1px solid #EEEEEE;
        padding-top: 0rem;
    }
    
    /* 앱 제목 스타일링 */
    .appview-container .main .block-container {
        max-width: 100%;
    }
    
    /* 헤더 영역 숨김 */
    header {
        visibility: hidden;
    }
    
    /* 푸터 영역 숨김 */
    footer {
        visibility: hidden;
    }
    
    /* "Made with Streamlit" 배너 숨김 */
    .viewerBadge_container__r5tak {
        display: none !important;
    }
    
    /* 스크롤바 스타일링 */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
</style>
""", unsafe_allow_html=True)

# DB 초기화 (최초 1회)
db.initialize_db()

# 채팅 세션 초기화
chat_interface.initialize_chat()

# 사이드바 렌더링 (폴더/페이지 관리)
folder_management.render_sidebar()

# 메인 컨텐츠 영역
main_container = st.container()

with main_container:
    # 페이지 선택 여부에 따라 상세 페이지 혹은 채팅 인터페이스 분기
    if 'selected_page_id' in st.session_state:
        folder_management.render_page_detail()
    else:
        chat_interface.render_chat_interface()
