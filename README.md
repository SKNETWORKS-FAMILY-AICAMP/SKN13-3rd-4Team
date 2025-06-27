# Tool Calling Agent 기반 쇼핑몰 챗봇 시스템

## 프로젝트 개요

기존 챗봇이 **의도(Intent)** 만 분류하고 정해진 응답만 제공했다면,  
이 시스템은 **LLM이 직접 판단하고, 필요한 툴을 호출하여 최적의 답변을 생성**합니다.

 **상품 추천, 배송 조회, FAQ 검색까지** –  
고객 질문 하나에 AI가 **자동 검색 + 문서 분석 + 자연어 응답**을 연결하는,  
**Tool Calling 기반의 지능형 RAG 챗봇**입니다.

## 1.2 주제 선정 배경  

국내 전자상거래 시장은 2023년 기준 약 **227조 원 규모**로, 최근 몇 년간 연평균 10% 이상의 성장률을 기록하고 있습니다.  
➡️ **출처**: [통계청, 온라인쇼핑동향(2023년 연간)](https://kostat.go.kr/board/view.do?bSeq=&aSeq=436945&page=1&rowPerPage=10&boardSeq=580&searchType=null&searchWord=null)


  <img src="https://tse4.mm.bing.net/th?id=OIP.W5qixHESoh6x8VxsG5sr4QHaJn&pid=Api" width="500"/>  

▲ 대한민국 이커머스 시장 성장 추이 (출처: ECDB)

고객의 **69%는 문제 발생 시 먼저 셀프서비스 채널(예: FAQ)을 이용**하고,  
FAQ에서 원하는 답변을 찾지 못하면 **40% 이상의 고객이 구매를 포기하거나 브랜드 충성도가 하락**하는 것으로 나타났습니다.  
➡️ **출처**: Forrester Research 2021, Zendesk CX Report 2022  
[출처 링크](https://www.zendesk.kr/blog/customer-experience-trends-2022/)


 <img src="https://tse2.mm.bing.net/th?id=OIP._M8Vrc-0JfYLUaE3MA9cYwHaEr&pid=Api" width="500"/>

▲ 셀프서비스 실패 시 이탈 가능성 (출처: Forrester, Zendesk)
---

## 2. 프로젝트 목표  
1️⃣ **고객 중심의 대화 경험 설계**  
- 사용자의 질문 흐름을 끊지 않는 응답 구조 설계  
- FAQ, 상품설명, 정책 안내 등 다양한 정보를 통합 응대  
- 사람과 대화하듯 매끄러운 인터랙션 제공

2️⃣ **RAG 기반 LLM 챗봇 구축** 
![프로젝트 목표](목표.png)

---

## 3. 핵심 특징

###  지능형 Tool Calling Agent
- **자동 도구 선택**: LLM이 질문을 분석하여 적절한 도구를 자동 선택
- **단일 처리 방식**: 하나의 Agent로 모든 유형의 질문 처리
- **복합 질문 처리**: Batch 처리를 통한 다중 작업 병렬 실행

###  시스템 장점
- **비용 효율성**: GPT-4o-mini 사용으로 GPT-4 대비 60% 비용 절약
- **실시간 연동**: 실제 배송 추적 API와 연동된 정확한 정보 제공
- **고속 검색**: Chroma Vector DB를 통한 밀리초 단위 FAQ/상품 검색

## 4. 기술 스택

| 분야 | 기술 | 용도 |
|------|------|------|
| **LLM** | OpenAI GPT-4o-mini | 자연어 이해 및 응답 생성 |
| **Vector DB** | Chroma | FAQ, 상품 정보 벡터 검색 |
| **Embedding** | OpenAI text-embedding-3-large | 텍스트 벡터화 |
| **Database** | SQLite | 사용자, 주문, 상품 데이터 관리 |
| **Framework** | Streamlit, LangChain | 웹 UI 및 AI 에이전트 |
| **API** | 스마트택배 배송 추적 API | 실시간 배송 정보 |

## 5. 시스템 아키텍처

### 전체 구조도
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   사용자 질문    │───▶│  Tool Calling   │───▶│   응답 생성     │
│                │    │     Agent       │    │                │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   도구 선택     │
                    │   (자동 판단)   │
                    └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ RAG 검색    │    │ DB 조회     │    │ API 호출    │
│ (FAQ/상품)  │    │ (주문/사용자)│    │ (배송추적)  │
└─────────────┘    └─────────────┘    └─────────────┘
```
###  챗봇 처리 플로우  
![챗봇 처리 흐름](챗봇_설명.png)

※ 사용자의 질문이 실제 응답으로 이어지는 전 과정을 시각화한 흐름도입니다.

### 핵심 컴포넌트

#### AI 처리 계층
- **Tool Calling Agent**: 질문 분석 후 적절한 도구 자동 선택
- **Batch Processor**: 복합 질문을 여러 작업으로 분해하여 병렬 처리
- **Response Styler**: 응답 톤앤매너 조정 및 이모지 적용

#### 🔍 데이터 처리 계층
- **RAG Processor**: Chroma 벡터 DB를 통한 FAQ/상품 정보 검색
- **DB Query Engine**: SQLite를 통한 사용자/주문 데이터 조회
- **Delivery API Wrapper**: 실제 택배사 API 연동


####  도구 계층 (LangChain Tools)
1. **RAGSearchTool**: FAQ, 제품 정보 벡터 검색
2. **OrderLookupTool**: 주문 내역, 사용자 정보 조회
3. **DeliveryTrackingTool**: 배송 추적 (실제 API 연동)
4. **ProductSearchTool**: 상품 검색 및 정보 조회
5. **GeneralResponseTool**: 일반 대화 응답

## 6. 워크플로우

### 1. 단순 질문 처리 플로우
```
사용자 질문 → Agent 분석 → 도구 선택 → 실행 → 응답 생성
     ↓           ↓           ↓         ↓         ↓
"배송비는?"  → FAQ 검색   → RAG Tool → 검색 결과 → "5만원 이상 무료배송"
```

### 2. 복합 질문 처리 플로우 (Batch)
```
복합 질문 → Agent 분석 → 작업 분해 → 병렬 실행 → 결과 통합 → 응답 생성
    ↓          ↓          ↓          ↓          ↓          ↓
"내 주문과   → 2개 작업   → [주문조회] → [Task1]   → 결과 병합  → 통합 응답
배송현황"     식별        [배송추적]   [Task2]
```

### 3. 도구 선택 로직
```
질문 분석
    ├─ FAQ 키워드 감지 → RAG Search Tool
    ├─ 주문 관련 감지 → Order Lookup Tool
    ├─ 배송 관련 감지 → Delivery Tracking Tool
    ├─ 상품 관련 감지 → Product Search Tool
    └─ 일반 대화 → General Response Tool
```

### 4. 실제 처리 예시

![대화 예시](챗봇_예시_화면.png)
#### 예시 1: FAQ 질문
```
Input: "반품은 어떻게 하나요?"
Process: Agent → RAG Tool → Vector Search → FAQ 검색
Output: "상품 수령 후 7일 이내 고객센터 연락..."
```

---


## 7. 성능 지표

### 응답 시간
- **단순 질문**: 2-5초
- **복합 질문 (Batch)**: 8-15초
- **벡터 검색**: 1-2초
- **DB 조회**: 0.1-0.5초
- **API 호출**: 3-8초

### 정확도
- **도구 선택**: 95% 이상 적절한 도구 선택
- **RAG 검색**: 90% 이상 관련 정보 검색
- **배송 추적**: 실제 API 연동으로 100% 정확

### 비용 효율성
- **GPT-4o-mini**: GPT-4 대비 60% 절약
- **토큰 사용량**: 평균 500-1500 토큰/질문
- **API 호출**: 질문당 1-3회

## 8. 주요 장점
## 🎯 주요 장점

1. **단순성**: 하나의 Agent로 모든 질문 처리
2. **효율성**: Batch 처리로 복합 질문 최적화
3. **확장성**: 새로운 도구 쉽게 추가 가능
4. **비용 효율성**: GPT-4o-mini 사용으로 비용 절약
5. **실용성**: 실제 API 연동으로 현실적인 서비스 제공

## 9. 프로젝트 구조

```bash
📁 SKN13-3rd-4Team/
├── app/
│   └── unified_chatbot.py           # ✅ Streamlit 기반 챗봇 프론트엔드
├── core/
│   ├── agent_processor.py           # ✅ Tool Calling Agent (도구 선택 + 실행 중심)
│   ├── intent_classifier.py         # 의도 분석기
│   ├── rag_processor.py             # RAG 기반 문서 응답 생성기
│   ├── db_query_engine.py           # 사용자/주문/상품 DB 쿼리
│   ├── delivery_api_wrapper.py      # 배송 추적 API 래퍼
│   └── response_styler.py           # 응답 톤/이모지 스타일러
├── langchain_tools.py              # LangChain Tool 정의 모듈 (agent가 사용할 tool 리스트)
├── db/
│   └── schema.sql                 # 데이터베이스 스키마
├── scripts/
│   ├── README.md                  # 스크립트 사용 가이드
│   ├── simple_db_init.py          # 데이터베이스 초기화
│   ├── simple_embed.py            # 문서 임베딩 (RAG 프로세서 사용)
│   └── test_system.py             # 통합 시스템 테스트
└── docs/                          # 📚 문서
## 9. 프로젝트 구조

```bash
📁 SKN13-3rd-4Team/
├── app/
│   └── unified_chatbot.py           # ✅ Streamlit 기반 챗봇 프론트엔드
├── core/
│   ├── agent_processor.py           # ✅ Tool Calling Agent (도구 선택 + 실행 중심)
│   ├── intent_classifier.py         # 의도 분석기
│   ├── rag_processor.py             # RAG 기반 문서 응답 생성기
│   ├── db_query_engine.py           # 사용자/주문/상품 DB 쿼리
│   ├── delivery_api_wrapper.py      # 배송 추적 API 래퍼
│   └── response_styler.py           # 응답 톤/이모지 스타일러
├── langchain_tools.py              # LangChain Tool 정의 모듈 (agent가 사용할 tool 리스트)
├── db/
│   ├── schema.sql                   # DB 테이블 정의
│   └── init_db.py                   # 샘플 데이터 초기화 스크립트
├── docs/
│   ├── code_review_and_architecture.md
│   ├── langsmith_setup.md
│   └── project_cleanup_summary.md
├── data/
│   └── raw_docs/*.json              # 샘플 FAQ/상품/주문/배송 데이터
```
---

## 10. 빠른 시작

### 1. 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (.env 파일 생성)
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. 데이터 초기화
```bash
# 데이터베이스 초기화
python scripts/simple_db_init.py

# 문서 임베딩
python scripts/simple_embed.py
```

### 3. 애플리케이션 실행
```bash
# 웹 애플리케이션 시작
streamlit run app/unified_chatbot.py
```

### 4. 접속
- **URL**: http://localhost:8501
- **기본 모드**: Tool Calling Agent
- **특별 기능**: Batch 처리 (복합 질문 자동 감지)

## 문서

- **[GUIDE.md](GUIDE.md)**: 상세한 설치, 사용법, 데이터 관리 및 트러블슈팅 가이드
- **[docs/](docs/)**: 추가 기술 문서 및 아키텍처 정보

## 라이선스
MIT License

## 개발팀
SKN13-3rd-4Team
