0. 프레임워크 이름 제안

AXIS를 그대로 쓰거나, 조직/제품군에 맞춰 AXIS-DS(Design System) / AXIS Enterprise로 명명

핵심 정의:

AXIS = “에이전트가 주도하는 경험(Agentic Experience)을 안전하게 표현/제어하기 위한 UI 시스템”

A2UI = UI를 ‘코드’가 아니라 ‘선언적 데이터’로 전달(안전/이식성)

AG-UI = 실행 중인 에이전트와 화면을 ‘양방향 이벤트 스트림’으로 동기화(협업/상태/툴/진행률)

1. 패러다임 변화: 레가시 UI → Agentic UI
   1.1 레가시 UI가 AI 시대에 “표현”이 부족한 이유

레가시 UI는 대부분 **정적 정보 구조(메뉴/폼/페이지)**와 요청-응답 모델을 전제합니다. 반면 에이전트 기반 UX는 다음을 전제로 합니다.

장시간 실행 / 중간 산출물 스트리밍

작업 계획(Plan) → 단계 실행(Steps) → 검증/회복(Recovery)

툴 호출(도구 실행), 상태 동기화, 사용자 개입(승인/수정/중단)

불확실성/근거/출처를 UI로 표현해야 하는 요구(신뢰 레이어)

AG-UI가 지향하는 바도 “기존 REST/GraphQL식 단발성 호출로는 에이전트 앱의 스트리밍/상태성/비결정성”을 담기 어렵다는 문제의식입니다.

1.2 A2UI + AG-UI 조합의 역할 분담

A2UI: 에이전트가 플랫폼 독립적 UI 정의를 스트리밍(JSONL 기반)으로 보냄 → 클라이언트는 신뢰된 컴포넌트 카탈로그로 렌더링

AG-UI: 에이전트 런(run)의 시작/종료, 텍스트 스트리밍, 툴 실행, 상태 스냅샷/델타(JSON Patch), 활동(activity) 업데이트를 이벤트로 표준화하고 양방향 연결을 제공

결론: “A2UI는 UI를 보내는 언어”, “AG-UI는 실행/상태/상호작용의 배선” 입니다.

2. 설계 원칙: AXIS 7대 원칙 + Enterprise 확장 3대 원칙

AXIS 7대 원칙(의도 우선/점진 공개/투명 자율/휴먼 인 더 루프/적응 컨텍스트/우아한 실패/멀티모달 유동성)을 기반으로 하되, 기업 서비스/미션 크리티컬 환경에서는 아래 3가지를 추가하는 것을 권장합니다.

2.1 AXIS 7대 원칙 (요약)

Intent-First Design: 사용자는 “무엇”을 말하고, “어떻게”는 에이전트가 수행

Progressive Disclosure: 필요한 순간 필요한 정보만

Transparent Autonomy: 왜/어떻게/불확실성을 UI로 노출

Human-in-the-Loop: 중요한 단계는 사용자 확인

Adaptive Context: 사용자/역할/디바이스에 따라 UI 자동 조정

Graceful Degradation: 실패 시 복구 경로 제공

Multimodal Fluidity: 텍스트↔음성↔UI 전환 유연

2.2 Enterprise 확장 3대 원칙 (추가 제안: 제 경험적 인사이트)

Policy-Aware UX (정책 인지 UX)

“가능한 것”과 “허용되는 것”이 다릅니다.

권한/보안/내부 규정(예: 결재, 개인정보, 외부 발송)은 UX 단계에서 선제적으로 제약/안내되어야 합니다.

Auditability by Design (감사 가능성 내재화)

에이전트가 한 행동을 나중에 “재현/설명/추적”할 수 있어야 운영이 가능합니다.

로그/근거/버전/권한/승인 히스토리를 UI 모델에 포함하세요.

Trust Ladder (신뢰 사다리)

처음부터 “완전 자동”은 실패합니다.

관찰→제안→반자동→자동을 성과/안전성 지표 기반으로 올리게 하는 UX가 채택률을 결정합니다.

3. 시스템 아키텍처: “프로토콜-기반 디자인 시스템”으로 재정의
   3.1 AXIS 아키텍처 스택

AXIS는 “디자인 시스템”을 UI 컴포넌트 라이브러리로만 보지 않고, A2UI/AG-UI를 포함한 런타임 계층까지 포함합니다.

권장 레이어

