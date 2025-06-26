"""
통합 RAG 기반 쇼핑몰 챗봇 시스템
- OpenAI GPT-4 기반 자연어 처리
- Chroma Vector DB를 통한 RAG 구현
- 사용자별 개인화 서비스
- LangSmith 모니터링 지원
"""
import streamlit as st
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
    from core.agent_processor import ToolCallingAgentProcessor  # Tool Calling Agent 프로세서

except ImportError as e:
    st.error(f"❌ 필요한 모듈을 임포트할 수 없습니다: {e}")
    st.stop()

class UnifiedChatbotSystem:
    """통합 챗봇 시스템"""
    
    def __init__(self):
        self.project_root = project_root
        # Tool Calling Agent 프로세서 초기화 (지연 로딩)
        self._agent_processor = None

    @property
    def agent_processor(self):
        """Agent Processor 지연 로딩"""
        if self._agent_processor is None:
            self._agent_processor = ToolCallingAgentProcessor()
        return self._agent_processor

    def process_query(self, user_input: str, current_user_id: Optional[int] = None,
                     session_id: Optional[str] = None, use_batch: bool = True) -> Dict[str, Any]:
        """Tool Calling Agent를 사용한 쿼리 처리"""
        start_time = time.time()

        try:
            # 복합 질문 키워드 감지
            complex_keywords = ['그리고', '그리고', '또', '언제', '어디', '뭐', '누구', '어떻게']
            is_likely_complex = any(keyword in user_input for keyword in complex_keywords) and len(user_input.split()) > 5

            if use_batch and is_likely_complex and hasattr(self.agent_processor, 'process_batch_query'):
                # Batch 처리 시도
                try:
                    agent_result = self.agent_processor.process_batch_query(
                        user_input,
                        str(current_user_id) if current_user_id else None,
                        session_id
                    )
                except Exception as e:
                    print(f"❌ Batch 처리 실패, 일반 처리로 폴백: {e}")
                    agent_result = self.agent_processor.process_query(
                        user_input,
                        str(current_user_id) if current_user_id else None,
                        session_id
                    )
            else:
                # 일반 Tool Calling Agent 처리
                agent_result = self.agent_processor.process_query(
                    user_input,
                    str(current_user_id) if current_user_id else None,
                    session_id
                )

            return {
                'response': agent_result['response'],
                'method': agent_result.get('method', 'tool_calling_agent'),
                'response_time': time.time() - start_time,
                'tools_used': agent_result.get('tools_used', []),
                'tasks_executed': agent_result.get('tasks_executed', 0),
                'success': agent_result.get('success', True)
            }

        except Exception as e:
            return {
                'response': f"죄송합니다. 시스템 오류가 발생했습니다: {str(e)}",
                'method': 'error',
                'response_time': time.time() - start_time
            }
    


