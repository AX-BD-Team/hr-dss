# HR 의사결정 지원 시스템 - Data Classification & Access Matrix v1

> 작성일: 2025-01-23 | 버전: 1.0

---

## 1. 개요

이 문서는 데이터의 민감도 분류와 접근 권한 매트릭스를 정의합니다.

---

## 2. 데이터 분류 체계

### 2.1 민감도 등급

| 등급             | 코드 | 설명                  | 예시                           |
| ---------------- | ---- | --------------------- | ------------------------------ |
| **Public**       | L1   | 공개 가능 데이터      | 조직 구조, 프로젝트명          |
| **Internal**     | L2   | 내부 공유 가능 데이터 | 프로젝트 일정, 배치 현황       |
| **Confidential** | L3   | 제한된 접근 필요      | 급여, 평가 결과                |
| **Restricted**   | L4   | 최소 접근 원칙 적용   | 개인 식별 정보, 민감 인사 정보 |

### 2.2 데이터 유형별 분류

| 유형             | 설명           | 기본 등급 |
| ---------------- | -------------- | --------- |
| **PII**          | 개인 식별 정보 | L4        |
| **HR Sensitive** | 민감 인사 정보 | L4        |
| **Financial**    | 재무 정보      | L3        |
| **Operational**  | 운영 정보      | L2        |
| **Public**       | 공개 정보      | L1        |

---

## 3. 엔터티별 데이터 분류

### 3.1 Employee (직원)

| 필드         | 분류         | 등급 | 마스킹      | 비고               |
| ------------ | ------------ | ---- | ----------- | ------------------ |
| `employeeId` | PII          | L4   | 부분 마스킹 | `EMP-***001`       |
| `name`       | PII          | L4   | 전체 마스킹 | `홍**`             |
| `email`      | PII          | L4   | 부분 마스킹 | `h***@company.com` |
| `grade`      | HR Sensitive | L3   | -           |                    |
| `status`     | Operational  | L2   | -           |                    |
| `hireDate`   | HR Sensitive | L3   | 연도만      | `2020년`           |
| `orgUnitId`  | Operational  | L2   | -           |                    |
| `jobRoleId`  | Operational  | L2   | -           |                    |
| `managerId`  | Operational  | L2   | 부분 마스킹 |                    |

### 3.2 OrgUnit (조직)

| 필드             | 분류        | 등급 | 마스킹      | 비고 |
| ---------------- | ----------- | ---- | ----------- | ---- |
| `orgUnitId`      | Public      | L1   | -           |      |
| `name`           | Public      | L1   | -           |      |
| `type`           | Public      | L1   | -           |      |
| `headEmployeeId` | Operational | L2   | 부분 마스킹 |      |
| `costCenter`     | Financial   | L3   | -           |      |

### 3.3 Project (프로젝트)

| 필드           | 분류        | 등급 | 마스킹      | 비고      |
| -------------- | ----------- | ---- | ----------- | --------- |
| `projectId`    | Operational | L2   | -           |           |
| `name`         | Operational | L2   | -           |           |
| `status`       | Operational | L2   | -           |           |
| `startDate`    | Operational | L2   | -           |           |
| `endDate`      | Operational | L2   | -           |           |
| `priority`     | Operational | L2   | -           |           |
| `pmEmployeeId` | Operational | L2   | 부분 마스킹 |           |
| `budgetAmount` | Financial   | L3   | 범위 표시   | `10-50억` |
| `actualCost`   | Financial   | L3   | 범위 표시   |           |

### 3.4 Opportunity (영업 기회)

| 필드               | 분류        | 등급 | 마스킹      | 비고 |
| ------------------ | ----------- | ---- | ----------- | ---- |
| `opportunityId`    | Operational | L2   | -           |      |
| `name`             | Operational | L2   | -           |      |
| `clientName`       | Operational | L2   | -           |      |
| `stage`            | Operational | L2   | -           |      |
| `dealValue`        | Financial   | L3   | 범위 표시   |      |
| `closeProbability` | Operational | L2   | -           |      |
| `ownerEmployeeId`  | Operational | L2   | 부분 마스킹 |      |

### 3.5 Assignment (배치)

