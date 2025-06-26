"""
데이터베이스 초기화 및 샘플 데이터 삽입 스크립트
"""
import sqlite3
import json
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv가 설치되지 않았습니다. 환경변수를 직접 설정해주세요.")

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "sample_db" / "ecommerce.db"

def create_database():
    """데이터베이스 생성 및 스키마 적용"""
    # 디렉토리 생성
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # 스키마 파일 읽기
    schema_path = PROJECT_ROOT / "db" / "schema.sql"
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # 데이터베이스 연결 및 스키마 실행
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 스키마 실행
    cursor.executescript(schema_sql)
    conn.commit()
    
    print(f"✅ 데이터베이스 생성 완료: {DB_PATH}")
    return conn

def load_json_data(file_path):
    """JSON 파일 로드"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def insert_users(conn):
    """사용자 데이터 삽입"""
    users_data = load_json_data(DATA_DIR / "raw_docs" / "sample_users.json")
    
    cursor = conn.cursor()
    for user in users_data:
        cursor.execute("""
            INSERT OR REPLACE INTO users 
            (user_id, username, email, phone, address, member_grade, join_date, total_orders, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user['user_id'], user['username'], user['email'], user['phone'],
            user['address'], user['member_grade'], user['join_date'],
            user['total_orders'], user['total_amount']
        ))
    
    conn.commit()
    print(f"✅ 사용자 데이터 {len(users_data)}건 삽입 완료")

def insert_products(conn):
    """상품 데이터 삽입"""
    products_data = load_json_data(DATA_DIR / "raw_docs" / "product_info.json")
    
    cursor = conn.cursor()
    for product in products_data:
        cursor.execute("""
            INSERT OR REPLACE INTO products 
            (product_id, name, category, description, specifications, features, price, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product['product_id'], product['name'], product['category'],
            product['description'], json.dumps(product['specifications'], ensure_ascii=False),
            json.dumps(product['features'], ensure_ascii=False), product['price'],
            json.dumps(product['keywords'], ensure_ascii=False)
        ))
    
    conn.commit()
    print(f"✅ 상품 데이터 {len(products_data)}건 삽입 완료")

def insert_orders(conn):
    """주문 데이터 삽입"""
    orders_data = load_json_data(DATA_DIR / "raw_docs" / "sample_orders.json")
    
    cursor = conn.cursor()
    for order in orders_data:
        # 주문 정보 삽입
        cursor.execute("""
            INSERT OR REPLACE INTO orders 
            (order_id, user_id, order_date, status, tracking_number, delivery_company, total_amount, shipping_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order['order_id'], order['user_id'], order['order_date'],
            order['status'], order['tracking_number'], order['delivery_company'],
            order['total_amount'], order['shipping_address']
        ))
        
        # 주문 상품 정보 삽입
        for item in order['items']:
            cursor.execute("""
                INSERT OR REPLACE INTO order_items 
                (order_id, product_id, product_name, quantity, price)
                VALUES (?, ?, ?, ?, ?)
            """, (
                order['order_id'], item['product_id'], item['product_name'],
                item['quantity'], item['price']
            ))
    
    conn.commit()
    print(f"✅ 주문 데이터 {len(orders_data)}건 삽입 완료")

def insert_faq(conn):
    """FAQ 데이터 삽입"""
    faq_data = load_json_data(DATA_DIR / "raw_docs" / "faq_data.json")
    
    cursor = conn.cursor()
    for faq in faq_data:
        cursor.execute("""
            INSERT OR REPLACE INTO faq 
            (id, category, question, answer, keywords)
            VALUES (?, ?, ?, ?, ?)
        """, (
            faq['id'], faq['category'], faq['question'],
            faq['answer'], json.dumps(faq['keywords'], ensure_ascii=False)
        ))
    
    conn.commit()
    print(f"✅ FAQ 데이터 {len(faq_data)}건 삽입 완료")

def insert_delivery_info(conn):
    """배송 정보 데이터 삽입"""
    delivery_data = load_json_data(DATA_DIR / "raw_docs" / "delivery_status.json")
    
    cursor = conn.cursor()
    for delivery in delivery_data:
        cursor.execute("""
            INSERT OR REPLACE INTO delivery_info 
            (tracking_number, delivery_company, status, current_location, delivery_date, estimated_delivery, recipient, tracking_history)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            delivery['tracking_number'], delivery['delivery_company'], delivery['status'],
            delivery['current_location'], delivery.get('delivery_date'), 
            delivery.get('estimated_delivery'), delivery['recipient'],
            json.dumps(delivery['tracking_history'], ensure_ascii=False)
        ))
    
    conn.commit()
    print(f"✅ 배송 정보 데이터 {len(delivery_data)}건 삽입 완료")

def main():
    """메인 실행 함수"""
    print("🚀 데이터베이스 초기화 시작...")
    
    # 데이터베이스 생성
    conn = create_database()
    
    try:
        # 샘플 데이터 삽입
        insert_users(conn)
        insert_products(conn)
        insert_orders(conn)
        insert_faq(conn)
        insert_delivery_info(conn)
        
        print("🎉 데이터베이스 초기화 완료!")
        
        # 데이터 확인
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM faq")
        faq_count = cursor.fetchone()[0]
        
        print(f"\n📊 데이터 현황:")
        print(f"   - 사용자: {user_count}명")
        print(f"   - 상품: {product_count}개")
        print(f"   - 주문: {order_count}건")
        print(f"   - FAQ: {faq_count}개")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
