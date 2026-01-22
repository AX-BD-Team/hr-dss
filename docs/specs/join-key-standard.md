# HR 의사결정 지원 시스템 - Join Key Standard v1

> 작성일: 2025-01-23 | 버전: 1.0

---

## 1. 개요

이 문서는 시스템 간 데이터 연결을 위한 Join Key 표준을 정의합니다.

---

## 2. Primary Key 표준

### 2.1 Key 명명 규칙

| 규칙      | 형식                   | 예시                        |
| --------- | ---------------------- | --------------------------- |
| PK 접미사 | `{entityName}Id`       | `employeeId`, `projectId`   |
| FK 접미사 | `{referenceEntity}Id`  | `orgUnitId`, `pmEmployeeId` |
| 복합 Key  | `{entity1}{entity2}Id` | `employeeProjectId`         |

### 2.2 Key 형식

| 엔터티      | Key 형식             | 예시                  | 원천       |
| ----------- | -------------------- | --------------------- | ---------- |
| Employee    | `EMP-{6자리숫자}`    | `EMP-000001`          | HR Master  |
| OrgUnit     | `ORG-{4자리숫자}`    | `ORG-0001`            | HR Master  |
| JobRole     | `JOB-{3자리숫자}`    | `JOB-001`             | HR Master  |
| Project     | `PRJ-{YYYY}-{4자리}` | `PRJ-2025-0001`       | TMS        |
| WorkPackage | `WP-{PRJ}-{2자리}`   | `WP-PRJ-2025-0001-01` | TMS        |
| Opportunity | `OPP-{YYYY}-{4자리}` | `OPP-2025-0001`       | BizForce   |
| Assignment  | `ASN-{8자리숫자}`    | `ASN-00000001`        | TMS        |
| Competency  | `CMP-{3자리숫자}`    | `CMP-001`             | Competency |

---

## 3. Join Key 매핑 테이블

### 3.1 시스템 간 Key 매핑

| 원천 시스템    | 원천 Key     | 표준 Key        | 변환 규칙                   |
| -------------- | ------------ | --------------- | --------------------------- |
| **HR Master**  |              |                 |                             |
| HR Master      | `사번`       | `employeeId`    | `EMP-{사번 6자리 패딩}`     |
| HR Master      | `조직코드`   | `orgUnitId`     | `ORG-{조직코드 4자리}`      |
| HR Master      | `직무코드`   | `jobRoleId`     | `JOB-{직무코드 3자리}`      |
| **TMS**        |              |                 |                             |
| TMS            | `프로젝트ID` | `projectId`     | `PRJ-{연도}-{4자리 시퀀스}` |
| TMS            | `사번`       | `employeeId`    | `EMP-{사번 6자리 패딩}`     |
| TMS            | `배치ID`     | `assignmentId`  | `ASN-{8자리 시퀀스}`        |
| **BizForce**   |              |                 |                             |
| BizForce       | `기회ID`     | `opportunityId` | `OPP-{연도}-{4자리 시퀀스}` |
| BizForce       | `담당자사번` | `employeeId`    | `EMP-{사번 6자리 패딩}`     |
| **Competency** |              |                 |                             |
| Competency     | `역량코드`   | `competencyId`  | `CMP-{3자리 코드}`          |
| Competency     | `사번`       | `employeeId`    | `EMP-{사번 6자리 패딩}`     |

### 3.2 Key 변환 함수

```python
def convert_employee_id(source_id: str, source_system: str) -> str:
    """사번을 표준 형식으로 변환"""
    # 숫자만 추출
    numeric = ''.join(filter(str.isdigit, source_id))
    # 6자리 패딩
    padded = numeric.zfill(6)
    return f"EMP-{padded}"

def convert_project_id(source_id: str, year: int) -> str:
    """프로젝트 ID를 표준 형식으로 변환"""
    numeric = ''.join(filter(str.isdigit, source_id))
    padded = numeric.zfill(4)
    return f"PRJ-{year}-{padded}"

def convert_org_id(source_id: str) -> str:
    """조직 ID를 표준 형식으로 변환"""
    numeric = ''.join(filter(str.isdigit, source_id))
    padded = numeric.zfill(4)
    return f"ORG-{padded}"
```

