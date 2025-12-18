"""
AI 작가와의 대화 - 통합 앱
학생용 앱과 교사용 대시보드를 하나의 앱으로 통합
"""

import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="AI 작가와의 대화",
    page_icon="📚",
    layout="wide"
)

# CSS 스타일
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .role-button {
        text-align: center;
        padding: 2rem;
        margin: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """세션 상태 초기화"""
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'teacher_authenticated' not in st.session_state:
        st.session_state.teacher_authenticated = False


def role_selection_page():
    """역할 선택 화면"""
    st.markdown('<div class="main-title">📚 AI 작가와의 대화</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">이야기를 읽고 AI 작가와 대화해보세요</div>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 👋 환영합니다!")
        st.markdown("사용하실 기능을 선택해주세요.")
        st.markdown("")

        # 학생 버튼
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("#### 📖 학생")
            st.markdown("이야기를 읽고 AI 작가님께 질문하고, 친구들의 질문도 살펴보세요.")
            if st.button("학생으로 시작하기", key="student_btn", use_container_width=True, type="primary"):
                st.session_state.role = "student"
                st.rerun()

        with col_b:
            st.markdown("#### 👨‍🏫 교사")
            st.markdown("학생들의 질문 품질과 학습 현황을 확인하고 리포트를 생성하세요.")
            if st.button("교사로 시작하기", key="teacher_btn", use_container_width=True):
                st.session_state.role = "teacher"
                st.rerun()


def teacher_login_page():
    """교사 로그인 화면"""
    st.markdown('<div class="main-title">🔐 교사 인증</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 비밀번호를 입력하세요")
        st.markdown("")

        password = st.text_input(
            "교사 비밀번호",
            type="password",
            placeholder="비밀번호 입력"
        )

        col_login, col_back = st.columns(2)

        with col_login:
            if st.button("로그인", use_container_width=True, type="primary"):
                # 간단한 비밀번호 체크 (실제 환경에서는 환경변수나 더 안전한 방법 사용)
                if password == "teacher2024":  # 기본 비밀번호
                    st.session_state.teacher_authenticated = True
                    st.success("✅ 로그인 성공!")
                    st.rerun()
                else:
                    st.error("❌ 비밀번호가 올바르지 않습니다.")

        with col_back:
            if st.button("뒤로 가기", use_container_width=True):
                st.session_state.role = None
                st.rerun()

        st.markdown("---")
        st.info("💡 **기본 비밀번호**: teacher2024\n\n실제 배포 시에는 환경변수로 설정하는 것을 권장합니다.")


def main():
    """메인 함수"""
    init_session_state()

    # 역할이 선택되지 않았으면 선택 화면 표시
    if st.session_state.role is None:
        role_selection_page()
        return

    # 교사 역할이지만 인증되지 않았으면 로그인 화면
    if st.session_state.role == "teacher" and not st.session_state.teacher_authenticated:
        teacher_login_page()
        return

    # 역할에 따라 적절한 앱 실행
    if st.session_state.role == "student":
        # 학생 앱 실행
        import student_app
        student_app.run()

    elif st.session_state.role == "teacher":
        # 교사 대시보드 실행
        import teacher_app
        teacher_app.run()


if __name__ == "__main__":
    main()
