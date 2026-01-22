"""Knowledge Graph API 라우터"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.api.dependencies import Neo4jService

router = APIRouter()


class GraphQuery(BaseModel):
    """그래프 쿼리"""

    cypher: str = Field(..., description="Cypher 쿼리")
    params: dict[str, Any] | None = Field(default=None, description="쿼리 파라미터")


class GraphQueryResult(BaseModel):
    """그래프 쿼리 결과"""

    success: bool
    data: list[dict[str, Any]]
    meta: dict[str, Any] | None = None


# 위험한 Cypher 키워드
DANGEROUS_KEYWORDS = ["DELETE", "REMOVE", "DROP", "CREATE INDEX", "CREATE CONSTRAINT", "DETACH"]


def validate_query(cypher: str) -> None:
    """쿼리 보안 검증"""
    query_upper = cypher.upper()
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in query_upper:
            raise HTTPException(
                status_code=400,
                detail=f"위험한 쿼리입니다: {keyword} 명령어는 허용되지 않습니다",
            )


@router.post("/query", response_model=GraphQueryResult)
async def execute_query(request: GraphQuery):
    """
    Cypher 쿼리 실행

    Neo4j Knowledge Graph에 Cypher 쿼리를 실행합니다.
    """
    start_time = datetime.now()

    # 보안 검증
    validate_query(request.cypher)

    try:
        data = await Neo4jService.execute_query(request.cypher, request.params)
        execution_time = (datetime.now() - start_time).total_seconds() * 1000

        return GraphQueryResult(
            success=True,
            data=data,
            meta={"execution_time_ms": round(execution_time, 2)},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/nodes")
async def list_node_types():
    """노드 타입 목록"""
    try:
        stats = await Neo4jService.get_stats()
        labels = stats.get("labels", {})

        # 라벨 설명 매핑
        label_descriptions = {
            "Employee": "직원",
            "Team": "팀",
            "Division": "본부",
            "OrgUnit": "조직",
            "Project": "프로젝트",
            "Skill": "스킬",
            "Competency": "역량",
            "Decision": "의사결정",
            "Option": "옵션",
            "Evidence": "근거",
            "Opportunity": "기회",
            "ResourceDemand": "리소스 수요",
            "TimeBucket": "기간",
        }

        node_types = [
            {
                "label": label,
                "count": count,
                "description": label_descriptions.get(label, label),
            }
            for label, count in labels.items()
        ]

        return {"node_types": node_types}
    except Exception:
        # 연결 실패 시 기본값 반환
        return {
            "node_types": [
                {"label": "Employee", "count": 0, "description": "직원"},
                {"label": "Team", "count": 0, "description": "팀"},
                {"label": "Division", "count": 0, "description": "본부"},
                {"label": "Project", "count": 0, "description": "프로젝트"},
                {"label": "Skill", "count": 0, "description": "스킬"},
                {"label": "Decision", "count": 0, "description": "의사결정"},
                {"label": "Option", "count": 0, "description": "옵션"},
                {"label": "Evidence", "count": 0, "description": "근거"},
            ]
        }


@router.get("/nodes/{label}")
async def get_nodes_by_label(
    label: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """특정 라벨의 노드 목록 조회"""
    try:
        # 먼저 전체 개수 조회
        count_query = f"MATCH (n:`{label}`) RETURN count(n) as total"
        count_result = await Neo4jService.execute_query(count_query)
        total = count_result[0]["total"] if count_result else 0

        # 노드 목록 조회
        nodes_query = f"""
        MATCH (n:`{label}`)
        RETURN properties(n) as properties
        SKIP $offset
        LIMIT $limit
        """
        nodes_result = await Neo4jService.execute_query(
            nodes_query, {"offset": offset, "limit": limit}
        )

        nodes = [record["properties"] for record in nodes_result]

        return {
            "label": label,
            "total": total,
            "limit": limit,
            "offset": offset,
            "nodes": nodes,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/schema")
async def get_schema():
    """그래프 스키마 조회"""
    try:
        # 노드 라벨 및 속성 조회
        labels_query = """
        CALL db.schema.nodeTypeProperties()
        YIELD nodeType, propertyName
        RETURN nodeType, collect(propertyName) as properties
        """
        labels_result = await Neo4jService.execute_query(labels_query)

        nodes = []
        for record in labels_result:
            node_type = record["nodeType"]
            # `:`를 제거하고 라벨 이름 추출
            label = node_type.replace(":`", "").replace("`", "")
            nodes.append({
                "label": label,
                "properties": record["properties"],
            })

        # 관계 타입 조회
        rel_query = """
        CALL db.schema.relTypeProperties()
        YIELD relType
        RETURN DISTINCT relType
        """
        rel_result = await Neo4jService.execute_query(rel_query)
        rel_types = [r["relType"].replace(":`", "").replace("`", "") for r in rel_result]

        # 관계 정보 조회 (from, to)
        relationships = []
        for rel_type in rel_types:
            rel_info_query = f"""
            MATCH (a)-[r:`{rel_type}`]->(b)
            RETURN DISTINCT labels(a)[0] as from_label, labels(b)[0] as to_label
            LIMIT 1
            """
            try:
                rel_info = await Neo4jService.execute_query(rel_info_query)
                if rel_info:
                    relationships.append({
                        "type": rel_type,
                        "from": rel_info[0].get("from_label", "Unknown"),
                        "to": rel_info[0].get("to_label", "Unknown"),
                    })
            except Exception:
                relationships.append({"type": rel_type, "from": "Unknown", "to": "Unknown"})

        return {"nodes": nodes, "relationships": relationships}
    except Exception:
        # 연결 실패 시 기본 스키마 반환
        return {
            "nodes": [
                {"label": "Employee", "properties": ["id", "name", "level", "team_id"]},
                {"label": "Team", "properties": ["id", "name", "division_id"]},
                {"label": "Division", "properties": ["id", "name"]},
                {"label": "Project", "properties": ["id", "name", "status", "start_date", "end_date"]},
                {"label": "Skill", "properties": ["id", "name", "category"]},
                {"label": "Decision", "properties": ["id", "title", "status", "question"]},
                {"label": "Option", "properties": ["id", "name", "type", "success_probability"]},
                {"label": "Evidence", "properties": ["id", "type", "content", "confidence"]},
            ],
            "relationships": [
                {"type": "BELONGS_TO", "from": "Employee", "to": "Team"},
                {"type": "BELONGS_TO", "from": "Team", "to": "Division"},
                {"type": "MANAGES", "from": "Employee", "to": "Team"},
                {"type": "ASSIGNED_TO", "from": "Employee", "to": "Project"},
                {"type": "HAS_SKILL", "from": "Employee", "to": "Skill"},
                {"type": "REQUIRES_SKILL", "from": "Project", "to": "Skill"},
                {"type": "HAS_OPTION", "from": "Decision", "to": "Option"},
                {"type": "SUPPORTS", "from": "Evidence", "to": "Option"},
                {"type": "CONTRADICTS", "from": "Evidence", "to": "Option"},
            ],
        }


@router.get("/stats")
async def get_stats():
    """그래프 통계"""
    try:
        stats = await Neo4jService.get_stats()
        return stats
    except Exception:
        return {
            "node_count": 0,
            "relationship_count": 0,
            "labels": {},
            "relationship_types": {},
        }


@router.get("/search")
async def search_graph(
    q: str = Query(..., description="검색어"),
    labels: list[str] | None = Query(None, description="검색할 노드 라벨"),
    limit: int = Query(20, ge=1, le=100),
):
    """그래프 검색"""
    try:
        results = await Neo4jService.search(q, labels, limit)
        return {
            "query": q,
            "labels": labels,
            "total": len(results),
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
