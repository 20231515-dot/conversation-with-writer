"""
질문 분석 모듈
AI를 사용하여 학생 질문의 질을 분석합니다.
"""

import json
import re
from .gemini_client import get_client
from .prompts import get_question_analysis_prompt


def analyze_question(question, story_content):
    """
    학생의 질문을 분석하여 점수를 매깁니다.

    Args:
        question (str): 학생의 질문
        story_content (str): 이야기 내용

    Returns:
        dict: 분석 결과
            {
                "total_score": float,
                "depth": int,
                "creativity": int,
                "comprehension": int,
                "thinking": int,
                "feedback": str
            }
    """
    try:
        # Gemini 클라이언트 가져오기
        client = get_client()

        # 프롬프트 생성
        prompt = get_question_analysis_prompt(story_content, question)

        # AI 응답 생성
        response = client.generate_response(prompt)

        # JSON 파싱
        score_data = parse_json_response(response)

        return score_data

    except Exception as e:
        print(f"질문 분석 오류: {e}")
        # 오류 발생시 기본 점수 반환
        return {
            "total_score": 3.0,
            "depth": 3,
            "creativity": 3,
            "comprehension": 3,
            "thinking": 3,
            "feedback": "분석 중 오류가 발생했습니다."
        }


def parse_json_response(response):
    """
    AI 응답에서 JSON을 파싱합니다.

    Args:
        response (str): AI 응답 텍스트

    Returns:
        dict: 파싱된 JSON 데이터
    """
    try:
        print(f"[DEBUG] Parsing response: {response[:200]}...")  # 첫 200자만 출력

        # 여러 패턴으로 JSON 찾기
        json_str = None

        # 패턴 1: ```json ... ``` 형식
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            print("[DEBUG] Found JSON in code block")
        else:
            # 패턴 2: ``` ... ``` 형식 (json 태그 없이)
            json_match = re.search(r'```\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                print("[DEBUG] Found JSON in code block (no tag)")
            else:
                # 패턴 3: 중괄호로 둘러싸인 부분 (가장 큰 것)
                json_match = re.search(r'\{[^}]*"total_score"[^}]*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    print("[DEBUG] Found JSON by braces")
                else:
                    # 전체 응답 사용
                    json_str = response
                    print("[DEBUG] Using entire response")

        # JSON 파싱
        data = json.loads(json_str)
        print(f"[DEBUG] Parsed JSON successfully: {data}")

        # 필수 필드 확인 및 기본값 설정
        result = {
            "total_score": float(data.get("total_score", 3.0)),
            "depth": int(data.get("depth", 3)),
            "creativity": int(data.get("creativity", 3)),
            "comprehension": int(data.get("comprehension", 3)),
            "thinking": int(data.get("thinking", 3)),
            "feedback": data.get("feedback", "좋은 질문입니다!")
        }

        # 점수 범위 검증 (1-5)
        for key in ["depth", "creativity", "comprehension", "thinking"]:
            if result[key] < 1:
                result[key] = 1
            elif result[key] > 5:
                result[key] = 5

        # total_score 범위 검증
        if result["total_score"] < 1.0:
            result["total_score"] = 1.0
        elif result["total_score"] > 5.0:
            result["total_score"] = 5.0

        print(f"[DEBUG] Final score result: {result}")
        return result

    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 파싱 오류: {e}")
        print(f"[ERROR] 응답 내용: {response}")
        # 기본 점수 반환
        return {
            "total_score": 3.0,
            "depth": 3,
            "creativity": 3,
            "comprehension": 3,
            "thinking": 3,
            "feedback": "질문을 분석했습니다."
        }
    except Exception as e:
        import traceback
        print(f"[ERROR] 파싱 오류: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return {
            "total_score": 3.0,
            "depth": 3,
            "creativity": 3,
            "comprehension": 3,
            "thinking": 3,
            "feedback": "분석 중 오류가 발생했습니다."
        }


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
