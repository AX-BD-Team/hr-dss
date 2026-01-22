"""
HR DSS - Impact Simulator Agent

대안별 영향도를 시뮬레이션하는 에이전트
As-Is vs To-Be 비교 분석
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """측정 지표 유형"""

    UTILIZATION = "UTILIZATION"
    HEADCOUNT = "HEADCOUNT"
    COST = "COST"
    REVENUE = "REVENUE"
    MARGIN = "MARGIN"
    RISK = "RISK"
    TIME = "TIME"
    QUALITY = "QUALITY"


@dataclass
class MetricValue:
    """지표 값"""

    metric_type: MetricType
    name: str
    as_is_value: float
    to_be_value: float
    unit: str
    change_percent: float = 0.0
    change_direction: str = "NEUTRAL"  # POSITIVE, NEGATIVE, NEUTRAL

    def __post_init__(self):
        if self.as_is_value != 0:
            self.change_percent = (self.to_be_value - self.as_is_value) / self.as_is_value * 100
        else:
            self.change_percent = 100 if self.to_be_value > 0 else 0

        # 지표별 방향 결정
        positive_metrics = {MetricType.REVENUE, MetricType.MARGIN, MetricType.QUALITY}
        negative_metrics = {MetricType.COST, MetricType.RISK, MetricType.TIME}

        if self.change_percent > 0:
            if self.metric_type in positive_metrics:
                self.change_direction = "POSITIVE"
            elif self.metric_type in negative_metrics:
                self.change_direction = "NEGATIVE"
        elif self.change_percent < 0:
            if self.metric_type in positive_metrics:
                self.change_direction = "NEGATIVE"
            elif self.metric_type in negative_metrics:
                self.change_direction = "POSITIVE"


@dataclass
class TimeSeriesPoint:
    """시계열 데이터 포인트"""

    period: str
    as_is_value: float
    to_be_value: float


@dataclass
class ImpactAnalysis:
    """영향도 분석 결과"""

    option_id: str
    option_name: str
    metrics: list[MetricValue]
    time_series: dict[str, list[TimeSeriesPoint]] = field(default_factory=dict)
    overall_impact_score: float = 0.0
    confidence_interval: tuple[float, float] = (0.0, 0.0)
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)


@dataclass
class ScenarioComparison:
    """시나리오 비교 결과"""

    query_type: str
    baseline: dict[str, Any]
    analyses: list[ImpactAnalysis]
    comparison_summary: dict[str, Any]
    best_option_id: str
    best_option_reason: str
    simulated_at: datetime = field(default_factory=datetime.now)


class ImpactSimulatorAgent:
    """영향도 시뮬레이션 에이전트"""

    # 지표별 가중치
    METRIC_WEIGHTS = {
        MetricType.UTILIZATION: 0.20,
        MetricType.COST: 0.15,
        MetricType.REVENUE: 0.20,
        MetricType.MARGIN: 0.15,
        MetricType.RISK: 0.15,
        MetricType.TIME: 0.10,
        MetricType.QUALITY: 0.05,
    }

    def __init__(self, kg_client: Any = None):
        """
        Args:
            kg_client: Knowledge Graph 클라이언트
        """
        self.kg_client = kg_client

    def simulate(
        self,
        query_type: str,
        options: list[dict],
        baseline: dict[str, Any],
        horizon_weeks: int = 12,
    ) -> ScenarioComparison:
        """
        대안별 영향도 시뮬레이션

        Args:
            query_type: 질문 유형
            options: 대안 목록
            baseline: 현재 상태 (As-Is)
            horizon_weeks: 시뮬레이션 기간 (주)

        Returns:
            ScenarioComparison: 비교 분석 결과
        """
        analyses = []

        for option in options:
            analysis = self._simulate_option(query_type, option, baseline, horizon_weeks)
            analyses.append(analysis)

        # 최적 옵션 결정
        best_option_id, best_reason = self._determine_best_option(analyses)

        # 비교 요약 생성
        comparison_summary = self._generate_comparison_summary(analyses)

        return ScenarioComparison(
            query_type=query_type,
            baseline=baseline,
            analyses=analyses,
            comparison_summary=comparison_summary,
            best_option_id=best_option_id,
            best_option_reason=best_reason,
        )

    def _simulate_option(
        self, query_type: str, option: dict, baseline: dict[str, Any], horizon_weeks: int
    ) -> ImpactAnalysis:
        """단일 대안 시뮬레이션"""

        option_id = option.get("option_id", "UNKNOWN")
        option_name = option.get("name", "Unknown Option")
        option_type = option.get("option_type", "BALANCED")

        # 기본 지표 계산
        metrics = []
        time_series = {}

        if query_type == "CAPACITY":
            metrics, time_series = self._simulate_capacity_impact(option, baseline, horizon_weeks)
        elif query_type == "GO_NOGO":
            metrics, time_series = self._simulate_gonogo_impact(option, baseline, horizon_weeks)
        elif query_type == "HEADCOUNT":
            metrics, time_series = self._simulate_headcount_impact(option, baseline, horizon_weeks)
        elif query_type == "COMPETENCY_GAP":
            metrics, time_series = self._simulate_competency_impact(option, baseline, horizon_weeks)
        else:
            metrics = self._simulate_generic_impact(option, baseline)

        # 종합 점수 계산
        overall_score = self._calculate_overall_score(metrics)

        # 신뢰구간 계산
        confidence = self._calculate_confidence_interval(metrics, option_type)

        # 가정 및 리스크 추출
        assumptions = option.get("prerequisites", [])
        risks = option.get("trade_offs", [])

        return ImpactAnalysis(
            option_id=option_id,
            option_name=option_name,
            metrics=metrics,
            time_series=time_series,
            overall_impact_score=overall_score,
            confidence_interval=confidence,
            assumptions=assumptions,
            risks=risks,
        )

    def _simulate_capacity_impact(
        self, option: dict, baseline: dict[str, Any], horizon_weeks: int
    ) -> tuple[list[MetricValue], dict]:
        """Capacity 영향도 시뮬레이션"""

        as_is_util = baseline.get("utilization", 0.85)
        _as_is_headcount = baseline.get("headcount", 10)  # 향후 확장용
        _gap_fte = baseline.get("gap_fte", 2)  # 향후 확장용

        option_type = option.get("option_type", "BALANCED")

        # 옵션별 To-Be 계산
        if option_type == "CONSERVATIVE":
            # 내부 재배치: 중간 정도의 개선
            to_be_util = as_is_util * 0.95  # 5% 개선
            to_be_cost_factor = 1.05
            to_be_risk = 0.2
        elif option_type == "AGGRESSIVE":
            # 정규직 채용: 큰 개선이지만 시간 소요
            to_be_util = as_is_util * 0.85  # 15% 개선
            to_be_cost_factor = 1.3
            to_be_risk = 0.5
        else:  # BALANCED
            # 외주 활용: 적절한 개선
            to_be_util = as_is_util * 0.90  # 10% 개선
            to_be_cost_factor = 1.15
            to_be_risk = 0.35

        metrics = [
            MetricValue(
                metric_type=MetricType.UTILIZATION,
                name="가동률",
                as_is_value=as_is_util * 100,
                to_be_value=to_be_util * 100,
                unit="%",
            ),
            MetricValue(
                metric_type=MetricType.COST,
                name="비용",
                as_is_value=baseline.get("cost", 100000000),
                to_be_value=baseline.get("cost", 100000000) * to_be_cost_factor,
                unit="원",
            ),
            MetricValue(
                metric_type=MetricType.RISK,
                name="리스크",
                as_is_value=baseline.get("risk", 0.3) * 100,
                to_be_value=to_be_risk * 100,
                unit="%",
            ),
        ]

        # 시계열 데이터 생성
        time_series = {
            "utilization": self._generate_time_series(
                as_is_util * 100, to_be_util * 100, horizon_weeks, option_type
            )
        }

        return metrics, time_series

    def _simulate_gonogo_impact(
        self, option: dict, baseline: dict[str, Any], horizon_weeks: int
    ) -> tuple[list[MetricValue], dict]:
        """Go/No-go 영향도 시뮬레이션"""

        deal_value = baseline.get("deal_value", 500000000)
        current_util = baseline.get("utilization", 0.8)
        current_margin = baseline.get("margin", 0.15)

        option_type = option.get("option_type", "BALANCED")

        if option_type == "CONSERVATIVE":  # No-Go
            to_be_revenue = 0
            to_be_margin = current_margin
            to_be_util = current_util
            to_be_risk = 0.1
        elif option_type == "AGGRESSIVE":  # Full Go
            to_be_revenue = deal_value
            to_be_margin = current_margin * 0.9  # 마진 약간 감소
            to_be_util = min(current_util + 0.15, 1.0)
            to_be_risk = 0.6
        else:  # Conditional Go
            to_be_revenue = deal_value * 0.8
            to_be_margin = current_margin * 0.95
            to_be_util = min(current_util + 0.10, 0.95)
            to_be_risk = 0.35

        metrics = [
            MetricValue(
                metric_type=MetricType.REVENUE,
                name="매출",
                as_is_value=0,
                to_be_value=to_be_revenue,
                unit="원",
            ),
            MetricValue(
                metric_type=MetricType.MARGIN,
                name="마진율",
                as_is_value=current_margin * 100,
                to_be_value=to_be_margin * 100,
                unit="%",
            ),
            MetricValue(
                metric_type=MetricType.UTILIZATION,
                name="가동률",
                as_is_value=current_util * 100,
                to_be_value=to_be_util * 100,
                unit="%",
            ),
            MetricValue(
                metric_type=MetricType.RISK,
                name="리스크",
                as_is_value=baseline.get("risk", 0.2) * 100,
                to_be_value=to_be_risk * 100,
                unit="%",
            ),
        ]

        time_series = {
            "revenue": self._generate_time_series(
                0, to_be_revenue / horizon_weeks, horizon_weeks, option_type
            )
        }

        return metrics, time_series

    def _simulate_headcount_impact(
        self, option: dict, baseline: dict[str, Any], horizon_weeks: int
    ) -> tuple[list[MetricValue], dict]:
        """증원 영향도 시뮬레이션"""

        current_hc = baseline.get("headcount", 10)
        requested_hc = baseline.get("requested_headcount", 2)
        current_util = baseline.get("utilization", 0.9)
        current_cost = baseline.get("cost", 500000000)

        option_type = option.get("option_type", "BALANCED")

        if option_type == "CONSERVATIVE":  # 불승인
            to_be_hc = current_hc
            to_be_util = current_util * 1.02  # 효율화로 약간 개선
            to_be_cost = current_cost * 1.02
        elif option_type == "AGGRESSIVE":  # 전체 승인
            to_be_hc = current_hc + requested_hc
            to_be_util = current_util * 0.75  # 큰 개선
            to_be_cost = current_cost * 1.4
        else:  # 부분 승인
            to_be_hc = current_hc + requested_hc // 2
            to_be_util = current_util * 0.85
            to_be_cost = current_cost * 1.2

        metrics = [
            MetricValue(
                metric_type=MetricType.HEADCOUNT,
                name="인원",
                as_is_value=current_hc,
                to_be_value=to_be_hc,
                unit="명",
            ),
            MetricValue(
                metric_type=MetricType.UTILIZATION,
                name="가동률",
                as_is_value=current_util * 100,
                to_be_value=to_be_util * 100,
                unit="%",
            ),
            MetricValue(
                metric_type=MetricType.COST,
                name="인건비",
                as_is_value=current_cost,
                to_be_value=to_be_cost,
                unit="원",
            ),
        ]

        time_series = {
            "headcount": self._generate_time_series(
                current_hc, to_be_hc, horizon_weeks, option_type
            )
        }

        return metrics, time_series

    def _simulate_competency_impact(
        self, option: dict, baseline: dict[str, Any], horizon_weeks: int
    ) -> tuple[list[MetricValue], dict]:
        """역량 갭 영향도 시뮬레이션"""

        current_gap = baseline.get("gap_count", 5)
        current_coverage = baseline.get("coverage", 0.6)

        option_type = option.get("option_type", "BALANCED")

        if option_type == "CONSERVATIVE":  # 내부 육성
            _to_be_gap = current_gap * 0.7  # 향후 확장용
            to_be_coverage = current_coverage * 1.2
            to_be_cost = 20000000
            to_be_time = 52  # 주
        elif option_type == "AGGRESSIVE":  # 팀 빌딩
            _to_be_gap = current_gap * 0.2  # 향후 확장용
            to_be_coverage = current_coverage * 1.8
            to_be_cost = 200000000
            to_be_time = 26
        else:  # 혼합
            _to_be_gap = current_gap * 0.5  # 향후 확장용
            to_be_coverage = current_coverage * 1.4
            to_be_cost = 80000000
            to_be_time = 20

        metrics = [
            MetricValue(
                metric_type=MetricType.QUALITY,
                name="역량 커버리지",
                as_is_value=current_coverage * 100,
                to_be_value=min(to_be_coverage * 100, 100),
                unit="%",
            ),
            MetricValue(
                metric_type=MetricType.COST,
                name="투자 비용",
                as_is_value=0,
                to_be_value=to_be_cost,
                unit="원",
            ),
            MetricValue(
                metric_type=MetricType.TIME,
                name="소요 기간",
                as_is_value=0,
                to_be_value=to_be_time,
                unit="주",
            ),
        ]

        time_series = {
            "coverage": self._generate_time_series(
                current_coverage * 100, to_be_coverage * 100, horizon_weeks, option_type
            )
        }

        return metrics, time_series

    def _simulate_generic_impact(self, option: dict, baseline: dict[str, Any]) -> list[MetricValue]:
        """일반 영향도 시뮬레이션"""
        return [
            MetricValue(
                metric_type=MetricType.QUALITY,
                name="품질",
                as_is_value=baseline.get("quality", 70),
                to_be_value=baseline.get("quality", 70) * 1.1,
                unit="점",
            ),
        ]

    def _generate_time_series(
        self, start_value: float, end_value: float, weeks: int, option_type: str
    ) -> list[TimeSeriesPoint]:
        """시계열 데이터 생성"""
        points = []

        for week in range(1, weeks + 1):
            # 옵션 유형별 변화 패턴
            if option_type == "CONSERVATIVE":
                # 느린 변화
                progress = (week / weeks) ** 0.5
            elif option_type == "AGGRESSIVE":
                # 늦게 시작해서 급격히 변화
                progress = max(0, (week - weeks * 0.5) / (weeks * 0.5)) ** 2
            else:
                # 선형 변화
                progress = week / weeks

            to_be = start_value + (end_value - start_value) * progress

            points.append(
                TimeSeriesPoint(
                    period=f"W{week:02d}",
                    as_is_value=start_value,
                    to_be_value=to_be,
                )
            )

        return points

    def _calculate_overall_score(self, metrics: list[MetricValue]) -> float:
        """종합 영향도 점수 계산 (0-100)"""
        if not metrics:
            return 50.0

        weighted_score = 0.0
        total_weight = 0.0

        for metric in metrics:
            weight = self.METRIC_WEIGHTS.get(metric.metric_type, 0.1)
            total_weight += weight

            # 방향에 따른 점수 계산
            if metric.change_direction == "POSITIVE":
                score = min(100, 50 + abs(metric.change_percent))
            elif metric.change_direction == "NEGATIVE":
                score = max(0, 50 - abs(metric.change_percent))
            else:
                score = 50

            weighted_score += score * weight

        return weighted_score / total_weight if total_weight > 0 else 50.0

    def _calculate_confidence_interval(
        self, metrics: list[MetricValue], option_type: str
    ) -> tuple[float, float]:
        """신뢰구간 계산"""
        base_score = self._calculate_overall_score(metrics)

        # 옵션 유형별 불확실성
        uncertainty = {
            "CONSERVATIVE": 0.10,
            "BALANCED": 0.15,
            "AGGRESSIVE": 0.25,
        }.get(option_type, 0.15)

        lower = max(0, base_score * (1 - uncertainty))
        upper = min(100, base_score * (1 + uncertainty))

        return (round(lower, 1), round(upper, 1))

    def _determine_best_option(self, analyses: list[ImpactAnalysis]) -> tuple[str, str]:
        """최적 옵션 결정"""
        if not analyses:
            return "", "분석할 옵션이 없습니다."

        # 신뢰구간 하한을 고려한 점수로 정렬
        scored = [
            (a, a.confidence_interval[0] * 0.3 + a.overall_impact_score * 0.7) for a in analyses
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        best = scored[0][0]
        reason = (
            f"{best.option_name}이(가) 종합 영향도 {best.overall_impact_score:.1f}점, "
            f"신뢰구간 [{best.confidence_interval[0]:.1f}, {best.confidence_interval[1]:.1f}]으로 "
            "가장 높은 기대 효과를 보임"
        )

        return best.option_id, reason

    def _generate_comparison_summary(self, analyses: list[ImpactAnalysis]) -> dict[str, Any]:
        """비교 요약 생성"""
        summary = {
            "option_count": len(analyses),
            "scores": {},
            "best_by_metric": {},
            "risk_comparison": {},
        }

        for analysis in analyses:
            summary["scores"][analysis.option_id] = analysis.overall_impact_score

            for metric in analysis.metrics:
                metric_name = metric.name
                if metric_name not in summary["best_by_metric"]:
                    summary["best_by_metric"][metric_name] = {
                        "option_id": analysis.option_id,
                        "value": metric.to_be_value,
                    }
                else:
                    current_best = summary["best_by_metric"][metric_name]["value"]
                    if metric.change_direction == "POSITIVE":
                        if metric.to_be_value > current_best:
                            summary["best_by_metric"][metric_name] = {
                                "option_id": analysis.option_id,
                                "value": metric.to_be_value,
                            }
                    elif metric.change_direction == "NEGATIVE":
                        if metric.to_be_value < current_best:
                            summary["best_by_metric"][metric_name] = {
                                "option_id": analysis.option_id,
                                "value": metric.to_be_value,
                            }

            summary["risk_comparison"][analysis.option_id] = len(analysis.risks)

        return summary

    def to_dict(self, comparison: ScenarioComparison) -> dict:
        """결과를 딕셔너리로 변환"""
        return {
            "query_type": comparison.query_type,
            "baseline": comparison.baseline,
            "analyses": [
                {
                    "option_id": a.option_id,
                    "option_name": a.option_name,
                    "metrics": [
                        {
                            "name": m.name,
                            "as_is": m.as_is_value,
                            "to_be": m.to_be_value,
                            "change_percent": round(m.change_percent, 2),
                            "change_direction": m.change_direction,
                            "unit": m.unit,
                        }
                        for m in a.metrics
                    ],
                    "time_series": {
                        key: [
                            {"period": p.period, "as_is": p.as_is_value, "to_be": p.to_be_value}
                            for p in points
                        ]
                        for key, points in a.time_series.items()
                    },
                    "overall_impact_score": round(a.overall_impact_score, 2),
                    "confidence_interval": a.confidence_interval,
                    "assumptions": a.assumptions,
                    "risks": a.risks,
                }
                for a in comparison.analyses
            ],
            "comparison_summary": comparison.comparison_summary,
            "best_option_id": comparison.best_option_id,
            "best_option_reason": comparison.best_option_reason,
            "simulated_at": comparison.simulated_at.isoformat(),
        }


# CLI 테스트용
if __name__ == "__main__":
    agent = ImpactSimulatorAgent()

    options = [
        {"option_id": "OPT-01", "name": "내부 재배치", "option_type": "CONSERVATIVE"},
        {"option_id": "OPT-02", "name": "외주 활용", "option_type": "BALANCED"},
        {"option_id": "OPT-03", "name": "정규직 채용", "option_type": "AGGRESSIVE"},
    ]

    baseline = {
        "utilization": 0.92,
        "headcount": 10,
        "gap_fte": 3,
        "cost": 100000000,
        "risk": 0.3,
    }

    result = agent.simulate(
        query_type="CAPACITY",
        options=options,
        baseline=baseline,
        horizon_weeks=12,
    )

    print("=" * 60)
    print("IMPACT SIMULATION RESULTS")
    print("=" * 60)

    for analysis in result.analyses:
        print(f"\n[{analysis.option_id}] {analysis.option_name}")
        print(f"  종합 점수: {analysis.overall_impact_score:.1f}")
        print(f"  신뢰구간: {analysis.confidence_interval}")
        for m in analysis.metrics:
            print(
                f"  - {m.name}: {m.as_is_value:.1f} → {m.to_be_value:.1f} ({m.change_percent:+.1f}%)"
            )

    print(f"\n최적 옵션: {result.best_option_id}")
    print(f"이유: {result.best_option_reason}")
