"""
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


class ResponseStyler:
    """응답 스타일링 클래스"""
    
    def __init__(self):
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


# 사용 예시
if __name__ == "__main__":
    styler = ResponseStyler()
    
    # 테스트 응답들
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
