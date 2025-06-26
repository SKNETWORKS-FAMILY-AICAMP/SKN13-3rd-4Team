"""
챗봇 기능 테스트 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.intent_classifier import IntentClassifier
from core.rag_processor import RAGProcessor
from core.db_query_engine import DatabaseQueryEngine
from core.delivery_api_wrapper import DeliveryAPIWrapper
from core.response_styler import ResponseStyler

def test_intent_classifier():
    """의도 분류기 테스트"""
    print("🔍 의도 분류기 테스트")
    print("-" * 50)
    
    classifier = IntentClassifier()
    
    test_cases = [
        "배송비는 얼마인가요?",
        "무선 이어폰 사양 알려주세요",
        "주문번호 ORD20241201001 상태 확인해주세요",
        "운송장번호 123456789012 배송 현황 알려주세요",
        "반품은 어떻게 하나요?",
        "안녕하세요",
        "이상한 질문입니다"
    ]
    
    for query in test_cases:
        result = classifier.classify(query)
        print(f"질문: {query}")
        print(f"의도: {result.intent.value} (신뢰도: {result.confidence:.2f})")
        print(f"엔티티: {result.entities}")
        print()

def test_rag_processor():
    """RAG 프로세서 테스트"""
    print("📚 RAG 프로세서 테스트")
    print("-" * 50)
    
    try:
        rag = RAGProcessor()
        rag.initialize_vector_store()
        
        test_queries = [
            "배송비는 얼마인가요?",
            "무선 이어폰 배터리는 얼마나 지속되나요?",
            "반품 절차를 알려주세요"
        ]
        
        for query in test_queries:
            result = rag.process_query(query)
            print(f"질문: {query}")
            print(f"답변: {result['response'][:150]}...")
            print(f"신뢰도: {result['confidence']:.2f}")
            print()
            
    except Exception as e:
        print(f"❌ RAG 프로세서 테스트 실패: {e}")

def test_db_query_engine():
    """DB 쿼리 엔진 테스트"""
    print("🗄️ DB 쿼리 엔진 테스트")
    print("-" * 50)
    
    try:
        db_engine = DatabaseQueryEngine()
        
        # 주문 조회 테스트
        order = db_engine.get_order_by_id("ORD20241201001")
        if order:
            print("주문 조회 성공:")
            print(db_engine.format_order_info(order)[:200] + "...")
        else:
            print("❌ 주문 조회 실패 - 데이터베이스를 초기화해주세요")
        
        print()
        
        # 사용자 주문 목록 테스트
        orders = db_engine.get_recent_orders_by_phone("010-1234-5678")
        if orders:
            print("사용자 주문 목록 조회 성공:")
            print(db_engine.format_user_orders(orders)[:200] + "...")
        else:
            print("❌ 사용자 주문 목록 조회 실패")
            
    except Exception as e:
        print(f"❌ DB 쿼리 엔진 테스트 실패: {e}")

def test_delivery_api():
    """배송 API 테스트"""
    print("🚚 배송 API 테스트")
    print("-" * 50)
    
    try:
        delivery_api = DeliveryAPIWrapper()
        
        # 배송 추적 테스트
        tracking_info = delivery_api.track_package("123456789012")
        if tracking_info:
            print("배송 추적 성공:")
            print(delivery_api.format_delivery_info(tracking_info)[:200] + "...")
        else:
            print("❌ 배송 추적 실패")
        
        print()
        
        # 배송 예상 시간 테스트
        estimate = delivery_api.get_delivery_estimate("서울", "부산")
        print(f"배송 예상 시간: {estimate['description']}")
        
    except Exception as e:
        print(f"❌ 배송 API 테스트 실패: {e}")

def test_response_styler():
    """응답 스타일러 테스트"""
    print("✨ 응답 스타일러 테스트")
    print("-" * 50)
    
    try:
        styler = ResponseStyler()
        
        test_responses = [
            ("배송비는 5만원 이상 주문시 무료입니다.", "friendly"),
            ("주문번호 ORD20241201001의 상태는 배송중입니다.", "informative"),
            ("죄송합니다. 해당 정보를 찾을 수 없습니다.", "apologetic")
        ]
        
        for response, tone_str in test_responses:
            from core.response_styler import ResponseTone
            tone = ResponseTone(tone_str)
            styled = styler.style_response(response, tone, include_greeting=True)
            
            print(f"원본: {response}")
            print(f"스타일링: {styled}")
            print()
            
    except Exception as e:
        print(f"❌ 응답 스타일러 테스트 실패: {e}")

def main():
    """메인 테스트 함수"""
    print("🧪 챗봇 시스템 통합 테스트")
    print("=" * 60)
    
    try:
        test_intent_classifier()
        test_rag_processor()
        test_db_query_engine()
        test_delivery_api()
        test_response_styler()
        
        print("✅ 모든 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
