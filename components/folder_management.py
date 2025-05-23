import streamlit as st
import db
import pdf_utils
from datetime import date


def render_sidebar():
    """사이드바: 폴더 및 페이지 관리 UI를 렌더링합니다."""
    st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #EF5D6B; font-weight: 600;">내 폴더</h2>
        <p style="color: #888888; font-size: 14px;">업무 문서를 효율적으로 관리하세요</p>
    </div>
    """, unsafe_allow_html=True)

    # 새 폴더 추가
    with st.sidebar.expander("+ 새 폴더 추가", expanded=False):
        with st.form(key="add_folder_form", clear_on_submit=True):
            new_folder = st.text_input(
                "폴더명",
                key="new_folder",
                placeholder="폴더 이름을 입력하세요",
                label_visibility="collapsed"
            )
            col1, col2 = st.columns([1, 1])
            with col1:
                submit = st.form_submit_button("추가")
            with col2:
                cancel = st.form_submit_button("취소")

            if submit and new_folder:
                if db.add_folder(new_folder):
                    st.success(f"'{new_folder}'가 추가되었습니다.")
                else:
                    st.error("동일한 이름의 폴더가 있습니다.")
                st.rerun()

    # 폴더 및 페이지 목록
    folders = db.get_all_folders()
    if 'expanded_folders' not in st.session_state:
        st.session_state.expanded_folders = {}

    for folder in folders:
        fid = folder['id']
        fname = folder['folder_name']

        if fid not in st.session_state.expanded_folders:
            st.session_state.expanded_folders[fid] = False

        with st.sidebar.expander(f"📁 {fname}", expanded=st.session_state.expanded_folders[fid]):
            st.session_state.expanded_folders[fid] = True
            pages = db.get_folder_pages(fid)

            if not pages:
                st.info("페이지가 없습니다. 아래에서 새 페이지를 추가하세요.")

            # 기존 페이지 리스트
            for page in pages:
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.button(
                            f"📄 {page['page_name']}",
                            key=f"select_page_{page['id']}",
                            help="페이지 열기",
                            use_container_width=True
                    ):
                        st.session_state.selected_page_id = page['id']
                        st.session_state.selected_folder_id = fid
                        st.rerun()
                with col2:
                    if st.button(
                            "🗑️",
                            key=f"delete_page_{page['id']}",
                            help="페이지 삭제"
                    ):
                        db.delete_page(page['id'])
                        st.rerun()

            # 새 페이지 추가 폼
            with st.form(key=f"add_page_form_{fid}", clear_on_submit=True):
                st.markdown(
                    "<p style='margin-top: 10px; font-weight: 500;'>새 페이지 추가</p>",
                    unsafe_allow_html=True
                )
                new_page_name = st.text_input(
                    "페이지 이름",
                    key=f"new_page_name_{fid}",
                    placeholder="페이지 이름 입력",
                    label_visibility="collapsed"
                )
                # 기록 날짜 입력
                selected_date = st.date_input(
                    "기록 날짜",
                    value=date.today(),
                    key=f"new_page_date_{fid}"
                )

                docs_type = st.selectbox(
                    "문서 유형",
                    ("문서", "회의록"),
                    key=f"new_page_type_{fid}"
                )
                # PDF 업로드 기능
                uploaded_pdf = st.file_uploader(
                    "(선택) PDF 업로드하여 회의록 생성",
                    type=["pdf"],
                    key=f"pdf_upload_{fid}",
                    help="PDF 파일을 업로드하면 AI가 회의록 형식으로 내용을 채워줍니다."
                )

                submit_button = st.form_submit_button("추가", use_container_width=True)

                if submit_button:
                    if not new_page_name:
                        st.error("페이지 이름을 입력해주세요.")
                    elif uploaded_pdf:
                        # PDF 파일이 있으면 회의록 생성
                        with st.spinner("AI가 PDF를 분석하여 페이지를 생성 중입니다..."):
                            date_str = selected_date.isoformat()
                            meeting_notes = pdf_utils.process_pdf_to_meeting_notes(uploaded_pdf, docs_type)
                            page_id = db.add_page_with_content(new_page_name, fid, meeting_notes, date_str)
                            if page_id:
                                st.session_state.selected_page_id = page_id
                                st.session_state.selected_folder_id = fid
                                st.success(f"'{new_page_name}' 페이지가 생성되었습니다.")
                                st.rerun()
                            else:
                                st.error("회의록 생성 중 오류가 발생했습니다.")
                    else:
                        # PDF 파일이 없으면 빈 페이지 생성
                        page_id = db.add_page_with_content(new_page_name, fid, "")
                        if page_id:
                            st.session_state.selected_page_id = page_id
                            st.session_state.selected_folder_id = fid
                            st.success(f"빈 페이지 '{new_page_name}'가 추가되었습니다.")
                            st.rerun()
                        else:
                            st.error("페이지 추가 중 오류가 발생했습니다.")


def render_page_detail():
    """메인 영역: 선택된 페이지의 상세 내용을 렌더링합니다."""
    pid = st.session_state.selected_page_id
    page = db.get_page(pid)

    # 폴더명 찾기
    folder_id = st.session_state.selected_folder_id
    folders = db.get_all_folders()
    folder_name = next((f['folder_name'] for f in folders if f['id'] == folder_id), "")

    # 상단 네비게이션 바
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        if st.button("← 뒤로", key="back_button"):
            del st.session_state['selected_page_id']
            st.rerun()
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center;">
                <h2>{page['page_name']}</h2>
                <p style="color: #888888; font-size: 14px;">📁 {folder_name}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        # 날짜 표시
        if page.get('date'):
            st.write(f"**기록 날짜:** {page['date']}")

    # 구분선 추가
    st.markdown(
        "<hr style='margin: 0 0 20px 0; border: none; height: 1px; background-color: #f0f0f0;'>",
        unsafe_allow_html=True
    )

    # 내용 편집 영역
    with st.form(key="edit_page_form", clear_on_submit=False):
        content = st.text_area("페이지 내용", value=page['content'], height=400)
        if st.form_submit_button("저장"):
            db.update_page_content(pid, content)
            st.success("저장되었습니다.")

    # 날짜 변경 폼
    with st.form(key="edit_date_form", clear_on_submit=False):
        new_date = st.date_input(
            "날짜 수정",
            value=date.fromisoformat(page.get('date') or date.today().isoformat()),
            key="edit_page_date"
        )
        if st.form_submit_button("날짜 저장"):
            db.update_page_date(pid, new_date.isoformat())
            st.success("날짜가 업데이트되었습니다.")
