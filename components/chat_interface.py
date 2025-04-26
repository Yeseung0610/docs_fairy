import streamlit as st
import openai_api
import db
import random
import re

def initialize_chat():
    """DB에서 채팅 탭과 메시지를 로드하여 세션 상태에 저장합니다."""
    if 'chat_tabs' not in st.session_state:
        chats = db.get_all_chats()
        if not chats:
            # 기본 탭이 없으면 생성
            db.add_chat("일반 대화")
            chats = db.get_all_chats()
        # 채팅 탭별 메시지 로드
        st.session_state.chat_tabs = {
            chat_name: db.get_chat_messages(chat_name)
            for chat_name in chats
        }
    if 'current_tab' not in st.session_state:
        # 첫 번째 탭(가장 왼쪽)을 기본 활성 탭으로 설정
        st.session_state.current_tab = list(st.session_state.chat_tabs.keys())[0]

def add_new_chat():
    """새 채팅 탭을 추가하고 DB에도 기록합니다."""
    new_tab_name = f"새 대화 {len(st.session_state.chat_tabs) + 1}"
    if db.add_chat(new_tab_name):
        st.session_state.chat_tabs[new_tab_name] = []
        st.session_state.current_tab = new_tab_name

def delete_chat(tab_name):
    """채팅 탭을 삭제하고 DB에서도 제거합니다."""
    if db.delete_chat(tab_name):
        del st.session_state.chat_tabs[tab_name]
        # 삭제된 탭이 활성 탭이었으면, 남은 첫 번째 탭을 활성으로
        if tab_name == st.session_state.current_tab:
            remaining = list(st.session_state.chat_tabs.keys())
            if remaining:
                st.session_state.current_tab = remaining[0]
            else:
                # 모두 삭제됐으면 기본 탭 복구
                db.add_chat("일반 대화")
                st.session_state.chat_tabs = {"일반 대화": []}
                st.session_state.current_tab = "일반 대화"

def highlight_important_info(text):
    """AI 응답 내 중요 정보에 하이라이트를 적용합니다."""
    text = re.sub(r'(https?://[^\s]+)', r'[링크](\1)', text)
    keywords = ["중요", "주의", "필수", "핵심", "요약", "결론"]
    for kw in keywords:
        text = re.sub(f'({kw}[:\\s])', r'**\1**', text)
    text = re.sub(r'(\d+\.?\d*\s*%)', r'**\1**', text)
    text = re.sub(r'(\d{4}-\d{2}-\d{2})', r'**\1**', text)
    return text

def render_chat_interface():
    """메인 영역에 탭 방식의 채팅 UI를 렌더링합니다."""
    st.title("My Task AI - 당신만을 위한 개인 업무 비서")
    st.caption("문서 요정 🧚🏻‍♀️")

    # CSS 캐시 강제 갱신 ID
    random_id = random.randint(1, 1_000_000)
    st.markdown(f"""
    <style data-version="{random_id}">
      [data-testid="StChatMessageAvatar"] > div > img {{ display: none!important; }}
      .highlighted {{ background-color: #FFEFD5; padding: 2px 4px; border-radius: 3px; }}
    </style>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <script data-version="{random_id}">
      document.querySelectorAll('style:not([data-version="{random_id}"])').forEach(el => {{
        if (el.innerHTML.includes('StChatMessageAvatar')) {{ el.remove(); }}
      }});
    </script>
    """, unsafe_allow_html=True)

    # 새 대화 / 대화 삭제 버튼 (삭제 버튼 우측 정렬)
    col_add, col_del = st.columns([0.9, 0.1], gap="small")
    with col_add:
        if st.button("➕ 새 대화", key="add_new_chat"):
            add_new_chat()
            st.rerun()
    with col_del:
        if len(st.session_state.chat_tabs) > 1 and st.button("🗑️", key="delete_current_chat"):
            delete_chat(st.session_state.current_tab)
            st.rerun()

    # 탭을 생성 (새로 만든 탭은 dict 삽입 순서대로 오른쪽에 위치)
    all_tabs = list(st.session_state.chat_tabs.keys())
    tabs = st.tabs(all_tabs)

    # 각 탭 컨테이너에서 대화 내용을 렌더링
    for tab_container, tab_name in zip(tabs, all_tabs):
        with tab_container:
            st.session_state.current_tab = tab_name
            messages = st.session_state.chat_tabs[tab_name]

            # 기존 메시지 출력
            for msg in messages:
                st.chat_message(msg["role"]).markdown(msg["content"], unsafe_allow_html=True)

            # 사용자 입력
            user_input = st.chat_input("메시지를 입력하세요…", key=f"input_{tab_name}")
            if user_input:
                # 유저 메시지 세션과 DB 저장
                messages.append({"role": "user", "content": user_input})
                db.add_message(tab_name, "user", user_input)

                # AI 응답 생성 및 저장
                with st.spinner("AI가 응답 중입니다..."):
                    api_payload = [{"role": m["role"], "content": m["content"]} for m in messages]
                    ai_resp = openai_api.get_ai_response(api_payload)
                    highlighted = highlight_important_info(ai_resp)

                messages.append({"role": "assistant", "content": highlighted})
                db.add_message(tab_name, "assistant", highlighted)

                # 세션 상태 업데이트 후 리런
                st.session_state.chat_tabs[tab_name] = messages
                st.rerun()