---

## 4. 관계 (Edge) Key 매핑

### 4.1 주요 관계 정의

| 관계              | From Node          | To Node            | Join Key                          | 설명               |
| ----------------- | ------------------ | ------------------ | --------------------------------- | ------------------ |
| `BELONGS_TO`      | Employee           | OrgUnit            | `employeeId` → `orgUnitId`        | 직원-조직 소속     |
| `HAS_JOBROLE`     | Employee           | JobRole            | `employeeId` → `jobRoleId`        | 직원-직무          |
| `ASSIGNED_TO`     | Employee           | Project            | `employeeId` → `projectId`        | 직원-프로젝트 배치 |
| `ASSIGNED_TO`     | Employee           | WorkPackage        | `employeeId` → `workPackageId`    | 직원-WP 배치       |
| `HAS_WORKPACKAGE` | Project            | WorkPackage        | `projectId` → `workPackageId`     | 프로젝트-WP        |
| `HAS_SIGNAL`      | Opportunity        | DemandSignal       | `opportunityId` → `signalId`      | 기회-수요신호      |
| `IMPLIES_DEMAND`  | DemandSignal       | ResourceDemand     | `signalId` → `demandId`           | 신호-리소스수요    |
| `HAS_EVIDENCE`    | Employee           | CompetencyEvidence | `employeeId` → `evidenceId`       | 직원-역량증거      |
| `FOR_COMPETENCY`  | CompetencyEvidence | Competency         | `evidenceId` → `competencyId`     | 증거-역량          |
| `PRIMARY_FOR`     | Employee           | Responsibility     | `employeeId` → `responsibilityId` | 직원-책임(주담당)  |
| `BACKUP_FOR`      | Employee           | Responsibility     | `employeeId` → `responsibilityId` | 직원-책임(대무)    |

### 4.2 관계 속성

| 관계          | 속성            | 타입   | 설명        |
| ------------- | --------------- | ------ | ----------- |
| `BELONGS_TO`  | `startDate`     | date   | 소속 시작일 |
| `BELONGS_TO`  | `endDate`       | date   | 소속 종료일 |
| `ASSIGNED_TO` | `allocationFTE` | number | 투입 FTE    |
| `ASSIGNED_TO` | `startDate`     | date   | 배치 시작일 |
| `ASSIGNED_TO` | `endDate`       | date   | 배치 종료일 |
| `ASSIGNED_TO` | `role`          | string | 역할        |
| `HAS_JOBROLE` | `startDate`     | date   | 직무 시작일 |
| `HAS_JOBROLE` | `endDate`       | date   | 직무 종료일 |
| `PRIMARY_FOR` | `startDate`     | date   | 담당 시작일 |
| `PRIMARY_FOR` | `endDate`       | date   | 담당 종료일 |

---

## 5. Cross-System Join 시나리오

### 5.1 직원-프로젝트-역량 연결

```cypher
// 특정 프로젝트의 투입 인력과 역량 조회
MATCH (e:Employee)-[a:ASSIGNED_TO]->(p:Project {projectId: $projectId})
MATCH (e)-[:HAS_EVIDENCE]->(ev:CompetencyEvidence)-[:FOR_COMPETENCY]->(c:Competency)
RETURN e.employeeId, e.name, a.allocationFTE, c.name as competency, ev.level
```

**Join Path:**

```
HR Master (Employee)
    --[employeeId]--> TMS (Assignment)
    --[projectId]--> TMS (Project)

HR Master (Employee)
    --[employeeId]--> Competency (CompetencyEvidence)
    --[competencyId]--> Competency (Competency)
```

### 5.2 Opportunity-Demand-Resource 연결

```cypher
// Opportunity의 리소스 수요와 가용 인력 매칭
MATCH (o:Opportunity {opportunityId: $oppId})-[:HAS_SIGNAL]->(ds:DemandSignal)
MATCH (ds)-[:IMPLIES_DEMAND]->(rd:ResourceDemand)-[:REQUIRES_ROLE]->(dr:DeliveryRole)
MATCH (e:Employee)-[:HAS_JOBROLE]->(jr:JobRole)
WHERE jr.name = dr.name
MATCH (e)-[:HAS_AVAILABILITY]->(av:Availability)
WHERE av.startDate <= rd.startDate AND av.endDate >= rd.endDate
RETURN o.name, rd.quantityFTE, dr.name, collect(e.name) as availableEmployees
```