| 필드            | 분류        | 등급 | 마스킹      | 비고 |
| --------------- | ----------- | ---- | ----------- | ---- |
| `assignmentId`  | Operational | L2   | -           |      |
| `employeeId`    | PII         | L4   | 부분 마스킹 |      |
| `projectId`     | Operational | L2   | -           |      |
| `allocationFTE` | Operational | L2   | -           |      |
| `startDate`     | Operational | L2   | -           |      |
| `endDate`       | Operational | L2   | -           |      |
| `role`          | Operational | L2   | -           |      |

### 3.6 CompetencyEvidence (역량 증거)

| 필드           | 분류         | 등급 | 마스킹      | 비고 |
| -------------- | ------------ | ---- | ----------- | ---- |
| `evidenceId`   | Operational  | L2   | -           |      |
| `employeeId`   | PII          | L4   | 부분 마스킹 |      |
| `competencyId` | Operational  | L2   | -           |      |
| `level`        | HR Sensitive | L3   | -           |      |
| `assessedAt`   | HR Sensitive | L3   | -           |      |
| `sourceType`   | HR Sensitive | L3   | -           |      |

---

## 4. 접근 권한 매트릭스

### 4.1 역할 정의

| 역할                | 코드 | 설명            |
| ------------------- | ---- | --------------- |
| **System Admin**    | SA   | 시스템 관리자   |
| **HR Admin**        | HA   | 인사 관리자     |
| **HR Analyst**      | HN   | 인사 분석가     |
| **Line Manager**    | LM   | 라인 매니저     |
| **Project Manager** | PM   | 프로젝트 매니저 |
| **Employee**        | EE   | 일반 직원       |
| **AI Agent**        | AI   | AI 에이전트     |

### 4.2 역할-등급 접근 매트릭스

| 역할 | L1 (Public) | L2 (Internal) | L3 (Confidential) | L4 (Restricted)     |
| ---- | ----------- | ------------- | ----------------- | ------------------- |
| SA   | ✅ Full     | ✅ Full       | ✅ Full           | ✅ Full             |
| HA   | ✅ Full     | ✅ Full       | ✅ Full           | ✅ Full (담당 범위) |
| HN   | ✅ Full     | ✅ Full       | ✅ Read           | ⚠️ Masked           |
| LM   | ✅ Full     | ✅ Full       | ✅ Read (팀원)    | ⚠️ Masked           |
| PM   | ✅ Full     | ✅ Read       | ⚠️ Masked         | ❌ No Access        |
| EE   | ✅ Full     | ⚠️ Limited    | ❌ No Access      | ❌ No Access        |
| AI   | ✅ Full     | ✅ Full       | ⚠️ Masked         | ⚠️ Masked           |

### 4.3 엔터티-역할 접근 매트릭스

| 엔터티             | SA  | HA  | HN  | LM  | PM  | EE  | AI  |
| ------------------ | --- | --- | --- | --- | --- | --- | --- |
| Employee (PII)     | ✅  | ✅  | ⚠️  | ⚠️  | ⚠️  | ❌  | ⚠️  |
| Employee (기본)    | ✅  | ✅  | ✅  | ✅  | ✅  | ⚠️  | ✅  |
| OrgUnit            | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  | ✅  |
| Project            | ✅  | ✅  | ✅  | ✅  | ✅  | ⚠️  | ✅  |
| Opportunity        | ✅  | ✅  | ✅  | ⚠️  | ⚠️  | ❌  | ⚠️  |
| Assignment         | ✅  | ✅  | ✅  | ✅  | ✅  | ⚠️  | ✅  |
| CompetencyEvidence | ✅  | ✅  | ⚠️  | ⚠️  | ❌  | ❌  | ⚠️  |

**범례:**

- ✅ Full Access
- ⚠️ Masked/Limited Access
- ❌ No Access

---

## 5. 마스킹 규칙

### 5.1 마스킹 함수

```python
def mask_employee_id(employee_id: str) -> str:
    """사번 마스킹: EMP-000001 -> EMP-***001"""
    return f"{employee_id[:4]}***{employee_id[-3:]}"

def mask_name(name: str) -> str:
    """이름 마스킹: 홍길동 -> 홍**"""
    if len(name) <= 1:
        return "*"
    return f"{name[0]}{'*' * (len(name) - 1)}"

def mask_email(email: str) -> str:
    """이메일 마스킹: hong@company.com -> h***@company.com"""
    local, domain = email.split('@')
    return f"{local[0]}***@{domain}"

def mask_amount(amount: int) -> str:
    """금액 범위 표시: 1500000000 -> 10-20억"""
    billions = amount / 1_000_000_000
    if billions < 1:
        return "1억 미만"
    elif billions < 10:
        lower = int(billions // 5) * 5
        upper = lower + 5
        return f"{lower}-{upper}억"
    else:
        lower = int(billions // 10) * 10
        upper = lower + 10
        return f"{lower}-{upper}억"
```

