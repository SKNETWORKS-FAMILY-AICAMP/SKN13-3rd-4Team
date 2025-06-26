"""
<<<<<<< HEAD
응답 스타일러 모듈
응답의 톤앤매너를 조정하고 이모지 및 포맷팅을 적용
"""
from enum import Enum
from typing import Optional


class ResponseTone(Enum):
    """응답 톤 유형"""
    FRIENDLY = "friendly"
    HELPFUL = "helpful"
    INFORMATIVE = "informative"
    FORMAL = "formal"
    APOLOGETIC = "apologetic"

=======
응답 스타일러
챗봇 응답의 톤앤매너를 조정하고 일관된 스타일로 변환
"""
import random
from typing import Dict, List, Optional
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class ResponseTone(Enum):
    """응답 톤 유형"""
    FRIENDLY = "friendly"      # 친근한
    FORMAL = "formal"          # 정중한
    HELPFUL = "helpful"        # 도움이 되는
    APOLOGETIC = "apologetic"  # 사과하는
    INFORMATIVE = "informative" # 정보 제공형
>>>>>>> 98f88f8369a00fea011ba0112cbc9097e2eb5e55

class ResponseStyler:
    """응답 스타일링 클래스"""
    
    def __init__(self):
<<<<<<< HEAD
        self.greeting_emojis = {
            ResponseTone.FRIENDLY: "😊",
            ResponseTone.HELPFUL: "🤝",
            ResponseTone.INFORMATIVE: "📋",
            ResponseTone.FORMAL: "💼",
            ResponseTone.APOLOGETIC: "😔"
        }
        
        self.greeting_phrases = {
            ResponseTone.FRIENDLY: "안녕하세요!",
            ResponseTone.HELPFUL: "도움을 드리겠습니다!",
            ResponseTone.INFORMATIVE: "정보를 안내해드리겠습니다.",
            ResponseTone.FORMAL: "안녕하십니까.",
            ResponseTone.APOLOGETIC: "죄송합니다."
        }
    
    def style_response(self, response: str, tone: ResponseTone = ResponseTone.FRIENDLY, 
                      include_greeting: bool = False) -> str:
        """
        응답에 스타일링 적용
        
        Args:
            response: 원본 응답 텍스트
            tone: 적용할 톤
            include_greeting: 인사말 포함 여부
            
        Returns:
            스타일링된 응답
        """
        styled_response = response
        
        # 인사말 추가
        if include_greeting:
            emoji = self.greeting_emojis.get(tone, "")
            greeting = self.greeting_phrases.get(tone, "안녕하세요!")
            styled_response = f"{emoji} {greeting}\n\n{styled_response}"
        
        # 톤에 따른 추가 스타일링
        if tone == ResponseTone.HELPFUL:
            styled_response += "\n\n추가로 궁금한 점이 있으시면 언제든 말씀해주세요! 🤗"
        elif tone == ResponseTone.APOLOGETIC:
            styled_response += "\n\n불편을 드려 죄송합니다. 더 나은 서비스로 보답하겠습니다."
        elif tone == ResponseTone.INFORMATIVE:
            styled_response = f"📌 {styled_response}"
        
        return styled_response
    
    def determine_tone(self, intent: str, confidence: float) -> ResponseTone:
        """
        의도와 신뢰도에 따른 톤 결정
        
        Args:
            intent: 의도 유형
            confidence: 신뢰도
            
        Returns:
            적절한 응답 톤
        """
        if confidence < 0.5:
            return ResponseTone.APOLOGETIC
        elif intent in ["FAQ", "PRODUCT_INFO"]:
            return ResponseTone.INFORMATIVE
        elif intent in ["ORDER_STATUS", "DELIVERY_TRACK"]:
            return ResponseTone.HELPFUL
        elif intent == "GENERAL":
            return ResponseTone.FRIENDLY
        else:
            return ResponseTone.FORMAL

=======
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3
        )
        
        # 기본 인사말 템플릿
        self.greetings = [
            "안녕하세요! 😊",
            "반갑습니다! 👋",
            "안녕하세요, 고객님! 🌟",
            "좋은 하루입니다! ☀️"
        ]
        
        # 마무리 문구 템플릿
        self.closings = {
            ResponseTone.FRIENDLY: [
                "더 궁금한 점이 있으시면 언제든 말씀해주세요! 😊",
                "도움이 되셨길 바라요! 좋은 하루 되세요! 🌟",
                "또 다른 질문이 있으시면 편하게 물어보세요! 👍"
            ],
            ResponseTone.FORMAL: [
                "추가 문의사항이 있으시면 언제든 연락주시기 바랍니다.",
                "더 자세한 상담이 필요하시면 고객센터(1588-1234)로 문의해주세요.",
                "감사합니다. 좋은 하루 되시기 바랍니다."
            ],
            ResponseTone.HELPFUL: [
                "이 정보가 도움이 되셨나요? 더 필요한 정보가 있으시면 말씀해주세요!",
                "문제 해결에 도움이 되었기를 바랍니다. 추가 질문 언제든 환영입니다!",
                "더 구체적인 도움이 필요하시면 언제든 말씀해주세요!"
            ],
            ResponseTone.APOLOGETIC: [
                "불편을 드려 죄송합니다. 더 나은 서비스로 보답하겠습니다.",
                "양해 부탁드리며, 추가 도움이 필요하시면 언제든 연락주세요.",
                "죄송합니다. 더 정확한 정보를 위해 고객센터로 문의해주시면 감사하겠습니다."
            ]
        }
        
        # 에러 메시지 템플릿
        self.error_messages = {
            "not_found": [
                "죄송합니다. 요청하신 정보를 찾을 수 없습니다.",
                "해당 정보가 확인되지 않습니다.",
                "요청하신 내용에 대한 정보가 없습니다."
            ],
            "system_error": [
                "일시적인 시스템 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "현재 시스템 점검 중입니다. 불편을 드려 죄송합니다.",
                "기술적인 문제가 발생했습니다. 고객센터로 문의해주세요."
            ],
            "insufficient_info": [
                "더 정확한 답변을 위해 추가 정보가 필요합니다.",
                "좀 더 구체적인 정보를 알려주시면 더 나은 도움을 드릴 수 있습니다.",
                "정확한 안내를 위해 세부 사항을 확인해주세요."
            ]
        }
        
        # 스타일링 프롬프트
        self.styling_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 쇼핑몰 고객 서비스 응답 스타일링 전문가입니다.

주어진 응답을 다음 가이드라인에 따라 스타일링해주세요:

**기본 원칙:**
1. 친근하고 정중한 어조 유지
2. 고객의 감정에 공감하며 응답
3. 구체적이고 실용적인 정보 제공
4. 적절한 이모지 사용으로 친근감 표현
5. 추가 도움 제안으로 마무리

**톤 별 특징:**
- friendly: 친근하고 따뜻한 어조, 이모지 적극 활용
- formal: 정중하고 격식 있는 어조, 이모지 최소화
- helpful: 도움이 되는 정보 중심, 실용적 조언 포함
- apologetic: 사과와 이해의 어조, 대안 제시
- informative: 정확한 정보 전달 중심, 체계적 구성

**응답 구조:**
1. 인사/공감 표현
2. 핵심 정보 제공
3. 추가 설명 (필요시)
4. 마무리 인사/추가 도움 제안

톤: {tone}
원본 응답: {original_response}

스타일링된 응답을 제공해주세요:"""),
            ("human", "원본 응답을 위의 가이드라인에 따라 스타일링해주세요.")
        ])
    
    def determine_tone(self, intent: str, confidence: float, 
                      has_error: bool = False) -> ResponseTone:
        """상황에 따른 적절한 톤 결정"""
        if has_error:
            return ResponseTone.APOLOGETIC
        
        if confidence < 0.5:
            return ResponseTone.HELPFUL
        
        # 의도별 기본 톤
        tone_mapping = {
            "faq": ResponseTone.FRIENDLY,
            "product_info": ResponseTone.INFORMATIVE,
            "order_status": ResponseTone.HELPFUL,
            "delivery_track": ResponseTone.INFORMATIVE,
            "user_info": ResponseTone.FORMAL,
            "general": ResponseTone.FRIENDLY,
            "unknown": ResponseTone.HELPFUL
        }
        
        return tone_mapping.get(intent, ResponseTone.FRIENDLY)
    
    def add_greeting(self, response: str, include_greeting: bool = True) -> str:
        """인사말 추가"""
        if not include_greeting:
            return response
        
        # 이미 인사말이 있는지 확인
        greeting_keywords = ["안녕", "반갑", "좋은", "감사"]
        if any(keyword in response[:20] for keyword in greeting_keywords):
            return response
        
        greeting = random.choice(self.greetings)
        return f"{greeting} {response}"
    
    def add_closing(self, response: str, tone: ResponseTone) -> str:
        """마무리 문구 추가"""
        # 이미 마무리 문구가 있는지 확인
        closing_keywords = ["문의", "연락", "도움", "감사", "바라", "환영"]
        if any(keyword in response[-50:] for keyword in closing_keywords):
            return response
        
        closings = self.closings.get(tone, self.closings[ResponseTone.FRIENDLY])
        closing = random.choice(closings)
        
        return f"{response}\n\n{closing}"
    
    def add_emojis(self, response: str, tone: ResponseTone) -> str:
        """적절한 이모지 추가"""
        if tone == ResponseTone.FORMAL:
            return response  # 격식 있는 톤에서는 이모지 최소화
        
        # 키워드별 이모지 매핑
        emoji_mapping = {
            "배송": "🚚",
            "주문": "📦",
            "상품": "🛍️",
            "결제": "💳",
            "반품": "↩️",
            "교환": "🔄",
            "완료": "✅",
            "확인": "✅",
            "문제": "⚠️",
            "오류": "❌",
            "죄송": "😔",
            "감사": "🙏",
            "도움": "💡",
            "정보": "📋"
        }
        
        # 이미 이모지가 충분히 있는지 확인
        emoji_count = len([char for char in response if ord(char) > 127])
        if emoji_count >= 3:
            return response
        
        # 키워드 기반 이모지 추가
        for keyword, emoji in emoji_mapping.items():
            if keyword in response and emoji not in response:
                response = response.replace(keyword, f"{keyword} {emoji}", 1)
                break
        
        return response
    
    def handle_error_response(self, error_type: str, 
                            additional_info: Optional[str] = None) -> str:
        """에러 상황별 응답 생성"""
        base_message = random.choice(self.error_messages.get(error_type, 
                                                           self.error_messages["system_error"]))
        
        response = base_message
        
        if additional_info:
            response += f" {additional_info}"
        
        # 대안 제시
        if error_type == "not_found":
            response += " 다른 키워드로 검색해보시거나 고객센터(1588-1234)로 문의해주세요."
        elif error_type == "insufficient_info":
            response += " 주문번호, 운송장번호, 또는 연락처 등을 함께 알려주시면 더 정확한 도움을 드릴 수 있습니다."
        
        return self.style_response(response, ResponseTone.APOLOGETIC)
    
    def style_response(self, response: str, tone: ResponseTone, 
                      use_llm: bool = False, include_greeting: bool = False) -> str:
        """응답 스타일링 메인 함수"""
        if use_llm:
            # LLM을 사용한 고급 스타일링
            try:
                chain = self.styling_prompt | self.llm
                styled = chain.invoke({
                    "tone": tone.value,
                    "original_response": response
                })
                return styled.content
            except Exception as e:
                print(f"❌ LLM 스타일링 실패: {e}")
                # 폴백으로 규칙 기반 스타일링 사용
        
        # 규칙 기반 스타일링
        styled_response = response
        
        # 1. 인사말 추가
        styled_response = self.add_greeting(styled_response, include_greeting)
        
        # 2. 이모지 추가
        styled_response = self.add_emojis(styled_response, tone)
        
        # 3. 마무리 문구 추가
        styled_response = self.add_closing(styled_response, tone)
        
        return styled_response
    
    def format_structured_response(self, title: str, content: str, 
                                 tone: ResponseTone = ResponseTone.FRIENDLY) -> str:
        """구조화된 응답 포맷팅"""
        formatted = f"**{title}**\n\n{content}"
        return self.style_response(formatted, tone)
    
    def create_quick_replies(self, suggestions: List[str]) -> str:
        """빠른 답변 제안 생성"""
        if not suggestions:
            return ""
        
        reply_text = "\n\n💡 **이런 것도 궁금하신가요?**\n"
        for i, suggestion in enumerate(suggestions[:3], 1):
            reply_text += f"{i}. {suggestion}\n"
        
        return reply_text
