"""
RAG (Retrieval-Augmented Generation) 처리기
FAQ와 상품 정보에 대한 벡터 검색 및 응답 생성
"""
import json
from typing import List, Dict, Any
from pathlib import Path

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
load_dotenv()

class RAGProcessor:
    """RAG 기반 문서 검색 및 응답 생성 클래스"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.vector_db_path = self.data_dir / "vectordb_chroma"
        
        # OpenAI 모델 초기화
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1
        )
        
        # 임베딩 모델 초기화
        self.embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-large"
        )
        
        # 벡터 데이터베이스 초기화
        self.vector_store = None
        self.retriever = None
        
        # 텍스트 분할기
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # 프롬프트 템플릿
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 쇼핑몰 고객 서비스 AI 어시스턴트입니다.
            
주요 역할:
- 고객의 질문에 대해 정확하고 친절한 답변 제공
- 제공된 문서 정보를 바탕으로 답변 생성
- 정보가 부족한 경우 정중하게 안내

답변 가이드라인:
1. 친근하고 정중한 어조 사용
2. 구체적이고 실용적인 정보 제공
3. 문서에 없는 정보는 추측하지 말고 안내
4. 필요시 추가 문의 방법 안내

검색된 문서 정보:
{context}
"""),
            ("human", "{question}")
        ])
    
    def initialize_vector_store(self):
        """벡터 스토어 초기화"""
        try:
            # 기존 벡터 스토어 로드 시도
            self.vector_store = Chroma(
                persist_directory=str(self.vector_db_path),
                embedding_function=self.embedding_model,
                collection_name="ecommerce_docs"
            )
            
            # 문서가 있는지 확인
            if self.vector_store._collection.count() == 0:
                print("📄 벡터 스토어가 비어있습니다. 문서를 임베딩합니다...")
                self._embed_documents()
            else:
                print(f"✅ 기존 벡터 스토어 로드 완료 (문서 수: {self.vector_store._collection.count()})")
            
            # 리트리버 설정
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            
        except Exception as e:
            print(f"❌ 벡터 스토어 초기화 실패: {e}")
            print("📄 새로운 벡터 스토어를 생성합니다...")
            self._create_new_vector_store()
    
    def _create_new_vector_store(self):
        """새로운 벡터 스토어 생성"""
        # 디렉토리 생성
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        
        # 새 벡터 스토어 생성
        self.vector_store = Chroma(
            persist_directory=str(self.vector_db_path),
            embedding_function=self.embedding_model,
            collection_name="ecommerce_docs"
        )
        
        # 문서 임베딩
        self._embed_documents()
        
        # 리트리버 설정
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
    
    def _embed_documents(self):
        """문서들을 임베딩하여 벡터 스토어에 저장"""
        documents = []
        
        # FAQ 문서 처리
        faq_docs = self._process_faq_documents()
        documents.extend(faq_docs)
        
        # 상품 정보 문서 처리
        product_docs = self._process_product_documents()
        documents.extend(product_docs)
        
        if documents:
            # 문서를 청크로 분할
            split_docs = self.text_splitter.split_documents(documents)
            
            # 벡터 스토어에 추가
            self.vector_store.add_documents(split_docs)
            print(f"✅ {len(split_docs)}개 문서 청크가 벡터 스토어에 저장되었습니다.")
        else:
            print("⚠️ 임베딩할 문서가 없습니다.")
    
    def _process_faq_documents(self) -> List[Document]:
        """FAQ 데이터를 Document 객체로 변환"""
        documents = []
        faq_file = self.data_dir / "raw_docs" / "faq_data.json"
        
        if faq_file.exists():
            with open(faq_file, 'r', encoding='utf-8') as f:
                faq_data = json.load(f)
            
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
                documents.append(doc)
            
            print(f"📋 FAQ 문서 {len(documents)}개 처리 완료")
        
        return documents
    
    def _process_product_documents(self) -> List[Document]:
        """상품 정보를 Document 객체로 변환"""
        documents = []
        product_file = self.data_dir / "raw_docs" / "product_info.json"
        
        if product_file.exists():
            with open(product_file, 'r', encoding='utf-8') as f:
                product_data = json.load(f)
            
            for product in product_data:
                # 상품 기본 정보
                content = f"상품명: {product['name']}\n"
                content += f"카테고리: {product['category']}\n"
                content += f"설명: {product['description']}\n"
                content += f"가격: {product['price']:,}원\n"
                
                # 사양 정보
                if 'specifications' in product:
                    content += "\n사양:\n"
                    for key, value in product['specifications'].items():
                        content += f"- {key}: {value}\n"
                
                # 특징 정보
                if 'features' in product:
                    content += "\n주요 특징:\n"
                    for feature in product['features']:
                        content += f"- {feature}\n"
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": "product",
                        "product_id": product['product_id'],
                        "category": product['category'],
                        "price": product['price'],
                        "keywords": product['keywords']
                    }
                )
                documents.append(doc)
            
            print(f"🛍️ 상품 문서 {len(documents)}개 처리 완료")
        
        return documents
    
    def search_documents(self, query: str, k: int = 3) -> List[Document]:
        """문서 검색"""
        if not self.retriever:
            self.initialize_vector_store()
        
        try:
            results = self.retriever.invoke(query)
            return results[:k]
        except Exception as e:
            print(f"❌ 문서 검색 실패: {e}")
            return []
    
    def generate_response(self, query: str, context_docs: List[Document]) -> str:
        """검색된 문서를 바탕으로 응답 생성"""
        # 컨텍스트 구성
        context = "\n\n".join([doc.page_content for doc in context_docs])

        # 체인 실행 (LangSmith 자동 트레이싱)
        chain = self.rag_prompt | self.llm

        try:
            # LangSmith에서 이 호출을 추적할 수 있도록 메타데이터 추가
            response = chain.invoke(
                {
                    "context": context,
                    "question": query
                },
                config={
                    "metadata": {
                        "component": "RAGProcessor",
                        "operation": "generate_response",
                        "context_docs_count": len(context_docs),
                        "query_length": len(query)
                    }
                }
            )
            return response.content
        except Exception as e:
            print(f"❌ 응답 생성 실패: {e}")
            return "죄송합니다. 현재 시스템에 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """쿼리 처리 (검색 + 응답 생성)"""
        # 문서 검색
        relevant_docs = self.search_documents(query)
        
        if not relevant_docs:
            return {
                "response": "죄송합니다. 관련된 정보를 찾을 수 없습니다. 고객센터(1588-1234)로 문의해주시면 더 자세한 도움을 받으실 수 있습니다.",
                "sources": [],
                "confidence": 0.0
            }
        
        # 응답 생성
        response = self.generate_response(query, relevant_docs)
        
        # 소스 정보 추출
        sources = []
        for doc in relevant_docs:
            source_info = {
                "source": doc.metadata.get("source", "unknown"),
                "content_preview": doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            }
            if doc.metadata.get("source") == "product":
                source_info["product_id"] = doc.metadata.get("product_id")
            elif doc.metadata.get("source") == "faq":
                source_info["faq_id"] = doc.metadata.get("faq_id")
                source_info["category"] = doc.metadata.get("category")
            
            sources.append(source_info)
        
        return {
            "response": response,
            "sources": sources,
            "confidence": len(relevant_docs) / 3.0  # 간단한 신뢰도 계산
        }

# 사용 예시
if __name__ == "__main__":
    rag = RAGProcessor()
    rag.initialize_vector_store()
    
    # 테스트 쿼리
    test_queries = [
        "배송비는 얼마인가요?",
        "무선 이어폰 사양이 어떻게 되나요?",
        "반품은 어떻게 하나요?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 질문: {query}")
        result = rag.process_query(query)
        print(f"💬 답변: {result['response']}")
        print(f"📊 신뢰도: {result['confidence']:.2f}")
        print(f"📚 소스 수: {len(result['sources'])}")