### 5.2 마스킹 적용 예시

| 원본 데이터        | 마스킹 결과        | 적용 역할      |
| ------------------ | ------------------ | -------------- |
| `EMP-000001`       | `EMP-***001`       | HN, LM, PM, AI |
| `홍길동`           | `홍**`             | HN, LM, PM, AI |
| `hong@company.com` | `h***@company.com` | HN, LM, PM, AI |
| `1,500,000,000원`  | `10-20억`          | PM, AI         |

---

## 6. PoC 데이터 정책

### 6.1 Mock 데이터 원칙

| 원칙       | 설명                             |
| ---------- | -------------------------------- |
| **익명화** | 모든 PII는 가상 데이터로 대체    |
| **현실성** | 실제 데이터 분포와 유사하게 생성 |
| **일관성** | Key 참조 무결성 유지             |
| **다양성** | 다양한 케이스 커버               |

### 6.2 Mock 데이터 생성 규칙

```python
# 가상 이름 생성
LAST_NAMES = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]
FIRST_NAMES = ["민준", "서연", "예준", "서윤", "도윤", "지우", "시우", "하은", "주원", "하윤"]

def generate_mock_name():
    return f"{random.choice(LAST_NAMES)}{random.choice(FIRST_NAMES)}"

# 가상 이메일 생성
def generate_mock_email(name: str, seq: int):
    romanized = romanize(name)  # 이름 로마자 변환
    return f"{romanized}{seq}@mock-company.com"

# 가상 사번 생성
def generate_mock_employee_id(seq: int):
    return f"EMP-{str(seq).zfill(6)}"
```

### 6.3 AI Agent 데이터 접근 정책

| 정책            | 내용                             |
| --------------- | -------------------------------- |
| **목적 제한**   | 의사결정 지원 목적으로만 사용    |
| **최소 권한**   | 분석에 필요한 최소 데이터만 접근 |
| **마스킹 적용** | PII는 항상 마스킹 상태로 처리    |
| **로깅**        | 모든 데이터 접근 기록            |
| **집계 우선**   | 개별 데이터보다 집계 데이터 활용 |

---

## 7. 감사 로깅

### 7.1 로그 항목

| 필드         | 설명                     |
| ------------ | ------------------------ |
| `timestamp`  | 접근 일시                |
| `userId`     | 접근자 ID                |
| `userRole`   | 접근자 역할              |
| `action`     | 액션 (READ/WRITE/DELETE) |
| `entityType` | 엔터티 유형              |
| `entityId`   | 엔터티 ID                |
| `dataLevel`  | 데이터 민감도 등급       |
| `masked`     | 마스킹 적용 여부         |
| `purpose`    | 접근 목적                |

### 7.2 로그 예시

```json
{
  "timestamp": "2025-01-23T10:30:00Z",
  "userId": "AI-AGENT-001",
  "userRole": "AI",
  "action": "READ",
  "entityType": "Employee",
  "entityId": "EMP-000001",
  "dataLevel": "L4",
  "masked": true,
  "purpose": "capacity-forecast-analysis"
}
```

---

## 8. 규정 준수

### 8.1 관련 규정

| 규정           | 설명               | 적용 범위      |
| -------------- | ------------------ | -------------- |
| 개인정보보호법 | 국내 개인정보 보호 | PII 전체       |
| GDPR           | EU 개인정보 보호   | EU 직원 데이터 |
| 내부 보안 정책 | 회사 내부 정책     | 전체 데이터    |

### 8.2 PoC 규정 준수 체크리스트

- [x] Mock 데이터 사용 (실제 PII 미사용)
- [x] 데이터 분류 체계 수립
- [x] 접근 권한 매트릭스 정의
- [x] 마스킹 규칙 정의
- [ ] 감사 로깅 구현
- [ ] 접근 제어 구현

---

## 9. 버전 이력

| 버전 | 날짜       | 변경 내용      |
| ---- | ---------- | -------------- |
| 1.0  | 2025-01-23 | 초기 버전 작성 |

---

_이 문서는 PoC 진행 중 정책이 변경될 수 있습니다._