User Interface Layer: Web/Mobile/Desktop 호스트 UI

A2UI Renderer Layer: A2UI UI 스펙을 실제 컴포넌트로 렌더링(카탈로그/바인딩/이벤트)

AG-UI Protocol Layer: 런/상태/메시지/툴/활동을 이벤트로 스트리밍

Transport Layer: SSE/WebSocket/HTTP 등(AG-UI는 transport-agnostic)

Agent Layer: Orchestrator + Sub-agents + Tool 실행

LLM Layer

A2UI는 플랫폼 독립적이며(클라이언트가 네이티브 위젯으로 매핑), **신뢰 경계(trust boundary)**를 넘어서 UI를 전달하기 위해 “코드가 아니라 데이터”라는 철학을 강조합니다.

3.2 “상태 모델” 설계 (AG-UI에 정합)

AG-UI는 StateSnapshot / StateDelta(JSON Patch, RFC 6902) 같은 표준 이벤트를 제공합니다.
따라서 AXIS에서는 상태를 다음 4축으로 분리하는 것이 안정적입니다.

Conversation State: thread, messages, attachments

Agent Run State: runId, stepName, phase, cancellation, retries

UI Surface State: A2UI surfaceId, component graph, form values, validation

Domain State: 업무 도메인(예: 결재 문서, 티켓, 일정, 주문)

인사이트: 레가시 UI는 “화면 단위 상태”였지만, Agentic UI는 **“컨텍스트 단위 상태(대화+실행+UI표면)”**가 기본 단위입니다.

4. 디자인 토큰: “Agent 상태/신뢰/자율성”이 1급 토큰이어야 함

AXIS 토큰 체계는 Core → Component → Semantic을 유지하되, Agentic UI에서 **Semantic 토큰의 중심이 ‘에이전트 상태’**로 이동합니다.

4.1 토큰 계층 구조

Core Tokens: 색/타이포/간격/라운드/그림자

Component Tokens: 버튼/카드/배지 등 컴포넌트별 변수

Semantic Tokens: 의미 기반(성공/경고/위험, 그리고 “Agent 상태/신뢰/자율성”)

4.2 AXIS 필수 시맨틱 토큰 3종

Agent Status Tokens (예: idle/thinking/processing/success/error/waiting-input)

Confidence Tokens (high/medium/low + threshold + requiresConfirmation)

Autonomy Level Tokens (0~3: Manual→Suggestion→Semi-Auto→Auto)

4.3 토큰 예시 (권장 네이밍)
{
"axis": {
"agent": {
"status": {
"thinking": { "color": "{color.primary.500}", "icon": "brain", "motion": "pulse" },
"processing": { "color": "{color.warning.500}", "icon": "loader", "motion": "spin" },
"error": { "color": "{color.error.500}", "icon": "alert-circle" }
}
},
"trust": {
"confidence": {
"high": { "threshold": 0.85, "label": "높은 신뢰", "indicator": "solid" },
"medium": { "threshold": 0.60, "label": "검토 권장", "indicator": "dashed" },
"low": { "threshold": 0.00, "label": "확인 필요", "indicator": "dotted", "requiresConfirmation": true }
}
}
}
}

(AXIS 문서의 토큰 구조/의도에 맞춘 형태)

5. 컴포넌트 체계: “Agent-Native + Dynamic Surface + Trust” 3축 확장

AXIS 컴포넌트 분류(Foundation/Primitives/Agent-Native/Dynamic Surfaces/Trust & Transparency/Control)를 그대로 채택하되, A2UI 카탈로그 확장 단위로 정리하면 구현이 쉬워집니다.

5.1 컴포넌트 레이어(권장)

Foundation: Typography/Color/Spacing/Icon

Primitives: Button/Input/Card/Badge/Avatar

Agent-Native (필수)

AgentMessage, ThinkingIndicator, StreamingText

ConfidenceBadge, ReasoningCard

ActionConfirmation, AutonomySlider

Dynamic Surfaces (필수)

GeneratedForm, SmartTable, ContextualPanel, InteractiveChart

Trust & Transparency (필수)

SourceAttribution, DecisionExplainer, UncertaintyIndicator, AuditTrail, FeedbackCollector

Control (필수)

AgentController(중단/재시도/롤백), InterventionPanel(사용자 개입), EmergencyStop

