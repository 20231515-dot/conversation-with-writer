"""
공유 관리 모듈
학생들의 질문 공유 설정 및 공유된 대화 조회를 관리합니다.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 데이터 디렉토리 경로
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SHARING_SETTINGS_FILE = DATA_DIR / "sharing_settings.json"
CONV_DIR = DATA_DIR / "conversations"


def initialize_sharing_settings():
    """
    sharing_settings.json 파일이 없으면 생성합니다.
    """
    if not SHARING_SETTINGS_FILE.exists():
        default_data = {"sharing_settings": []}
        try:
            with open(SHARING_SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            print("[DEBUG] sharing_settings.json 파일 생성됨")
        except Exception as e:
            print(f"공유 설정 파일 생성 오류: {e}")


def load_sharing_settings() -> List[Dict]:
    """
    모든 학생의 공유 설정을 로드합니다.

    Returns:
        list: 공유 설정 리스트
    """
    initialize_sharing_settings()

    try:
        with open(SHARING_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('sharing_settings', [])
    except Exception as e:
        print(f"공유 설정 로드 오류: {e}")
        return []


def get_sharing_status(student_id: str) -> Dict:
    """
    특정 학생의 공유 설정을 조회합니다.

    Args:
        student_id (str): 학번

    Returns:
        dict: 공유 설정 정보 (없으면 기본값)
    """
    settings = load_sharing_settings()

    for setting in settings:
        if setting['student_id'] == student_id:
            return setting

    # 기본값 반환
    return {
        'student_id': student_id,
        'is_shared': False,
        'display_as': 'named'
    }


def save_sharing_preference(student_id: str, name: str, is_shared: bool, display_as: str = "named") -> bool:
    """
    학생의 공유 설정을 저장합니다.

    Args:
        student_id (str): 학번
        name (str): 이름
        is_shared (bool): 공유 여부
        display_as (str): 표시 방식 ('named' 또는 'anonymous')

    Returns:
        bool: 성공 여부
    """
    try:
        settings = load_sharing_settings()

        # 기존 설정 찾기
        existing_index = None
        for i, setting in enumerate(settings):
            if setting['student_id'] == student_id:
                existing_index = i
                break

        # 새 설정 데이터
        new_setting = {
            'student_id': student_id,
            'name': name,
            'is_shared': is_shared,
            'display_as': display_as,
            'anonymous_id': None,  # 나중에 동적으로 할당
            'last_toggled': datetime.now().isoformat()
        }

        # 기존 설정이 있으면 업데이트, 없으면 추가
        if existing_index is not None:
            # created_at 유지
            if 'created_at' in settings[existing_index]:
                new_setting['created_at'] = settings[existing_index]['created_at']
            else:
                new_setting['created_at'] = datetime.now().isoformat()
            settings[existing_index] = new_setting
        else:
            new_setting['created_at'] = datetime.now().isoformat()
            settings.append(new_setting)

        # 저장
        with open(SHARING_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'sharing_settings': settings}, f, ensure_ascii=False, indent=2)

        print(f"[DEBUG] 공유 설정 저장 완료: {student_id}, is_shared={is_shared}")
        return True

    except Exception as e:
        print(f"공유 설정 저장 오류: {e}")
        return False


def remove_scores_from_conversation(conversation: Dict) -> Dict:
    """
    대화 데이터에서 모든 점수 정보를 제거합니다.

    Args:
        conversation (dict): 원본 대화 데이터

    Returns:
        dict: 점수가 제거된 대화 데이터
    """
    cleaned_conv = conversation.copy()

    # score 필드 완전히 제거
    if 'score' in cleaned_conv:
        del cleaned_conv['score']

    return cleaned_conv


def get_student_conversation_count(student_id: str) -> int:
    """
    특정 학생의 대화(질문) 개수를 반환합니다.

    Args:
        student_id (str): 학번

    Returns:
        int: 대화 개수
    """
    conv_file = CONV_DIR / f"{student_id}.json"

    if not conv_file.exists():
        return 0

    try:
        with open(conv_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            conversations = data.get('conversations', [])
            return len(conversations)
    except Exception as e:
        print(f"대화 개수 조회 오류: {e}")
        return 0


def get_shared_conversations(sort_by: str = "recent", filter_anonymous: bool = False) -> List[Dict]:
    """
    공유된 모든 대화를 조회합니다. 점수 정보는 제거됩니다.

    Args:
        sort_by (str): 정렬 방식 ('recent' 또는 'questions')
        filter_anonymous (bool): True이면 익명만 표시

    Returns:
        list: 공유된 학생들의 대화 데이터
    """
    settings = load_sharing_settings()

    # 공유 활성화된 학생만 필터링
    shared_students = [s for s in settings if s.get('is_shared', False)]

    # 익명 필터 적용
    if filter_anonymous:
        shared_students = [s for s in shared_students if s.get('display_as') == 'anonymous']

    # 익명 ID 할당 (동적)
    anonymous_counter = 1
    for student in shared_students:
        if student.get('display_as') == 'anonymous':
            student['anonymous_id'] = anonymous_counter
            anonymous_counter += 1

    # 각 학생의 대화 로드
    result = []
    for student in shared_students:
        student_id = student['student_id']
        conv_file = CONV_DIR / f"{student_id}.json"

        if not conv_file.exists():
            continue

        try:
            with open(conv_file, 'r', encoding='utf-8') as f:
                conv_data = json.load(f)
                conversations = conv_data.get('conversations', [])

                # 점수 제거
                cleaned_conversations = [
                    remove_scores_from_conversation(conv)
                    for conv in conversations
                ]

                # 표시 이름 결정
                if student.get('display_as') == 'anonymous':
                    display_name = f"익명 학생 #{student.get('anonymous_id', '?')}"
                else:
                    display_name = student.get('name', '학생')

                # 마지막 활동 시간
                last_activity = None
                if conversations:
                    last_activity = conversations[-1].get('timestamp', '')

                result.append({
                    'student_id': student_id,
                    'display_name': display_name,
                    'conversations': cleaned_conversations,
                    'question_count': len(conversations),
                    'last_activity': last_activity
                })

        except Exception as e:
            print(f"대화 로드 오류 ({student_id}): {e}")
            continue

    # 정렬
    if sort_by == "recent":
        result.sort(key=lambda x: x.get('last_activity', ''), reverse=True)
    elif sort_by == "questions":
        result.sort(key=lambda x: x.get('question_count', 0), reverse=True)

    return result
