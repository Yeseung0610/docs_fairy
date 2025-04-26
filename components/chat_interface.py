import streamlit as st
import openai_api
import random  # Add randomness to force CSS refresh
import re

def initialize_chat():
    """Initialize the chat session state if not already done"""
    # 기존 워크플로우 유지를 위해 messages 키는 더 이상 직접 사용하지 않지만,
    # 초기 마이그레이션을 위해 남겨둡니다.
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # chat_tabs: 탭 단위로 메시지를 관리
    if 'chat_tabs' not in st.session_state:
        st.session_state.chat_tabs = {
            "일반 대화": []
        }

    # 현재 활성 탭
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "일반 대화"

    # (기존 코드에서 messages 만 쓰던 경우 탭 시스템으로 데이터 이동)
    if st.session_state.messages:
        st.session_state.chat_tabs[st.session_state.current_tab] = st.session_state.messages
        st.session_state.messages = []

def add_new_chat():
    """Add a new chat tab"""
    new_tab_name = f"새 대화 {len(st.session_state.chat_tabs) + 1}"
    st.session_state.chat_tabs[new_tab_name] = []
    st.session_state.current_tab = new_tab_name

def delete_chat(tab_name):
    """Delete a chat tab"""
    if tab_name in st.session_state.chat_tabs:
        del st.session_state.chat_tabs[tab_name]
        # 삭제한 탭이 활성 탭이었다면 첫 번째 탭으로 이동
        if tab_name == st.session_state.current_tab:
            if st.session_state.chat_tabs:
                st.session_state.current_tab = list(st.session_state.chat_tabs.keys())[0]
            else:
                st.session_state.chat_tabs = {"일반 대화": []}
                st.session_state.current_tab = "일반 대화"

def highlight_important_info(text):
    """Highlight links, important phrases and data in AI response"""
    # URL 하이라이트
    text = re.sub(r'(https?://[^\s]+)', r'[링크](\1)', text)

    # 키워드 강조
    keywords = ["중요", "주의", "필수", "핵심", "요약", "결론"]
    for kw in keywords:
        text = re.sub(f'({kw}[:\\s])', r'**\1**', text)

    # 퍼센트, 날짜 강조
    text = re.sub(r'(\d+\.?\d*\s*%)', r'**\1**', text)
    text = re.sub(r'(\d{4}-\d{2}-\d{2})', r'**\1**', text)

    return text

def render_chat_interface():
    """Render the main chat interface"""
    st.title("My Task AI - 당신만을 위한 개인 업무 비서")
    st.caption("문서 요정 🧚🏻‍♀️")

    # CSS 캐시 강제 갱신 ID
    random_id = random.randint(1, 1_000_000)

    # 커스텀 CSS (아바타 감추기, 하이라이트 스타일)
    st.markdown(f"""
    <style data-version="{random_id}">
      [data-testid="StChatMessageAvatar"] > div > img {{
        display: none !important;
      }}
      .highlighted {{
        background-color: #FFEFD5;
        padding: 2px 4px;
        border-radius: 3px;
      }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <script data-version="{random_id}">
      document.querySelectorAll('style:not([data-version="{random_id}"])').forEach(el => {{
        if (el.innerHTML.includes('StChatMessageAvatar')) {{
          el.remove();
        }}
      }});
    </script>
    """, unsafe_allow_html=True)

    # ── 새 대화 / 대화 삭제 버튼 ──
    col_add, col_del = st.columns([0.1, 0.1], gap="small")
    with col_add:
        if st.button("➕ 새 대화", key="add_new_chat"):
            add_new_chat()
            st.rerun()
    with col_del:
        if len(st.session_state.chat_tabs) > 1 and st.button("🗑️ 대화 삭제", key="delete_current_chat"):
            delete_chat(st.session_state.current_tab)
            st.rerun()

    # ── 탭 생성 및 렌더링 ──
    all_tabs = list(st.session_state.chat_tabs.keys())
    tabs = st.tabs(all_tabs)

    for tab_container, tab_name in zip(tabs, all_tabs):
        with tab_container:
            # 탭이 활성화될 때 current_tab 갱신
            st.session_state.current_tab = tab_name
            messages = st.session_state.chat_tabs[tab_name]

            # 기존 메시지 출력
            for msg in messages:
                st.chat_message(msg["role"]).markdown(
                    msg["content"], unsafe_allow_html=True
                )

            # 사용자 입력 받기
            user_input = st.chat_input("메시지를 입력하세요…", key=f"input_{tab_name}")
            if user_input:
                # 사용자 메시지 저장
                messages.append({"role": "user", "content": user_input})

                # AI 응답 생성
                with st.spinner("AI가 응답 중입니다..."):
                    api_payload = [
                        {"role": m["role"], "content": m["content"]}
                        for m in messages
                    ]
                    ai_resp = openai_api.get_ai_response(api_payload)
                    highlighted = highlight_important_info(ai_resp)

                # AI 메시지 저장 및 상태 갱신
                messages.append({"role": "assistant", "content": highlighted})
                st.session_state.chat_tabs[tab_name] = messages
                st.rerun()