5.2 “컴포넌트 계약(Contract)” — A2UI/AG-UI 연결을 위한 핵심

각 컴포넌트는 단순 UI가 아니라, 아래 3가지 계약을 가집니다.

(A) Rendering Contract: A2UI payload → props 매핑 규칙

(B) Interaction Contract: 사용자 이벤트 → AG-UI로 전달되는 이벤트/액션 규칙

(C) Observability Contract: 텔레메트리(성공/실패/개입률/취소율) 메타데이터

인사이트: “컴포넌트”를 디자인 팀 산출물로 끝내지 말고, 에이전트 운영 지표가 심어지는 실행 단위로 정의해야 Agentic UX가 운영됩니다.

5.3 A2UI 카탈로그 확장(예시)

A2UI는 “클라이언트가 신뢰하는 카탈로그 컴포넌트만 렌더 가능”이라는 철학이 강합니다.
따라서 AXIS 확장 컴포넌트를 카탈로그로 선언하세요.

{
"catalogId": "axis-v1",
"extends": "https://a2ui.org/specification/v0.8-a2ui/",
"components": {
"standard": ["Text", "Button", "TextField", "Card", "Row", "Column", "List"],
"axisExtensions": [
{
"name": "AgentMessage",
"category": "agent-native",
"properties": {
"content": { "type": "string", "required": true },
"status": { "type": "enum", "values": ["streaming", "complete", "error"] },
"confidence": { "type": "number", "min": 0, "max": 1 }
}
},
{
"name": "ActionConfirmation",
"category": "control",
"properties": {
"impact": { "type": "enum", "values": ["low", "medium", "high", "critical"] },
"reversible": { "type": "boolean" }
}
}
]
}
}

(AXIS 문서의 “A2UI 표준 카탈로그 확장” 방향과 동일)

6. 인터랙션 패턴: “대화” + “동적 UI” + “진행률/상태”를 패턴으로 고정

AXIS가 제시한 패턴 6개는 실제 서비스에 바로 적용 가능한 “최소 패턴 세트”입니다.
여기에, 엔터프라이즈 적용 시 2개를 추가하면 완성도가 올라갑니다.

6.1 기본 6대 패턴 (AXIS)

Clarification Loop: 의도 불명확 → 명확화 질문 + 빠른 선택 UI

Progressive Action: 단계별 실행 + 중간 확인

Multi-Option Response: 다중 해석/해결책 제시

Context-Aware Form Generation: 대화 맥락 기반 동적 폼 생성

Streaming Data Visualization: 실시간 생성/시각화 점진 렌더링

Graceful Failure with Recovery: 실패 원인/영향/대안/재시도/수동전환 제시

6.2 추가 추천 패턴 2개 (인사이트)

Plan-Execute-Review 패턴

에이전트가 먼저 “계획(Plan)”을 카드로 제시(편집 가능)

승인 후 실행(Progressive Action)

결과는 “요약 + 근거 + 다음 행동”으로 정리
→ 사용자가 “통제감”을 갖고, 실패 시 롤백이 쉬워집니다.

Parallel Workstreams(멀티 에이전트 작업 보드)

복합 업무(예: RFP 분석 + 경쟁사 조사 + 제안서 초안 + 내부 승인)는 병렬화됩니다.

UI는 “작업 스트림(Agent 별)”을 칸반/타임라인 형태로 보여주고, 각 스트림은 AG-UI의 StepStarted/Finished + ActivitySnapshot/Delta로 업데이트하는 구조가 좋습니다.

7. 신뢰 & 투명성 시스템: “설명 가능한 UI 레이어”를 기본값으로

Agentic UX에서 신뢰는 “문구”가 아니라 컴포넌트/패턴/토큰으로 구현돼야 합니다. AXIS는 이를 Confidence Display / Source Attribution / Explainability Layers로 정리합니다.

7.1 신뢰 표시(Confidence) 원칙

숫자(0.73)보다 라벨(검토 권장) 우선

색만 쓰지 말고 색 + 텍스트(접근성)

신뢰가 낮을수록 액션을 제한(확인 버튼/추가 검증)

7.2 설명 레이어(Explainability Layers) 3단

L1 요약: 기본 표시

L2 근거: 사용자가 펼치면 근거 리스트/지표

L3 감사 모드: 로그/쿼리/모델/버전/툴 실행 기록까지(권한 기반)

7.3 AG-UI 이벤트와의 정합(운영 관점)

