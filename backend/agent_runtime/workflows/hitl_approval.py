"""
HR DSS - Human-in-the-Loop (HITL) Approval System

의사결정에 대한 인간 검토 및 승인 시스템
의사결정 로그 관리 포함
"""

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """승인 상태"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"      # 수정 후 승인
    ESCALATED = "ESCALATED"    # 상위 결재자로 에스컬레이션
    EXPIRED = "EXPIRED"        # 타임아웃
    CANCELLED = "CANCELLED"


class ApprovalLevel(Enum):
    """승인 레벨"""
    TEAM_LEAD = "TEAM_LEAD"       # 팀장급
    DEPARTMENT = "DEPARTMENT"     # 부서장급
    DIVISION = "DIVISION"         # 본부장급
    EXECUTIVE = "EXECUTIVE"       # 임원급


class DecisionType(Enum):
    """의사결정 유형"""
    CAPACITY = "CAPACITY"
    GO_NOGO = "GO_NOGO"
    HEADCOUNT = "HEADCOUNT"
    COMPETENCY_GAP = "COMPETENCY_GAP"
    OTHER = "OTHER"


@dataclass
class ApprovalRequest:
    """승인 요청"""
    request_id: str
    execution_id: str
    decision_type: DecisionType
    title: str
    summary: str
    options: list[dict[str, Any]]
    recommendation: dict[str, Any]
    impact_analysis: dict[str, Any]
    evidence: list[dict[str, Any]]
    validation_result: dict[str, Any]
    requester_id: str
    required_level: ApprovalLevel
    deadline: datetime | None = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalResponse:
    """승인 응답"""
    response_id: str
    request_id: str
    status: ApprovalStatus
    selected_option_id: str | None = None
    approver_id: str = ""
    approver_name: str = ""
    approval_level: ApprovalLevel | None = None
    rationale: str = ""
    modifications: dict[str, Any] | None = None
    conditions: list[str] = field(default_factory=list)
    responded_at: datetime = field(default_factory=datetime.now)


@dataclass
class DecisionLog:
    """의사결정 로그"""
    log_id: str
    execution_id: str
    decision_type: DecisionType
    query: str
    context_summary: str
    options_presented: list[dict[str, Any]]
    recommendation: dict[str, Any]
    final_decision: dict[str, Any]
    approval_chain: list[ApprovalResponse]
    evidence_used: list[dict[str, Any]]
    validation_score: float
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


class HITLApprovalSystem:
    """Human-in-the-Loop 승인 시스템"""

    # 의사결정 유형별 필요 승인 레벨
    APPROVAL_LEVEL_MATRIX = {
        DecisionType.CAPACITY: {
            "default": ApprovalLevel.TEAM_LEAD,
            "high_impact": ApprovalLevel.DEPARTMENT,
        },
        DecisionType.GO_NOGO: {
            "default": ApprovalLevel.DEPARTMENT,
            "high_value": ApprovalLevel.DIVISION,
        },
        DecisionType.HEADCOUNT: {
            "default": ApprovalLevel.DEPARTMENT,
            "large_count": ApprovalLevel.DIVISION,
        },
        DecisionType.COMPETENCY_GAP: {
            "default": ApprovalLevel.TEAM_LEAD,
            "strategic": ApprovalLevel.DEPARTMENT,
        },
    }

    # 에스컬레이션 경로
    ESCALATION_PATH = {
        ApprovalLevel.TEAM_LEAD: ApprovalLevel.DEPARTMENT,
        ApprovalLevel.DEPARTMENT: ApprovalLevel.DIVISION,
        ApprovalLevel.DIVISION: ApprovalLevel.EXECUTIVE,
        ApprovalLevel.EXECUTIVE: None,
    }

    def __init__(
        self,
        notification_handler: Callable[[str, dict], None] | None = None,
        approval_timeout_hours: int = 24,
    ):
        """
        Args:
            notification_handler: 알림 전송 핸들러
            approval_timeout_hours: 승인 타임아웃 시간
        """
        self.notification_handler = notification_handler
        self.approval_timeout_hours = approval_timeout_hours
        self.pending_requests: dict[str, ApprovalRequest] = {}
        self.responses: dict[str, ApprovalResponse] = {}
        self.decision_logs: dict[str, DecisionLog] = {}

    def create_approval_request(
        self,
        execution_id: str,
        decision_type: DecisionType,
        workflow_context: dict[str, Any],
        requester_id: str,
    ) -> ApprovalRequest:
        """
        승인 요청 생성

        Args:
            execution_id: 워크플로 실행 ID
            decision_type: 의사결정 유형
            workflow_context: 워크플로 컨텍스트
            requester_id: 요청자 ID

        Returns:
            ApprovalRequest: 승인 요청
        """
        request_id = f"APPROVAL-{uuid.uuid4().hex[:12].upper()}"

        # 필요 승인 레벨 결정
        required_level = self._determine_approval_level(decision_type, workflow_context)

        # 요약 생성
        summary = self._generate_summary(decision_type, workflow_context)

        request = ApprovalRequest(
            request_id=request_id,
            execution_id=execution_id,
            decision_type=decision_type,
            title=f"{decision_type.value} 의사결정 승인 요청",
            summary=summary,
            options=workflow_context.get("options", {}).get("options", []),
            recommendation={
                "option_id": workflow_context.get("options", {}).get("recommendation"),
                "reason": workflow_context.get("options", {}).get("recommendation_reason", ""),
            },
            impact_analysis=workflow_context.get("impact_analysis", {}),
            evidence=self._extract_evidence(workflow_context),
            validation_result=workflow_context.get("validation_result", {}),
            requester_id=requester_id,
            required_level=required_level,
            deadline=self._calculate_deadline(),
        )

        self.pending_requests[request_id] = request

        # 알림 전송
        self._send_notification(request)

        logger.info(f"승인 요청 생성: {request_id} (레벨: {required_level.value})")

        return request

    def process_approval(
        self,
        request_id: str,
        status: ApprovalStatus,
        approver_id: str,
        approver_name: str,
        approval_level: ApprovalLevel,
        selected_option_id: str | None = None,
        rationale: str = "",
        modifications: dict[str, Any] | None = None,
        conditions: list[str] | None = None,
    ) -> ApprovalResponse:
        """
        승인 처리 (submit_response의 별칭)

        Args:
            request_id: 요청 ID
            status: 승인 상태
            approver_id: 승인자 ID
            approver_name: 승인자 이름
            approval_level: 승인자 레벨
            selected_option_id: 선택된 대안 ID
            rationale: 승인/거절 사유
            modifications: 수정 내용
            conditions: 조건부 승인 조건

        Returns:
            ApprovalResponse: 승인 응답
        """
        return self.submit_response(
            request_id=request_id,
            status=status,
            approver_id=approver_id,
            approver_name=approver_name,
            approval_level=approval_level,
            selected_option_id=selected_option_id,
            rationale=rationale,
            modifications=modifications,
            conditions=conditions,
        )

    def submit_response(
        self,
        request_id: str,
        status: ApprovalStatus,
        approver_id: str,
        approver_name: str,
        approval_level: ApprovalLevel,
        selected_option_id: str | None = None,
        rationale: str = "",
        modifications: dict[str, Any] | None = None,
        conditions: list[str] | None = None,
    ) -> ApprovalResponse:
        """
        승인 응답 제출

        Args:
            request_id: 요청 ID
            status: 승인 상태
            approver_id: 승인자 ID
            approver_name: 승인자 이름
            approval_level: 승인자 레벨
            selected_option_id: 선택된 대안 ID
            rationale: 승인/거절 사유
            modifications: 수정 내용
            conditions: 조건부 승인 조건

        Returns:
            ApprovalResponse: 승인 응답
        """
        if request_id not in self.pending_requests:
            raise ValueError(f"승인 요청을 찾을 수 없음: {request_id}")

        request = self.pending_requests[request_id]

        # 승인 레벨 검증
        if not self._validate_approval_level(approval_level, request.required_level):
            raise ValueError(f"승인 권한 부족: {approval_level.value} < {request.required_level.value}")

        response_id = f"RESP-{uuid.uuid4().hex[:12].upper()}"

        response = ApprovalResponse(
            response_id=response_id,
            request_id=request_id,
            status=status,
            selected_option_id=selected_option_id,
            approver_id=approver_id,
            approver_name=approver_name,
            approval_level=approval_level,
            rationale=rationale,
            modifications=modifications,
            conditions=conditions or [],
        )

        self.responses[response_id] = response

        # 승인 완료 시 대기 목록에서 제거
        if status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED, ApprovalStatus.MODIFIED]:
            del self.pending_requests[request_id]

        logger.info(f"승인 응답: {response_id} - {status.value} by {approver_name}")

        return response

    def escalate_request(
        self,
        request_id: str,
        escalation_reason: str,
        escalated_by: str,
    ) -> ApprovalRequest:
        """
        승인 요청 에스컬레이션

        Args:
            request_id: 요청 ID
            escalation_reason: 에스컬레이션 사유
            escalated_by: 에스컬레이션 수행자

        Returns:
            ApprovalRequest: 업데이트된 승인 요청
        """
        if request_id not in self.pending_requests:
            raise ValueError(f"승인 요청을 찾을 수 없음: {request_id}")

        request = self.pending_requests[request_id]
        current_level = request.required_level
        next_level = self.ESCALATION_PATH.get(current_level)

        if not next_level:
            raise ValueError(f"더 이상 에스컬레이션 불가: {current_level.value}")

        # 에스컬레이션 응답 기록
        response = ApprovalResponse(
            response_id=f"RESP-ESC-{uuid.uuid4().hex[:8].upper()}",
            request_id=request_id,
            status=ApprovalStatus.ESCALATED,
            approver_id=escalated_by,
            rationale=escalation_reason,
        )
        self.responses[response.response_id] = response

        # 요청 레벨 업데이트
        request.required_level = next_level
        request.deadline = self._calculate_deadline()
        request.metadata["escalation_history"] = request.metadata.get("escalation_history", [])
        request.metadata["escalation_history"].append({
            "from_level": current_level.value,
            "to_level": next_level.value,
            "reason": escalation_reason,
            "escalated_by": escalated_by,
            "timestamp": datetime.now().isoformat(),
        })

        # 새 승인자에게 알림
        self._send_notification(request)

        logger.info(f"에스컬레이션: {request_id} ({current_level.value} -> {next_level.value})")

        return request

    def create_decision_log(
        self,
        execution_id: str,
        decision_type: DecisionType,
        workflow_context: dict[str, Any],
        approval_responses: list[ApprovalResponse],
    ) -> DecisionLog:
        """
        의사결정 로그 생성

        Args:
            execution_id: 실행 ID
            decision_type: 의사결정 유형
            workflow_context: 워크플로 컨텍스트
            approval_responses: 승인 응답 목록

        Returns:
            DecisionLog: 의사결정 로그
        """
        log_id = f"DECISION-{uuid.uuid4().hex[:12].upper()}"

        # 최종 결정 추출
        final_response = next(
            (r for r in reversed(approval_responses)
             if r.status in [ApprovalStatus.APPROVED, ApprovalStatus.MODIFIED]),
            None
        )

        final_decision = {}
        if final_response:
            final_decision = {
                "selected_option_id": final_response.selected_option_id,
                "approver": final_response.approver_name,
                "approval_level": final_response.approval_level.value if final_response.approval_level else None,
                "rationale": final_response.rationale,
                "modifications": final_response.modifications,
                "conditions": final_response.conditions,
                "approved_at": final_response.responded_at.isoformat(),
            }

        # 검증 점수
        validation_result = workflow_context.get("validation_result", {})
        validation_score = 1.0 - validation_result.get("hallucination_risk", 0.0)

        log = DecisionLog(
            log_id=log_id,
            execution_id=execution_id,
            decision_type=decision_type,
            query=workflow_context.get("user_query", ""),
            context_summary=self._generate_context_summary(workflow_context),
            options_presented=workflow_context.get("options", {}).get("options", []),
            recommendation={
                "option_id": workflow_context.get("options", {}).get("recommendation"),
                "reason": workflow_context.get("options", {}).get("recommendation_reason", ""),
            },
            final_decision=final_decision,
            approval_chain=approval_responses,
            evidence_used=self._extract_evidence(workflow_context),
            validation_score=validation_score,
        )

        self.decision_logs[log_id] = log

        logger.info(f"의사결정 로그 생성: {log_id}")

        return log

    def get_pending_requests(
        self,
        approver_level: ApprovalLevel | None = None,
    ) -> list[ApprovalRequest]:
        """
        대기 중인 승인 요청 조회

        Args:
            approver_level: 필터링할 승인 레벨

        Returns:
            list[ApprovalRequest]: 대기 중인 승인 요청 목록
        """
        requests = list(self.pending_requests.values())

        if approver_level:
            requests = [
                r for r in requests
                if self._validate_approval_level(approver_level, r.required_level)
            ]

        # 마감일 순 정렬
        requests.sort(key=lambda r: r.deadline or datetime.max)

        return requests

    def get_decision_logs(
        self,
        decision_type: DecisionType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[DecisionLog]:
        """
        의사결정 로그 조회

        Args:
            decision_type: 필터링할 의사결정 유형
            start_date: 시작 날짜
            end_date: 종료 날짜
            limit: 최대 개수

        Returns:
            list[DecisionLog]: 의사결정 로그 목록
        """
        logs = list(self.decision_logs.values())

        if decision_type:
            logs = [log for log in logs if log.decision_type == decision_type]

        if start_date:
            logs = [log for log in logs if log.created_at >= start_date]

        if end_date:
            logs = [log for log in logs if log.created_at <= end_date]

        # 최신순 정렬
        logs.sort(key=lambda log: log.created_at, reverse=True)

        return logs[:limit]

    def get_approval_statistics(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """
        승인 통계 조회

        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            dict: 승인 통계
        """
        responses = list(self.responses.values())

        if start_date:
            responses = [r for r in responses if r.responded_at >= start_date]
        if end_date:
            responses = [r for r in responses if r.responded_at <= end_date]

        total = len(responses)
        if total == 0:
            return {"total": 0, "message": "데이터 없음"}

        approved = sum(1 for r in responses if r.status == ApprovalStatus.APPROVED)
        rejected = sum(1 for r in responses if r.status == ApprovalStatus.REJECTED)
        modified = sum(1 for r in responses if r.status == ApprovalStatus.MODIFIED)
        escalated = sum(1 for r in responses if r.status == ApprovalStatus.ESCALATED)

        return {
            "total": total,
            "approved": approved,
            "rejected": rejected,
            "modified": modified,
            "escalated": escalated,
            "approval_rate": round(approved / total * 100, 1),
            "modification_rate": round(modified / total * 100, 1),
            "escalation_rate": round(escalated / total * 100, 1),
            "by_level": self._count_by_level(responses),
            "by_type": self._count_by_type(responses),
        }

    # ============================================================
    # Private Methods
    # ============================================================

    def _determine_approval_level(
        self,
        decision_type: DecisionType,
        context: dict[str, Any],
    ) -> ApprovalLevel:
        """필요 승인 레벨 결정"""
        level_config = self.APPROVAL_LEVEL_MATRIX.get(
            decision_type,
            {"default": ApprovalLevel.TEAM_LEAD}
        )

        # 영향도 기반 레벨 결정 (향후 확장용)
        _impact_analysis = context.get("impact_analysis", {})

        if decision_type == DecisionType.GO_NOGO:
            deal_value = context.get("opportunity", {}).get("deal_value", 0)
            if deal_value > 1000000000:  # 10억 이상
                return level_config.get("high_value", ApprovalLevel.DIVISION)

        elif decision_type == DecisionType.HEADCOUNT:
            headcount = context.get("requested_headcount", 0)
            if headcount >= 5:
                return level_config.get("large_count", ApprovalLevel.DIVISION)

        elif decision_type == DecisionType.CAPACITY:
            gap_fte = context.get("gap_fte", 0)
            if gap_fte >= 5:
                return level_config.get("high_impact", ApprovalLevel.DEPARTMENT)

        return level_config.get("default", ApprovalLevel.TEAM_LEAD)

    def _validate_approval_level(
        self,
        approver_level: ApprovalLevel,
        required_level: ApprovalLevel,
    ) -> bool:
        """승인 레벨 검증"""
        level_order = [
            ApprovalLevel.TEAM_LEAD,
            ApprovalLevel.DEPARTMENT,
            ApprovalLevel.DIVISION,
            ApprovalLevel.EXECUTIVE,
        ]

        approver_idx = level_order.index(approver_level)
        required_idx = level_order.index(required_level)

        return approver_idx >= required_idx

    def _generate_summary(
        self,
        decision_type: DecisionType,
        context: dict[str, Any],
    ) -> str:
        """승인 요청 요약 생성"""
        summaries = {
            DecisionType.CAPACITY: "가동률 병목 해결을 위한 인력 배치 의사결정",
            DecisionType.GO_NOGO: "프로젝트 수주 여부 의사결정",
            DecisionType.HEADCOUNT: "인력 증원 승인 의사결정",
            DecisionType.COMPETENCY_GAP: "역량 갭 해소 방안 의사결정",
        }

        base_summary = summaries.get(decision_type, "의사결정 요청")

        # 컨텍스트 기반 추가 정보
        options = context.get("options", {}).get("options", [])
        if options:
            recommendation = context.get("options", {}).get("recommendation", "")
            rec_opt = next((o for o in options if o.get("option_id") == recommendation), None)
            if rec_opt:
                base_summary += f"\n추천 대안: {rec_opt.get('name', '')} ({rec_opt.get('option_type', '')})"

        return base_summary

    def _generate_context_summary(self, context: dict[str, Any]) -> str:
        """컨텍스트 요약 생성"""
        parts = []

        if "user_query" in context:
            parts.append(f"질문: {context['user_query']}")

        if "org_unit_id" in context:
            parts.append(f"대상 조직: {context['org_unit_id']}")

        kg_results = context.get("kg_results", {})
        if kg_results:
            if "utilization" in kg_results:
                parts.append(f"현재 가동률: {kg_results['utilization'].get('current', 'N/A')}")
            if "bottleneck_weeks" in kg_results:
                parts.append(f"병목 구간: {', '.join(kg_results['bottleneck_weeks'])}")

        return "\n".join(parts)

    def _extract_evidence(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """컨텍스트에서 증거 추출"""
        evidence = []

        kg_results = context.get("kg_results", {})
        if kg_results:
            evidence.append({
                "type": "KG_QUERY",
                "source": "Knowledge Graph",
                "data": kg_results,
            })

        impact_analysis = context.get("impact_analysis", {})
        if impact_analysis:
            evidence.append({
                "type": "SIMULATION",
                "source": "Impact Simulator",
                "data": impact_analysis,
            })

        probabilities = context.get("probabilities", {})
        if probabilities:
            evidence.append({
                "type": "PREDICTION",
                "source": "Success Probability",
                "data": probabilities,
            })

        return evidence

    def _calculate_deadline(self) -> datetime:
        """승인 마감일 계산"""
        from datetime import timedelta
        return datetime.now() + timedelta(hours=self.approval_timeout_hours)

    def _send_notification(self, request: ApprovalRequest) -> None:
        """승인 요청 알림 전송"""
        if self.notification_handler:
            self.notification_handler(
                request.required_level.value,
                {
                    "request_id": request.request_id,
                    "title": request.title,
                    "summary": request.summary,
                    "deadline": request.deadline.isoformat() if request.deadline else None,
                }
            )

    def _count_by_level(self, responses: list[ApprovalResponse]) -> dict[str, int]:
        """승인 레벨별 카운트"""
        counts = {}
        for r in responses:
            if r.approval_level:
                level = r.approval_level.value
                counts[level] = counts.get(level, 0) + 1
        return counts

    def _count_by_type(self, responses: list[ApprovalResponse]) -> dict[str, int]:
        """상태별 카운트"""
        counts = {}
        for r in responses:
            status = r.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts

    # ============================================================
    # Serialization Methods
    # ============================================================

    def request_to_dict(self, request: ApprovalRequest) -> dict:
        """승인 요청을 딕셔너리로 변환"""
        return {
            "request_id": request.request_id,
            "execution_id": request.execution_id,
            "decision_type": request.decision_type.value,
            "title": request.title,
            "summary": request.summary,
            "options": request.options,
            "recommendation": request.recommendation,
            "impact_analysis": request.impact_analysis,
            "evidence_count": len(request.evidence),
            "validation_result": request.validation_result,
            "requester_id": request.requester_id,
            "required_level": request.required_level.value,
            "deadline": request.deadline.isoformat() if request.deadline else None,
            "created_at": request.created_at.isoformat(),
        }

    def response_to_dict(self, response: ApprovalResponse) -> dict:
        """승인 응답을 딕셔너리로 변환"""
        return {
            "response_id": response.response_id,
            "request_id": response.request_id,
            "status": response.status.value,
            "selected_option_id": response.selected_option_id,
            "approver_id": response.approver_id,
            "approver_name": response.approver_name,
            "approval_level": response.approval_level.value if response.approval_level else None,
            "rationale": response.rationale,
            "modifications": response.modifications,
            "conditions": response.conditions,
            "responded_at": response.responded_at.isoformat(),
        }

    def log_to_dict(self, log: DecisionLog) -> dict:
        """의사결정 로그를 딕셔너리로 변환"""
        return {
            "log_id": log.log_id,
            "execution_id": log.execution_id,
            "decision_type": log.decision_type.value,
            "query": log.query,
            "context_summary": log.context_summary,
            "options_presented": log.options_presented,
            "recommendation": log.recommendation,
            "final_decision": log.final_decision,
            "approval_chain": [
                self.response_to_dict(r) for r in log.approval_chain
            ],
            "evidence_count": len(log.evidence_used),
            "validation_score": log.validation_score,
            "created_at": log.created_at.isoformat(),
        }


# CLI 테스트용
if __name__ == "__main__":
    import json

    system = HITLApprovalSystem()

    # 승인 요청 생성
    context = {
        "user_query": "향후 12주간 AI팀의 가동률 병목 구간과 해결 방안은?",
        "org_unit_id": "ORG-AI-001",
        "kg_results": {
            "utilization": {"current": 0.85},
            "bottleneck_weeks": ["W05", "W06"],
            "gap_fte": 2.5,
        },
        "options": {
            "options": [
                {"option_id": "OPT-01", "name": "내부 재배치", "option_type": "CONSERVATIVE"},
                {"option_id": "OPT-02", "name": "외부 인력 활용", "option_type": "BALANCED"},
                {"option_id": "OPT-03", "name": "정규직 채용", "option_type": "AGGRESSIVE"},
            ],
            "recommendation": "OPT-02",
            "recommendation_reason": "비용 대비 효과 최적",
        },
        "impact_analysis": {"baseline": {"utilization": 0.85}},
        "validation_result": {"hallucination_risk": 0.08},
    }

    print("=" * 60)
    print("HITL APPROVAL SYSTEM TEST")
    print("=" * 60)

    # 승인 요청 생성
    request = system.create_approval_request(
        execution_id="EXEC-001",
        decision_type=DecisionType.CAPACITY,
        workflow_context=context,
        requester_id="user@example.com",
    )
    print("\n[승인 요청]")
    print(json.dumps(system.request_to_dict(request), indent=2, ensure_ascii=False))

    # 승인 응답 제출
    response = system.submit_response(
        request_id=request.request_id,
        status=ApprovalStatus.APPROVED,
        approver_id="manager@example.com",
        approver_name="김팀장",
        approval_level=ApprovalLevel.TEAM_LEAD,
        selected_option_id="OPT-02",
        rationale="균형잡힌 접근 방식이 현 상황에 적합함",
        conditions=["외주 인력 품질 관리 필수", "3개월 후 재검토"],
    )
    print("\n[승인 응답]")
    print(json.dumps(system.response_to_dict(response), indent=2, ensure_ascii=False))

    # 의사결정 로그 생성
    log = system.create_decision_log(
        execution_id="EXEC-001",
        decision_type=DecisionType.CAPACITY,
        workflow_context=context,
        approval_responses=[response],
    )
    print("\n[의사결정 로그]")
    print(json.dumps(system.log_to_dict(log), indent=2, ensure_ascii=False))

    # 통계
    print("\n[승인 통계]")
    stats = system.get_approval_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))


# =============================================================================
# Backward Compatibility Alias
# =============================================================================

# 테스트 호환성을 위한 alias
HITLApprovalManager = HITLApprovalSystem