**Join Path:**

```
BizForce (Opportunity)
    --[opportunityId]--> BizForce (DemandSignal)
    --[signalId]--> TMS (ResourceDemand)
    --[deliveryRoleId]--> HR Master (DeliveryRole)

HR Master (Employee)
    --[jobRoleId]--> HR Master (JobRole)
    --[employeeId]--> TMS (Availability)
```

### 5.3 조직-가동률 연결

```cypher
// 조직별 주차별 가동률 계산
MATCH (ou:OrgUnit {orgUnitId: $orgUnitId})<-[:BELONGS_TO]-(e:Employee)
MATCH (e)-[a:ASSIGNED_TO]->(p:Project)
MATCH (tb:TimeBucket {granularity: 'WEEK'})
WHERE a.startDate <= tb.endDate AND a.endDate >= tb.startDate
WITH ou, tb, sum(a.allocationFTE) as totalAllocation, count(DISTINCT e) as headcount
RETURN ou.name, tb.year, tb.week, totalAllocation / headcount as utilization
```

---

## 6. Key 매칭 검증

### 6.1 검증 쿼리

```cypher
// 고아 Employee (조직 없음) 검출
MATCH (e:Employee)
WHERE NOT (e)-[:BELONGS_TO]->(:OrgUnit)
RETURN e.employeeId, e.name

// Key 중복 검출
MATCH (e:Employee)
WITH e.employeeId as id, count(*) as cnt
WHERE cnt > 1
RETURN id, cnt

// FK 무결성 검증 (존재하지 않는 조직 참조)
MATCH (e:Employee)-[:BELONGS_TO]->(ou:OrgUnit)
WHERE ou IS NULL
RETURN e.employeeId
```

### 6.2 매칭률 KPI

| 지표                      | 설명                        | 목표  | 측정 쿼리    |
| ------------------------- | --------------------------- | ----- | ------------ |
| Employee-Org 매칭률       | 조직에 연결된 직원 비율     | > 99% | 위 쿼리 참조 |
| Employee-Project 매칭률   | 프로젝트에 배치된 직원 비율 | > 80% | 유사 쿼리    |
| Opportunity-Demand 매칭률 | 수요 신호가 있는 기회 비율  | > 90% | 유사 쿼리    |

---

## 7. 데이터 품질 규칙

### 7.1 Key 유효성 검사

```python
import re

KEY_PATTERNS = {
    "employeeId": r"^EMP-\d{6}$",
    "orgUnitId": r"^ORG-\d{4}$",
    "projectId": r"^PRJ-\d{4}-\d{4}$",
    "opportunityId": r"^OPP-\d{4}-\d{4}$",
    "competencyId": r"^CMP-\d{3}$",
}

def validate_key(key_type: str, value: str) -> bool:
    """Key 형식 유효성 검사"""
    pattern = KEY_PATTERNS.get(key_type)
    if not pattern:
        return False
    return bool(re.match(pattern, value))
```

### 7.2 참조 무결성 검사

| 검사                  | From                    | To                          | 액션               |
| --------------------- | ----------------------- | --------------------------- | ------------------ |
| Employee → OrgUnit    | `Employee.orgUnitId`    | `OrgUnit.orgUnitId`         | 필수, 오류 시 거부 |
| Assignment → Employee | `Assignment.employeeId` | `Employee.employeeId`       | 필수, 오류 시 거부 |
| Assignment → Project  | `Assignment.projectId`  | `Project.projectId`         | 필수, 오류 시 거부 |
| Project → Opportunity | `Project.opportunityId` | `Opportunity.opportunityId` | 선택, 오류 시 경고 |

---

## 8. 버전 이력

| 버전 | 날짜       | 변경 내용      |
| ---- | ---------- | -------------- |
| 1.0  | 2025-01-23 | 초기 버전 작성 |

---

_이 문서는 PoC 진행 중 Key 표준이 변경될 수 있습니다._
