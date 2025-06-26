"""
문서 임베딩 스크립트
FAQ와 상품 정보를 벡터 데이터베이스에 임베딩
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.rag_processor import RAGProcessor

def main():
    """메인 실행 함수"""
    print("🚀 문서 임베딩 시작...")
    
    try:
        # RAG 프로세서 초기화
        rag_processor = RAGProcessor()
        
        # 벡터 스토어 초기화 (문서 임베딩 포함)
        rag_processor.initialize_vector_store()
        
        print("✅ 문서 임베딩 완료!")
        
        # 테스트 쿼리 실행
        test_queries = [
            "배송비는 얼마인가요?",
            "무선 이어폰 사양이 어떻게 되나요?",
            "반품은 어떻게 하나요?"
        ]
        
        print("\n🔍 테스트 쿼리 실행:")
        for query in test_queries:
            print(f"\n질문: {query}")
            result = rag_processor.process_query(query)
            print(f"답변: {result['response'][:100]}...")
            print(f"신뢰도: {result['confidence']:.2f}")
            print(f"소스 수: {len(result['sources'])}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
