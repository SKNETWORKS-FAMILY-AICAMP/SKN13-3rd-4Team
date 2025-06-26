"""
배송 API 래퍼
실제 택배사 API 연동 및 배송 추적 정보 제공
"""
import requests
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

class DeliveryAPIWrapper:
    """배송 추적 API 래퍼 클래스"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.mock_data_path = self.project_root / "data" / "raw_docs" / "delivery_status.json"

        # 스마트택배 API 설정 (환경변수에서 로드)
        import os
        self.api_base_url = os.getenv("DELIVERY_API_BASE_URL", "https://info.sweettracker.co.kr")
        self.api_key = os.getenv("DELIVERY_API_KEY")

        # 스마트택배 택배사 코드 매핑
        self.carrier_codes = {
            "CJ대한통운": "04",
            "로젠택배": "06",
            "한진택배": "05",
            "우체국택배": "01",
            "롯데택배": "08",
            "대한통운": "04",
            "CJ": "04",
            "로젠": "06",
            "한진": "05",
            "우체국": "01",
            "롯데": "08"
        }
        
        # 상태 한글 매핑
        self.status_mapping = {
            "상품접수": "상품을 접수했습니다",
            "집화완료": "상품을 수거했습니다",
            "간선상차": "간선 운송을 시작했습니다",
            "간선하차": "간선 운송이 완료되었습니다",
            "배송출발": "배송을 시작했습니다",
            "배송중": "배송 중입니다",
            "배송완료": "배송이 완료되었습니다",
            "배송준비중": "배송을 준비 중입니다"
        }
    
    def _load_mock_data(self) -> List[Dict[str, Any]]:
        """목 데이터 로드"""
        try:
            with open(self.mock_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 목 데이터 로드 실패: {e}")
            return []
    
    def _get_carrier_code(self, carrier_name: str) -> Optional[str]:
        """택배사 이름을 코드로 변환"""
        return self.carrier_codes.get(carrier_name)
    
    def track_package_real_api(self, tracking_number: str, carrier: str) -> Optional[Dict[str, Any]]:
        """스마트택배 API를 사용한 실제 배송 추적"""
        try:
            print(f"🔍 배송 추적 시작: 운송장번호={tracking_number}, 택배사={carrier}")

            carrier_code = self._get_carrier_code(carrier)
            if not carrier_code:
                print(f"⚠️ 지원하지 않는 택배사: {carrier}")
                print(f"📋 지원 택배사: {list(self.carrier_codes.keys())}")
                return None

            if not self.api_key:
                print("⚠️ 스마트택배 API 키가 설정되지 않았습니다.")
                return None

            # 스마트택배 API 호출
            url = f"{self.api_base_url}/api/v1/trackingInfo"

            params = {
                't_key': self.api_key,
                't_code': carrier_code,
                't_invoice': tracking_number
            }

            print(f"🌐 API 호출: {url}")
            print(f"📋 파라미터: 택배사코드={carrier_code}, 운송장번호={tracking_number}")

            response = requests.get(url, params=params, timeout=10)
            print(f"📡 응답 상태: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"📦 응답 데이터: {data}")

                # 스마트택배 응답을 우리 형식으로 변환
                if data.get('result') == 'Y' and data.get('trackingDetails'):
                    print("✅ 배송 정보 조회 성공")
                    return self._convert_sweettracker_response(data, tracking_number, carrier)
                else:
                    error_msg = data.get('msg', '알 수 없는 오류')
                    error_code = data.get('code', '')
                    print(f"❌ 배송 정보 없음: {error_msg} (코드: {error_code})")

                    # API 제한 오류 처리
                    if '요청 건수를 초과' in error_msg or error_code == '105':
                        return {
                            'error_type': 'api_limit_exceeded',
                            'tracking_number': tracking_number,
                            'carrier': carrier,
                            'error_message': error_msg,
                            'user_message': f"죄송합니다. 배송 추적 API의 일일 요청 한도를 초과했습니다.\n\n📦 **운송장번호**: {tracking_number}\n🚚 **택배사**: {carrier}\n\n택배사 홈페이지나 고객센터(1588-0011)로 직접 문의하시거나, 내일 다시 시도해 주세요."
                        }

                    # 기타 오류
                    return {
                        'error_type': 'tracking_failed',
                        'tracking_number': tracking_number,
                        'carrier': carrier,
                        'error_message': error_msg,
                        'user_message': f"배송 정보를 조회할 수 없습니다.\n\n📦 **운송장번호**: {tracking_number}\n🚚 **택배사**: {carrier}\n\n운송장번호를 다시 확인하시거나 택배사에 직접 문의해 주세요."
                    }
            else:
                print(f"❌ API 호출 실패: {response.status_code}")
                print(f"📄 응답 내용: {response.text}")
                return None

        except requests.RequestException as e:
            print(f"❌ 네트워크 오류: {e}")
            return None
        except Exception as e:
            print(f"❌ API 호출 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _convert_sweettracker_response(self, data: Dict, tracking_number: str, carrier: str) -> Dict[str, Any]:
        """스마트택배 API 응답을 우리 형식으로 변환"""
        tracking_details = data.get('trackingDetails', [])

        if not tracking_details:
            return None

        # 최신 상태 정보
        latest = tracking_details[-1] if tracking_details else {}

        # 배송 이력 변환
        history = []
        for detail in tracking_details:
            history.append({
                'date': f"{detail.get('timeString', '')}",
                'status': detail.get('kind', ''),
                'location': detail.get('where', ''),
                'description': detail.get('telno', '')
            })

        # 배송 상태 매핑
        status_mapping = {
            '상품접수': '상품접수',
            '집화완료': '집화완료',
            '간선상차': '간선상차',
            '간선하차': '간선하차',
            '배송출발': '배송출발',
            '배송완료': '배송완료'
        }

        current_status = latest.get('kind', '알 수 없음')
        mapped_status = status_mapping.get(current_status, current_status)

        return {
            'tracking_number': tracking_number,
            'delivery_company': carrier,
            'status': mapped_status,
            'current_location': latest.get('where', ''),
            'delivery_date': latest.get('timeString', '') if mapped_status == '배송완료' else None,
            'estimated_delivery': None,  # 스마트택배에서 제공하지 않음
            'recipient': data.get('receiverName', ''),
            'tracking_history': history
        }
    
    def track_package_mock(self, tracking_number: str) -> Optional[Dict[str, Any]]:
        """목 데이터를 사용한 배송 추적"""
        mock_data = self._load_mock_data()

        for delivery in mock_data:
            if delivery['tracking_number'] == tracking_number:
                print(f"✅ Mock 데이터에서 배송 정보 발견: {tracking_number}")
                return delivery

        print(f"❌ Mock 데이터에서 운송장번호 {tracking_number}를 찾을 수 없습니다.")
        print(f"📋 사용 가능한 운송장번호: {[d['tracking_number'] for d in mock_data]}")
        return None
    
    def track_package(self, tracking_number: str, carrier: Optional[str] = None,
                     use_mock: bool = False) -> Optional[Dict[str, Any]]:
        """배송 추적 메인 함수"""
        if use_mock or not self.api_key:
            # 목 데이터 사용 (API 키가 없거나 명시적으로 목 데이터 사용 요청)
            print("📦 목 데이터를 사용하여 배송 정보를 조회합니다.")
            return self.track_package_mock(tracking_number)
        else:
            # 실제 API 사용
            if not carrier:
                # 택배사 정보가 없으면 목 데이터로 폴백
                print("⚠️ 택배사 정보가 없어 목 데이터를 사용합니다.")
                return self.track_package_mock(tracking_number)

            print(f"🌐 실제 API를 사용하여 {carrier} 배송 정보를 조회합니다.")
            result = self.track_package_real_api(tracking_number, carrier)

            # API 호출 실패 시 목 데이터로 폴백
            if not result:
                print("⚠️ 실제 API 조회 실패, 목 데이터를 사용합니다.")
                mock_result = self.track_package_mock(tracking_number)
                if mock_result:
                    return mock_result
                else:
                    # 목 데이터도 없으면 기본 메시지 반환
                    return {
                        "tracking_number": tracking_number,
                        "delivery_company": carrier or "알 수 없음",
                        "status": "조회불가",
                        "current_location": "",
                        "message": "배송 정보를 조회할 수 없습니다. 운송장번호를 확인해주세요."
                    }

            return result
    
    def get_delivery_status_by_order(self, order_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """주문 정보를 통한 배송 상태 조회"""
        tracking_number = order_info.get('tracking_number')
        carrier = order_info.get('delivery_company')
        
        if not tracking_number:
            return {
                "status": "배송준비중",
                "message": "아직 배송이 시작되지 않았습니다. 상품 준비가 완료되면 배송을 시작합니다.",
                "tracking_number": None,
                "carrier": carrier
            }
        
        # 실제 API 우선 사용, 실패 시 목 데이터로 폴백
        delivery_info = self.track_package(tracking_number, carrier, use_mock=False)

        if delivery_info:
            return delivery_info
        else:
            return {
                "status": "조회불가",
                "message": "배송 정보를 조회할 수 없습니다. 운송장번호를 확인해주세요.",
                "tracking_number": tracking_number,
                "carrier": carrier
            }
    
    def format_delivery_info(self, delivery_info: Dict[str, Any]) -> str:
        """배송 정보를 사용자 친화적 형태로 포맷팅"""
        if not delivery_info:
            return "배송 정보를 찾을 수 없습니다."

        # 오류 응답 처리
        if delivery_info.get('error_type'):
            return delivery_info.get('user_message', '배송 정보 조회 중 오류가 발생했습니다.')

        result = f"🚚 **배송 현황**\n"
        result += f"• 운송장번호: {delivery_info.get('tracking_number', 'N/A')}\n"
        result += f"• 택배사: {delivery_info.get('delivery_company', 'N/A')}\n"
        result += f"• 현재 상태: {delivery_info.get('status', 'N/A')}\n"
        
        if delivery_info.get('current_location'):
            result += f"• 현재 위치: {delivery_info['current_location']}\n"
        
        if delivery_info.get('recipient'):
            result += f"• 수취인: {delivery_info['recipient']}\n"
        
        # 배송 완료일 또는 예상 배송일
        if delivery_info.get('delivery_date'):
            result += f"• 배송 완료일: {delivery_info['delivery_date']}\n"
        elif delivery_info.get('estimated_delivery'):
            result += f"• 배송 예정일: {delivery_info['estimated_delivery']}\n"
        
        # 배송 이력
        if delivery_info.get('tracking_history'):
            result += f"\n📋 **배송 이력**\n"
            history = delivery_info['tracking_history']
            
            # 최신 순으로 정렬 (최대 5개)
            recent_history = sorted(history, key=lambda x: x['date'], reverse=True)[:5]
            
            for event in recent_history:
                date_str = event['date']
                status = event['status']
                location = event.get('location', '')
                
                # 상태 설명 추가
                status_desc = self.status_mapping.get(status, status)
                
                result += f"• {date_str} - {status_desc}"
                if location:
                    result += f" ({location})"
                result += "\n"
        
        return result
    
    def get_delivery_estimate(self, origin: str, destination: str, 
                            carrier: str = "CJ대한통운") -> Dict[str, Any]:
        """배송 예상 시간 계산 (간단한 로직)"""
        # 실제로는 택배사 API나 복잡한 로직을 사용
        # 여기서는 간단한 규칙 기반 예측
        
        base_days = 2  # 기본 배송일
        
        # 지역별 추가 일수
        if "제주" in destination or "울릉" in destination:
            base_days += 1
        elif any(region in destination for region in ["강원", "경북", "경남", "전북", "전남"]):
            base_days += 0.5
        
        # 택배사별 조정
        if carrier in ["CJ대한통운", "한진택배"]:
            base_days -= 0.5
        elif carrier in ["우체국택배"]:
            base_days += 0.5
        
        return {
            "estimated_days": max(1, int(base_days)),
            "description": f"약 {max(1, int(base_days))}일 소요 예상"
        }
    
    def check_delivery_availability(self, address: str) -> Dict[str, Any]:
        """배송 가능 지역 확인"""
        # 간단한 배송 가능 지역 체크
        unavailable_keywords = ["북한", "해외", "국외"]
        
        for keyword in unavailable_keywords:
            if keyword in address:
                return {
                    "available": False,
                    "reason": f"{keyword} 지역은 배송이 불가능합니다."
                }
        
        # 도서산간 지역 체크
        island_keywords = ["제주", "울릉", "독도", "백령", "연평"]
        is_island = any(keyword in address for keyword in island_keywords)
        
        return {
            "available": True,
            "is_island": is_island,
            "additional_fee": 3000 if is_island else 0,
            "note": "도서산간 지역 추가 배송비 3,000원" if is_island else None
        }

# 사용 예시
if __name__ == "__main__":
    delivery_api = DeliveryAPIWrapper()
    
    # 배송 추적 테스트
    print("🔍 배송 추적 테스트:")
    tracking_info = delivery_api.track_package("123456789012")
    if tracking_info:
        print(delivery_api.format_delivery_info(tracking_info))
    
    print("\n🔍 배송 예상 시간 테스트:")
    estimate = delivery_api.get_delivery_estimate("서울", "부산")
    print(f"배송 예상: {estimate['description']}")
    
    print("\n🔍 배송 가능 지역 테스트:")
    availability = delivery_api.check_delivery_availability("제주시 연동")
    print(f"배송 가능: {availability['available']}")
    if availability.get('note'):
        print(f"참고사항: {availability['note']}")
