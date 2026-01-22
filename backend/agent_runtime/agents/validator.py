"""
HR DSS - Validator Agent

근거 없는 주장을 탐지하고 주장-근거 연결을 검증하는 에이전트
환각(Hallucination) 방지를 위한 검증 수행
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ClaimType(Enum):
    """주장 유형"""

    FACTUAL = "FACTUAL"  # 사실적 주장
    NUMERICAL = "NUMERICAL"  # 수치적 주장
    COMPARATIVE = "COMPARATIVE"  # 비교 주장
    PREDICTIVE = "PREDICTIVE"  # 예측 주장
    RECOMMENDATION = "RECOMMENDATION"  # 추천 주장


class EvidenceType(Enum):
    """근거 유형"""

    DATA_POINT = "DATA_POINT"  # 데이터 포인트
    CALCULATION = "CALCULATION"  # 계산 결과
    HISTORICAL = "HISTORICAL"  # 과거 사례
    RULE = "RULE"  # 규칙/정책
    EXTERNAL = "EXTERNAL"  # 외부 소스


class ValidationStatus(Enum):
    """검증 상태"""

    VERIFIED = "VERIFIED"  # 근거 있음
    PARTIAL = "PARTIAL"  # 부분적 근거
    UNVERIFIED = "UNVERIFIED"  # 근거 없음 (환각 위험)
    ASSUMPTION = "ASSUMPTION"  # 가정으로 표시됨


@dataclass
class EvidenceLink:
    """근거 연결"""

    evidence_id: str
    evidence_type: EvidenceType
    source: str
    description: str
    value: Any = None
    confidence: float = 1.0
    timestamp: datetime | None = None


@dataclass
class Claim:
    """주장"""

    claim_id: str
    claim_type: ClaimType
    text: str
    extracted_values: dict[str, Any] = field(default_factory=dict)


@dataclass
class ClaimValidation:
    """주장 검증 결과"""

    claim: Claim
    status: ValidationStatus
    evidence_links: list[EvidenceLink]
    confidence: float
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """전체 검증 결과"""

    total_claims: int
    verified_claims: int
    partial_claims: int
    unverified_claims: int
    assumption_claims: int
    evidence_link_rate: float  # 근거 연결률
    hallucination_risk: float  # 환각 위험도
    validations: list[ClaimValidation]
    overall_issues: list[str]
    validated_at: datetime = field(default_factory=datetime.now)


class ValidatorAgent:
    """검증 에이전트"""

    # 주장 패턴 (수치, 비교, 예측 등)
    CLAIM_PATTERNS = {
        ClaimType.NUMERICAL: [
            r"(\d+(?:\.\d+)?)\s*(?:명|FTE|%|원|건|주)",
            r"약\s*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*(?:증가|감소|개선)",
        ],
        ClaimType.COMPARATIVE: [
            r"보다\s*(?:높|낮|많|적|크|작)",
            r"(?:최고|최저|가장)",
            r"대비\s*(\d+(?:\.\d+)?)\s*%",
        ],
        ClaimType.PREDICTIVE: [
            r"(?:예상|예측|전망)",
            r"(?:될\s*것|할\s*것|일\s*것)",
            r"(?:가능성|확률)이?\s*(\d+(?:\.\d+)?)",
        ],
        ClaimType.RECOMMENDATION: [
            r"(?:추천|권장|제안)",
            r"(?:하는\s*것이\s*좋|해야\s*함)",
            r"(?:필요함|필요합니다)",
        ],
    }

    # 불확실성 표현
    UNCERTAINTY_MARKERS = [
        "약",
        "대략",
        "추정",
        "예상",
        "아마",
        "가능성",
        "might",
        "may",
        "could",
        "probably",
        "likely",
    ]

    def __init__(self, kg_client: Any = None):
        """
        Args:
            kg_client: Knowledge Graph 클라이언트 (근거 조회용)
        """
        self.kg_client = kg_client

    def validate(
        self,
        response_text: str,
        available_evidence: list[dict] | None = None,
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """
        응답 텍스트의 주장을 검증

        Args:
            response_text: 검증할 응답 텍스트
            available_evidence: 사용 가능한 근거 목록
            context: 추가 컨텍스트

        Returns:
            ValidationResult: 검증 결과
        """
        available_evidence = available_evidence or []
        context = context or {}

        # 1. 주장 추출
        claims = self._extract_claims(response_text)

        # 2. 각 주장 검증
        validations = []
        for claim in claims:
            validation = self._validate_claim(claim, available_evidence, context)
            validations.append(validation)

        # 3. 전체 통계 계산
        total = len(validations)
        verified = sum(1 for v in validations if v.status == ValidationStatus.VERIFIED)
        partial = sum(1 for v in validations if v.status == ValidationStatus.PARTIAL)
        unverified = sum(1 for v in validations if v.status == ValidationStatus.UNVERIFIED)
        assumption = sum(1 for v in validations if v.status == ValidationStatus.ASSUMPTION)

        evidence_rate = (verified + partial * 0.5) / total if total > 0 else 1.0
        hallucination_risk = unverified / total if total > 0 else 0.0

        # 4. 전체 이슈 수집
        overall_issues = self._collect_overall_issues(validations)

        return ValidationResult(
            total_claims=total,
            verified_claims=verified,
            partial_claims=partial,
            unverified_claims=unverified,
            assumption_claims=assumption,
            evidence_link_rate=round(evidence_rate, 3),
            hallucination_risk=round(hallucination_risk, 3),
            validations=validations,
            overall_issues=overall_issues,
        )

    def _extract_claims(self, text: str) -> list[Claim]:
        """텍스트에서 주장 추출"""
        claims = []
        sentences = re.split(r"[.。!?]\s*", text)

        for idx, sentence in enumerate(sentences):
            if not sentence.strip():
                continue

            claim_type = self._classify_claim(sentence)
            extracted_values = self._extract_values(sentence, claim_type)

            claim = Claim(
                claim_id=f"CLM-{idx + 1:03d}",
                claim_type=claim_type,
                text=sentence.strip(),
                extracted_values=extracted_values,
            )
            claims.append(claim)

        return claims

    def _classify_claim(self, text: str) -> ClaimType:
        """주장 유형 분류"""
        for claim_type, patterns in self.CLAIM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return claim_type

        return ClaimType.FACTUAL

    def _extract_values(self, text: str, claim_type: ClaimType) -> dict[str, Any]:
        """주장에서 값 추출"""
        values = {}

        # 숫자 추출
        numbers = re.findall(r"(\d+(?:\.\d+)?)", text)
        if numbers:
            values["numbers"] = [float(n) for n in numbers]

        # 백분율 추출
        percentages = re.findall(r"(\d+(?:\.\d+)?)\s*%", text)
        if percentages:
            values["percentages"] = [float(p) for p in percentages]

        # 기간 추출
        periods = re.findall(r"(\d+)\s*(?:주|개월|년)", text)
        if periods:
            values["periods"] = periods

        # 불확실성 표시 확인
        has_uncertainty = any(marker in text.lower() for marker in self.UNCERTAINTY_MARKERS)
        values["has_uncertainty_marker"] = has_uncertainty

        return values

    def _validate_claim(
        self, claim: Claim, available_evidence: list[dict], context: dict[str, Any]
    ) -> ClaimValidation:
        """단일 주장 검증"""
        evidence_links = []
        issues = []
        suggestions = []

        # 1. 근거 매칭
        matching_evidence = self._find_matching_evidence(claim, available_evidence, context)

        for ev in matching_evidence:
            evidence_links.append(
                EvidenceLink(
                    evidence_id=ev.get("evidence_id", "EV-UNKNOWN"),
                    evidence_type=EvidenceType(ev.get("type", "DATA_POINT")),
                    source=ev.get("source", "Unknown"),
                    description=ev.get("description", ""),
                    value=ev.get("value"),
                    confidence=ev.get("confidence", 1.0),
                )
            )

        # 2. 검증 상태 결정
        status, confidence = self._determine_validation_status(claim, evidence_links, context)

        # 3. 이슈 및 제안 생성
        if status == ValidationStatus.UNVERIFIED:
            issues.append(f"주장 '{claim.text[:50]}...'에 대한 근거를 찾을 수 없습니다.")
            suggestions.append("KG에서 관련 데이터를 조회하거나 가정임을 명시하세요.")

        elif status == ValidationStatus.PARTIAL:
            issues.append("주장의 일부만 근거가 있습니다.")
            suggestions.append("추가 근거를 제시하거나 확실하지 않은 부분을 표시하세요.")

        # 수치 검증
        if claim.claim_type == ClaimType.NUMERICAL:
            validation_issues = self._validate_numerical_claim(claim, evidence_links, context)
            issues.extend(validation_issues)

        return ClaimValidation(
            claim=claim,
            status=status,
            evidence_links=evidence_links,
            confidence=confidence,
            issues=issues,
            suggestions=suggestions,
        )

    def _find_matching_evidence(
        self, claim: Claim, available_evidence: list[dict], context: dict[str, Any]
    ) -> list[dict]:
        """주장에 맞는 근거 찾기"""
        matching = []

        claim_text_lower = claim.text.lower()
        claim_numbers = claim.extracted_values.get("numbers", [])

        for ev in available_evidence:
            ev_text = str(ev.get("description", "")).lower()
            ev_value = ev.get("value")

            # 텍스트 유사성 체크 (간단한 키워드 매칭)
            text_match = any(
                keyword in claim_text_lower for keyword in ev_text.split() if len(keyword) > 2
            )

            # 수치 매칭 체크
            value_match = False
            if ev_value is not None and claim_numbers:
                try:
                    ev_num = float(ev_value)
                    # 10% 이내 오차 허용
                    value_match = any(abs(n - ev_num) / max(ev_num, 1) < 0.1 for n in claim_numbers)
                except (ValueError, TypeError):
                    pass

            if text_match or value_match:
                matching.append(ev)

        return matching

    def _determine_validation_status(
        self, claim: Claim, evidence_links: list[EvidenceLink], context: dict[str, Any]
    ) -> tuple[ValidationStatus, float]:
        """검증 상태 결정"""

        # 불확실성 표시가 있으면 가정으로 처리
        if claim.extracted_values.get("has_uncertainty_marker"):
            if evidence_links:
                return ValidationStatus.VERIFIED, 0.9
            else:
                return ValidationStatus.ASSUMPTION, 0.7

        # 근거 수에 따른 상태 결정
        if len(evidence_links) >= 2:
            return ValidationStatus.VERIFIED, 0.95
        elif len(evidence_links) == 1:
            confidence = evidence_links[0].confidence
            if confidence >= 0.8:
                return ValidationStatus.VERIFIED, confidence
            else:
                return ValidationStatus.PARTIAL, confidence
        else:
            # 예측 주장은 불확실성 허용
            if claim.claim_type == ClaimType.PREDICTIVE:
                return ValidationStatus.ASSUMPTION, 0.5
            return ValidationStatus.UNVERIFIED, 0.2

    def _validate_numerical_claim(
        self, claim: Claim, evidence_links: list[EvidenceLink], context: dict[str, Any]
    ) -> list[str]:
        """수치 주장 추가 검증"""
        issues = []

        claim_numbers = claim.extracted_values.get("numbers", [])

        for num in claim_numbers:
            # 비현실적인 값 체크
            if num > 1000000000:  # 10억 이상
                issues.append(f"수치 {num:,.0f}이 비정상적으로 큽니다. 단위를 확인하세요.")

            # 백분율 범위 체크
            if "%" in claim.text or "퍼센트" in claim.text:
                if num > 100:
                    issues.append(f"백분율 {num}%가 100%를 초과합니다.")

        # 근거 값과 비교
        for ev in evidence_links:
            if ev.value is not None:
                try:
                    ev_num = float(ev.value)
                    for claim_num in claim_numbers:
                        diff = abs(claim_num - ev_num)
                        if ev_num != 0 and diff / ev_num > 0.2:
                            issues.append(
                                f"주장 값 {claim_num}과 근거 값 {ev_num}의 차이가 20% 이상입니다."
                            )
                except (ValueError, TypeError):
                    pass

        return issues

    def _collect_overall_issues(self, validations: list[ClaimValidation]) -> list[str]:
        """전체 이슈 수집"""
        issues = []

        unverified_count = sum(1 for v in validations if v.status == ValidationStatus.UNVERIFIED)

        if unverified_count > 0:
            issues.append(f"{unverified_count}개의 주장에 근거가 없습니다 (환각 위험).")

        low_confidence = [v for v in validations if v.confidence < 0.5]
        if low_confidence:
            issues.append(f"{len(low_confidence)}개의 주장이 낮은 신뢰도를 보입니다.")

        return issues

    def create_evidence_report(self, result: ValidationResult) -> str:
        """근거 보고서 생성"""
        lines = []
        lines.append("=" * 60)
        lines.append("       VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append(f"검증 시간: {result.validated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("SUMMARY")
        lines.append("-" * 60)
        lines.append(f"총 주장 수: {result.total_claims}")
        lines.append(f"  - 검증됨: {result.verified_claims}")
        lines.append(f"  - 부분 검증: {result.partial_claims}")
        lines.append(f"  - 미검증: {result.unverified_claims}")
        lines.append(f"  - 가정: {result.assumption_claims}")
        lines.append(f"근거 연결률: {result.evidence_link_rate * 100:.1f}%")
        lines.append(f"환각 위험도: {result.hallucination_risk * 100:.1f}%")
        lines.append("")

        if result.overall_issues:
            lines.append("-" * 60)
            lines.append("ISSUES")
            lines.append("-" * 60)
            for issue in result.overall_issues:
                lines.append(f"  [!] {issue}")
            lines.append("")

        lines.append("-" * 60)
        lines.append("CLAIM DETAILS")
        lines.append("-" * 60)

        for v in result.validations:
            status_icon = {
                ValidationStatus.VERIFIED: "[OK]",
                ValidationStatus.PARTIAL: "[??]",
                ValidationStatus.UNVERIFIED: "[NG]",
                ValidationStatus.ASSUMPTION: "[--]",
            }.get(v.status, "[??]")

            lines.append(f"\n{status_icon} {v.claim.claim_id} ({v.claim.claim_type.value})")
            lines.append(
                f'    "{v.claim.text[:80]}..."'
                if len(v.claim.text) > 80
                else f'    "{v.claim.text}"'
            )
            lines.append(f"    상태: {v.status.value}, 신뢰도: {v.confidence:.2f}")

            if v.evidence_links:
                lines.append("    근거:")
                for ev in v.evidence_links:
                    lines.append(f"      - [{ev.evidence_type.value}] {ev.description}")

            if v.issues:
                for issue in v.issues:
                    lines.append(f"    [!] {issue}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def to_dict(self, result: ValidationResult) -> dict:
        """결과를 딕셔너리로 변환"""
        return {
            "total_claims": result.total_claims,
            "verified_claims": result.verified_claims,
            "partial_claims": result.partial_claims,
            "unverified_claims": result.unverified_claims,
            "assumption_claims": result.assumption_claims,
            "evidence_link_rate": result.evidence_link_rate,
            "hallucination_risk": result.hallucination_risk,
            "validations": [
                {
                    "claim_id": v.claim.claim_id,
                    "claim_type": v.claim.claim_type.value,
                    "claim_text": v.claim.text,
                    "status": v.status.value,
                    "confidence": v.confidence,
                    "evidence_count": len(v.evidence_links),
                    "evidence_links": [
                        {
                            "evidence_id": ev.evidence_id,
                            "type": ev.evidence_type.value,
                            "source": ev.source,
                            "description": ev.description,
                        }
                        for ev in v.evidence_links
                    ],
                    "issues": v.issues,
                    "suggestions": v.suggestions,
                }
                for v in result.validations
            ],
            "overall_issues": result.overall_issues,
            "validated_at": result.validated_at.isoformat(),
        }


# CLI 테스트용
if __name__ == "__main__":
    agent = ValidatorAgent()

    test_response = """
    향후 12주간 AI팀의 가동률은 약 92%로 예상됩니다.
    현재 가용 인력은 8명이며, 필요 인력은 10명입니다.
    이는 지난 분기 대비 15% 증가한 수치입니다.
    따라서 2명의 추가 인력 확보가 필요합니다.
    외주 활용 시 비용은 약 4천만원이 예상됩니다.
    성공 확률은 75%로 추정됩니다.
    """

    available_evidence = [
        {
            "evidence_id": "EV-001",
            "type": "DATA_POINT",
            "source": "HR System",
            "description": "AI팀 가용 인력 8명",
            "value": 8,
            "confidence": 1.0,
        },
        {
            "evidence_id": "EV-002",
            "type": "CALCULATION",
            "source": "Capacity Model",
            "description": "예상 가동률 92%",
            "value": 92,
            "confidence": 0.85,
        },
        {
            "evidence_id": "EV-003",
            "type": "DATA_POINT",
            "source": "TMS",
            "description": "필요 인력 10 FTE",
            "value": 10,
            "confidence": 1.0,
        },
    ]

    result = agent.validate(test_response, available_evidence)
    report = agent.create_evidence_report(result)
    print(report)
