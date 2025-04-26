import streamlit as st
import openai_api
import db
import random
import re

def initialize_chat():
    # DB에서 채팅 탭과 메시지를 로드하여 세션 상태에 저장
    if 'chat_tabs' not in st.session_state:
        chats = db.get_all_chats()
        if not chats:
            db.add_chat("일반 대화")
            chats = db.get_all_chats()
        st.session_state.chat_tabs = {name: db.get_chat_messages(name) for name in chats}
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = list(st.session_state.chat_tabs.keys())[0]


def highlight_important_info(text: str) -> str:
    """AI 응답 내 중요 키워드 및 링크 하이라이트"""
    text = re.sub(r'(https?://[^\s]+)', r'[링크](\1)', text)
    keywords = ["중요", "주의", "필수", "핵심", "요약", "결론"]
    for kw in keywords:
        text = re.sub(f'({kw}[:\s])', r'**\1**', text)
    text = re.sub(r'(\d+\.?\d*\s*%)', r'**\1**', text)
    text = re.sub(r'(\d{4}-\d{2}-\d{2})', r'**\1**', text)
    return text


def add_new_chat():
    new_name = f"새 대화 {len(st.session_state.chat_tabs) + 1}"
    if db.add_chat(new_name):
        st.session_state.chat_tabs[new_name] = []
        st.session_state.current_tab = new_name


def delete_chat(tab_name: str):
    if db.delete_chat(tab_name):
        del st.session_state.chat_tabs[tab_name]
        if st.session_state.current_tab == tab_name:
            rem = list(st.session_state.chat_tabs.keys())
            if rem:
                st.session_state.current_tab = rem[0]
            else:
                db.add_chat("일반 대화")
                st.session_state.chat_tabs = {"일반 대화": []}
                st.session_state.current_tab = "일반 대화"


def render_chat_interface():
    st.title("문서 요정 🧚🏻‍")

    rid = random.randint(1, 1_000_000)
    st.markdown(f"""
    <style data-rid="{rid}">
      [data-testid="StChatMessageAvatar"] > div > img {{ display: none!important; }}
      .highlighted {{ background-color: #FFEFD5; padding: 2px 4px; border-radius: 3px; }}
    </style>
    """, unsafe_allow_html=True)

    col_add, col_del = st.columns([0.9, 0.1], gap="small")
    with col_add:
        if st.button("➕ 새 대화", key="add_new_chat"):
            add_new_chat()
            st.rerun()
    with col_del:
        if len(st.session_state.chat_tabs) > 1 and st.button("🗑️", key="delete_current_chat"):
            delete_chat(st.session_state.current_tab)
            st.rerun()

    all_tabs = list(st.session_state.chat_tabs.keys())
    tabs = st.tabs(all_tabs)
    for tab_c, tab_name in zip(tabs, all_tabs):
        with tab_c:
            st.session_state.current_tab = tab_name
            messages = st.session_state.chat_tabs[tab_name]

            for idx, msg in enumerate(messages):
                st.chat_message(msg["role"]).markdown(msg["content"], unsafe_allow_html=True)
                if msg["role"] == "assistant":
                    refs = re.findall(r'\[([^\]]+)\]\(page://(\d+)\)', msg["content"])
                    if refs:
                        cols = st.columns(len(refs))
                        for col, (title, pid) in zip(cols, refs):
                            with col:
                                if st.button(f"🔗 {title} 바로가기", key=f"nav_{tab_name}_{idx}_{pid}"):
                                    selected_id = int(pid)
                                    st.session_state.selected_page_id = selected_id
                                    page = db.get_page(selected_id)
                                    st.session_state.selected_folder_id = page['folder_id']
                                    st.rerun()

            user_input = st.chat_input("메시지를 입력하세요…", key=f"input_{tab_name}")
            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})
            db.add_message(tab_name, "user", user_input)

            # 시스템 메시지: 페이지 내용과 형식 지침 포함
            page_records = []
            for f in db.get_all_folders():
                page_records.extend(db.get_folder_pages(f['id']))
            docs = []
            for p in page_records:
                name = p['page_name']
                content = p['content'].strip() or "(내용 없음)"
                docs.append(f"■ [{name}](page://{p['id']})\n{content}")
            system_prompt = (
                "아래는 저장된 페이지 목록 및 내용입니다. "
                "답변에 문서를 인용하거나 참조할 경우, 반드시 제목을 [제목](page://id) 형식으로 링크하여 포함하십시오.\n\n"
                + "\n\n".join(docs)
            )

            payload = [{"role": "system", "content": system_prompt}]
            payload += [{"role": m["role"], "content": m["content"]} for m in messages]

            with st.spinner("AI가 응답 중입니다..."):
                ai_text = openai_api.get_ai_response(payload)
                ai_text = highlight_important_info(ai_text)

            messages.append({"role": "assistant", "content": ai_text})
            db.add_message(tab_name, "assistant", ai_text)
            st.session_state.chat_tabs[tab_name] = messages
            st.rerun()
