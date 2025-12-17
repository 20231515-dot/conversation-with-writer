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
    load_guide_questions,
    get_student_sharing_status,
    update_student_sharing,
    get_shared_conversations
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


def generate_conversation_summary(conversations, student_name):
    """대화 내용을 요약 텍스트로 변환합니다."""
    summary_lines = [
        f"📚 {student_name}님의 AI 작가와의 대화",
        "=" * 50,
        ""
    ]

    for i, conv in enumerate(conversations, 1):
        summary_lines.append(f"[질문 {i}]")
        summary_lines.append(f"Q: {conv['question']}")
        summary_lines.append("")
        summary_lines.append(f"A: {conv['answer']}")
        summary_lines.append("")
        summary_lines.append("-" * 50)
        summary_lines.append("")

    summary_lines.append(f"총 질문 개수: {len(conversations)}개")
    summary_lines.append("")
    summary_lines.append("🤖 AI 작가와의 대화 플랫폼으로 생성됨")

    return "\n".join(summary_lines)


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
    if 'input_key' not in st.session_state:
        st.session_state.input_key = 0
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 0  # 0=My Conversation, 1=Peer Discussions
    if 'sharing_enabled' not in st.session_state:
        st.session_state.sharing_enabled = False


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


def show_my_conversation():
    """내 대화 탭 - 이야기 읽기 및 AI 작가와 대화"""
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

        # 통계 표시 (학생용 - 질문 수만)
        stats = st.session_state.conversation_data.get('statistics', {})
        total_q = stats.get('total_questions', 0)

        st.markdown("---")
        st.markdown("### 📊 나의 활동")
        st.metric("총 질문 수", f"{total_q}개")

        # 공유 설정
        st.markdown("---")
        st.markdown("### ⚙️ 공유 설정")
        with st.expander("친구들과 공유하기"):
            sharing_status = get_student_sharing_status(st.session_state.student_id)

            is_shared = st.checkbox(
                "내 질문을 다른 학생들과 공유하기",
                value=sharing_status.get('is_shared', False),
                help="다른 친구들이 내 질문을 볼 수 있어요 (점수는 보이지 않아요)",
                key="share_checkbox"
            )

            display_option = st.radio(
                "이름 표시 방식",
                ["이름 보이기", "익명으로 공유"],
                index=0 if sharing_status.get('display_as', 'named') == 'named' else 1,
                key="display_option"
            )

            if st.button("저장", use_container_width=True, key="save_sharing"):
                display_as = "named" if display_option == "이름 보이기" else "anonymous"
                success = update_student_sharing(
                    st.session_state.student_id,
                    st.session_state.student_name,
                    is_shared,
                    display_as
                )
                if success:
                    st.success("✅ 설정이 저장되었습니다!")
                    st.rerun()
                else:
                    st.error("설정 저장에 실패했습니다.")

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

        # 대화 요약 (복사용)
        if len(conversations) > 0:
            st.markdown("---")
            with st.expander("📋 대화 요약 (복사하기)"):
                summary = generate_conversation_summary(conversations, st.session_state.student_name)
                st.text_area(
                    "아래 내용을 복사하여 친구들과 공유하세요",
                    value=summary,
                    height=200,
                    key="summary_text",
                    label_visibility="collapsed"
                )
                st.caption("💡 위 텍스트를 드래그하여 복사(Ctrl+C 또는 Cmd+C)하세요")

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
            key=f"question_input_{st.session_state.input_key}"
        )

        if st.button("📤 질문하기", use_container_width=True, type="primary"):
            if user_question.strip():
                process_question(user_question.strip())
            else:
                st.warning("질문을 입력해주세요.")


def show_peer_discussions():
    """친구들의 질문 보기 탭 - 공유된 대화 조회"""
    st.markdown("### 📚 친구들의 질문")
    st.caption("다른 학생들이 어떤 질문을 했는지 살펴보세요")

    # 정렬/필터 옵션
    col1, col2 = st.columns([2, 1])
    with col1:
        sort_option = st.selectbox(
            "정렬",
            ["최근 활동순", "질문 많은 순"],
            key="sort_option"
        )
    with col2:
        filter_option = st.selectbox(
            "필터",
            ["전체", "익명만"],
            key="filter_option"
        )

    # 정렬 및 필터 파라미터 변환
    sort_by = "recent" if sort_option == "최근 활동순" else "questions"
    filter_anonymous = (filter_option == "익명만")

    # 공유된 대화 가져오기
    shared_conversations = get_shared_conversations(sort_by=sort_by, filter_anonymous=filter_anonymous)

    if not shared_conversations:
        st.info("🌟 아직 공유된 질문이 없어요. 첫 번째로 공유해보세요!")
        st.markdown("---")
        st.markdown("💡 **공유하려면:**")
        st.markdown("1. '📖 내 대화' 탭으로 이동하세요")
        st.markdown("2. 왼쪽의 '⚙️ 공유 설정'을 펼치세요")
        st.markdown("3. '내 질문을 다른 학생들과 공유하기'를 체크하세요")
        return

    st.markdown(f"**총 {len(shared_conversations)}명의 학생이 질문을 공유했어요!**")
    st.markdown("---")

    # 학생별 카드 표시
    for student_data in shared_conversations:
        student_id = student_data['student_id']
        display_name = student_data['display_name']
        conversations = student_data['conversations']
        question_count = student_data['question_count']

        # 학생 카드
        with st.expander(f"👤 {display_name} ({question_count}개 질문)", expanded=False):
            if question_count == 0:
                st.caption("아직 질문이 없어요")
            else:
                for i, conv in enumerate(conversations, 1):
                    st.markdown(f"**질문 {i}**")
                    with st.chat_message("user"):
                        st.markdown(conv['question'])
                    with st.chat_message("assistant", avatar="✍️"):
                        st.markdown(conv['answer'])

                    if i < len(conversations):
                        st.markdown("---")


def main_page():
    """메인 학습 화면 - 탭 레이아웃"""
    # 헤더
    col_left, col_right = st.columns([3, 1])
    with col_left:
        st.markdown(f'<div class="main-title">📚 AI 작가와의 대화</div>', unsafe_allow_html=True)
    with col_right:
        st.markdown(f"**{st.session_state.student_name}** 학생")
        st.caption(f"학번: {st.session_state.student_id}")

    st.markdown("---")

    # 탭 레이아웃
    tab1, tab2 = st.tabs(["📖 내 대화", "📚 친구들 질문 보기"])

    with tab1:
        show_my_conversation()

    with tab2:
        show_peer_discussions()


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

            # 5. 입력 필드 초기화를 위해 key 변경
            st.session_state.input_key += 1

            # 6. 화면 갱신
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
