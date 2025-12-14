"""
데이터 관리 모듈
학생 정보 및 대화 이력을 JSON 파일로 관리합니다.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 데이터 디렉토리 경로
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONV_DIR = DATA_DIR / "conversations"
STUDENTS_FILE = DATA_DIR / "students.json"

# 디렉토리가 없으면 생성
CONV_DIR.mkdir(parents=True, exist_ok=True)


def load_students():
    """
    students.json 파일에서 학생 목록을 로드합니다.

    Returns:
        list: 학생 정보 리스트
    """
    try:
        if STUDENTS_FILE.exists():
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('students', [])
        else:
            return []
    except Exception as e:
        print(f"학생 데이터 로드 오류: {e}")
        return []


def save_student(student_id, name):
    """
    새 학생을 students.json에 추가합니다.
    이미 존재하는 학생이면 추가하지 않습니다.

    Args:
        student_id (str): 학번
        name (str): 이름

    Returns:
        bool: 성공 여부
    """
    try:
        students = load_students()

        # 이미 존재하는 학생인지 확인
        for student in students:
            if student['student_id'] == student_id:
                return True  # 이미 존재함

        # 새 학생 추가
        new_student = {
            "student_id": student_id,
            "name": name,
            "created_at": datetime.now().isoformat()
        }
        students.append(new_student)

        # 저장
        with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"students": students}, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f"학생 저장 오류: {e}")
        return False


def get_student(student_id):
    """
    특정 학생 정보를 조회합니다.

    Args:
        student_id (str): 학번

    Returns:
        dict: 학생 정보 (없으면 None)
    """
    students = load_students()
    for student in students:
        if student['student_id'] == student_id:
            return student
    return None


def load_conversation(student_id):
    """
    특정 학생의 대화 이력을 로드합니다.

    Args:
        student_id (str): 학번

    Returns:
        dict: 대화 이력 데이터
    """
    conv_file = CONV_DIR / f"{student_id}.json"
    try:
        if conv_file.exists():
            with open(conv_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 새 대화 이력 생성
            return {
                "student_id": student_id,
                "name": "",
                "conversations": [],
                "statistics": {
                    "total_questions": 0,
                    "average_score": 0.0,
                    "last_activity": None
                }
            }
    except Exception as e:
        print(f"대화 이력 로드 오류: {e}")
        return {
            "student_id": student_id,
            "name": "",
            "conversations": [],
            "statistics": {
                "total_questions": 0,
                "average_score": 0.0,
                "last_activity": None
            }
        }


def save_conversation(student_id, name, conversation_data):
    """
    학생의 대화 이력을 저장합니다.

    Args:
        student_id (str): 학번
        name (str): 이름
        conversation_data (dict): 전체 대화 데이터

    Returns:
        bool: 성공 여부
    """
    conv_file = CONV_DIR / f"{student_id}.json"
    try:
        print(f"[DEBUG] Saving conversation for {student_id}")

        # 이름과 통계 업데이트
        conversation_data['student_id'] = student_id
        conversation_data['name'] = name

        # 통계 계산
        conversations = conversation_data.get('conversations', [])
        print(f"[DEBUG] Total conversations to save: {len(conversations)}")

        if conversations:
            # 안전하게 점수 합계 계산
            total_score = 0
            valid_count = 0
            for conv in conversations:
                score = conv.get('score', {})
                if isinstance(score, dict) and 'total' in score:
                    total_score += score['total']
                    valid_count += 1

            avg_score = total_score / valid_count if valid_count > 0 else 0.0

            conversation_data['statistics'] = {
                "total_questions": len(conversations),
                "average_score": round(avg_score, 2),
                "last_activity": conversations[-1].get('timestamp') if conversations else None
            }
            print(f"[DEBUG] Statistics: questions={len(conversations)}, avg_score={avg_score:.2f}")

        # 저장
        print(f"[DEBUG] Writing to file: {conv_file}")
        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)

        print(f"[DEBUG] Save successful!")
        return True
    except Exception as e:
        import traceback
        print(f"대화 이력 저장 오류: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False


def get_all_students_with_stats():
    """
    모든 학생의 정보와 통계를 함께 가져옵니다 (교사 대시보드용).

    Returns:
        list: 학생 정보 + 통계 리스트
    """
    students = load_students()
    result = []

    for student in students:
        student_id = student['student_id']
        conv_data = load_conversation(student_id)

        result.append({
            "student_id": student_id,
            "name": student['name'],
            "total_questions": conv_data['statistics']['total_questions'],
            "average_score": conv_data['statistics']['average_score'],
            "last_activity": conv_data['statistics']['last_activity']
        })

    return result


def load_guide_questions():
    """
    가이드 질문 목록을 로드합니다.

    Returns:
        list: 가이드 질문 리스트
    """
    guide_file = DATA_DIR / "guide_questions.json"
    try:
        if guide_file.exists():
            with open(guide_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('questions', [])
        else:
            return []
    except Exception as e:
        print(f"가이드 질문 로드 오류: {e}")
        return []
