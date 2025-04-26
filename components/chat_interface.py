import streamlit as st
import openai_api
import random
import re

def initialize_chat():
    """Initialize the chat session state if not already done"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize chat tabs
    if 'chat_tabs' not in st.session_state:
        st.session_state.chat_tabs = {
            "일반 대화": []
        }
    
    # Initialize current tab
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "일반 대화"
        
    # Migrate old messages to the tab system if needed
    if st.session_state.messages and not st.session_state.chat_tabs["일반 대화"]:
        st.session_state.chat_tabs["일반 대화"] = st.session_state.messages.copy()

def add_new_chat():
    """Add a new chat tab"""
    new_tab_name = f"새 대화 {len(st.session_state.chat_tabs) + 1}"
    st.session_state.chat_tabs[new_tab_name] = []
    st.session_state.current_tab = new_tab_name
    
def delete_chat(tab_name):
    """Delete a chat tab"""
    if tab_name in st.session_state.chat_tabs:
        # Delete the tab
        del st.session_state.chat_tabs[tab_name]
        
        # Set current tab to the first tab if the deleted tab was the current tab
        if tab_name == st.session_state.current_tab:
            if st.session_state.chat_tabs:
                st.session_state.current_tab = list(st.session_state.chat_tabs.keys())[0]
            else:
                # If no tabs left, create a new default tab
                st.session_state.chat_tabs = {"일반 대화": []}
                st.session_state.current_tab = "일반 대화"
    
def highlight_important_info(text):
    """Highlight links, important phrases and data in AI response"""
    # Highlight URLs with markdown syntax
    text = re.sub(r'(https?://[^\s]+)', r'[링크](\1)', text)
    
    # Highlight important keywords with bold
    keywords = ["중요", "주의", "필수", "핵심", "요약", "결론"]
    for keyword in keywords:
        text = re.sub(f'({keyword}[:\\s])', r'**\1**', text)
    
    # Highlight data points and numbers
    text = re.sub(r'(\d+\.?\d*\s*%)', r'**\1**', text) # Percentages
    text = re.sub(r'(\d{4}-\d{2}-\d{2})', r'**\1**', text) # Dates
    
    return text
    
def render_chat_interface():
    """Render the main chat interface"""
    # Title with improved design
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <h1 style="color: #4B9FE1; margin-bottom: 5px;">My Task AI</h1>
        <p style="color: #888888; font-size: 16px; margin-top: 0;">당신만을 위한 개인 업무 비서</p>
        <div style="font-size: 24px; margin: 10px 0;">🧚🏻‍♀️</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Force all CSS cache to refresh
    random_id = random.randint(1, 1000000)
    
    # Apply custom CSS for the chat interface
    st.markdown(f"""
    <style data-version="{random_id}">
    /* 전체 배경 및 기본 스타일 */
    .main .block-container {{
        padding-top: 2rem;
        max-width: 1000px;
        margin: 0 auto;
    }}
    
    /* 채팅 메시지 스타일링 */
    [data-testid="stChatMessage"] {{
        border-radius: 12px !important;
        border: 1px solid #f0f2f6 !important;
        padding: 0.5rem 1rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease !important;
    }}
    
    /* 사용자 메시지 스타일링 */
    .element-container .stChatMessage.user [data-testid="StChatMessageContent"] {{
        background-color: #EBF5FF !important;
    }}
    
    /* AI 메시지 스타일링 */
    .element-container .stChatMessage.assistant [data-testid="StChatMessageContent"] {{
        background-color: #FFFFFF !important;
    }}
    
    /* Hide default avatar images */
    [data-testid="StChatMessageAvatar"] > div > img {{
        display: none !important;
    }}
    
    /* User avatar styling */
    .element-container .stChatMessage.user [data-testid="StChatMessageAvatar"] {{
        background-color: #D1F5F0 !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }}
    
    .element-container .stChatMessage.user [data-testid="StChatMessageAvatar"]::after {{
        content: "👤";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 20px;
    }}
    
    /* Assistant avatar styling */
    .element-container .stChatMessage.assistant [data-testid="StChatMessageAvatar"] {{
        background-color: #FFFFFF !important;
        border: 1px solid #F0F2F6 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }}
    
    .element-container .stChatMessage.assistant [data-testid="StChatMessageAvatar"]::after {{
        content: "🧚🏻‍♀️";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 20px;
    }}
    
    /* 탭 스타일링 */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 8px 16px;
        background-color: #f0f2f6;
    }}
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background-color: #4B9FE1;
        color: white;
    }}
    
    /* 버튼 스타일링 */
    .stButton button {{
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    
    .stButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    
    /* 입력 필드 스타일링 */
    [data-testid="stChatInput"] {{
        border-radius: 20px;
        border: 1px solid #E0E4E8;
        padding: 8px 16px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    
    /* Style for highlighted information */
    .highlighted {{
        background-color: #FFEFD5;
        padding: 2px 4px;
        border-radius: 3px;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Clear existing cache
    st.markdown(f"""
    <script data-version="{random_id}">
    document.querySelectorAll('style:not([data-version="{random_id}"])').forEach(el => {{
        if (el.innerHTML.includes('StChatMessageAvatar')) {{
            el.remove();
        }}
    }});
    </script>
    """, unsafe_allow_html=True)
    
    # 대화 관리 영역
    with st.container():
        # 상단 탭 및 컨트롤 행
        col1, col2 = st.columns([7, 3])
        
        with col1:
            # 탭 생성 (모던한 디자인)
            all_tabs = list(st.session_state.chat_tabs.keys())
            # 탭 스타일을 더 시각적으로 구분되게 만들기
            tabs = st.tabs(all_tabs)
            
            # 현재 탭 인덱스 찾기
            current_tab_index = all_tabs.index(st.session_state.current_tab)
        
        with col2:
            # 대화 관리 버튼들
            button_cols = st.columns([1, 1])
            with button_cols[0]:
                if st.button("💬 새 대화", key="add_new_chat", use_container_width=True):
                    add_new_chat()
                    st.rerun()
            
            with button_cols[1]:
                if st.button("🗑️ 대화 초기화", key="reset_chat", use_container_width=True):
                    st.session_state.chat_tabs[st.session_state.current_tab] = []
                    st.rerun()
    
    # 구분선 추가
    st.markdown("<hr style='margin: 15px 0; border: none; height: 1px; background-color: #f0f0f0;'>", unsafe_allow_html=True)
    
    # 현재 선택된 탭의 내용 표시
    with tabs[current_tab_index]:
        # 현재 탭의 메시지 참조
        messages = st.session_state.chat_tabs[st.session_state.current_tab]
        
        # 탭 컨트롤 (이름 변경, 삭제 등)
        tab_control_cols = st.columns([4, 1])
        with tab_control_cols[0]:
            st.markdown(f"<p style='color: #888888; margin-bottom: 10px;'>현재 대화: <b>{st.session_state.current_tab}</b></p>", unsafe_allow_html=True)
            
        with tab_control_cols[1]:
            # 탭 삭제 버튼 (마지막 탭은 삭제 불가)
            if len(st.session_state.chat_tabs) > 1 and st.button("삭제", key=f"delete_tab_{current_tab_index}", use_container_width=True):
                delete_chat(st.session_state.current_tab)
                st.rerun()
        
        # 채팅 컨테이너 (스크롤 가능)
        chat_container = st.container()
        
        # 입력 컨테이너 (화면 하단에 고정)
        input_container = st.container()
        
        # 채팅 입력창 (하단에 배치)
        with input_container:
            # chat_input에는 label 매개변수가 없어서 다른 방식으로 접근성 지원
            # st.chat_input API는 placeholder만 지원하므로 
            # 숨겨진 label 요소를 추가하여 스크린 리더 접근성 지원
            st.markdown('<label for="chat_input" style="display: none;">채팅 메시지 입력</label>', unsafe_allow_html=True)
            user_input = st.chat_input("무엇이든 물어보세요", key="chat_input")
        
        # 대화 내용 표시
        with chat_container:
            if not messages:
                # 비어있는 대화일 경우 가이드 텍스트 표시
                st.markdown("""
                <div style="text-align: center; padding: 40px 20px; color: #888888;">
                    <div style="font-size: 48px; margin-bottom: 20px;">👋</div>
                    <h3>반갑습니다!</h3>
                    <p>업무에 도움이 필요하신가요? 무엇이든 물어보세요.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 대화 메시지 표시 (최신 메시지가 하단에 오도록)
            for i, message in enumerate(messages):
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])
                else:
                    with st.chat_message("assistant"):
                        st.markdown(message["content"], unsafe_allow_html=True)
        
        # 사용자 입력 처리
        if user_input:
            # 사용자 메시지를 대화 기록에 추가
            messages.append({"role": "user", "content": user_input})
            
            # AI 응답 얻기
            with st.spinner("AI가 응답 중입니다..."):
                # API 호출 형식으로 변환
                api_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
                ai_response = openai_api.get_ai_response(api_messages)
                
                # 중요 정보 강조
                highlighted_response = highlight_important_info(ai_response)
                
                # AI 응답을 대화 기록에 추가
                messages.append({"role": "assistant", "content": highlighted_response})
                
            # 채팅 탭 데이터 업데이트 및 화면 갱신
            st.session_state.chat_tabs[st.session_state.current_tab] = messages
            st.rerun()
