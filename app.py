"""
AI 작가와의 대화 - 학생용 메인 앱
초등학교 6학년 학생들이 이야기를 읽고 AI 작가와 대화합니다.
"""

import streamlit as st
from datetime import datetime
from pathlib import Path

# 유틸리티 임포트
from utils.data_manager import (
    save_student,
    get_student,
    load_conversation,
    save_conversation,
    load_guide_questions
)
from utils.gemini_client import get_client
from utils.prompts import get_author_role_prompt
from utils.question_analyzer import analyze_question, get_score_level
from utils.report_generator import generate_report

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
    .story-box {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin-bottom: 1rem;
        color: #000000;
        line-height: 1.8;
    }
    .score-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .score-excellent {
        background-color: #d4edda;
        color: #155724;
    }
    .score-good {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    .score-normal {
        background-color: #fff3cd;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)


def load_story():
    """이야기 파일을 로드합니다."""
    story_path = Path(__file__).parent / "story.txt"
    try:
        with open(story_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "이야기 파일을 찾을 수 없습니다. story.txt 파일을 확인해주세요."


def init_session_state():
    """세션 상태 초기화"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'student_id' not in st.session_state:
        st.session_state.student_id = ""
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ""
    if 'conversation_data' not in st.session_state:
        st.session_state.conversation_data = None
    if 'story_content' not in st.session_state:
        st.session_state.story_content = load_story()


def login_page():
    """로그인/식별 화면"""
    st.markdown('<div class="main-title">📚 AI 작가와의 대화</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">이야기를 읽고 작가님께 질문해보세요!</div>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 👋 환영합니다!")
        st.markdown("이야기를 읽고 AI 작가님과 대화를 나눌 수 있어요.")
        st.markdown("")

        # 학번 입력
        student_id = st.text_input(
            "학번을 입력하세요",
            placeholder="예: 20231",
            help="숫자로 된 학번을 입력하세요"
        )

        # 이름 입력
        student_name = st.text_input(
            "이름을 입력하세요",
            placeholder="예: 홍길동",
            help="본인의 이름을 입력하세요"
        )

        st.markdown("")

        # 시작하기 버튼
        if st.button("🚀 시작하기", use_container_width=True, type="primary"):
            if not student_id or not student_name:
                st.error("학번과 이름을 모두 입력해주세요.")
            else:
                # 학생 정보 저장
                save_student(student_id, student_name)

                # 세션 상태 업데이트
                st.session_state.logged_in = True
                st.session_state.student_id = student_id
                st.session_state.student_name = student_name

                # 대화 이력 로드
                conv_data = load_conversation(student_id)
                conv_data['name'] = student_name
                st.session_state.conversation_data = conv_data

                st.rerun()


def main_page():
    """메인 학습 화면"""
    # 헤더
    col_left, col_right = st.columns([3, 1])
    with col_left:
        st.markdown(f'<div class="main-title">📚 AI 작가와의 대화</div>', unsafe_allow_html=True)
    with col_right:
        st.markdown(f"**{st.session_state.student_name}** 학생")
        st.caption(f"학번: {st.session_state.student_id}")

    st.markdown("---")

    # 2단 레이아웃
    left_col, right_col = st.columns([1, 1])

    # 왼쪽: 이야기 표시
    with left_col:
        st.markdown("### 📖 이야기")
        with st.container():
            st.markdown(
                f'<div class="story-box">{st.session_state.story_content.replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True
            )

        # 통계 표시
        stats = st.session_state.conversation_data.get('statistics', {})
        total_q = stats.get('total_questions', 0)
        avg_score = stats.get('average_score', 0.0)

        st.markdown("---")
        st.markdown("### 📊 나의 활동")
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric("총 질문 수", f"{total_q}개")
        with metric_col2:
            st.metric("평균 점수", f"{avg_score:.1f}/5.0")

        # 리포트 다운로드 버튼
        if total_q > 0:
            if st.button("📄 내 리포트 보기", use_container_width=True):
                with st.spinner("리포트 생성 중..."):
                    report = generate_report(st.session_state.student_id)
                    st.download_button(
                        label="📥 리포트 다운로드",
                        data=report,
                        file_name=f"학습리포트_{st.session_state.student_id}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )

    # 오른쪽: 대화 영역
    with right_col:
        st.markdown("### 💬 작가님과의 대화")

        # 가이드 질문
        with st.expander("💡 질문 아이디어 보기"):
            guide_questions = load_guide_questions()
            st.markdown("**이런 질문을 해볼 수 있어요:**")
            for i, q in enumerate(guide_questions[:5], 1):
                if st.button(f"{i}. {q}", key=f"guide_{i}", use_container_width=True):
                    st.session_state.temp_question = q

        # 대화 이력 표시
        conversations = st.session_state.conversation_data.get('conversations', [])

        # 대화 컨테이너
        chat_container = st.container(height=400)

        with chat_container:
            if len(conversations) == 0:
                st.info("👋 작가님께 첫 질문을 해보세요!")
            else:
                for conv in conversations:
                    # 학생 질문
                    with st.chat_message("user"):
                        st.markdown(conv['question'])

                    # AI 답변
                    with st.chat_message("assistant", avatar="✍️"):
                        st.markdown(conv['answer'])

        # 질문 입력 영역
        st.markdown("---")

        # 임시 질문이 있으면 사용
        default_question = st.session_state.get('temp_question', '')
        if default_question:
            del st.session_state.temp_question

        user_question = st.text_area(
            "작가님께 질문하기",
            value=default_question,
            placeholder="이야기에 대해 궁금한 점을 물어보세요...",
            height=100,
            key="question_input"
        )

        if st.button("📤 질문하기", use_container_width=True, type="primary"):
            if user_question.strip():
                process_question(user_question.strip())
            else:
                st.warning("질문을 입력해주세요.")


def process_question(question):
    """질문 처리 로직"""
    with st.spinner("작가님이 답변을 생각하고 있어요..."):
        try:
            # 1. AI 작가 답변 생성
            client = get_client()
            prompt = get_author_role_prompt(st.session_state.story_content, question)
            answer = client.generate_response(prompt)

            # 2. 질문 분석 (백그라운드)
            score_data = analyze_question(question, st.session_state.story_content)
            print(f"[DEBUG] Score data: {score_data}")  # 디버깅

            # 3. 대화 이력에 추가
            new_conv = {
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "answer": answer,
                "score": score_data
            }

            st.session_state.conversation_data['conversations'].append(new_conv)
            print(f"[DEBUG] Added to session, total conversations: {len(st.session_state.conversation_data['conversations'])}")

            # 4. 저장
            success = save_conversation(
                st.session_state.student_id,
                st.session_state.student_name,
                st.session_state.conversation_data
            )
            print(f"[DEBUG] Save result: {success}")

            # 5. 화면 갱신
            st.success("답변을 받았어요!")
            st.rerun()

        except Exception as e:
            import traceback
            print(f"[ERROR] {traceback.format_exc()}")
            st.error(f"오류가 발생했습니다: {str(e)}")


def main():
    """메인 함수"""
    init_session_state()

    if not st.session_state.logged_in:
        login_page()
    else:
        main_page()


if __name__ == "__main__":
    main()
