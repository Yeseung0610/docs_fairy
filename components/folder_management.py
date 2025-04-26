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
            st.rerun()

    # 저장된 폴더를 가져와서 expander 형태로 표시
    folders = db.get_all_folders()
    if 'expanded_folders' not in st.session_state:
        st.session_state.expanded_folders = {}

    for folder in folders:
        fid = folder['id']
        fname = folder['folder_name']

        # expander 상태 초기화
        if fid not in st.session_state.expanded_folders:
            st.session_state.expanded_folders[fid] = False

        with st.sidebar.expander(fname, expanded=st.session_state.expanded_folders[fid]):
            # 클릭 시 expander 열림 상태 유지
            st.session_state.expanded_folders[fid] = True

            # --- 폴더 내 페이지 목록 ---
            pages = db.get_folder_pages(fid)
            for page in pages:
                col1, col2 = st.columns([4, 1], gap="small")
                with col1:
                    # 페이지 선택 버튼
                    if st.button(page['page_name'], key=f"select_page_{page['id']}"):
                        st.session_state.selected_page_id = page['id']
                        st.session_state.selected_folder_id = fid
                        st.rerun()
                with col2:
                    # 페이지 삭제 버튼
                    if st.button("🗑️", key=f"delete_page_{page['id']}"):
                        db.delete_page(page['id'])
                        st.rerun()

            # --- 새 페이지 추가 폼 ---
            with st.form(key=f"add_page_form_{fid}", clear_on_submit=True):
                new_page = st.text_input("새 페이지 추가", key=f"new_page_{fid}")
                if st.form_submit_button("페이지 추가") and new_page:
                    db.add_page(new_page, fid)
                    st.rerun()


def render_page_detail():
    """메인 영역: 선택된 페이지의 상세 내용을 렌더링합니다."""
    pid = st.session_state.selected_page_id
    page = db.get_page(pid)

    # 폴더명 찾기
    folder_id = st.session_state.selected_folder_id
    folders = db.get_all_folders()
    folder_name = next((f['folder_name'] for f in folders if f['id'] == folder_id), "")

    # 뒤로 가기 버튼
    if st.button("← 뒤로", key="back_button"):
        del st.session_state['selected_page_id']
        del st.session_state['selected_folder_id']
        st.rerun()

    # 상세 페이지 헤더
    st.header(page['page_name'])
    st.subheader(f"폴더: {folder_name}")

    # 내용 편집 폼
    with st.form(key="edit_page_form", clear_on_submit=False):
        content = st.text_area("페이지 내용", value=page['content'], height=400)
        if st.form_submit_button("저장"):
            db.update_page_content(pid, content)
            st.success("저장되었습니다.")
