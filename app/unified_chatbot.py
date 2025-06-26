"""
통합 RAG 기반 쇼핑몰 챗봇 시스템
- OpenAI GPT-4 기반 자연어 처리
- Chroma Vector DB를 통한 RAG 구현
- 사용자별 개인화 서비스
- LangSmith 모니터링 지원
"""
import streamlit as st
import json
import os
import time
import uuid
from pathlib import Path
import sys
from typing import Dict, Any, Optional

# 프로젝트 루트 설정
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 환경변수 로드 (가장 먼저 실행)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    st.warning("python-dotenv가 설치되지 않았습니다.")

# LangSmith 설정 (모듈 임포트 전에 설정)
langsmith_enabled = False
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")

if langchain_api_key and langchain_api_key != "your_langsmith_api_key_here":
    # 환경변수 설정
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "ecommerce-chatbot")
    langsmith_enabled = True

# 핵심 모듈 임포트
try:
    from core.intent_classifier import IntentClassifier
    from core.rag_processor import RAGProcessor
    from core.db_query_engine import DatabaseQueryEngine
    from core.delivery_api_wrapper import DeliveryAPIWrapper
    from core.response_styler import ResponseStyler
    
    # OpenAI 클라이언트 (간단한 응답용)
    from openai import OpenAI
    
    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("❌ OpenAI API 키가 설정되지 않았습니다.")
        st.stop()
    
    openai_client = OpenAI(api_key=api_key)
    
except ImportError as e:
    st.error(f"❌ 필요한 모듈을 임포트할 수 없습니다: {e}")
    st.stop()

