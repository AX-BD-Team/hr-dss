"""
Knowledge Graph 쿼리 테스트 스크립트
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

from backend.agent_runtime.ontology.kg_query import KnowledgeGraphQuery


def test_queries():
    """KG 쿼리 테스트"""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    print("=" * 60)
    print("       KG Query Test")
    print("=" * 60)
    print()

    try:
        kg = KnowledgeGraphQuery(uri, user, password)
        kg.connect()
        print("[OK] Neo4j 연결 성공")
        print()

        # 테스트 1: 조직별 가동률 조회
        print("-" * 60)
        print("TEST 1: 조직별 가동률 조회 (A-1 유스케이스)")
        print("-" * 60)
        try:
            result = kg.get_org_utilization()
            if result:
                for org in result[:3]:  # 상위 3개만 출력
                    print(f"  - {org.get('orgName', 'N/A')}: "
                          f"{org.get('utilization', 0):.1f}% "
                          f"({org.get('totalFTE', 0):.1f} FTE)")
            else:
                print("  (결과 없음 - 배치 데이터 확인 필요)")
        except Exception as e:
            print(f"  [ERROR] {e}")
        print()

        # 테스트 2: 프로젝트 정보 조회
        print("-" * 60)
        print("TEST 2: 프로젝트 목록 조회")
        print("-" * 60)
        try:
            with kg._driver.session() as session:
                result = session.run("""
                    MATCH (p:Project)
                    OPTIONAL MATCH (p)-[:MANAGED_BY]->(pm:Employee)
                    RETURN p.projectId AS id, p.name AS name,
                           p.status AS status, pm.name AS pm
                    ORDER BY p.startDate DESC
                    LIMIT 5
                """)
                records = list(result)
                for r in records:
                    print(f"  - [{r['status']}] {r['name']} (PM: {r['pm'] or 'N/A'})")
        except Exception as e:
            print(f"  [ERROR] {e}")
        print()

        # 테스트 3: 역량 보유 현황
        print("-" * 60)
        print("TEST 3: 역량별 보유 인원 현황")
        print("-" * 60)
        try:
            with kg._driver.session() as session:
                result = session.run("""
                    MATCH (e:Employee)-[r:HAS_COMPETENCY]->(c:Competency)
                    WITH c, count(e) AS holders, avg(r.level) AS avgLevel
                    ORDER BY holders DESC
                    LIMIT 5
                    RETURN c.name AS competency, holders, round(avgLevel, 1) AS avgLevel
                """)
                records = list(result)
                for r in records:
                    print(f"  - {r['competency']}: {r['holders']}명 (평균 Level {r['avgLevel']})")
        except Exception as e:
            print(f"  [ERROR] {e}")
        print()

        # 테스트 4: 기회 파이프라인
        print("-" * 60)
        print("TEST 4: 기회 파이프라인 현황 (B-1 유스케이스)")
        print("-" * 60)
        try:
            with kg._driver.session() as session:
                result = session.run("""
                    MATCH (o:Opportunity)
                    RETURN o.stage AS stage,
                           count(o) AS count,
                           sum(o.dealValue) AS totalValue
                    ORDER BY count DESC
                """)
                records = list(result)
                for r in records:
                    value = r['totalValue'] or 0
                    print(f"  - {r['stage']}: {r['count']}건 ({value/1e8:.1f}억원)")
        except Exception as e:
            print(f"  [ERROR] {e}")
        print()

        # 테스트 5: 의사결정 케이스 현황
        print("-" * 60)
        print("TEST 5: 의사결정 케이스 현황")
        print("-" * 60)
        try:
            with kg._driver.session() as session:
                result = session.run("""
                    MATCH (dc:DecisionCase)
                    OPTIONAL MATCH (dc)-[:HAS_OPTION]->(opt:Option)
                    WITH dc, count(opt) AS optionCount
                    RETURN dc.decisionCaseId AS id,
                           dc.type AS type,
                           dc.status AS status,
                           optionCount
                    ORDER BY dc.createdAt DESC
                    LIMIT 5
                """)
                records = list(result)
                for r in records:
                    print(f"  - [{r['status']}] {r['type']}: {r['optionCount']}개 옵션")
        except Exception as e:
            print(f"  [ERROR] {e}")
        print()

        kg.close()
        print("=" * 60)
        print("       테스트 완료")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"[ERROR] 연결 실패: {e}")
        return False


if __name__ == "__main__":
    success = test_queries()
    sys.exit(0 if success else 1)
