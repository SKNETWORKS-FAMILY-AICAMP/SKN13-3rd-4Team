# 코드 리뷰 및 아키텍처 분석

## 📊 시스템 아키텍처 개요

### 🏗️ 전체 워크플로우

```
[사용자 입력] 
    ↓
[통합 챗봇 시스템]
    ↓
[처리 모드 선택]
    ├── 간단 모드: OpenAI 직접 호출
    └── 고급 모드: Intent Classifier → Tool Routing
    ↓
[응답 생성 및 반환]
```

## 🔍 핵심 모듈 분석

### 1. Vector DB 전처리 과정

#### 📁 **파일 위치:** `core/rag_processor.py`

#### 🔧 **전처리 워크플로우:**

```python
# 1. 문서 로드 및 변환
def _process_faq_documents(self) -> List[Document]:
    # FAQ JSON → LangChain Document 객체 변환
    for faq in faq_data:
        content = f"질문: {faq['question']}\n답변: {faq['answer']}"
        doc = Document(
            page_content=content,
            metadata={
                "source": "faq",
                "category": faq['category'],
                "faq_id": faq['id'],
                "keywords": faq['keywords']
            }
        )

# 2. 텍스트 분할
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
)

# 3. 임베딩 및 저장
def _embed_documents(self):
    split_docs = self.text_splitter.split_documents(documents)
    self.vector_store.add_documents(split_docs)
```

#### 🗂️ **데이터 소스:**
- `data/raw_docs/faq_data.json` → FAQ 문서
- `data/raw_docs/product_info.json` → 상품 정보 문서

#### 🔍 **검색 과정:**
```python
def search_documents(self, query: str, k: int = 3) -> List[Document]:
    results = self.retriever.invoke(query)  # 유사도 검색
    return results[:k]
```

### 2. Intent Classifier 처리 과정

#### 📁 **파일 위치:** `core/intent_classifier.py`

#### 🧠 **분류 워크플로우:**

```python
def classify(self, text: str, use_llm: bool = True) -> IntentResult:
    # 1. 엔티티 추출 (정규식 기반)
    entities = self.extract_entities(text)
    
    # 2. 키워드 기반 분류
    keyword_intent, keyword_confidence = self.classify_by_keywords(text)
    
    # 3. LLM 기반 분류 (신뢰도 낮을 때)
    if use_llm and keyword_confidence < 0.7:
        llm_intent, llm_confidence, keywords = self.classify_by_llm(text)
        
    # 4. 최종 의도 결정
    return IntentResult(intent, confidence, entities, keywords)
```

#### 🎯 **의도 유형:**
- `FAQ`: 자주 묻는 질문
- `PRODUCT_INFO`: 상품 정보 문의
- `ORDER_STATUS`: 주문 상태 조회
- `DELIVERY_TRACK`: 배송 추적
- `USER_INFO`: 사용자 정보 관련
- `GENERAL`: 일반적인 질문
- `UNKNOWN`: 분류 불가

#### 🔗 **처리 전략 매핑:**
```python
def get_processing_strategy(self, intent_result: IntentResult) -> str:
    strategies = {
        IntentType.FAQ: "rag_processor",
        IntentType.PRODUCT_INFO: "rag_processor",
        IntentType.ORDER_STATUS: "db_query",
        IntentType.DELIVERY_TRACK: "delivery_api",
        IntentType.USER_INFO: "db_query",
        IntentType.GENERAL: "general_response",
        IntentType.UNKNOWN: "fallback"
    }
```

### 3. Tool Binding 및 Agent 아키텍처

#### 🔧 **Tool 구성:**

1. **RAG Processor** (`core/rag_processor.py`)
   - Chroma Vector DB 검색
   - OpenAI GPT-4 응답 생성
   - FAQ 및 상품 정보 처리

2. **DB Query Engine** (`core/db_query_engine.py`)
   - SQLite 데이터베이스 쿼리
   - 사용자/주문 정보 조회
   - 데이터 포맷팅

3. **Delivery API Wrapper** (`core/delivery_api_wrapper.py`)
   - 스마트택배 API 연동
   - 배송 추적 정보 제공
   - Mock 데이터 지원

4. **Response Styler** (`core/response_styler.py`)
   - 응답 톤앤매너 조정
   - 이모지 및 포맷팅
   - 상황별 스타일링

#### 🤖 **Agent 아키텍처:**

```python
class UnifiedChatbotSystem:
    def __init__(self):
        # 지연 로딩으로 메모리 효율성 확보
        self._intent_classifier = None
        self._rag_processor = None
        self._db_engine = None
        self._delivery_api = None
        self._response_styler = None
    
    @property
    def rag_processor(self):
        # 필요할 때만 초기화
        if self._rag_processor is None:
            self._rag_processor = RAGProcessor()
            self._rag_processor.initialize_vector_store()
        return self._rag_processor
```

#### 🔄 **Tool 라우팅 로직:**

```python
def process_query(self, user_input: str, use_advanced_rag: bool = False):
    # 1. 주문 내역 요청 우선 처리
    if is_order_inquiry:
        return self.format_user_orders(user_orders)
    
    # 2. 처리 모드에 따른 분기
    if use_advanced_rag:
        # Intent Classifier → Tool 선택
        intent_result = self.intent_classifier.classify(user_input)
        strategy = self.intent_classifier.get_processing_strategy(intent_result)
        
        if strategy == "rag_processor":
            return self.rag_processor.process_query(user_input)
    else:
        # 직접 OpenAI 호출 (빠른 응답)
        return self._simple_openai_response(user_input, current_user_id)
```

## 🧹 리팩토링 결과

### ✅ **개선 사항:**

1. **코드 중복 제거**
   - 3개의 앱 파일 → 1개 통합 시스템
   - 공통 로직 추상화

2. **성능 최적화**
   - 지연 로딩으로 초기화 시간 단축
   - 간단/고급 모드 선택 가능

3. **사용자 경험 개선**
   - 개인화된 응답 제공
   - 실시간 성능 지표 표시

4. **모니터링 강화**
   - LangSmith 통합 지원
   - 응답 시간 및 처리 방식 추적

### 🎯 **핵심 특징:**

1. **모듈러 설계**: 각 기능이 독립적으로 동작
2. **확장 가능성**: 새로운 Tool 쉽게 추가 가능
3. **성능 최적화**: 필요에 따른 선택적 기능 사용
4. **사용자 중심**: 개인화 및 컨텍스트 인식

## 🚀 사용 방법

### 통합 챗봇 실행:
```bash
streamlit run app/unified_chatbot.py
```

### 기능 선택:
- **간단 모드**: 빠른 OpenAI 직접 응답
- **고급 모드**: Intent Classifier + Vector DB 검색

### 개인화 서비스:
- 사이드바에서 사용자 선택
- 자동 주문 내역 연동
- 맞춤형 응답 제공

이제 하나의 통합된 시스템으로 모든 기능을 효율적으로 사용할 수 있습니다!