class UnifiedChatbotSystem:
    """통합 챗봇 시스템"""
    
    def __init__(self):
        self.project_root = project_root
        
        # 데이터 로드
        self.faq_data = self._load_json_data("faq_data.json")
        self.product_data = self._load_json_data("product_info.json")
        self.order_data = self._load_json_data("sample_orders.json")
        self.user_data = self._load_json_data("sample_users.json")
        
        # 모듈 초기화 (지연 로딩)
        self._intent_classifier = None
        self._rag_processor = None
        self._db_engine = None
        self._delivery_api = None
        self._response_styler = None
        
        # OpenAI 클라이언트
        self.openai_client = openai_client
        
        # 시스템 프롬프트 생성
        self.system_prompt = self._create_system_prompt()
    
    def _load_json_data(self, filename: str) -> list:
        """JSON 데이터 로드"""
        try:
            file_path = self.project_root / "data" / "raw_docs" / filename
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"{filename} 로드 실패: {e}")
            return []
    
    def _create_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        faq_text = "\n".join([f"Q: {faq['question']}\nA: {faq['answer']}" for faq in self.faq_data])
        
        product_text = ""
        for product in self.product_data:
            product_text += f"\n상품명: {product['name']}\n"
            product_text += f"가격: {product['price']:,}원\n"
            product_text += f"설명: {product['description']}\n"
            if 'specifications' in product:
                for key, value in product['specifications'].items():
                    product_text += f"{key}: {value}\n"
            product_text += "\n"
        
        return f"""당신은 쇼핑몰 고객 서비스 AI 어시스턴트입니다.

주요 역할:
1. 고객의 질문에 정확하고 친절한 답변 제공
2. FAQ, 상품 정보, 주문 관련 문의 처리
3. 적절한 이모지와 친근한 어조 사용

답변 가이드라인:
- 친근하고 정중한 어조 사용
- 구체적이고 실용적인 정보 제공
- 정보가 부족한 경우 추가 문의 방법 안내
- 적절한 이모지 사용으로 친근감 표현

=== FAQ 정보 ===
{faq_text}

=== 상품 정보 ===
{product_text}

=== 주문 상태 정보 ===
- 주문확인: 주문이 접수되어 확인 중입니다
- 상품준비중: 상품을 준비하고 있습니다
- 배송준비중: 배송을 준비하고 있습니다
- 배송중: 상품이 배송 중입니다
- 배송완료: 배송이 완료되었습니다

{{user_context}}

고객의 질문에 위 정보를 바탕으로 정확하고 친절하게 답변해주세요."""
    
    @property
    def intent_classifier(self):
        """Intent Classifier 지연 로딩"""
        if self._intent_classifier is None:
            self._intent_classifier = IntentClassifier()
        return self._intent_classifier
    
    @property
    def rag_processor(self):
        """RAG Processor 지연 로딩"""
        if self._rag_processor is None:
            self._rag_processor = RAGProcessor()
            if not hasattr(self._rag_processor, 'retriever') or self._rag_processor.retriever is None:
                self._rag_processor.initialize_vector_store()
        return self._rag_processor
    
    @property
    def db_engine(self):
        """DB Engine 지연 로딩"""
        if self._db_engine is None:
            self._db_engine = DatabaseQueryEngine()
        return self._db_engine
    
    @property
    def delivery_api(self):
        """Delivery API 지연 로딩"""
        if self._delivery_api is None:
            self._delivery_api = DeliveryAPIWrapper()
        return self._delivery_api
    
    @property
    def response_styler(self):
        """Response Styler 지연 로딩"""
        if self._response_styler is None:
            self._response_styler = ResponseStyler()
        return self._response_styler
    
    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """사용자 정보 조회"""
        for user in self.user_data:
            if user['user_id'] == user_id:
                return user
        return None
    
    def get_user_orders(self, user_id: int) -> list:
        """사용자 주문 목록 조회"""
        user_orders = [order for order in self.order_data if order['user_id'] == user_id]
        return sorted(user_orders, key=lambda x: x['order_date'], reverse=True)
    
    def format_user_orders(self, orders: list) -> str:
        """사용자 주문 목록 포맷팅"""
        if not orders:
            return "주문 내역이 없습니다."
        
        result = f"📋 **주문 내역** (총 {len(orders)}건)\n\n"
        
        for i, order in enumerate(orders, 1):
            items_text = ", ".join([item['product_name'] for item in order['items']])
            status_emoji = {
                '주문확인': '📝', '상품준비중': '📦', '배송준비중': '🚛',
                '배송중': '🚚', '배송완료': '✅'
            }.get(order['status'], '📋')
            
            result += f"{i}. **{order['order_id']}** ({order['order_date']})\n"
            result += f"   {status_emoji} 상태: {order['status']}\n"
            result += f"   💰 금액: {order['total_amount']:,}원\n"
            result += f"   🛍️ 상품: {items_text}\n"
            
            if order.get('tracking_number'):
                result += f"   📮 운송장: {order['tracking_number']} ({order['delivery_company']})\n"
            result += "\n"
        
        return result
    
    def process_query(self, user_input: str, current_user_id: Optional[int] = None, 
                     session_id: Optional[str] = None, use_advanced_rag: bool = False) -> Dict[str, Any]:
        """통합 쿼리 처리"""
        start_time = time.time()
        
        try:
            # 1. 명확한 주문 내역 요청 확인
            order_inquiry_keywords = ['내 주문', '주문 내역', '구매 내역', '주문한 것', '내가 산', '내가 주문한']
            is_order_inquiry = any(keyword in user_input.lower() for keyword in order_inquiry_keywords)
            
            if current_user_id and is_order_inquiry:
                user_orders = self.get_user_orders(current_user_id)
                response = self.format_user_orders(user_orders)
                return {
                    'response': response,
                    'method': 'order_lookup',
                    'response_time': time.time() - start_time
                }
            
            # 2. 고급 RAG 사용 여부 결정
            if use_advanced_rag:
                # Intent Classifier + RAG Processor 사용
                intent_result = self.intent_classifier.classify(user_input)
                processing_strategy = self.intent_classifier.get_processing_strategy(intent_result)
                
                if processing_strategy == "rag_processor":
                    rag_result = self.rag_processor.process_query(user_input)
                    response = rag_result['response']
                    method = 'advanced_rag'
                else:
                    response = self._simple_openai_response(user_input, current_user_id)
                    method = 'openai_direct'
            else:
                # 간단한 OpenAI 직접 호출
                response = self._simple_openai_response(user_input, current_user_id)
                method = 'openai_direct'
            
            return {
                'response': response,
                'method': method,
                'response_time': time.time() - start_time
            }
            
        except Exception as e:
            return {
                'response': f"죄송합니다. 시스템 오류가 발생했습니다: {str(e)}",
                'method': 'error',
                'response_time': time.time() - start_time
            }
    
    def _simple_openai_response(self, user_input: str, current_user_id: Optional[int] = None) -> str:
        """간단한 OpenAI 응답 생성"""
        # 사용자 컨텍스트 추가
        user_context = ""
        if current_user_id:
            user_info = self.get_user_info(current_user_id)
            user_orders = self.get_user_orders(current_user_id)
            
            if user_info:
                user_context = f"\n=== 현재 로그인한 사용자 정보 ===\n"
                user_context += f"이름: {user_info['username']}\n"
                user_context += f"회원등급: {user_info['member_grade']}\n"
                
                if user_orders:
                    user_context += f"\n=== 최근 주문 내역 ===\n"
                    for order in user_orders[:3]:  # 최근 3개만
                        items = ", ".join([item['product_name'] for item in order['items']])
                        user_context += f"주문번호: {order['order_id']}, 상태: {order['status']}, 상품: {items}\n"
        
        system_prompt = self.system_prompt.format(user_context=user_context)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"

