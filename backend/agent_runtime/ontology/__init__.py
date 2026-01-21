"""Ontology Package - Knowledge Graph 관리 모듈"""

from backend.agent_runtime.ontology.data_loader import (
    LoadResult,
    LoadSummary,
    Neo4jDataLoader,
)
from backend.agent_runtime.ontology.kg_query import (
    Evidence,
    KnowledgeGraphQuery,
    QueryResult,
)
from backend.agent_runtime.ontology.validator import (
    PredicateConstraint,
    TripleValidator,
    ValidationError,
    ValidationErrorCode,
    ValidationResult,
)

__all__ = [
    # Validator
    "TripleValidator",
    "ValidationResult",
    "ValidationError",
    "ValidationErrorCode",
    "PredicateConstraint",
    # Data Loader
    "Neo4jDataLoader",
    "LoadResult",
    "LoadSummary",
    # KG Query
    "KnowledgeGraphQuery",
    "QueryResult",
    "Evidence",
]
