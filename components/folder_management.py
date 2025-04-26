import streamlit as st
import db

def render_sidebar():
    """사이드바: 폴더 및 페이지 관리 UI를 렌더링합니다."""
    st.sidebar.title("폴더 관리")

    # --- 새 폴더 추가 폼 ---
    with st.sidebar.form(key="add_folder_form", clear_on_submit=True):
        new_folder = st.text_input("새 폴더 추가", key="new_folder")
        if st.form_submit_button("폴더 추가") and new_folder:
            if db.add_folder(new_folder):
                st.success(f"폴더 '{new_folder}'가 추가되었습니다.")
            else:
                st.error("해당 이름의 폴더가 이미 존재합니다.")

    # --- 폴더 트리 & 페이지 목록 ---
    folders = db.get_all_folders()
    for folder in folders:
        folder_id = folder['id']
        folder_name = folder['folder_name']

        with st.sidebar.expander(folder_name, expanded=True):
            pages = db.get_pages_in_folder(folder_id)
            for page in pages:
                if st.button(page['page_name'], key=f"page_{page['id']}"):
                    st.session_state.selected_folder_id = folder_id
                    st.session_state.selected_page_id = page['id']
                    st.rerun()  # 페이지 전환을 위해 재실행

            # 페이지 추가
            new_page = st.text_input("➕ 새 페이지", key=f"new_page_{folder_id}")
            if st.button("추가", key=f"add_page_{folder_id}") and new_page:
                db.add_page(new_page, folder_id)
                st.success(f"페이지 '{new_page}'가 생성되었습니다.")
                st.rerun()

def render_page_detail():
    """메인 영역: 선택된 페이지의 상세 내용을 보여주고 편집할 수 있습니다."""
    pid = st.session_state.selected_page_id
    page = db.get_page(pid)
    folder = db.get_all_folders()
    folder_name = next(f['folder_name'] for f in folder if f['id'] == page['folder_id'])

    # 페이지 헤더와 삭제 버튼
    col_title, col_del = st.columns([0.9, 0.1], gap="small")
    with col_title:
        st.header(page['page_name'])
        st.subheader(f"폴더: {folder_name}")
    with col_del:
        if st.button("🗑️ 페이지 삭제"):
            db.delete_page(pid)
            del st.session_state['selected_page_id']
            st.rerun()

    # 내용 편집 폼
    with st.form(key="edit_page_form", clear_on_submit=False):
        content = st.text_area("페이지 내용", value=page['content'], height=400)
        if st.form_submit_button("저장"):
            db.update_page_content(pid, content)
            st.success("저장되었습니다.")
