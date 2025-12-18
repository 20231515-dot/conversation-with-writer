# 📚 AI 작가와의 대화

초등학교 6학년 학생들을 위한 AI 기반 독해 및 사고력 향상 플랫폼

## 📖 프로젝트 소개

이 프로젝트는 초등학교 6학년 학생들이 짧은 이야기를 읽고, AI 작가와 대화하며 독해력과 비판적 사고력을 향상시킬 수 있도록 돕는 교육 플랫폼입니다.

### 핵심 기능

- **동일한 이야기**: 모든 학생이 같은 이야기를 읽어 표준화된 학습과 비교 가능
- **AI 작가와의 대화**: Gemini API를 활용한 실시간 질의응답
- **질문의 질 분석**: AI가 학생의 질문을 4가지 기준(깊이, 창의성, 이해도, 사고력)으로 평가
- **학생용 앱**: 이야기 읽기 + AI 작가와 대화
- **교사용 대시보드**: 모든 학생의 진행도와 수준을 한눈에 확인
- **학습 리포트**: 개별 학생의 활동을 분석한 리포트 자동 생성

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **AI**: Google Gemini API
- **Data Storage**: JSON
- **Language**: Python 3.8+

## 📁 프로젝트 구조

```
assignment/
├── main.py                     # 🆕 통합 앱 진입점 (역할 선택)
├── student_app.py              # 🆕 학생용 앱 모듈
├── teacher_app.py              # 🆕 교사용 대시보드 모듈
├── app.py                      # 학생용 앱 (레거시, 로컬 테스트용)
├── teacher_dashboard.py        # 교사용 대시보드 (레거시, 로컬 테스트용)
├── story.txt                   # 고정된 이야기
├── requirements.txt            # Python 패키지 의존성
├── README.md                   # 이 파일
├── PROGRESS.md                 # 프로젝트 진행 상황
├── .env.example               # API 키 예시
├── .gitignore                 # Git 제외 파일
├── utils/                     # 유틸리티 모듈
│   ├── gemini_client.py       # Gemini API 클라이언트
│   ├── question_analyzer.py   # 질문 분석
│   ├── data_manager.py        # 데이터 관리
│   ├── sharing_manager.py     # 🆕 공유 관리
│   ├── report_generator.py    # 리포트 생성
│   └── prompts.py             # AI 프롬프트
└── data/                      # 데이터 파일 (자동 생성)
    ├── students.json          # 학생 정보
    ├── sharing_settings.json  # 🆕 공유 설정
    ├── guide_questions.json   # 가이드 질문
    └── conversations/         # 학생별 대화 이력
```

## 🚀 설치 방법

### 1. Python 설치

Python 3.8 이상이 필요합니다.

```bash
python --version  # Python 버전 확인
```

### 2. 프로젝트 클론

```bash
git clone <repository-url>
cd assignment
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. Gemini API 키 설정

1. [Google AI Studio](https://aistudio.google.com/app/apikey)에서 Gemini API 키를 발급받으세요.

2. 프로젝트 루트 디렉토리에 `.env` 파일을 생성하세요:

```bash
cp .env.example .env
```

3. `.env` 파일을 열어 API 키를 입력하세요:

```
GEMINI_API_KEY=your_api_key_here
```

### 5. 이야기 작성

`story.txt` 파일을 열어 학생들이 읽을 이야기를 작성하세요.
예시 이야기가 이미 포함되어 있으니 참고하세요.

## 💻 사용 방법

### 통합 앱 실행 (권장) ⭐

학생용 앱과 교사용 대시보드가 하나로 통합되었습니다:

```bash
streamlit run main.py
```

브라우저가 열리면:
1. **역할 선택**: 학생 또는 교사 선택
2. **교사 로그인**: 교사 선택 시 비밀번호 입력 (기본: `teacher2024`)
3. **앱 사용**: 선택한 역할에 맞는 화면이 표시됩니다

### 개별 앱 실행 (로컬 테스트용)

개발/테스트 목적으로 개별 앱을 실행할 수도 있습니다:

```bash
# 학생용 앱만 실행
streamlit run app.py --server.port 23082