def main():
    """Streamlit 메인 함수"""
    st.set_page_config(
        page_title="통합 쇼핑몰 챗봇",
        page_icon="🤖",
        layout="wide"
    )

    st.title("🤖 통합 RAG 기반 쇼핑몰 챗봇")
    st.markdown("**OpenAI GPT-4 + Vector DB + 개인화 서비스**")

    # 챗봇 시스템 초기화 (캐시 클리어를 위해 강제 재초기화)
    if 'unified_chatbot' not in st.session_state or st.button("🔄 시스템 재시작"):
        with st.spinner("🚀 통합 챗봇 시스템을 초기화하는 중..."):
            st.session_state.unified_chatbot = UnifiedChatbotSystem()
            if 'unified_chatbot' in st.session_state:
                st.success("✅ 시스템이 성공적으로 재시작되었습니다!")

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

        st.divider()

        # 사용자 로그인
        st.header("👤 사용자 로그인")

        # 데이터베이스에서 사용자 목록 조회
        try:
            from core.db_query_engine import DatabaseQueryEngine
            db_engine = DatabaseQueryEngine()
            users = db_engine.get_all_users()
            user_options = ["로그인하지 않음"] + [f"{user['username']} ({user['email']})" for user in users]
            selected_user = st.selectbox("테스트용 계정 선택:", user_options, index=0)

            # 사용자 정보 업데이트
            if selected_user == "로그인하지 않음":
                st.session_state.current_user_id = None
                current_user = None
            else:
                current_user = None
                for user in users:
                    if f"{user['username']} ({user['email']})" == selected_user:
                        st.session_state.current_user_id = user['user_id']
                        current_user = user
                        break
        except Exception as e:
            st.error(f"사용자 목록 조회 실패: {e}")
            st.session_state.current_user_id = None
            current_user = None

        # 로그인된 사용자 정보 표시
        if current_user:
            st.success(f"✅ {current_user['username']}님 로그인됨")
            # 데이터베이스에서 사용자 정보 조회
            try:
                from core.db_query_engine import DatabaseQueryEngine
                db_engine = DatabaseQueryEngine()
                user_info = db_engine.get_user_by_id(current_user['user_id'])
                if user_info:
                    st.info(f"📦 총 주문: {user_info.get('total_orders', 0)}건")
                    st.write(f"**회원등급:** {user_info.get('member_grade', 'BRONZE')}")
            except Exception as e:
                st.warning(f"사용자 정보 조회 실패: {e}")
        else:
            st.info("로그인하지 않은 상태입니다")

        st.divider()

        # 시스템 정보
        st.header("📊 시스템 정보")
        st.markdown(f"""
        **처리 모드:** 🚀 Tool Calling Agent (LLM 자동 도구 선택)

        **LLM 모델:** GPT-4o-mini (비용 효율적)

        **세션 ID:** `{st.session_state.session_id[:8]}...`
        """)

        if st.button("🔄 대화 기록 초기화"):
            st.session_state.chat_history = []
            # Agent 모드의 대화 기록도 초기화
            if hasattr(chatbot, '_agent_processor') and chatbot._agent_processor:
                chatbot._agent_processor.clear_chat_history()
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
                st.caption("🚀 Tool Calling Agent")

            # 사용된 도구 표시
            if chat.get('tools_used'):
                st.caption(f"🔧 사용된 도구: {', '.join(chat['tools_used'])}")

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
                    st.session_state.session_id
                )

            st.write(result['response'])

            # 메타 정보 표시
            if result.get('method') == 'batch_processing':
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.caption(f"⏱️ {result['response_time']:.2f}초")
                with col2:
                    st.caption(f"🔧 {result['method']}")
                with col3:
                    st.caption(f"📦 {result.get('tasks_executed', 0)}개 작업")
                with col4:
                    st.caption("🚀 Batch Processing")
            else:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"⏱️ {result['response_time']:.2f}초")
                with col2:
                    st.caption(f"🔧 {result['method']}")
                with col3:
                    st.caption("🚀 Tool Calling Agent")

            # 사용된 도구 표시
            if result.get('tools_used'):
                st.caption(f"🔧 사용된 도구: {', '.join(result['tools_used'])}")

            # Batch 처리 상세 정보 표시
            if result.get('method') == 'batch_processing' and result.get('tasks_executed', 0) > 0:
                with st.expander("📊 배치 처리 상세 정보"):
                    st.write(f"**실행된 작업 수**: {result.get('tasks_executed', 0)}개")
                    if result.get('batch_results'):
                        for _, task_result in result['batch_results'].items():
                            if task_result['success']:
                                st.success(f"✅ {task_result['description']}")
                            else:
                                st.error(f"❌ {task_result['description']}: {task_result.get('error', '알 수 없는 오류')}")

            # 대화 기록에 추가
            st.session_state.chat_history.append({
                "user": user_input,
                "bot": result['response'],
                "response_time": result['response_time'],
                "method": result['method'],
                "tools_used": result.get('tools_used', [])
            })

if __name__ == "__main__":
    main()