AG-UI는 런/스텝/툴/상태/활동을 이벤트로 표준화합니다.
따라서 “신뢰 UI”는 다음과 같이 자동 구성될 수 있습니다.

StepStarted/Finished → ThinkingIndicator(단계/진행률)

ToolCallStart/Args/Result → DecisionExplainer(무슨 도구를 왜 썼는지)

RunError → Graceful Failure 패턴 자동 트리거

StateDelta → UI/도메인 상태의 실시간 반영

8. 구현 가이드: 바로 개발 가능한 구조/가드레일
   8.1 기술/구현 포인트(표준 기반)

A2UI는 JSONL 기반 스트리밍 UI 프로토콜이며, 선언적 구조/플랫 컴포넌트 리스트/데이터-컴포넌트 분리를 통해 LLM이 생성하기 쉽게 설계되어 있습니다.

A2UI는 클라이언트 카탈로그 기반이므로, “허용 컴포넌트/액션”을 엄격히 통제할 수 있습니다(보안/브랜드/접근성).

AG-UI는 이벤트 기반 + transport-agnostic이며 SSE/WebSocket 등으로 스트리밍 가능합니다.

8.2 “AXIS Guardrails” (반드시 넣을 것)

UI Injection 방지: A2UI 카탈로그 외 컴포넌트는 렌더 거부

High-risk action gating: impact=high/critical은 ActionConfirmation 필수

권한 기반 Explainability: L3(감사 모드)는 RBAC/승인 필요

Fallback 루트: A2UI 렌더 실패 시 텍스트/레가시 화면(iframe/딥링크)로 우아하게 다운그레이드

관찰→제안→반자동→자동 신뢰 사다리 도입(자동화는 “성과로 획득”)

8.3 패키지/레포 구조(권장)

AXIS 문서의 프로젝트 구조(토큰/컴포넌트/카탈로그/패턴/도구)를 그대로 가져가면, “디자인 시스템”이 실제 제품에서 굴러갑니다.

packages/tokens : core/semantic/agent/trust 토큰 JSON

packages/components : primitives/agent-native/dynamic-surfaces/trust/control

packages/a2ui-catalog : catalog.json + renderer

packages/patterns : clarification-loop, progressive-action …

tools/a2ui-validator : 스키마/보안/제약 검증

docs/ : 원칙/패턴/예시/가이드

8.4 점진적 도입 로드맵(현실적인 전환 전략)

Phase 1 (1~2개월): 토큰+기본 컴포넌트 + A2UI 렌더러 + 단일 에이전트 PoC

Phase 2 (2~3개월): Agent-Native + Trust 시스템 + 핵심 패턴 + AG-UI 연동

Phase 3 (3~4개월): 멀티 에이전트/적응형 UI/오프라인/에러 패턴 고도화

Phase 4 (상시): 성능/접근성/사용자 피드백 기반 최적화

9. 바로 적용 가능한 “표준 시나리오” 2개 (A2UI+AG-UI UX 설계 예)
   시나리오 A: “회의 잡아줘” (동적 폼 + 승인)

사용자가 자연어로 요청

에이전트가 Context-Aware Form을 A2UI로 생성(날짜/시간/참석자/회의실)

사용자가 폼에서 선택 → AG-UI로 상태 델타 전송/동기화

에이전트가 “예약 실행” 직전 ActionConfirmation(impact=medium)

승인 시 tool call 실행, 결과는 ReasoningCard/SourceAttribution으로 요약

시나리오 B: “보고서 만들어줘” (명확화 루프 + 진행률)

Clarification Loop로 리포트 종류/기간/지표를 빠른 선택 UI로 수렴

Progressive Action으로 데이터 수집→정제→분석→시각화→문서화 단계 표시

Streaming Visualization으로 차트/인사이트가 점진 생성

마무리: 이 프레임워크의 핵심 포인트(요약)

A2UI는 “동적 UI를 안전하게 전달”(카탈로그 기반/데이터 기반/플랫폼 독립)

AG-UI는 “실행/상태/툴/진행률을 이벤트로 동기화”(양방향/스트리밍/표준 이벤트)

Agentic UX의 차별점은 “챗 UI”가 아니라

Agent-Native 컴포넌트,

Dynamic Surface,

Trust & Control 시스템을 디자인 시스템 레벨에서 제공하는 것입니다.
