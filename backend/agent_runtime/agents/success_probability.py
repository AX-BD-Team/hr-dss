"""
HR DSS - Success Probability Agent

프로젝트/의사결정의 성공 확률을 예측하는 에이전트
휴리스틱 + ML 모델 기반 예측
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RiskCategory(Enum):
    """리스크 카테고리"""

    RESOURCE = "RESOURCE"  # 리소스 관련
    COMPETENCY = "COMPETENCY"  # 역량 관련
    SCHEDULE = "SCHEDULE"  # 일정 관련
    TECHNICAL = "TECHNICAL"  # 기술 관련
    CUSTOMER = "CUSTOMER"  # 고객 관련
    ORGANIZATIONAL = "ORGANIZATIONAL"  # 조직 관련
    EXTERNAL = "EXTERNAL"  # 외부 요인


class RiskLevel(Enum):
    """리스크 수준"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskFactor:
    """리스크 요인"""

    factor_id: str
    category: RiskCategory
    name: str
    description: str
    probability: float  # 발생 확률 (0-1)
    impact: float  # 영향도 (0-1)
    risk_score: float = 0.0  # probability * impact
    level: RiskLevel = RiskLevel.MEDIUM
    mitigation: str = ""
    evidence: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.risk_score = self.probability * self.impact

        # 리스크 수준 자동 결정
        if self.risk_score >= 0.6:
            self.level = RiskLevel.CRITICAL
        elif self.risk_score >= 0.4:
            self.level = RiskLevel.HIGH
        elif self.risk_score >= 0.2:
            self.level = RiskLevel.MEDIUM
        else:
            self.level = RiskLevel.LOW


@dataclass
class SuccessFactor:
    """성공 요인"""

    factor_id: str
    name: str
    weight: float  # 가중치 (0-1)
    score: float  # 점수 (0-100)
    weighted_score: float = 0.0
    evidence: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.weighted_score = self.weight * self.score


@dataclass
class ProbabilityResult:
    """성공 확률 결과"""

    subject_type: str  # PROJECT, OPPORTUNITY, OPTION
    subject_id: str
    subject_name: str
    success_probability: float  # 0-1
    confidence: float  # 예측 신뢰도 (0-1)
    success_factors: list[SuccessFactor]
    risk_factors: list[RiskFactor]
    overall_risk_score: float
    recommendation: str
    calculated_at: datetime = field(default_factory=datetime.now)


