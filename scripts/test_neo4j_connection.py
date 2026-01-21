"""
Neo4j 연결 테스트 스크립트
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(project_root / ".env")


def test_connection():
    """Neo4j 연결 테스트"""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("[ERROR] neo4j 패키지가 설치되지 않았습니다.")
        print("   설치: pip install neo4j")
        return False

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    print("Neo4j 연결 테스트")
    print(f"  URI: {uri}")
    print(f"  User: {user}")
    print()

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print("[OK] Neo4j 연결 성공!")

        # 기본 정보 조회
        with driver.session() as session:
            result = session.run("CALL dbms.components() YIELD name, versions RETURN name, versions")
            for record in result:
                print(f"  - {record['name']}: {record['versions']}")

            # 노드/관계 수 조회
            result = session.run("MATCH (n) RETURN count(n) AS nodes")
            nodes = result.single()["nodes"]

            result = session.run("MATCH ()-[r]->() RETURN count(r) AS rels")
            rels = result.single()["rels"]

            print(f"\n현재 데이터베이스 상태:")
            print(f"  - 노드 수: {nodes}")
            print(f"  - 관계 수: {rels}")

        driver.close()
        return True

    except Exception as e:
        print(f"[ERROR] Neo4j 연결 실패: {e}")
        print()
        print("해결 방법:")
        print("  1. Neo4j Desktop이 실행 중인지 확인")
        print("  2. .env 파일의 NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD 확인")
        print("  3. Docker: docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
