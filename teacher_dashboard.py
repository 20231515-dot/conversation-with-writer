"""
AI 작가와의 대화 - 교사용 대시보드
교사가 모든 학생의 활동을 모니터링할 수 있습니다.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# 유틸리티 임포트
from utils.data_manager import get_all_students_with_stats, load_conversation
from utils.report_generator import generate_report
from utils.question_analyzer import get_score_level

# 페이지 설정
st.set_page_config(
    page_title="교사용 대시보드",
    page_icon="👨‍🏫",
    layout="wide"
)

# CSS 스타일
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .metric-label {
        font-size: 1rem;
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)


def show_overview():
    """전체 통계 표시"""
    st.markdown('<div class="main-title">👨‍🏫 교사용 대시보드</div>', unsafe_allow_html=True)
    st.markdown("모든 학생의 학습 활동을 모니터링할 수 있습니다.")
    st.markdown("---")

    # 전체 통계 데이터 로드
    students_data = get_all_students_with_stats()

    if not students_data:
        st.warning("아직 활동한 학생이 없습니다.")
        return

    # 전체 통계 계산
    total_students = len(students_data)
    total_questions = sum(s['total_questions'] for s in students_data)
    avg_questions_per_student = total_questions / total_students if total_students > 0 else 0
    overall_avg_score = sum(s['average_score'] for s in students_data if s['average_score'] > 0) / len([s for s in students_data if s['average_score'] > 0]) if any(s['average_score'] > 0 for s in students_data) else 0

    # 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">총 학생 수</div>
        </div>
        """.format(total_students), unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">총 질문 수</div>
        </div>
        """.format(total_questions), unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{:.1f}</div>
            <div class="metric-label">학생당 평균 질문 수</div>
        </div>
        """.format(avg_questions_per_student), unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{:.1f}/5.0</div>
            <div class="metric-label">전체 평균 점수</div>
        </div>
        """.format(overall_avg_score), unsafe_allow_html=True)


def show_students_table():
    """학생 목록 테이블 표시"""
    st.markdown("---")
    st.markdown("### 📊 학생 목록")

    students_data = get_all_students_with_stats()

    if not students_data:
        return

    # 데이터프레임 생성
    df_data = []
    for student in students_data:
        last_activity = student['last_activity']
        if last_activity:
            try:
                last_activity_dt = datetime.fromisoformat(last_activity)
                last_activity_str = last_activity_dt.strftime('%Y-%m-%d %H:%M')
            except:
                last_activity_str = "없음"
        else:
            last_activity_str = "없음"

        df_data.append({
            "학번": student['student_id'],
            "이름": student['name'],
            "질문 수": student['total_questions'],
            "평균 점수": f"{student['average_score']:.1f}",
            "수준": get_score_level(student['average_score']),
            "마지막 활동": last_activity_str
        })

    df = pd.DataFrame(df_data)

    # 테이블 표시
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # 정렬 옵션
    col1, col2 = st.columns([1, 3])
    with col1:
        sort_by = st.selectbox(
            "정렬 기준",
            ["평균 점수 (높은 순)", "평균 점수 (낮은 순)", "질문 수 (많은 순)", "질문 수 (적은 순)"]
        )

    # 정렬된 학생 목록
    if "높은 순" in sort_by or "많은 순" in sort_by:
        ascending = False
    else:
        ascending = True

    if "평균 점수" in sort_by:
        students_data_sorted = sorted(students_data, key=lambda x: x['average_score'], reverse=not ascending)
    else:
        students_data_sorted = sorted(students_data, key=lambda x: x['total_questions'], reverse=not ascending)

    return students_data_sorted


def show_student_detail(student_id):
    """학생 상세 정보 표시"""
    conv_data = load_conversation(student_id)

    if not conv_data:
        st.error("학생 정보를 찾을 수 없습니다.")
        return

    st.markdown(f"### 📝 {conv_data['name']} 학생 상세 정보")
    st.markdown(f"**학번**: {student_id}")

    stats = conv_data.get('statistics', {})
    total_q = stats.get('total_questions', 0)
    avg_score = stats.get('average_score', 0.0)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("총 질문 수", f"{total_q}개")
    with col2:
        st.metric("평균 점수", f"{avg_score:.1f}/5.0 ({get_score_level(avg_score)})")

    st.markdown("---")

    # 대화 이력
    st.markdown("#### 💬 대화 이력")

    conversations = conv_data.get('conversations', [])

    if not conversations:
        st.info("아직 대화 기록이 없습니다.")
    else:
        for i, conv in enumerate(conversations, 1):
            with st.expander(f"질문 {i}: {conv['question'][:50]}..."):
                st.markdown(f"**질문**: {conv['question']}")
                st.markdown(f"**답변**: {conv['answer']}")

                score = conv.get('score', {})
                st.markdown(f"**점수**: {score.get('total', 0):.1f}/5.0")
                st.markdown(f"- 깊이: {score.get('depth', 0)}/5")
                st.markdown(f"- 창의성: {score.get('creativity', 0)}/5")
                st.markdown(f"- 이해도: {score.get('comprehension', 0)}/5")
                st.markdown(f"- 사고력: {score.get('thinking', 0)}/5")
                st.markdown(f"**평가**: {score.get('feedback', '')}")

                timestamp = conv.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        st.caption(f"작성 시각: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    except:
                        pass

    # 리포트 생성
    st.markdown("---")
    if total_q > 0:
        if st.button(f"📄 {conv_data['name']} 학생 리포트 생성", use_container_width=True):
            with st.spinner("리포트 생성 중..."):
                report = generate_report(student_id)
                st.download_button(
                    label="📥 리포트 다운로드",
                    data=report,
                    file_name=f"학습리포트_{student_id}_{conv_data['name']}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                st.success("리포트가 생성되었습니다!")


def main():
    """메인 함수"""
    # 세션 상태 초기화
    if 'selected_student' not in st.session_state:
        st.session_state.selected_student = None

    # 전체 통계 표시
    show_overview()

    # 학생 목록 표시
    students_sorted = show_students_table()

    if students_sorted:
        st.markdown("---")
        st.markdown("### 🔍 학생 상세 보기")

        # 학생 선택
        student_options = [f"{s['student_id']} - {s['name']}" for s in students_sorted]
        selected = st.selectbox(
            "학생 선택",
            ["선택하세요..."] + student_options
        )

        if selected != "선택하세요...":
            student_id = selected.split(" - ")[0]
            st.session_state.selected_student = student_id

        # 선택된 학생 상세 정보 표시
        if st.session_state.selected_student:
            show_student_detail(st.session_state.selected_student)


if __name__ == "__main__":
    main()
