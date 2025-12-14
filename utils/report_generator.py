"""
학습 리포트 생성 모듈
학생의 활동을 분석하여 학습 리포트를 생성합니다.
"""

from datetime import datetime
from .data_manager import load_conversation
from .gemini_client import get_client
from .prompts import get_report_generation_prompt


def generate_report(student_id):
    """
    학생의 학습 리포트를 생성합니다.

    Args:
        student_id (str): 학번

    Returns:
        str: 마크다운 형식의 리포트
    """
    try:
        # 학생 대화 이력 로드
        conv_data = load_conversation(student_id)

        if not conv_data or not conv_data.get('conversations'):
            return generate_empty_report(student_id, conv_data.get('name', ''))

        # 통계 정보
        student_name = conv_data.get('name', '')
        conversations = conv_data.get('conversations', [])
        stats = conv_data.get('statistics', {})

        total_questions = stats.get('total_questions', len(conversations))
        avg_score = stats.get('average_score', 0.0)

        # 대표 질문 선정 (점수가 높은 상위 3개와 낮은 1개)
        sorted_convs = sorted(conversations, key=lambda x: x.get('score', {}).get('total', 0), reverse=True)

        sample_questions = []
        # 좋은 질문 (상위 3개)
        for i, conv in enumerate(sorted_convs[:3]):
            score = conv.get('score', {}).get('total', 0)
            sample_questions.append(f"{i+1}. [{score:.1f}점] {conv['question']}")

        # 개선이 필요한 질문 (하위 1개)
        if len(sorted_convs) > 3:
            low_conv = sorted_convs[-1]
            low_score = low_conv.get('score', {}).get('total', 0)
            sample_questions.append(f"\n[참고] 개선이 필요한 질문 [{low_score:.1f}점]: {low_conv['question']}")

        sample_questions_str = "\n".join(sample_questions)

        # AI에게 리포트 생성 요청
        client = get_client()
        prompt = get_report_generation_prompt(
            student_id,
            student_name,
            total_questions,
            avg_score,
            sample_questions_str
        )

        ai_report = client.generate_response(prompt)

        # 최종 리포트 조합
        report = f"""# {student_name} 학생 학습 리포트

**학번**: {student_id}
**생성 일자**: {datetime.now().strftime('%Y년 %m월 %d일')}

---

## 활동 요약
- 총 질문 개수: **{total_questions}개**
- 평균 질문 점수: **{avg_score:.1f}/5.0** ({get_score_level(avg_score)})

---

{ai_report}

---

*이 리포트는 AI가 자동으로 생성한 것입니다.*
"""

        return report

    except Exception as e:
        print(f"리포트 생성 오류: {e}")
        return f"# 리포트 생성 오류\n\n리포트를 생성하는 중 오류가 발생했습니다: {str(e)}"


def generate_empty_report(student_id, student_name):
    """
    활동이 없는 학생을 위한 리포트 생성

    Args:
        student_id (str): 학번
        student_name (str): 이름

    Returns:
        str: 리포트
    """
    return f"""# {student_name} 학생 학습 리포트

**학번**: {student_id}
**생성 일자**: {datetime.now().strftime('%Y년 %m월 %d일')}

---

## 활동 요약
아직 활동 기록이 없습니다.

---

## 안내
{student_name} 학생은 아직 작가님께 질문을 하지 않았습니다.

이야기를 읽고 궁금한 점이나 작가님께 묻고 싶은 것을 자유롭게 질문해보세요!

---

*이 리포트는 AI가 자동으로 생성한 것입니다.*
"""


def get_score_level(score):
    """
    점수를 레벨로 변환합니다.

    Args:
        score (float): 점수 (1.0-5.0)

    Returns:
        str: 레벨 설명
    """
    if score >= 4.5:
        return "매우 우수"
    elif score >= 3.5:
        return "우수"
    elif score >= 2.5:
        return "보통"
    elif score >= 1.5:
        return "노력 필요"
    else:
        return "더 노력 필요"


def export_report_as_text(report, student_id):
    """
    리포트를 텍스트 파일로 내보내기 위한 파일명 생성

    Args:
        report (str): 리포트 내용
        student_id (str): 학번

    Returns:
        tuple: (filename, content)
    """
    filename = f"학습리포트_{student_id}_{datetime.now().strftime('%Y%m%d')}.md"
    return filename, report