>>>>>>> 98f88f8369a00fea011ba0112cbc9097e2eb5e55

# 사용 예시
if __name__ == "__main__":
    styler = ResponseStyler()
    
    # 테스트 응답들
<<<<<<< HEAD
    test_cases = [
        ("배송비는 5만원 이상 주문시 무료입니다.", ResponseTone.INFORMATIVE),
        ("주문번호 ORD123의 상태는 배송중입니다.", ResponseTone.HELPFUL),
        ("죄송합니다. 해당 정보를 찾을 수 없습니다.", ResponseTone.APOLOGETIC),
        ("안녕하세요! 무엇을 도와드릴까요?", ResponseTone.FRIENDLY)
    ]
    
    print("🎨 응답 스타일러 테스트:")
    print("=" * 50)
    
    for response, tone in test_cases:
        styled = styler.style_response(response, tone, include_greeting=True)
        print(f"톤: {tone.value}")
        print(f"원본: {response}")
        print(f"스타일링: {styled}")
        print("-" * 30)
=======
    test_responses = [
        ("배송비는 5만원 이상 주문시 무료입니다.", ResponseTone.FRIENDLY),
        ("주문번호 ORD20241201001의 상태는 배송중입니다.", ResponseTone.INFORMATIVE),
        ("죄송합니다. 해당 정보를 찾을 수 없습니다.", ResponseTone.APOLOGETIC),
        ("상품 사양은 다음과 같습니다.", ResponseTone.HELPFUL)
    ]
    
    for response, tone in test_responses:
        print(f"\n원본: {response}")
        styled = styler.style_response(response, tone, include_greeting=True)
        print(f"스타일링: {styled}")
        print("-" * 50)
>>>>>>> 98f88f8369a00fea011ba0112cbc9097e2eb5e55
