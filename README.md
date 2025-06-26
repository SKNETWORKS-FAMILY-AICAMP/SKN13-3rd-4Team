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
chatbot/
├── app/
│   └── unified_chatbot.py         # 🎯 메인 Streamlit 애플리케이션
├── core/
│   ├── agent_processor.py         # 🚀 Tool Calling Agent (메인 처리기)
│   ├── langchain_tools.py         # LangChain Tool 래퍼들
│   ├── rag_processor.py           # RAG 검색 처리기
│   ├── db_query_engine.py         # 데이터베이스 쿼리 엔진
│   ├── delivery_api_wrapper.py    # 배송 추적 API 래퍼
│   └── response_styler.py         # 응답 스타일링
├── data/
│   ├── raw_docs/                  # 원본 문서 (JSON)
│   ├── sample_db/                 # SQLite 데이터베이스
│   └── vectordb_chroma/           # Chroma 벡터 데이터베이스
├── db/
│   └── schema.sql                 # 데이터베이스 스키마
├── scripts/
│   ├── simple_db_init.py          # 간단한 DB 초기화
│   └── simple_embed.py            # 문서 임베딩
└── docs/                          # 📚 문서
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
`.env` 파일에 필요한 API 키들 설정:
```
OPENAI_API_KEY=your_openai_api_key_here
DELIVERY_API_KEY=your_sweettracker_api_key_here
DELIVERY_API_BASE_URL=https://info.sweettracker.co.kr
```

**배송 API 설정 (선택사항)**:
- 스마트택배 API 키가 있으면 실제 배송 추적 가능
- API 키가 없으면 목 데이터로 자동 폴백

### 4. 데이터베이스 초기화
```bash
python scripts/simple_db_init.py
```

### 5. 문서 임베딩
```bash
python scripts/simple_embed.py
```

### 6. 통합 챗봇 실행
```bash
streamlit run app/unified_chatbot.py
```

### 7. Jupyter 노트북 실행 (선택사항)
```bash
jupyter notebook notebooks/01_RAG_System_Demo.ipynb
```

## 🎯 통합 챗봇 주요 기능

### 🔄 **처리 모드 선택**
- **🚀 Tool Calling Agent 모드**: LLM이 자동으로 도구 선택 (기본, 권장)
- **🧠 Intent Classifier 모드**: 의도 분류 + 전용 도구 사용 (빠름, 정확)

### 👤 **개인화 서비스**
- 사용자별 로그인 시뮬레이션
- 개인 주문 내역 자동 연동
- 맞춤형 응답 생성

### 🚚 **실시간 배송 추적**
- 스마트택배 API 연동으로 실제 배송 상태 조회
- 운송장번호 또는 주문번호로 배송 추적
- API 실패 시 목 데이터로 자동 폴백
- 상세한 배송 이력 및 현재 위치 제공

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
- `core/agent_processor.py`: Tool Calling Agent 메인 처리기 (Batch 처리 포함)
- `core/langchain_tools.py`: LangChain Tool 래퍼들 (RAG, 주문조회, 배송추적 등)
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
- `scripts/simple_embed.py`: 문서 임베딩 스크립트
- `scripts/simple_db_init.py`: 데이터베이스 초기화

## 시스템 아키텍처

### 🚀 Tool Calling Agent (단일 처리 방식)
```
[사용자 입력]
   ↓
[복합 질문 분석] → Batch 처리 여부 결정
   ↓
[GPT-4o-mini 분석] → 자동 도구 선택
   ↓
[Tool Execution]
   ├── [RAGSearchTool] (FAQ, 제품 정보)
   ├── [OrderLookupTool] (주문/사용자 정보 조회)
   ├── [DeliveryTrackingTool] (배송 추적)
   ├── [ProductSearchTool] (상품 검색)
   └── [GeneralResponseTool] (일반 응답)
   ↓
[결과 종합] → 자연스러운 응답 생성
   ↓
[최종 응답]
```

### 📦 Batch 처리 워크플로우 (복합 질문)
```
[복합 질문] → "내 이름 뭐고 내 옷 어디왔는지 알려줘"
   ↓
[질문 분석] → 개별 작업으로 분해
   ├── 사용자 정보 조회
   └── 배송 추적
   ↓
[병렬 실행] → 여러 도구 동시 실행
   ↓
[결과 통합] → 하나의 자연스러운 응답으로 종합
   ↓
[최종 응답]
```

## 📚 문서

- **[GUIDE.md](GUIDE.md)**: 상세한 설치, 사용법, 데이터 관리 및 트러블슈팅 가이드
- **[docs/](docs/)**: 추가 기술 문서 및 아키텍처 정보

## 라이선스
MIT License

## 개발팀
SKN13-3rd-4Team
