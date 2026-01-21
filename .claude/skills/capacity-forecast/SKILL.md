# Capacity Forecast Skill

12주 가동률 병목 예측 분석을 수행합니다. (유스케이스 A-1)

## 트리거

- `/capacity-forecast` 명령
- "가동률 예측", "병목 분석", "리소스 부족" 프롬프트

## 실행 흐름

```
1단계: 질문 분해
    ↓
2단계: 데이터 조회
    ↓
3단계: 가동률 시뮬레이션
    ↓
4단계: 병목 분석
    ↓
5단계: 결과 시각화
```

## 실행 단계

### 1단계: 질문 분해

query-decomposition 에이전트를 호출하여 질문을 분해합니다.

**추출 항목:**
- 목표: 가동률 예측, 병목 식별
- 제약: 조직 범위, 임계값
- 기간: 향후 N주

### 2단계: 데이터 조회

Knowledge Graph에서 필요한 데이터를 조회합니다.

**조회 데이터:**
```cypher
// 팀별 가용 시간
MATCH (t:Team)-[:HAS_MEMBER]->(e:Employee)
RETURN t.name, sum(e.available_hours) as capacity

// 프로젝트 수요
MATCH (p:Project)-[:REQUIRES]->(a:Allocation)
WHERE a.start_date <= date() + duration('P12W')
RETURN p.name, a.team, a.required_hours

// 현재 배정
MATCH (t:Team)-[:ALLOCATED_TO]->(p:Project)
RETURN t.name, sum(p.allocated_hours) as allocated
```

### 3단계: 가동률 시뮬레이션

impact-simulator 에이전트를 호출하여 시뮬레이션합니다.

**계산 공식:**
```
utilization_rate = allocated_hours / available_hours
bottleneck = utilization_rate > 0.9
```

### 4단계: 병목 분석

병목 원인을 분석합니다.

**분석 항목:**
| 원인 유형 | 설명 |
|----------|------|
| 수요 집중 | 특정 주차에 프로젝트 집중 |
| 역량 부족 | 특정 스킬 보유 인력 부족 |
| 비효율 배치 | 역량 미스매치 |

### 5단계: 결과 시각화

GraphViewer 컴포넌트용 데이터를 생성합니다.

**시각화 데이터:**
```json
{
  "chart_type": "heatmap",
  "x_axis": "week",
  "y_axis": "team",
  "values": "utilization_rate",
  "threshold": 0.9
}
```

## 자동 판단 로직

### 병목 심각도 판정

1. **경미 (Yellow)**:
   - 가동률 80-90%
   - 1-2주 발생

2. **심각 (Red)**:
   - 가동률 90% 초과
   - 3주 이상 연속

3. **위험 (Critical)**:
   - 가동률 100% 초과
   - 대체 인력 없음

## 출력 예시

```
🔄 Capacity Forecast 시작...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 1. 분석 범위
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

기간: 2025-01-22 ~ 2025-04-16 (12주)
범위: 전사 (5개 본부, 20개 팀)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 2. 가동률 예측
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| 본부 | 팀 | W1 | W2 | W3 | ... | W12 |
|------|-----|----|----|----| --- |-----|
| 디지털혁신 | AI팀 | 85% | 92% | 96% | ... | 88% |
| 디지털혁신 | 데이터팀 | 78% | 85% | 91% | ... | 82% |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 3. 병목 예측
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Critical] AI팀: W3-W5 (96%, 98%, 95%)
  └ 원인: 'DX 프로젝트' + 'AI PoC' 동시 진행
  └ 권고: 외부 인력 2명 투입 또는 일정 조정

[Warning] 데이터팀: W3 (91%)
  └ 원인: 데이터 마이그레이션 작업
  └ 권고: AI팀 지원 인력 재배치

✅ 분석 완료!
```

## 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--weeks` | 예측 기간 (주) | 12 |
| `--threshold` | 병목 임계값 | 0.9 |
| `--scope` | 조직 범위 | 전사 |
| `--granularity` | 세분화 수준 (본부/팀/개인) | 팀 |

## 에러 처리

| 에러 | 메시지 | 해결 방법 |
|------|--------|----------|
| 데이터 부족 | "팀 가용 시간 데이터가 없습니다" | HR Master 데이터 확인 |
| 프로젝트 없음 | "예정된 프로젝트가 없습니다" | BizForce 데이터 확인 |

## 사용법

```
/capacity-forecast                      # 기본 12주 예측
/capacity-forecast --weeks 24           # 24주 예측
/capacity-forecast --scope "AI팀"       # 특정 팀만
/capacity-forecast --threshold 0.85     # 임계값 85%
```

## 연계 Skill/Agent

| Skill/Agent | 역할 | 연계 방식 |
|-------------|------|----------|
| query-decomposition | 질문 분해 | 초기 분석 |
| impact-simulator | 가동률 시뮬레이션 | 예측 계산 |
| option-generator | 대응 옵션 생성 | 병목 해소 방안 |

## 관련 문서

- [CLAUDE.md](../../../CLAUDE.md) - 프로젝트 개발 문서
- [hr-prototype-plan-v2.md](../../../hr-prototype-plan-v2.md) - 유스케이스 A-1 상세
