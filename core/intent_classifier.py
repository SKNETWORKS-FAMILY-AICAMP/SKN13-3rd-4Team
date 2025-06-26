"""
의도 분류기 (Intent Classifier)
사용자 질문의 의도를 분류하여 적절한 처리 방식을 결정
"""
import re
from typing import Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class IntentType(Enum):
    """의도 유형 정의"""
    FAQ = "faq"                    # FAQ 관련 질문
    PRODUCT_INFO = "product_info"  # 상품 정보 문의
    ORDER_STATUS = "order_status"  # 주문 상태 조회
    DELIVERY_TRACK = "delivery_track"  # 배송 추적
    USER_INFO = "user_info"        # 사용자 정보 관련
    GENERAL = "general"            # 일반적인 질문
    UNKNOWN = "unknown"            # 분류 불가

@dataclass
class IntentResult:
    """의도 분류 결과"""
    intent: IntentType
    confidence: float
    entities: Dict[str, str]  # 추출된 엔티티 (주문번호, 상품명 등)
    keywords: List[str]       # 핵심 키워드

class IntentClassifier:
    """의도 분류기 클래스"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1
        )
        
        # 키워드 기반 분류 규칙
        self.keyword_patterns = {
            IntentType.FAQ: [
                r'배송비|배송료|택배비|무료배송',
                r'반품|환불|취소|돌려보내기',
                r'교환|바꾸기|사이즈변경|색상변경',
                r'결제|결제방법|카드|계좌이체|카카오페이',
                r'회원가입|적립금|혜택|할인|등급',
                r'고객센터|운영시간|상담|문의|전화',
                r'쿠폰|할인|사용방법|적용|유효기간'
            ],
            IntentType.PRODUCT_INFO: [
                r'상품|제품|사양|스펙|크기|사이즈|무게',
                r'가격|얼마|비용|금액',
                r'색상|컬러|디자인|모델',
                r'배터리|충전|연결|블루투스',
                r'재고|품절|재입고|알림',
                r'이어폰|워치|키보드|웹캠|충전기'
            ],
            IntentType.ORDER_STATUS: [
                r'주문|주문상태|주문확인|주문내역',
                r'결제완료|결제확인|입금확인',
                r'상품준비|포장|발송준비'
            ],
            IntentType.DELIVERY_TRACK: [
                r'배송|택배|배송상태|배송현황|배송추적',
                r'언제|며칠|얼마나|도착|받을|수령',
                r'운송장|송장번호|추적번호',
                r'CJ|로젠|한진|우체국|택배사'
            ],
            IntentType.USER_INFO: [
                r'내정보|회원정보|개인정보|프로필',
                r'주소변경|연락처변경|정보수정',
                r'비밀번호|로그인|회원탈퇴'
            ]
        }
        
        # LLM 기반 분류 프롬프트
        self.classification_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 쇼핑몰 고객 문의 의도 분류 전문가입니다.

사용자의 질문을 다음 카테고리 중 하나로 분류해주세요:

1. faq: 자주 묻는 질문 (배송비, 반품, 교환, 결제방법, 회원혜택 등)
2. product_info: 상품 정보 문의 (사양, 가격, 재고, 특징 등)
3. order_status: 주문 상태 조회 (주문확인, 결제상태, 상품준비 등)
4. delivery_track: 배송 추적 (배송현황, 도착예정, 운송장번호 등)
5. user_info: 사용자 정보 관련 (개인정보, 주소변경, 로그인 등)
6. general: 일반적인 질문이나 인사
7. unknown: 분류하기 어려운 질문

응답 형식:
분류: [카테고리]
신뢰도: [0.0-1.0]
키워드: [핵심 키워드들을 쉼표로 구분]
엔티티: [주문번호, 상품명, 운송장번호 등이 있다면 추출]

예시:
질문: "내 주문 배송 언제 오나요?"
분류: delivery_track
신뢰도: 0.9
키워드: 주문, 배송, 언제
엔티티: 없음"""),
            ("human", "질문: {question}")
        ])
    
    def extract_entities(self, text: str) -> Dict[str, str]:
        """텍스트에서 엔티티 추출"""
        entities = {}
        
        # 주문번호 패턴 (ORD로 시작하는 패턴)
        order_pattern = r'ORD\d{8}\d{3}'
        order_match = re.search(order_pattern, text)
        if order_match:
            entities['order_id'] = order_match.group()
        
        # 운송장번호 패턴 (10-15자리 숫자)
        tracking_pattern = r'\b\d{10,15}\b'
        tracking_match = re.search(tracking_pattern, text)
        if tracking_match:
            entities['tracking_number'] = tracking_match.group()
        
        # 상품 ID 패턴 (P로 시작하는 패턴)
        product_pattern = r'P\d{3,}'
        product_match = re.search(product_pattern, text)
        if product_match:
            entities['product_id'] = product_match.group()
        
        # 전화번호 패턴
        phone_pattern = r'010-?\d{4}-?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            entities['phone'] = phone_match.group()
        
        return entities
    
    def classify_by_keywords(self, text: str) -> Tuple[IntentType, float]:
        """키워드 기반 의도 분류"""
        text_lower = text.lower()
        scores = {}
        
        for intent, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return IntentType.UNKNOWN, 0.0
        
        # 가장 높은 점수의 의도 반환
        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]
        
        # 신뢰도 계산 (간단한 정규화)
        confidence = min(max_score / 3.0, 1.0)
        
        return best_intent, confidence
    
    def classify_by_llm(self, text: str) -> Tuple[IntentType, float, List[str]]:
        """LLM 기반 의도 분류"""
        try:
            chain = self.classification_prompt | self.llm
            # LangSmith 트레이싱을 위한 메타데이터 추가
            response = chain.invoke(
                {"question": text},
                config={
                    "metadata": {
                        "component": "IntentClassifier",
                        "operation": "classify_by_llm",
                        "question_length": len(text),
                        "question_preview": text[:50] + "..." if len(text) > 50 else text
                    }
                }
            )
            
            # 응답 파싱
            lines = response.content.strip().split('\n')
            
            intent_str = "unknown"
            confidence = 0.0
            keywords = []
            
            for line in lines:
                if line.startswith('분류:'):
                    intent_str = line.split(':', 1)[1].strip()
                elif line.startswith('신뢰도:'):
                    try:
                        confidence = float(line.split(':', 1)[1].strip())
                    except:
                        confidence = 0.5
                elif line.startswith('키워드:'):
                    keyword_text = line.split(':', 1)[1].strip()
                    if keyword_text and keyword_text != '없음':
                        keywords = [k.strip() for k in keyword_text.split(',')]
            
            # 의도 타입 변환
            try:
                intent = IntentType(intent_str)
            except ValueError:
                intent = IntentType.UNKNOWN
                confidence = 0.0
            
            return intent, confidence, keywords
            
        except Exception as e:
            print(f"❌ LLM 분류 실패: {e}")
            return IntentType.UNKNOWN, 0.0, []
    
    def classify(self, text: str, use_llm: bool = True) -> IntentResult:
        """의도 분류 메인 함수"""
        # 엔티티 추출
        entities = self.extract_entities(text)
        
        # 키워드 기반 분류
        keyword_intent, keyword_confidence = self.classify_by_keywords(text)
        
        if use_llm and keyword_confidence < 0.7:
            # LLM 기반 분류 (키워드 분류 신뢰도가 낮을 때)
            llm_intent, llm_confidence, keywords = self.classify_by_llm(text)
            
            # 두 결과 조합
            if llm_confidence > keyword_confidence:
                final_intent = llm_intent
                final_confidence = llm_confidence
            else:
                final_intent = keyword_intent
                final_confidence = keyword_confidence
                keywords = []
        else:
            final_intent = keyword_intent
            final_confidence = keyword_confidence
            keywords = []
        
        # 특정 엔티티가 있으면 의도 조정
        if 'order_id' in entities or 'tracking_number' in entities:
            if final_intent in [IntentType.UNKNOWN, IntentType.GENERAL]:
                final_intent = IntentType.DELIVERY_TRACK
                final_confidence = max(final_confidence, 0.8)
        
        return IntentResult(
            intent=final_intent,
            confidence=final_confidence,
            entities=entities,
            keywords=keywords
        )
    
    def get_processing_strategy(self, intent_result: IntentResult) -> str:
        """의도에 따른 처리 전략 반환"""
        strategies = {
            IntentType.FAQ: "rag_processor",
            IntentType.PRODUCT_INFO: "rag_processor",
            IntentType.ORDER_STATUS: "db_query",
            IntentType.DELIVERY_TRACK: "delivery_api",
            IntentType.USER_INFO: "db_query",
            IntentType.GENERAL: "general_response",
            IntentType.UNKNOWN: "fallback"
        }
        
        return strategies.get(intent_result.intent, "fallback")

# 사용 예시
if __name__ == "__main__":
    classifier = IntentClassifier()
    
    # 테스트 질문들
    test_questions = [
        "배송비는 얼마인가요?",
        "무선 이어폰 사양이 어떻게 되나요?",
        "내 주문 ORD20241201001 상태 알려주세요",
        "운송장번호 123456789012 배송 현황 확인해주세요",
        "반품은 어떻게 하나요?",
        "안녕하세요",
        "이상한 질문입니다"
    ]
    
    for question in test_questions:
        print(f"\n🔍 질문: {question}")
        result = classifier.classify(question)
        strategy = classifier.get_processing_strategy(result)
        
        print(f"📋 의도: {result.intent.value}")
        print(f"📊 신뢰도: {result.confidence:.2f}")
        print(f"🏷️ 엔티티: {result.entities}")
        print(f"🔑 키워드: {result.keywords}")
        print(f"⚙️ 처리 전략: {strategy}")