def main():
    """Streamlit 메인 함수"""
    st.set_page_config(
        page_title="통합 쇼핑몰 챗봇",
        page_icon="🤖",
        layout="wide"
    )

    st.title("🤖 통합 RAG 기반 쇼핑몰 챗봇")
    st.markdown("**OpenAI GPT-4 + Vector DB + 개인화 서비스**")

    # 챗봇 시스템 초기화
    if 'unified_chatbot' not in st.session_state:
        with st.spinner("🚀 통합 챗봇 시스템을 초기화하는 중..."):
            st.session_state.unified_chatbot = UnifiedChatbotSystem()

    chatbot = st.session_state.unified_chatbot

    # 세션 상태 초기화
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_user_id' not in st.session_state:
        st.session_state.current_user_id = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # 사이드바
    with st.sidebar:
        st.header("🔧 시스템 설정")

        # LangSmith 상태
        if langsmith_enabled:
            st.success("✅ LangSmith 추적 활성화됨")
            st.caption(f"프로젝트: {os.getenv('LANGCHAIN_PROJECT', 'ecommerce-chatbot')}")
        else:
            st.info("ℹ️ LangSmith 추적 비활성화됨")

        # 처리 모드 선택
        use_advanced_rag = st.checkbox(
            "🧠 고급 RAG 모드 사용",
            value=False,
            help="Intent Classifier + Vector DB 검색 사용 (느리지만 정확)"
        )

        st.divider()

        # 사용자 로그인
        st.header("👤 사용자 로그인")
        user_options = ["로그인하지 않음"] + [f"{user['username']} ({user['email']})" for user in chatbot.user_data]
        selected_user = st.selectbox("테스트용 계정 선택:", user_options, index=0)

        # 사용자 정보 업데이트
        if selected_user == "로그인하지 않음":
            st.session_state.current_user_id = None
            current_user = None
        else:
            for user in chatbot.user_data:
                if f"{user['username']} ({user['email']})" == selected_user:
                    st.session_state.current_user_id = user['user_id']
                    current_user = user
                    break

        # 로그인된 사용자 정보 표시
        if current_user:
            st.success(f"✅ {current_user['username']}님 로그인됨")
            user_orders = chatbot.get_user_orders(current_user['user_id'])
            if user_orders:
                st.info(f"📦 주문 내역: {len(user_orders)}건")
                recent_order = user_orders[0]
                st.write(f"**최근 주문:** {recent_order['order_id']}")
                st.write(f"상태: {recent_order['status']}")
        else:
            st.info("로그인하지 않은 상태입니다")

        st.divider()

        # 시스템 정보
        st.header("📊 시스템 정보")
        st.markdown(f"""
        **데이터 현황:**
        - 사용자: {len(chatbot.user_data)}명
        - FAQ: {len(chatbot.faq_data)}개
        - 상품: {len(chatbot.product_data)}개
        - 주문: {len(chatbot.order_data)}건

        **세션 ID:** `{st.session_state.session_id[:8]}...`
        """)

        if st.button("🔄 대화 기록 초기화"):
            st.session_state.chat_history = []
            st.rerun()

    # 대화 기록 표시
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["user"])

        with st.chat_message("assistant"):
            st.write(chat["bot"])

            # 메타 정보 표시
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"⏱️ {chat['response_time']:.2f}초")
            with col2:
                st.caption(f"🔧 {chat['method']}")
            with col3:
                if chat.get('advanced_mode'):
                    st.caption("🧠 고급 모드")

    # 사용자 입력
    if user_input := st.chat_input("무엇을 도와드릴까요?"):
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.write(user_input)

        # 봇 응답 생성 및 표시
        with st.chat_message("assistant"):
            with st.spinner("🤖 AI가 답변을 생성하는 중..."):
                result = chatbot.process_query(
                    user_input,
                    st.session_state.current_user_id,
                    st.session_state.session_id,
                    use_advanced_rag
                )

            st.write(result['response'])

            # 메타 정보 표시
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"⏱️ {result['response_time']:.2f}초")
            with col2:
                st.caption(f"🔧 {result['method']}")
            with col3:
                if use_advanced_rag:
                    st.caption("🧠 고급 모드")

            # 대화 기록에 추가
            st.session_state.chat_history.append({
                "user": user_input,
                "bot": result['response'],
                "response_time": result['response_time'],
                "method": result['method'],
                "advanced_mode": use_advanced_rag
            })

if __name__ == "__main__":
    main()
