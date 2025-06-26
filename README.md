# 쇼핑몰 고객응대 챗봇 (RAG 기반)

## 프로젝트 개요
RAG(Retrieval-Augmented Generation) 기반의 쇼핑몰 고객 응대 챗봇 시스템입니다.

### 주요 기능
- **FAQ 응답 자동화**: 반품, 교환, 배송비 등 자주 묻는 질문에 벡터 검색 기반 응답
- **상품 제원 정보 응답**: 제품 설명서에서 관련 정보 추출
- **배송 현황 응답**: 주문정보 확인 및 택배 API 연동
- **Intent 분류**: 질문 유형 분석 후 적절한 처리 방식 선택
- **대화 컨텍스트 유지**: 자연스러운 대화 지속

### 기술 스택
- **LLM**: OpenAI GPT-4
- **Vector DB**: Chroma
- **Embedding**: OpenAI text-embedding-3-large
- **Database**: SQLite
- **Framework**: Streamlit (시연용)
- **Language**: Python

## 프로젝트 구조
```
rag_chatbot_project/
├── app/
│   └── unified_chatbot.py         # 🎯 통합 메인 애플리케이션
├── core/
│   ├── intent_classifier.py       # 의도 분류기
│   ├── rag_processor.py           # RAG 처리기
│   ├── db_query_engine.py         # DB 쿼리 엔진
│   ├── delivery_api_wrapper.py    # 배송 API 래퍼
│   └── response_styler.py         # 응답 스타일러
├── data/
│   ├── raw_docs/                  # 원본 문서 (JSON)
│   ├── sample_db/                 # SQLite DB
│   └── vectordb_chroma/           # Chroma Vector DB
├── db/
│   ├── schema.sql                 # DB 스키마
│   └── init_db.py                 # DB 초기화
├── docs/                          # 📚 문서
│   ├── code_review_and_architecture.md
│   └── langsmith_setup.md
├── notebooks/                     # Jupyter 노트북
├── scripts/                       # 유틸리티 스크립트
└── tests/                         # 테스트 코드
```

## 설치 및 실행

### 1. 가상환경 활성화
```bash
conda activate 3rd
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env` 파일에 OpenAI API 키 설정:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 데이터베이스 초기화
```bash
python db/init_db.py
```

### 5. 문서 임베딩
```bash
python scripts/embed_documents.py
```

### 6. 시스템 테스트
```bash
python scripts/test_chatbot.py
```

### 7. 통합 챗봇 실행
```bash
streamlit run app/unified_chatbot.py
```

### 8. Jupyter 노트북 실행 (선택사항)
```bash
jupyter notebook notebooks/01_RAG_System_Demo.ipynb
```

## 🎯 통합 챗봇 주요 기능

### 🔄 **처리 모드 선택**
- **간단 모드**: OpenAI 직접 호출 (빠른 응답)
- **고급 모드**: Intent Classifier + Vector DB (정확한 응답)

### 👤 **개인화 서비스**
- 사용자별 로그인 시뮬레이션
- 개인 주문 내역 자동 연동
- 맞춤형 응답 생성

### 📊 **모니터링 기능**
- 실시간 응답 시간 측정
- 처리 방식 추적
- LangSmith 통합 지원 (선택적)

## 사용 예시
- "반품은 어떻게 하나요?" → FAQ 검색 후 응답
- "무선 이어폰 사양이 어떻게 되나요?" → 제품 설명서 검색
- "주문번호 ORD20241201001 상태 확인해주세요" → DB 조회
- "운송장번호 123456789012 배송 현황 알려주세요" → 배송 API 연동

## 주요 파일 설명

### 핵심 모듈
- `core/intent_classifier.py`: 사용자 의도 분류
- `core/rag_processor.py`: RAG 기반 문서 검색 및 응답 생성
- `core/db_query_engine.py`: 데이터베이스 쿼리 처리
- `core/delivery_api_wrapper.py`: 배송 추적 API 연동
- `core/response_styler.py`: 응답 스타일링

### 데이터
- `data/raw_docs/faq_data.json`: FAQ 데이터
- `data/raw_docs/product_info.json`: 상품 정보
- `data/raw_docs/sample_users.json`: 샘플 사용자 데이터
- `data/raw_docs/sample_orders.json`: 샘플 주문 데이터

### 유틸리티
- `scripts/embed_documents.py`: 문서 임베딩 스크립트
- `scripts/test_chatbot.py`: 시스템 테스트 스크립트
- `db/init_db.py`: 데이터베이스 초기화

## 시스템 아키텍처

```
[사용자 입력]
   ↓
[IntentClassifier] → 질문 분류
   ↓
[DataRouter]
   ├── [RAGProcessor] (FAQ, 제품 설명)
   ├── [DBQueryEngine] (주문/사용자 정보)
   └── [DeliveryAPIWrapper] (배송 추적)
   ↓
[ResponseStyler] → 응답 스타일링
   ↓
[최종 응답]
```

## 트러블슈팅

### 일반적인 문제
1. **OpenAI API 키 오류**: `.env` 파일에 올바른 API 키가 설정되어 있는지 확인
2. **데이터베이스 오류**: `python db/init_db.py` 실행하여 데이터베이스 초기화
3. **벡터 DB 오류**: `python scripts/embed_documents.py` 실행하여 문서 재임베딩
4. **모듈 임포트 오류**: 프로젝트 루트에서 실행하고 있는지 확인

### 성능 최적화
- 벡터 검색 결과 수 조정: `search_kwargs={"k": 3}`
- LLM 모델 변경: `model="gpt-3.5-turbo"` (비용 절약)
- 캐싱 활용: 자주 묻는 질문에 대한 응답 캐싱

## 향후 개선 사항
- [ ] 실제 택배사 API 연동
- [ ] 사용자 인증 시스템
- [ ] 대화 컨텍스트 유지 개선
- [ ] 다국어 지원
- [ ] 음성 인터페이스 추가
- [ ] 성능 모니터링 대시보드

## 라이선스
MIT License

## 개발팀
SKN13-3rd-4Team

