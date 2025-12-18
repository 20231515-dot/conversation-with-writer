# Streamlit Cloud 배포 가이드

## 🚀 빠른 배포 체크리스트

### 1. GitHub 리포지토리 준비
- [ ] 코드를 GitHub에 푸시
- [ ] `.gitignore`에 `.env` 파일 포함 확인
- [ ] `requirements.txt` 파일 존재 확인

### 2. Streamlit Cloud 설정

#### App 설정
```
Repository: your-username/your-repo-name
Branch: main
Main file path: main.py  ⭐ 중요!
```

#### Secrets 설정 (Settings → Secrets)
```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
TEACHER_PASSWORD = "your-secure-password-here"
```

### 3. 배포 후 확인사항
- [ ] 앱이 정상적으로 로드되는지 확인
- [ ] 역할 선택 화면이 표시되는지 확인
- [ ] 학생 모드 테스트:
  - [ ] 로그인
  - [ ] 이야기 읽기
  - [ ] AI 작가와 대화
  - [ ] 친구들 질문 보기
- [ ] 교사 모드 테스트:
  - [ ] 비밀번호 로그인
  - [ ] 학생 통계 확인
  - [ ] 학생 상세 정보 조회

## 📝 상세 배포 가이드

### Step 1: Streamlit Cloud 계정 생성

1. https://share.streamlit.io/ 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭

### Step 2: 앱 설정

**Repository 선택:**
- Organization/username 선택
- Repository 선택
- Branch: `main` (또는 배포할 브랜치)

**Main file path 설정:**
```
main.py
```

⚠️ **중요**: `app.py`가 아닌 `main.py`를 사용해야 합니다!

### Step 3: Secrets 설정

배포 후 App 설정에서:

1. "Settings" 클릭
2. "Secrets" 섹션으로 이동
3. 다음 내용 입력:

```toml
# Gemini API 키
GEMINI_API_KEY = "AIzaSy..."

# 교사 비밀번호 (기본값: teacher2024)
TEACHER_PASSWORD = "your-secure-password"
```

### Step 4: 환경 변수 사용 (선택사항)

교사 비밀번호를 환경 변수로 관리하려면 `main.py` 수정:

```python
import os

# teacher_login_page() 함수 내에서
teacher_password = os.getenv("TEACHER_PASSWORD", "teacher2024")
if password == teacher_password:
    st.session_state.teacher_authenticated = True
    # ...
```

## ⚠️ 중요 주의사항

### 데이터 지속성

**Streamlit Cloud Community 제한사항:**
- 앱 재시작 시 로컬 파일 시스템 초기화
- `data/` 디렉토리의 JSON 파일이 삭제됨

**해결 방법:**

1. **단기 데모/테스트**: 현재 구조 그대로 사용
2. **프로덕션 환경**: 외부 데이터베이스 사용
   - PostgreSQL (Supabase, Neon, etc.)
   - MongoDB (MongoDB Atlas)
   - Firebase Realtime Database
   - Google Cloud Storage

### 성능 최적화

**리소스 제한:**
- Community 플랜: 1GB RAM, 1 CPU core
- 동시 접속자가 많으면 느려질 수 있음

**최적화 팁:**
- `@st.cache_data` 데코레이터 활용
- 대용량 데이터는 외부 저장소 사용
- 이미지/파일은 CDN 사용 권장

## 🔐 보안 권장사항

### API 키 관리
- ✅ Streamlit Secrets에 저장
- ❌ 코드에 직접 입력 금지
- ❌ `.env` 파일을 Git에 커밋 금지

### 교사 비밀번호
- 기본 비밀번호(`teacher2024`)를 반드시 변경
- 강력한 비밀번호 사용 (최소 12자, 대소문자+숫자+특수문자)
- Secrets에 저장하여 환경 변수로 관리

### 학생 데이터
- 최소한의 개인정보만 수집 (학번, 이름)
- 민감 정보는 수집하지 않음
- GDPR/개인정보보호법 준수

## 📊 모니터링

### 앱 상태 확인

Streamlit Cloud 대시보드에서:
- 앱 실행 상태
- 로그 확인
- 리소스 사용량
- 에러 메시지

### 에러 디버깅

1. Streamlit Cloud 로그 확인
2. 로컬에서 동일한 환경으로 테스트:
   ```bash
   streamlit run main.py
   ```
3. Python 에러 메시지 분석

## 🔄 업데이트 배포

코드 변경 후 배포:

```bash
git add -A
git commit -m "업데이트 내용"
git push origin main
```

Streamlit Cloud가 자동으로 감지하여 재배포합니다.

## 💡 추가 팁

### 커스텀 도메인
- Streamlit Cloud Pro 플랜에서 지원
- 또는 Cloudflare 등으로 프록시 설정

### 비용 절감
- Community 플랜 (무료) 활용
- 필요시 Pro 플랜($20/월) 업그레이드
- 또는 자체 서버에 Docker로 배포

### 백업
- 정기적으로 `data/` 디렉토리 백업
- 또는 외부 DB 사용으로 자동 백업

## 📞 문제 해결

### 자주 발생하는 문제

**1. "ModuleNotFoundError"**
- `requirements.txt`에 모든 패키지 포함 확인
- 로컬과 배포 환경의 패키지 버전 일치 확인

**2. "API Key Error"**
- Secrets에 `GEMINI_API_KEY` 올바르게 설정 확인
- API 키 유효성 확인

**3. "앱이 느려요"**
- 캐싱 활용 (`@st.cache_data`)
- 불필요한 API 호출 최소화
- 리소스 사용량 확인

**4. "데이터가 사라져요"**
- Community 플랜의 제한사항
- 외부 DB 사용 권장

## 🎓 학습 자료

- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [Streamlit Community Cloud 가이드](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Secrets 관리](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

---

**질문이나 문제가 있으면 GitHub Issues로 문의하세요!**
