"""
RAG (Retrieval-Augmented Generation) 프로세서
벡터 DB를 사용한 문서 검색 및 응답 생성
"""
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()


class RAGProcessor:
    """RAG 기반 문서 검색 및 응답 생성 클래스"""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name, temperature=0.1)
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        
        # 프로젝트 루트 경로 설정
        self.project_root = Path(__file__).parent.parent
        self.vector_db_path = self.project_root / "data" / "vectordb_chroma"
        self.raw_docs_path = self.project_root / "data" / "raw_docs"
    
    def initialize_vector_store(self):
        """벡터 스토어 초기화"""
        try:
            if self.vector_db_path.exists():
                # 기존 벡터 스토어 로드
                self.vectorstore = Chroma(
                    persist_directory=str(self.vector_db_path),
                    embedding_function=self.embeddings
                )
                print(f"✅ 벡터 스토어 로드 완료: {self.vector_db_path}")
            else:
                # 새로운 벡터 스토어 생성
                print("⚠️ 벡터 스토어가 없습니다. 새로 생성합니다...")
                self._create_vector_store()
        except Exception as e:
            print(f"❌ 벡터 스토어 초기화 실패: {e}")
            raise
    
    def _create_vector_store(self):
        """벡터 스토어 생성"""
        documents = self._load_documents()
        
        if not documents:
            raise ValueError("로드할 문서가 없습니다.")
        
        # 벡터 스토어 생성
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=str(self.vector_db_path)
        )
        
        # 저장
        self.vectorstore.persist()
        print(f"✅ 벡터 스토어 생성 완료: {self.vector_db_path}")
    
    def _load_documents(self) -> List[Document]:
        """문서 로드 및 Document 객체 변환"""
        documents = []
        
        # FAQ 문서 처리
        faq_documents = self._process_faq_documents()
        documents.extend(faq_documents)
        
        # 제품 정보 문서 처리
        product_documents = self._process_product_documents()
        documents.extend(product_documents)
        
        return documents
    
    def _process_faq_documents(self) -> List[Document]:
        """FAQ 문서 처리"""
        documents = []
        faq_file = self.raw_docs_path / "faq_data.json"
        
        if not faq_file.exists():
            print(f"⚠️ FAQ 파일이 없습니다: {faq_file}")
            return documents
        
        try:
            with open(faq_file, 'r', encoding='utf-8') as f:
                faq_data = json.load(f)
            
            for faq in faq_data:
                content = f"질문: {faq['question']}\n답변: {faq['answer']}"
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": "faq",
                        "category": faq.get('category', 'general'),
                        "faq_id": faq.get('id', ''),
                        "keywords": faq.get('keywords', [])
                    }
                )
                documents.append(doc)
            
            print(f"✅ FAQ 문서 {len(documents)}개 로드 완료")
        except Exception as e:
            print(f"❌ FAQ 문서 로드 실패: {e}")
        
        return documents
    
    def _process_product_documents(self) -> List[Document]:
        """제품 정보 문서 처리"""
        documents = []
        product_file = self.raw_docs_path / "product_info.json"
        
        if not product_file.exists():
            print(f"⚠️ 제품 정보 파일이 없습니다: {product_file}")
            return documents
        
        try:
            with open(product_file, 'r', encoding='utf-8') as f:
                product_data = json.load(f)
            
            for product in product_data:
                # 제품 정보를 텍스트로 변환
                content_parts = [
                    f"제품명: {product['name']}",
                    f"가격: {product['price']:,}원",
                    f"설명: {product['description']}"
                ]
                
                if 'specifications' in product:
                    specs = product['specifications']
                    content_parts.append("사양:")
                    for key, value in specs.items():
                        content_parts.append(f"- {key}: {value}")
                
                content = "\n".join(content_parts)
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": "product",
                        "product_id": product.get('id', ''),
                        "category": product.get('category', ''),
                        "price": product.get('price', 0),
                        "name": product.get('name', '')
                    }
                )
                documents.append(doc)
            
            print(f"✅ 제품 정보 문서 {len(documents)}개 로드 완료")
        except Exception as e:
            print(f"❌ 제품 정보 문서 로드 실패: {e}")
        
        return documents
    
    def process_query(self, query: str, k: int = 3) -> Dict[str, Any]:
        """
        쿼리 처리 및 응답 생성
        
        Args:
            query: 사용자 질문
            k: 검색할 문서 수
            
        Returns:
            응답 결과 딕셔너리
        """
        start_time = time.time()
        
        if not self.vectorstore:
            return {
                "response": "죄송합니다. 검색 시스템이 초기화되지 않았습니다.",
                "confidence": 0.0,
                "sources": [],
                "response_time": time.time() - start_time
            }
        
        try:
            # 벡터 검색 수행
            search_results = self.vectorstore.similarity_search(query, k=k)
            
            if not search_results:
                return {
                    "response": "죄송합니다. 관련 정보를 찾을 수 없습니다.",
                    "confidence": 0.0,
                    "sources": [],
                    "response_time": time.time() - start_time
                }
            
            # 검색 결과를 컨텍스트로 변환
            context = self._format_search_results(search_results)
            
            # LLM을 사용한 응답 생성
            response = self._generate_response(query, context)
            
            # 소스 정보 추출
            sources = self._extract_source_info(search_results)
            
            # 신뢰도 계산 (간단한 휴리스틱)
            confidence = self._calculate_confidence(search_results, query)
            
            return {
                "response": response,
                "confidence": confidence,
                "sources": sources,
                "response_time": time.time() - start_time
            }
            
        except Exception as e:
            return {
                "response": f"죄송합니다. 검색 중 오류가 발생했습니다: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "response_time": time.time() - start_time
            }
    
    def _format_search_results(self, search_results: List[Document]) -> str:
        """검색 결과를 컨텍스트 문자열로 변환"""
        context_parts = []
        for i, doc in enumerate(search_results, 1):
            context_parts.append(f"[참고자료 {i}]\n{doc.page_content}")
        
        return "\n\n".join(context_parts)
    
    def _generate_response(self, query: str, context: str) -> str:
        """LLM을 사용한 응답 생성"""
        prompt_template = ChatPromptTemplate.from_template("""
당신은 친절하고 전문적인 쇼핑몰 고객센터 직원입니다.
아래 참고자료를 바탕으로 고객의 질문에 정확하고 도움이 되는 답변을 제공해주세요.

참고자료:
{context}

고객 질문: {query}

답변 가이드라인:
1. 참고자료에 있는 정보만 사용하여 답변하세요
2. 정확하지 않은 정보는 제공하지 마세요
3. 친근하고 도움이 되는 톤으로 답변하세요
4. 필요시 추가 문의를 안내하세요

답변:
""")
        
        try:
            messages = prompt_template.format_messages(
                context=context,
                query=query
            )
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _extract_source_info(self, search_results: List[Document]) -> List[Dict[str, Any]]:
        """검색 결과에서 소스 정보 추출"""
        sources = []
        for doc in search_results:
            source_info = {
                "source": doc.metadata.get("source", "unknown"),
                "content_preview": doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content,
                "metadata": doc.metadata
            }
            sources.append(source_info)
        
        return sources
    
    def _calculate_confidence(self, search_results: List[Document], query: str) -> float:
        """신뢰도 계산 (간단한 휴리스틱)"""
        if not search_results:
            return 0.0
        
        # 검색 결과 수에 따른 기본 신뢰도
        base_confidence = min(len(search_results) * 0.3, 0.9)
        
        # 쿼리 키워드가 결과에 포함되어 있는지 확인
        query_lower = query.lower()
        keyword_matches = 0
        
        for doc in search_results:
            content_lower = doc.page_content.lower()
            if any(word in content_lower for word in query_lower.split() if len(word) > 2):
                keyword_matches += 1
        
        # 키워드 매치에 따른 신뢰도 조정
        keyword_confidence = keyword_matches / len(search_results) * 0.3
        
        return min(base_confidence + keyword_confidence, 1.0)


# 사용 예시
if __name__ == "__main__":
    # RAG 프로세서 초기화
    rag = RAGProcessor()
    rag.initialize_vector_store()
    
    # 테스트 쿼리들
    test_queries = [
        "배송비는 얼마인가요?",
        "무선 이어폰 배터리 지속시간은?",
        "반품 절차를 알려주세요"
    ]
    
    print("🔍 RAG 프로세서 테스트 시작\n")
    
    for query in test_queries:
        print(f"질문: {query}")
        result = rag.process_query(query)
        
        print(f"답변: {result['response'][:200]}...")
        print(f"신뢰도: {result['confidence']:.2f}")
        print(f"응답 시간: {result['response_time']:.2f}초")
        print(f"소스 수: {len(result['sources'])}")
        print("-" * 50)