# 교사용 대시보드만 실행
streamlit run teacher_dashboard.py --server.port 23083
```

### 기능 안내

**학생 기능**:
1. 학번과 이름을 입력하여 시작
2. 이야기 읽기 및 AI 작가와 대화
3. 친구들 질문 공유/조회 (피어 디스커션 보드)
4. 공유 설정 (실명/익명 선택)
5. 대화 요약 복사

**교사 기능**:
1. 전체 학생 통계 확인
2. 학생별 진행도 모니터링
3. 개별 학생 대화 이력 조회
4. 학습 리포트 생성 및 다운로드

## ☁️ Streamlit Cloud 배포

### 1. 배포 준비

Streamlit Cloud Community에 배포하려면 main.py를 진입점으로 사용하세요:

```
Main file path: main.py
```

### 2. Secrets 설정

Streamlit Cloud의 Settings → Secrets에서 다음을 추가하세요:

```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
TEACHER_PASSWORD = "your-teacher-password-here"
```

### 3. 데이터 지속성 주의사항

⚠️ **중요**: Streamlit Cloud Community는 앱 재시작 시 로컬 파일 시스템이 초기화됩니다.

프로덕션 환경에서는 다음 중 하나를 사용하세요:
- **외부 데이터베이스**: PostgreSQL, MongoDB, Firebase 등
- **클라우드 스토리지**: Google Cloud Storage, AWS S3 등
- **Streamlit Cloud 유료 플랜**: 지속적 스토리지 제공

로컬 테스트 및 단기 데모용으로는 현재 JSON 파일 방식도 충분합니다.

## 🔧 포트 설정

사용 가능한 포트: **23082 - 23089**

포트를 변경하려면:
```bash
streamlit run main.py --server.port 23084
```

## 📊 데이터 관리

### 데이터 저장 위치

모든 데이터는 `data/` 디렉토리에 JSON 형식으로 저장됩니다:
- `data/students.json`: 학생 정보
- `data/conversations/{학번}.json`: 개별 학생의 대화 이력

### 백업

정기적으로 `data/` 디렉토리를 백업하는 것을 권장합니다:

```bash
# 백업 생성 (날짜별)
cp -r data data_backup_$(date +%Y%m%d)
```

### 데이터 초기화

새 학기를 시작하려면:
1. 기존 `data/` 디렉토리를 백업
2. `data/` 내용을 삭제하거나 이름 변경
3. 앱이 새로운 `data/` 디렉토리를 자동 생성

## ❓ 문제 해결 (FAQ)

### Q1: API 키 오류가 발생해요

**A:** `.env` 파일이 올바르게 생성되었는지, API 키가 정확한지 확인하세요.

```bash
# .env 파일 확인
cat .env
```

### Q2: 포트가 이미 사용 중이라고 나와요

**A:** 다른 포트 번호를 사용하세요:

```bash
streamlit run app.py --server.port 23085
```

### Q3: 학생 데이터가 사라졌어요

**A:** `data/` 디렉토리가 삭제되었거나 `.gitignore`에 포함되어 있을 수 있습니다.
백업에서 복원하거나, 앱을 다시 실행하여 새로 시작하세요.

### Q4: AI 응답이 너무 느려요

**A:** 네트워크 상태를 확인하거나, Gemini API 할당량을 확인하세요.
무료 요금제는 분당 요청 수에 제한이 있을 수 있습니다.

### Q5: 질문 점수가 이상해요

**A:** AI 평가는 완벽하지 않을 수 있습니다.
교사가 직접 확인하고 학생에게 피드백을 제공하세요.

## 📝 이야기 작성 가이드

`story.txt`에 이야기를 작성할 때:

- **길이**: 6학년이 10-15분 안에 읽을 수 있는 분량
- **난이도**: 초등학교 6학년 수준의 어휘와 문장 구조
- **주제**: 교육적이고 흥미로운 내용
- **구조**: 명확한 시작, 중간, 끝
- **메시지**: 학생들이 생각해볼 만한 주제나 교훈

## 🎯 활용 팁

### 학생들을 위한 팁

1. **이야기를 천천히 읽으세요**: 급하게 읽지 말고 내용을 이해하며 읽으세요.
2. **깊이 있게 질문하세요**: "누구", "무엇"보다는 "왜", "어떻게"를 물어보세요.
3. **가이드 질문을 참고하세요**: 어떻게 질문할지 모르겠다면 예시를 참고하세요.
4. **점수에 너무 집착하지 마세요**: 점수보다 생각하는 과정이 중요합니다.

### 교사들을 위한 팁

1. **정기적으로 모니터링**: 주 1회 정도 대시보드에서 학생들의 진행도를 확인하세요.
2. **개별 피드백**: 점수가 낮은 학생에게는 어떻게 질문할지 가이드를 제공하세요.
3. **우수 사례 공유**: 좋은 질문을 한 학생의 예시를 익명으로 공유하세요.
4. **리포트 활용**: 학기말에 리포트를 생성하여 학생 평가에 활용하세요.

## 🔐 보안 및 개인정보

- **API 키**: `.env` 파일은 절대 공유하지 마세요.
- **학생 데이터**: 학번과 이름만 저장되며, 로컬에만 보관됩니다.
- **백업**: 중요한 데이터는 정기적으로 백업하세요.

## 📄 라이선스

이 프로젝트는 교육 목적으로 자유롭게 사용할 수 있습니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

---

**개발 정보**
- 대상: 초등학교 6학년 학생
- 언어: 한국어
- AI: Google Gemini
- 개발: Streamlit + Python

궁금한 점이 있으시면 문의해주세요!
