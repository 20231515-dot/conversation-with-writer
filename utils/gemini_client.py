"""
Gemini API 클라이언트
Google Gemini API를 사용하여 AI 응답을 생성합니다.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# 환경 변수 로드
load_dotenv()

class GeminiClient:
    def __init__(self):
        """Gemini API 클라이언트 초기화"""
        api_key = os.getenv('GEMINI_API_KEY')

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY가 설정되지 않았습니다. "
                ".env 파일을 생성하고 API 키를 설정해주세요."
            )

        # Gemini API 설정
        genai.configure(api_key=api_key)

        # 안전 설정 (초등학생 대상이므로 엄격하게)
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        # 모델 초기화
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings=self.safety_settings
        )

    def generate_response(self, prompt, max_retries=3):
        """
        프롬프트에 대한 AI 응답 생성

        Args:
            prompt (str): 입력 프롬프트
            max_retries (int): 최대 재시도 횟수

        Returns:
            str: AI 생성 응답
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)

                # 응답이 차단되었는지 확인
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                    return "죄송합니다. 이 질문에 대해서는 답변을 드릴 수 없습니다. 다른 질문을 해주세요."

                # 응답 텍스트 반환
                if response.text:
                    return response.text.strip()
                else:
                    return "죄송합니다. 답변을 생성할 수 없습니다. 다시 시도해주세요."

            except Exception as e:
                if attempt < max_retries - 1:
                    # 재시도 전 잠시 대기
                    time.sleep(1)
                    continue
                else:
                    # 최대 재시도 횟수 초과
                    return f"오류가 발생했습니다: {str(e)}\n다시 시도해주세요."

        return "응답을 생성할 수 없습니다. 나중에 다시 시도해주세요."


# 전역 클라이언트 인스턴스
_client = None

def get_client():
    """전역 GeminiClient 인스턴스 반환"""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
