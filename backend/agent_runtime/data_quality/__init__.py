# HR DSS - Data Quality Module
"""데이터 품질 평가 및 Data Readiness Scorecard 모듈"""

from .scorecard import DataReadinessScorecard, ScorecardResult

__all__ = ["DataReadinessScorecard", "ScorecardResult"]
