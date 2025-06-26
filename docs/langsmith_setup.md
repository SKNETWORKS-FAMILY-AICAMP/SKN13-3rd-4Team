# LangSmith 설정 가이드

LangSmith를 사용하여 챗봇의 API 호출 내역, 성능 지표, 대화 품질을 모니터링할 수 있습니다.

## 1. LangSmith 계정 생성

1. [LangSmith 웹사이트](https://smith.langchain.com) 방문
2. 계정 생성 또는 로그인
3. 새 프로젝트 생성 (예: `ecommerce-chatbot`)

## 2. API 키 발급

1. LangSmith 대시보드에서 **Settings** → **API Keys** 이동
2. **Create API Key** 클릭
3. API 키 복사

## 3. 환경변수 설정

`.env` 파일에 다음 설정 추가:

```bash
# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=ecommerce-chatbot
```

## 4. 통합 챗봇 실행

```bash
# LangSmith 모니터링이 포함된 통합 챗봇 실행
streamlit run app/unified_chatbot.py
```

**참고**: 사이드바에서 "✅ LangSmith 추적 활성화됨" 메시지를 확인하세요.

## 5. 모니터링 가능한 항목

### 📊 **대화 추적**
- 사용자 입력과 AI 응답
- 응답 생성 시간
- 토큰 사용량
- 비용 추적

### 🔍 **성능 지표**
- 평균 응답 시간
- 성공/실패율
- 사용자 만족도
- API 호출 빈도

### 🎯 **품질 분석**
- 응답 품질 평가
- 할루시네이션 감지
- 사용자 피드백 수집
- A/B 테스트

### 📈 **사용 패턴**
- 자주 묻는 질문 분석
- 사용자 행동 패턴
- 시간대별 사용량
- 기능별 사용 통계

## 6. LangSmith 대시보드 활용

### 실시간 모니터링
1. **Traces** 탭에서 실시간 대화 확인
2. 각 대화의 상세 정보 (입력, 출력, 메타데이터)
3. 오류 발생 시 즉시 알림

### 성능 분석
1. **Analytics** 탭에서 성능 지표 확인
2. 응답 시간, 토큰 사용량 그래프
3. 비용 분석 및 예측

### 품질 개선
1. **Evaluations** 탭에서 응답 품질 평가
2. 사용자 피드백 수집
3. 모델 성능 비교

## 7. 고급 기능

### 커스텀 메타데이터
```python
metadata = {
    "user_id": current_user_id,
    "session_id": session_id,
    "intent": "order_inquiry",
    "confidence": 0.95
}
```

### 평가 지표 설정
- 응답 정확도
- 사용자 만족도
- 작업 완료율
- 응답 시간

### 알림 설정
- 오류 발생 시 이메일 알림
- 성능 저하 시 Slack 알림
- 일일/주간 리포트 자동 생성

## 8. 문제 해결

### API 키 오류
```
Error: LangSmith API key not found
```
→ `.env` 파일의 `LANGCHAIN_API_KEY` 확인

### 추적 비활성화
```
Warning: LangSmith tracing is disabled
```
→ `LANGCHAIN_TRACING_V2=true` 설정 확인

### 프로젝트 생성 오류
```
Error: Project not found
```
→ LangSmith 대시보드에서 프로젝트 생성 확인

## 9. 비용 최적화

### 추적 범위 제한
- 개발 환경에서만 활성화
- 중요한 대화만 추적
- 샘플링 비율 조정

### 데이터 보존 기간
- 필요한 기간만 데이터 보존
- 자동 삭제 정책 설정
- 중요 데이터만 장기 보관

## 10. 보안 고려사항

### 민감 정보 제외
- 개인정보 마스킹
- 결제 정보 제외
- 로그 암호화

### 접근 권한 관리
- 팀원별 권한 설정
- API 키 정기 교체
- 감사 로그 유지

이제 LangSmith를 통해 챗봇의 모든 상호작용을 모니터링하고 성능을 개선할 수 있습니다!
