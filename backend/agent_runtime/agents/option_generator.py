"""
HR DSS - Option Generator Agent

의사결정을 위한 대안(Option)을 생성하는 에이전트
각 질문 유형별로 3가지 대안을 생성
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class OptionType(Enum):
    """대안 유형"""

    CONSERVATIVE = "CONSERVATIVE"  # 보수적
    BALANCED = "BALANCED"  # 균형
    AGGRESSIVE = "AGGRESSIVE"  # 적극적


@dataclass
class ResourceAllocation:
    """리소스 배분"""

    employee_id: str | None = None
    org_unit_id: str | None = None
    allocation_fte: float = 0.0
    role: str = ""
    start_date: str = ""
    end_date: str = ""


@dataclass
class DecisionOption:
    """의사결정 대안"""

    option_id: str
    option_type: OptionType
    name: str
    description: str
    actions: list[str]
    resource_allocations: list[ResourceAllocation] = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_benefit: float = 0.0
    risk_level: str = "MEDIUM"
    implementation_time: str = ""
    prerequisites: list[str] = field(default_factory=list)
    trade_offs: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)


@dataclass
class OptionSet:
    """대안 세트"""

    query_type: str
    context: dict[str, Any]
    options: list[DecisionOption]
    recommendation: str
    recommendation_reason: str
    generated_at: datetime = field(default_factory=datetime.now)


class OptionGeneratorAgent:
    """대안 생성 에이전트"""

    def __init__(self, llm_client: Any = None, kg_client: Any = None):
        """
        Args:
            llm_client: LLM 클라이언트
            kg_client: Knowledge Graph 클라이언트
        """
        self.llm_client = llm_client
        self.kg_client = kg_client

    def generate_options(
        self, query_type: str, context: dict[str, Any], constraints: dict[str, Any] | None = None
    ) -> OptionSet:
        """
        질문 유형에 맞는 3가지 대안 생성

        Args:
            query_type: 질문 유형 (CAPACITY, GO_NOGO, HEADCOUNT, COMPETENCY_GAP)
            context: 분석 컨텍스트 (KG 쿼리 결과 등)
            constraints: 제약조건

        Returns:
            OptionSet: 3가지 대안 세트
        """
        constraints = constraints or {}

        if query_type == "CAPACITY":
            return self._generate_capacity_options(context, constraints)
        elif query_type == "GO_NOGO":
            return self._generate_gonogo_options(context, constraints)
        elif query_type == "HEADCOUNT":
            return self._generate_headcount_options(context, constraints)
        elif query_type == "COMPETENCY_GAP":
            return self._generate_competency_options(context, constraints)
        else:
            return self._generate_generic_options(context, constraints)

    def _generate_capacity_options(
        self, context: dict[str, Any], constraints: dict[str, Any]
    ) -> OptionSet:
        """Capacity 병목 해결 대안 생성"""

        _bottleneck_weeks = context.get("bottleneck_weeks", [])  # 향후 확장용
        gap_fte = context.get("gap_fte", 0)
        _org_unit = context.get("org_unit", "대상 조직")  # 향후 확장용

        options = [
            DecisionOption(
                option_id="CAP-OPT-01",
                option_type=OptionType.CONSERVATIVE,
                name="내부 재배치",
                description="유휴 인력을 병목 구간으로 재배치하여 해결",
                actions=[
                    f"유휴 인력 {max(1, int(gap_fte * 0.5))}명 병목 조직으로 임시 배치",
                    "비핵심 프로젝트 일정 조정 (2-4주 연기)",
                    "크로스 트레이닝을 통한 역량 전환",
                ],
                estimated_cost=gap_fte * 5000000,  # 재배치 비용
                estimated_benefit=gap_fte * 15000000,  # 병목 해소 이익
                risk_level="LOW",
                implementation_time="2-4주",
                prerequisites=["유휴 인력 존재", "역량 전환 가능성"],
                trade_offs=[
                    "원래 프로젝트 일정 지연 가능",
                    "재배치 인력의 생산성 저하 (학습 곡선)",
                ],
                scores={
                    "impact": 65,
                    "feasibility": 85,
                    "risk": 25,
                    "cost": 30,
                    "time": 20,
                },
            ),
            DecisionOption(
                option_id="CAP-OPT-02",
                option_type=OptionType.BALANCED,
                name="외부 인력 활용",
                description="외주/파견 인력을 활용하여 단기 병목 해소",
                actions=[
                    f"외주 인력 {max(1, int(gap_fte))}명 투입 (3개월 계약)",
                    "내부 핵심 인력은 기술 리드 역할 유지",
                    "지식 이전 계획 수립",
                ],
                estimated_cost=gap_fte * 20000000,  # 외주 비용 (3개월)
                estimated_benefit=gap_fte * 25000000,
                risk_level="MEDIUM",
                implementation_time="4-6주",
                prerequisites=["예산 확보", "외주사 풀 존재"],
                trade_offs=[
                    "비용 증가",
                    "품질 관리 필요",
                    "보안/지적재산권 이슈",
                ],
                scores={
                    "impact": 80,
                    "feasibility": 70,
                    "risk": 45,
                    "cost": 60,
                    "time": 40,
                },
            ),
            DecisionOption(
                option_id="CAP-OPT-03",
                option_type=OptionType.AGGRESSIVE,
                name="정규직 채용",
                description="병목 해소를 위한 정규직 채용 진행",
                actions=[
                    f"정규직 {max(1, int(gap_fte * 1.2))}명 채용 (역량 갭 고려)",
                    "채용 파이프라인 구축 및 JD 작성",
                    "온보딩 프로그램 준비",
                ],
                estimated_cost=gap_fte * 80000000,  # 연봉 + 채용비
                estimated_benefit=gap_fte * 50000000,  # 장기 효과
                risk_level="HIGH",
                implementation_time="8-12주",
                prerequisites=["채용 승인", "인력 계획 반영"],
                trade_offs=[
                    "채용까지 시간 소요",
                    "고정비 증가",
                    "인력 적합성 리스크",
                ],
                scores={
                    "impact": 95,
                    "feasibility": 50,
                    "risk": 65,
                    "cost": 80,
                    "time": 70,
                },
            ),
        ]

        # 추천 결정
        recommendation, reason = self._determine_recommendation(options, "CAPACITY")

        return OptionSet(
            query_type="CAPACITY",
            context=context,
            options=options,
            recommendation=recommendation,
            recommendation_reason=reason,
        )

    def _generate_gonogo_options(
        self, context: dict[str, Any], constraints: dict[str, Any]
    ) -> OptionSet:
        """Go/No-go 의사결정 대안 생성"""

        opportunity = context.get("opportunity", {})
        resource_fit = context.get("resource_fit", 0.7)
        success_prob = context.get("success_probability", 0.6)

        options = [
            DecisionOption(
                option_id="GNG-OPT-01",
                option_type=OptionType.CONSERVATIVE,
                name="No-Go (거절)",
                description="리소스 부족 및 리스크로 인해 수주 거절",
                actions=[
                    "고객에게 정중히 거절 의사 전달",
                    "향후 협력 가능성 열어두기",
                    "거절 사유 문서화 (VRB 기록)",
                ],
                estimated_cost=0,
                estimated_benefit=0,
                risk_level="LOW",
                implementation_time="즉시",
                prerequisites=[],
                trade_offs=[
                    "매출 기회 손실",
                    "고객 관계 영향 가능",
                    "경쟁사에 기회 양보",
                ],
                scores={
                    "impact": 20,
                    "feasibility": 100,
                    "risk": 10,
                    "cost": 0,
                    "time": 0,
                },
            ),
            DecisionOption(
                option_id="GNG-OPT-02",
                option_type=OptionType.BALANCED,
                name="조건부 Go",
                description="일정/범위 조정을 전제로 수주 진행",
                actions=[
                    "일정 4주 연장 협상",
                    "1차 범위 축소 (MVP 접근)",
                    "주요 리스크에 대한 고객 합의",
                    "마일스톤별 검토 조건 추가",
                ],
                estimated_cost=opportunity.get("deal_value", 0) * 0.1,  # 협상 비용
                estimated_benefit=opportunity.get("deal_value", 0) * 0.8,
                risk_level="MEDIUM",
                implementation_time="2-4주 협상",
                prerequisites=["고객 협상 가능", "범위 조정 가능"],
                trade_offs=[
                    "마진율 감소 가능",
                    "고객 기대치 관리 필요",
                    "일정 리스크 존재",
                ],
                scores={
                    "impact": 70,
                    "feasibility": 75,
                    "risk": 40,
                    "cost": 35,
                    "time": 35,
                },
            ),
            DecisionOption(
                option_id="GNG-OPT-03",
                option_type=OptionType.AGGRESSIVE,
                name="Full Go (수락)",
                description="현재 조건으로 수주 진행",
                actions=[
                    "계약 체결 진행",
                    "프로젝트 팀 즉시 구성",
                    "킥오프 준비",
                    "리스크 완화 계획 수립",
                ],
                estimated_cost=opportunity.get("deal_value", 0) * 0.15,  # 프로젝트 비용
                estimated_benefit=opportunity.get("deal_value", 0),
                risk_level="HIGH",
                implementation_time="즉시",
                prerequisites=["리소스 확보", "리스크 수용"],
                trade_offs=[
                    "리소스 과부하 리스크",
                    "품질 저하 가능성",
                    "기존 프로젝트 영향",
                ],
                scores={
                    "impact": 95,
                    "feasibility": 55,
                    "risk": 70,
                    "cost": 50,
                    "time": 20,
                },
            ),
        ]

        recommendation, reason = self._determine_recommendation(
            options, "GO_NOGO", {"success_probability": success_prob, "resource_fit": resource_fit}
        )

        return OptionSet(
            query_type="GO_NOGO",
            context=context,
            options=options,
            recommendation=recommendation,
            recommendation_reason=reason,
        )

    def _generate_headcount_options(
        self, context: dict[str, Any], constraints: dict[str, Any]
    ) -> OptionSet:
        """증원 분석 대안 생성"""

        requested_headcount = context.get("requested_headcount", 2)
        current_utilization = context.get("utilization", 0.85)
        _pipeline_demand = context.get("pipeline_demand", 0)  # 향후 확장용

        options = [
            DecisionOption(
                option_id="HC-OPT-01",
                option_type=OptionType.CONSERVATIVE,
                name="증원 불승인",
                description="현재 인력으로 효율화를 통해 대응",
                actions=[
                    "업무 프로세스 효율화",
                    "비핵심 업무 자동화/외주화",
                    "크로스 스킬링 강화",
                    "3개월 후 재검토",
                ],
                estimated_cost=requested_headcount * 5000000,  # 효율화 비용
                estimated_benefit=requested_headcount * 10000000,
                risk_level="MEDIUM",
                implementation_time="4-8주",
                prerequisites=["효율화 여지 존재"],
                trade_offs=[
                    "직원 피로도 증가",
                    "이직 리스크",
                    "성장 기회 제한",
                ],
                scores={
                    "impact": 40,
                    "feasibility": 85,
                    "risk": 50,
                    "cost": 20,
                    "time": 30,
                },
            ),
            DecisionOption(
                option_id="HC-OPT-02",
                option_type=OptionType.BALANCED,
                name="부분 승인",
                description=f"요청의 50% ({max(1, requested_headcount // 2)}명)만 승인",
                actions=[
                    f"{max(1, requested_headcount // 2)}명 정규직 채용",
                    "나머지는 외주/계약직으로 대응",
                    "6개월 후 추가 증원 재검토",
                ],
                estimated_cost=requested_headcount * 40000000,  # 절반 채용
                estimated_benefit=requested_headcount * 35000000,
                risk_level="LOW",
                implementation_time="8-12주",
                prerequisites=["채용 예산 일부 확보"],
                trade_offs=[
                    "완전한 문제 해결 안됨",
                    "혼합 인력 관리 필요",
                ],
                scores={
                    "impact": 65,
                    "feasibility": 75,
                    "risk": 30,
                    "cost": 50,
                    "time": 50,
                },
            ),
            DecisionOption(
                option_id="HC-OPT-03",
                option_type=OptionType.AGGRESSIVE,
                name="전체 승인",
                description=f"요청 인원 {requested_headcount}명 전원 채용 승인",
                actions=[
                    f"정규직 {requested_headcount}명 채용 진행",
                    "채용 파이프라인 가속화",
                    "온보딩 프로그램 준비",
                ],
                estimated_cost=requested_headcount * 80000000,  # 전체 채용
                estimated_benefit=requested_headcount * 60000000,
                risk_level="MEDIUM",
                implementation_time="12-16주",
                prerequisites=["예산 전액 확보", "인력 계획 승인"],
                trade_offs=[
                    "고정비 증가",
                    "채용 실패 리스크",
                    "수요 감소 시 과잉 인력",
                ],
                scores={
                    "impact": 90,
                    "feasibility": 55,
                    "risk": 45,
                    "cost": 80,
                    "time": 70,
                },
            ),
        ]

        recommendation, reason = self._determine_recommendation(
            options, "HEADCOUNT", {"utilization": current_utilization}
        )

        return OptionSet(
            query_type="HEADCOUNT",
            context=context,
            options=options,
            recommendation=recommendation,
            recommendation_reason=reason,
        )

    def _generate_competency_options(
        self, context: dict[str, Any], constraints: dict[str, Any]
    ) -> OptionSet:
        """역량 갭 해소 대안 생성"""

        gap_competencies = context.get("gap_competencies", [])
        gap_count = len(gap_competencies)

        options = [
            DecisionOption(
                option_id="CG-OPT-01",
                option_type=OptionType.CONSERVATIVE,
                name="내부 육성",
                description="기존 인력 대상 교육 및 역량 개발",
                actions=[
                    "내부 교육 프로그램 운영",
                    "멘토링 체계 구축",
                    "자기 학습 지원 (교육비, 시간)",
                    "프로젝트 로테이션",
                ],
                estimated_cost=gap_count * 5000000,  # 교육비
                estimated_benefit=gap_count * 15000000,
                risk_level="LOW",
                implementation_time="6-12개월",
                prerequisites=["교육 대상자 선정", "교육 예산"],
                trade_offs=[
                    "시간이 오래 걸림",
                    "교육 중 생산성 저하",
                    "이직 시 투자 손실",
                ],
                scores={
                    "impact": 50,
                    "feasibility": 90,
                    "risk": 20,
                    "cost": 25,
                    "time": 70,
                },
            ),
            DecisionOption(
                option_id="CG-OPT-02",
                option_type=OptionType.BALANCED,
                name="외부 교육 + 채용 혼합",
                description="집중 외부 교육과 핵심 인력 채용 병행",
                actions=[
                    "핵심 역량 보유자 1-2명 경력 채용",
                    "외부 전문 교육 위탁 (부트캠프)",
                    "채용 인력 통한 지식 전파",
                ],
                estimated_cost=gap_count * 30000000,
                estimated_benefit=gap_count * 40000000,
                risk_level="MEDIUM",
                implementation_time="3-6개월",
                prerequisites=["채용 예산", "교육 파트너"],
                trade_offs=[
                    "초기 비용 높음",
                    "채용 실패 리스크",
                    "조직 적응 시간 필요",
                ],
                scores={
                    "impact": 75,
                    "feasibility": 70,
                    "risk": 40,
                    "cost": 55,
                    "time": 45,
                },
            ),
            DecisionOption(
                option_id="CG-OPT-03",
                option_type=OptionType.AGGRESSIVE,
                name="팀 빌딩",
                description="해당 역량 전문 팀 신설 및 대규모 채용",
                actions=[
                    f"전문 팀 신설 ({max(3, gap_count)}명 규모)",
                    "시니어 리더 영입",
                    "전문 채용 에이전시 활용",
                ],
                estimated_cost=gap_count * 100000000,
                estimated_benefit=gap_count * 80000000,
                risk_level="HIGH",
                implementation_time="6-12개월",
                prerequisites=["대규모 예산", "경영진 승인"],
                trade_offs=[
                    "매우 높은 투자 비용",
                    "조직 구조 변경 필요",
                    "실패 시 큰 손실",
                ],
                scores={
                    "impact": 95,
                    "feasibility": 40,
                    "risk": 70,
                    "cost": 90,
                    "time": 65,
                },
            ),
        ]

        recommendation, reason = self._determine_recommendation(options, "COMPETENCY_GAP")

        return OptionSet(
            query_type="COMPETENCY_GAP",
            context=context,
            options=options,
            recommendation=recommendation,
            recommendation_reason=reason,
        )

    def _generate_generic_options(
        self, context: dict[str, Any], constraints: dict[str, Any]
    ) -> OptionSet:
        """일반 대안 생성"""
        options = [
            DecisionOption(
                option_id="GEN-OPT-01",
                option_type=OptionType.CONSERVATIVE,
                name="현상 유지",
                description="현재 상태 유지 및 모니터링",
                actions=["상황 모니터링", "추가 데이터 수집"],
                risk_level="LOW",
                scores={"impact": 30, "feasibility": 95, "risk": 15, "cost": 10, "time": 10},
            ),
            DecisionOption(
                option_id="GEN-OPT-02",
                option_type=OptionType.BALANCED,
                name="점진적 개선",
                description="단계적으로 변화 적용",
                actions=["1단계 변화 적용", "결과 평가", "2단계 진행"],
                risk_level="MEDIUM",
                scores={"impact": 60, "feasibility": 70, "risk": 35, "cost": 45, "time": 50},
            ),
            DecisionOption(
                option_id="GEN-OPT-03",
                option_type=OptionType.AGGRESSIVE,
                name="전면 개편",
                description="근본적인 변화 추진",
                actions=["전략 재수립", "조직 재편", "대규모 투자"],
                risk_level="HIGH",
                scores={"impact": 90, "feasibility": 45, "risk": 65, "cost": 80, "time": 75},
            ),
        ]

        return OptionSet(
            query_type="UNKNOWN",
            context=context,
            options=options,
            recommendation="GEN-OPT-02",
            recommendation_reason="불확실한 상황에서는 점진적 접근이 안전함",
        )

    def _determine_recommendation(
        self,
        options: list[DecisionOption],
        query_type: str,
        metrics: dict[str, float] | None = None,
    ) -> tuple[str, str]:
        """추천 대안 결정"""
        metrics = metrics or {}

        # 가중치 기반 종합 점수 계산
        weights = {
            "impact": 0.35,
            "feasibility": 0.25,
            "risk": -0.20,  # 리스크는 낮을수록 좋음
            "cost": -0.10,  # 비용도 낮을수록 좋음
            "time": -0.10,  # 시간도 적을수록 좋음
        }

        best_option = None
        best_score = float("-inf")
        reason_parts = []

        for opt in options:
            score = sum(opt.scores.get(metric, 50) * weight for metric, weight in weights.items())

            # 컨텍스트 기반 조정
            if query_type == "GO_NOGO":
                success_prob = metrics.get("success_probability", 0.5)
                _resource_fit = metrics.get("resource_fit", 0.5)  # 향후 확장용

                if opt.option_type == OptionType.AGGRESSIVE and success_prob < 0.5:
                    score -= 20
                elif opt.option_type == OptionType.CONSERVATIVE and success_prob > 0.7:
                    score -= 10

            elif query_type == "HEADCOUNT":
                utilization = metrics.get("utilization", 0.8)
                if utilization > 0.9 and opt.option_type == OptionType.CONSERVATIVE:
                    score -= 15

            if score > best_score:
                best_score = score
                best_option = opt
                reason_parts = [
                    f"영향도({opt.scores.get('impact', 0)}점)",
                    f"실현가능성({opt.scores.get('feasibility', 0)}점)",
                    f"리스크({opt.scores.get('risk', 0)}점)",
                ]

        reason = f"{best_option.name}이(가) 종합 점수가 가장 높음: {', '.join(reason_parts)}"

        return best_option.option_id, reason

    def to_dict(self, option_set: OptionSet) -> dict:
        """결과를 딕셔너리로 변환"""
        return {
            "query_type": option_set.query_type,
            "context": option_set.context,
            "options": [
                {
                    "option_id": opt.option_id,
                    "option_type": opt.option_type.value,
                    "name": opt.name,
                    "description": opt.description,
                    "actions": opt.actions,
                    "estimated_cost": opt.estimated_cost,
                    "estimated_benefit": opt.estimated_benefit,
                    "risk_level": opt.risk_level,
                    "implementation_time": opt.implementation_time,
                    "prerequisites": opt.prerequisites,
                    "trade_offs": opt.trade_offs,
                    "scores": opt.scores,
                }
                for opt in option_set.options
            ],
            "recommendation": option_set.recommendation,
            "recommendation_reason": option_set.recommendation_reason,
            "generated_at": option_set.generated_at.isoformat(),
        }


# CLI 테스트용
if __name__ == "__main__":
    agent = OptionGeneratorAgent()

    # Capacity 테스트
    result = agent.generate_options(
        query_type="CAPACITY",
        context={"bottleneck_weeks": ["W05", "W06"], "gap_fte": 3, "org_unit": "AI팀"},
    )

    print("=" * 60)
    print("CAPACITY OPTIONS")
    print("=" * 60)
    for opt in result.options:
        print(f"\n[{opt.option_type.value}] {opt.name}")
        print(f"  - {opt.description}")
        print(f"  - 리스크: {opt.risk_level}, 기간: {opt.implementation_time}")
        print(f"  - 점수: {opt.scores}")

    print(f"\n추천: {result.recommendation}")
    print(f"이유: {result.recommendation_reason}")