class SuccessProbabilityAgent:
    """성공 확률 예측 에이전트"""

    # 프로젝트 유형별 기본 성공률
    PROJECT_TYPE_BASE_PROB = {
        "AI/ML": 0.65,
        "DATA_ENGINEERING": 0.70,
        "CLOUD_MIGRATION": 0.75,
        "ERP_IMPLEMENTATION": 0.60,
        "CUSTOM_DEVELOPMENT": 0.65,
        "CONSULTING": 0.80,
        "DEFAULT": 0.70,
    }

    # 성공 요인 정의
    SUCCESS_FACTORS = {
        "resource_match": {
            "name": "리소스 매칭",
            "weight": 0.25,
            "description": "필요 인력 대비 가용 인력 비율",
        },
        "competency_match": {
            "name": "역량 매칭",
            "weight": 0.25,
            "description": "필요 역량 대비 보유 역량 수준",
        },
        "historical_success": {
            "name": "과거 성공률",
            "weight": 0.15,
            "description": "유사 프로젝트 과거 성공 기록",
        },
        "customer_relationship": {
            "name": "고객 관계",
            "weight": 0.10,
            "description": "고객사와의 기존 협력 관계",
        },
        "schedule_buffer": {
            "name": "일정 여유",
            "weight": 0.15,
            "description": "계획 대비 일정 버퍼 존재 여부",
        },
        "team_experience": {
            "name": "팀 경험",
            "weight": 0.10,
            "description": "팀원들의 관련 경험 수준",
        },
    }

    def __init__(self, kg_client: Any = None, ml_model: Any = None):
        """
        Args:
            kg_client: Knowledge Graph 클라이언트
            ml_model: ML 예측 모델 (선택)
        """
        self.kg_client = kg_client
        self.ml_model = ml_model

    def calculate_probability(
        self, subject_type: str, subject_id: str, subject_name: str, context: dict[str, Any]
    ) -> ProbabilityResult:
        """
        성공 확률 계산

        Args:
            subject_type: 대상 유형 (PROJECT, OPPORTUNITY, OPTION)
            subject_id: 대상 ID
            subject_name: 대상 이름
            context: 분석 컨텍스트

        Returns:
            ProbabilityResult: 성공 확률 결과
        """
        # 1. 성공 요인 분석
        success_factors = self._analyze_success_factors(context)

        # 2. 리스크 요인 분석
        risk_factors = self._analyze_risk_factors(context)

        # 3. 성공 확률 계산
        base_prob = self._get_base_probability(context)
        factor_adjustment = self._calculate_factor_adjustment(success_factors)
        risk_adjustment = self._calculate_risk_adjustment(risk_factors)

        success_probability = base_prob * (1 + factor_adjustment) * (1 - risk_adjustment)
        success_probability = max(0.05, min(0.95, success_probability))  # 5-95% 범위

        # 4. 신뢰도 계산
        confidence = self._calculate_confidence(success_factors, risk_factors, context)

        # 5. 전체 리스크 점수
        overall_risk = (
            sum(rf.risk_score for rf in risk_factors) / len(risk_factors) if risk_factors else 0
        )

        # 6. 추천 결정
        recommendation = self._generate_recommendation(
            success_probability, overall_risk, success_factors, risk_factors
        )

        return ProbabilityResult(
            subject_type=subject_type,
            subject_id=subject_id,
            subject_name=subject_name,
            success_probability=round(success_probability, 3),
            confidence=round(confidence, 3),
            success_factors=success_factors,
            risk_factors=risk_factors,
            overall_risk_score=round(overall_risk, 3),
            recommendation=recommendation,
        )

    def _get_base_probability(self, context: dict[str, Any]) -> float:
        """기본 성공 확률 조회"""
        project_type = context.get("project_type", "DEFAULT")
        return self.PROJECT_TYPE_BASE_PROB.get(project_type, self.PROJECT_TYPE_BASE_PROB["DEFAULT"])

    def _analyze_success_factors(self, context: dict[str, Any]) -> list[SuccessFactor]:
        """성공 요인 분석"""
        factors = []

        for factor_id, factor_def in self.SUCCESS_FACTORS.items():
            score = self._calculate_factor_score(factor_id, context)
            evidence = self._get_factor_evidence(factor_id, context)

            factor = SuccessFactor(
                factor_id=factor_id,
                name=factor_def["name"],
                weight=factor_def["weight"],
                score=score,
                evidence=evidence,
            )
            factors.append(factor)

        return factors

    def _calculate_factor_score(self, factor_id: str, context: dict[str, Any]) -> float:
        """요인별 점수 계산"""

        if factor_id == "resource_match":
            available_fte = context.get("available_fte", 0)
            required_fte = context.get("required_fte", 1)
            if required_fte == 0:
                return 100
            ratio = available_fte / required_fte
            return min(100, ratio * 100)

        elif factor_id == "competency_match":
            match_score = context.get("competency_match_score", 0.7)
            return match_score * 100

        elif factor_id == "historical_success":
            past_success_rate = context.get("historical_success_rate", 0.7)
            return past_success_rate * 100

        elif factor_id == "customer_relationship":
            relationship_score = context.get("customer_relationship", 0.5)
            is_existing_customer = context.get("is_existing_customer", False)
            base_score = relationship_score * 80
            if is_existing_customer:
                base_score += 20
            return min(100, base_score)

        elif factor_id == "schedule_buffer":
            planned_duration = context.get("planned_duration_weeks", 12)
            buffer_weeks = context.get("buffer_weeks", 0)
            buffer_ratio = buffer_weeks / planned_duration if planned_duration > 0 else 0
            # 20% 버퍼가 이상적
            if buffer_ratio >= 0.2:
                return 100
            elif buffer_ratio >= 0.1:
                return 80
            elif buffer_ratio > 0:
                return 60
            else:
                return 40

        elif factor_id == "team_experience":
            avg_experience = context.get("team_avg_experience_years", 3)
            similar_project_count = context.get("similar_project_count", 0)
            exp_score = min(50, avg_experience * 10)
            proj_score = min(50, similar_project_count * 10)
            return exp_score + proj_score

        return 50  # 기본값

    def _get_factor_evidence(self, factor_id: str, context: dict[str, Any]) -> list[str]:
        """요인별 근거 수집"""
        evidence = []

        if factor_id == "resource_match":
            available = context.get("available_fte", 0)
            required = context.get("required_fte", 0)
            evidence.append(f"가용 FTE: {available}, 필요 FTE: {required}")

        elif factor_id == "competency_match":
            match_score = context.get("competency_match_score", 0)
            evidence.append(f"역량 매칭 점수: {match_score * 100:.1f}%")

        elif factor_id == "historical_success":
            rate = context.get("historical_success_rate", 0)
            count = context.get("historical_project_count", 0)
            evidence.append(f"과거 {count}건 중 성공률 {rate * 100:.1f}%")

        return evidence

    def _analyze_risk_factors(self, context: dict[str, Any]) -> list[RiskFactor]:
        """리스크 요인 분석"""
        risks = []

        # 리소스 리스크
        available_fte = context.get("available_fte", 0)
        required_fte = context.get("required_fte", 1)
        if available_fte < required_fte:
            gap = required_fte - available_fte
            probability = min(0.9, gap / required_fte)
            risks.append(
                RiskFactor(
                    factor_id="RISK-RES-01",
                    category=RiskCategory.RESOURCE,
                    name="리소스 부족",
                    description=f"필요 인력 대비 {gap:.1f} FTE 부족",
                    probability=probability,
                    impact=0.7,
                    mitigation="외주 인력 활용 또는 일정 연장",
                    evidence=[f"필요: {required_fte} FTE, 가용: {available_fte} FTE"],
                )
            )

        # 역량 리스크
        competency_match = context.get("competency_match_score", 0.7)
        if competency_match < 0.8:
            probability = (0.8 - competency_match) / 0.8
            risks.append(
                RiskFactor(
                    factor_id="RISK-COMP-01",
                    category=RiskCategory.COMPETENCY,
                    name="역량 부족",
                    description=f"역량 매칭률 {competency_match * 100:.1f}%로 미달",
                    probability=probability,
                    impact=0.6,
                    mitigation="교육 또는 외부 전문가 영입",
                    evidence=[f"역량 매칭률: {competency_match * 100:.1f}%"],
                )
            )

        # 일정 리스크
        buffer_weeks = context.get("buffer_weeks", 0)
        planned_duration = context.get("planned_duration_weeks", 12)
        if buffer_weeks < planned_duration * 0.1:
            risks.append(
                RiskFactor(
                    factor_id="RISK-SCH-01",
                    category=RiskCategory.SCHEDULE,
                    name="일정 촉박",
                    description="충분한 일정 버퍼가 없음",
                    probability=0.5,
                    impact=0.5,
                    mitigation="범위 조정 또는 일정 협상",
                    evidence=[f"버퍼: {buffer_weeks}주 / 전체: {planned_duration}주"],
                )
            )

        # 기술 리스크
        tech_complexity = context.get("tech_complexity", "MEDIUM")
        if tech_complexity == "HIGH":
            risks.append(
                RiskFactor(
                    factor_id="RISK-TECH-01",
                    category=RiskCategory.TECHNICAL,
                    name="기술 복잡성",
                    description="높은 기술 난이도로 인한 리스크",
                    probability=0.4,
                    impact=0.6,
                    mitigation="PoC 선행 또는 전문가 투입",
                    evidence=[f"기술 복잡도: {tech_complexity}"],
                )
            )

        # 고객 리스크
        is_new_customer = not context.get("is_existing_customer", False)
        if is_new_customer:
            risks.append(
                RiskFactor(
                    factor_id="RISK-CUST-01",
                    category=RiskCategory.CUSTOMER,
                    name="신규 고객",
                    description="신규 고객으로 요구사항 불확실성 존재",
                    probability=0.3,
                    impact=0.4,
                    mitigation="철저한 요구사항 정의 및 변경 관리 프로세스",
                    evidence=["신규 고객"],
                )
            )

        # 조직 리스크
        utilization = context.get("current_utilization", 0.8)
        if utilization > 0.9:
            risks.append(
                RiskFactor(
                    factor_id="RISK-ORG-01",
                    category=RiskCategory.ORGANIZATIONAL,
                    name="조직 과부하",
                    description=f"현재 가동률 {utilization * 100:.1f}%로 과부하 상태",
                    probability=0.6,
                    impact=0.5,
                    mitigation="우선순위 조정 또는 증원",
                    evidence=[f"현재 가동률: {utilization * 100:.1f}%"],
                )
            )

        return risks

    def _calculate_factor_adjustment(self, success_factors: list[SuccessFactor]) -> float:
        """성공 요인에 의한 조정값 계산"""
        if not success_factors:
            return 0.0

        total_weighted = sum(f.weighted_score for f in success_factors)
        total_weight = sum(f.weight for f in success_factors)

        # 기준값 50점 대비 차이를 조정값으로 사용
        avg_score = total_weighted / total_weight if total_weight > 0 else 50
        adjustment = (avg_score - 50) / 100  # -0.5 ~ +0.5

        return adjustment

    def _calculate_risk_adjustment(self, risk_factors: list[RiskFactor]) -> float:
        """리스크에 의한 조정값 계산"""
        if not risk_factors:
            return 0.0

        # 리스크 점수 합계를 조정값으로 변환
        total_risk = sum(rf.risk_score for rf in risk_factors)
        # 최대 5개 리스크 가정, 각 최대 1.0
        max_possible_risk = 5.0
        adjustment = min(total_risk / max_possible_risk, 0.5)  # 최대 50% 감소

        return adjustment

    def _calculate_confidence(
        self,
        success_factors: list[SuccessFactor],
        risk_factors: list[RiskFactor],
        context: dict[str, Any],
    ) -> float:
        """예측 신뢰도 계산"""
        base_confidence = 0.7

        # 데이터 완전성에 따른 조정
        data_completeness = context.get("data_completeness", 0.8)
        data_bonus = (data_completeness - 0.5) * 0.3

        # 과거 데이터 존재 여부
        has_historical = context.get("historical_project_count", 0) > 5
        historical_bonus = 0.1 if has_historical else 0

        # 리스크 불확실성
        high_risk_count = sum(
            1 for rf in risk_factors if rf.level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        risk_penalty = high_risk_count * 0.05

        confidence = base_confidence + data_bonus + historical_bonus - risk_penalty
        return max(0.3, min(0.95, confidence))

    def _generate_recommendation(
        self,
        probability: float,
        overall_risk: float,
        success_factors: list[SuccessFactor],
        risk_factors: list[RiskFactor],
    ) -> str:
        """추천 생성"""
        parts = []

        # 확률 기반 판단
        if probability >= 0.8:
            parts.append("성공 확률이 높아 진행을 권장합니다.")
        elif probability >= 0.6:
            parts.append("성공 확률이 적정하나 리스크 관리가 필요합니다.")
        elif probability >= 0.4:
            parts.append("성공 확률이 낮아 조건 조정을 권장합니다.")
        else:
            parts.append("성공 확률이 매우 낮아 재검토가 필요합니다.")

        # 주요 개선 포인트
        weak_factors = [f for f in success_factors if f.score < 60]
        if weak_factors:
            weak_names = ", ".join(f.name for f in weak_factors[:2])
            parts.append(f"개선 필요 영역: {weak_names}")

        # 주요 리스크
        critical_risks = [
            rf for rf in risk_factors if rf.level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]
        if critical_risks:
            risk_names = ", ".join(rf.name for rf in critical_risks[:2])
            parts.append(f"주요 리스크: {risk_names}")

        return " ".join(parts)

    def to_dict(self, result: ProbabilityResult) -> dict:
        """결과를 딕셔너리로 변환"""
        return {
            "subject_type": result.subject_type,
            "subject_id": result.subject_id,
            "subject_name": result.subject_name,
            "success_probability": result.success_probability,
            "confidence": result.confidence,
            "success_factors": [
                {
                    "factor_id": f.factor_id,
                    "name": f.name,
                    "weight": f.weight,
                    "score": round(f.score, 2),
                    "weighted_score": round(f.weighted_score, 2),
                    "evidence": f.evidence,
                }
                for f in result.success_factors
            ],
            "risk_factors": [
                {
                    "factor_id": rf.factor_id,
                    "category": rf.category.value,
                    "name": rf.name,
                    "description": rf.description,
                    "probability": round(rf.probability, 2),
                    "impact": round(rf.impact, 2),
                    "risk_score": round(rf.risk_score, 2),
                    "level": rf.level.value,
                    "mitigation": rf.mitigation,
                    "evidence": rf.evidence,
                }
                for rf in result.risk_factors
            ],
            "overall_risk_score": result.overall_risk_score,
            "recommendation": result.recommendation,
            "calculated_at": result.calculated_at.isoformat(),
        }


# CLI 테스트용
if __name__ == "__main__":
    agent = SuccessProbabilityAgent()

    context = {
        "project_type": "AI/ML",
        "available_fte": 4,
        "required_fte": 5,
        "competency_match_score": 0.75,
        "historical_success_rate": 0.8,
        "historical_project_count": 10,
        "is_existing_customer": True,
        "planned_duration_weeks": 24,
        "buffer_weeks": 2,
        "team_avg_experience_years": 5,
        "similar_project_count": 3,
        "tech_complexity": "HIGH",
        "current_utilization": 0.85,
        "data_completeness": 0.9,
    }

    result = agent.calculate_probability(
        subject_type="PROJECT",
        subject_id="PRJ-2025-0001",
        subject_name="AI 챗봇 프로젝트",
        context=context,
    )

    print("=" * 60)
    print("SUCCESS PROBABILITY ANALYSIS")
    print("=" * 60)
    print(f"\n대상: {result.subject_name}")
    print(f"성공 확률: {result.success_probability * 100:.1f}%")
    print(f"신뢰도: {result.confidence * 100:.1f}%")

    print("\n[성공 요인]")
    for f in result.success_factors:
        print(f"  - {f.name}: {f.score:.1f}점 (가중 {f.weighted_score:.1f})")

    print("\n[리스크 요인]")
    for rf in result.risk_factors:
        print(f"  - [{rf.level.value}] {rf.name}: 점수 {rf.risk_score:.2f}")
        print(f"    완화책: {rf.mitigation}")

    print(f"\n추천: {result.recommendation}")
