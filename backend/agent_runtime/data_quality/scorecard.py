"""
HR DSS - Data Readiness Scorecard

데이터 품질을 평가하고 Scorecard를 생성하는 모듈
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class MetricResult:
    """개별 지표 평가 결과"""

    name: str
    description: str
    value: float
    target: float
    unit: str
    status: str  # PASS, WARNING, FAIL
    details: dict = field(default_factory=dict)

    @property
    def is_passed(self) -> bool:
        return self.status == "PASS"


@dataclass
class EntityResult:
    """엔터티별 평가 결과"""

    entity_name: str
    record_count: int
    metrics: list[MetricResult] = field(default_factory=list)

    @property
    def overall_status(self) -> str:
        if all(m.is_passed for m in self.metrics):
            return "PASS"
        elif any(m.status == "FAIL" for m in self.metrics):
            return "FAIL"
        return "WARNING"


@dataclass
class ScorecardResult:
    """Data Readiness Scorecard 전체 결과"""

    generated_at: datetime
    data_source: str
    entity_results: list[EntityResult] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    @property
    def overall_score(self) -> float:
        """전체 점수 계산 (0-100)"""
        if not self.entity_results:
            return 0.0

        total_metrics = 0
        passed_metrics = 0

        for entity in self.entity_results:
            for metric in entity.metrics:
                total_metrics += 1
                if metric.is_passed:
                    passed_metrics += 1

        return (passed_metrics / total_metrics * 100) if total_metrics > 0 else 0.0

    @property
    def overall_status(self) -> str:
        score = self.overall_score
        if score >= 90:
            return "READY"
        elif score >= 70:
            return "WARNING"
        return "NOT_READY"

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "generated_at": self.generated_at.isoformat(),
            "data_source": self.data_source,
            "overall_score": round(self.overall_score, 2),
            "overall_status": self.overall_status,
            "summary": self.summary,
            "entity_results": [
                {
                    "entity_name": e.entity_name,
                    "record_count": e.record_count,
                    "overall_status": e.overall_status,
                    "metrics": [
                        {
                            "name": m.name,
                            "description": m.description,
                            "value": round(m.value, 4),
                            "target": m.target,
                            "unit": m.unit,
                            "status": m.status,
                            "details": m.details,
                        }
                        for m in e.metrics
                    ],
                }
                for e in self.entity_results
            ],
        }


class DataReadinessScorecard:
    """Data Readiness Scorecard 생성기"""

    # 지표별 목표값
    TARGETS = {
        "missing_rate": 0.10,  # < 10%
        "duplicate_rate": 0.01,  # < 1%
        "key_match_rate": 0.95,  # > 95%
        "required_field_rate": 0.80,  # > 80%
    }

    # 엔터티별 필수 필드 정의
    REQUIRED_FIELDS = {
        "employees": ["employeeId", "name", "grade", "status", "hireDate", "orgUnitId"],
        "orgUnits": ["orgUnitId", "name", "type", "status"],
        "projects": ["projectId", "name", "status", "startDate", "endDate", "pmEmployeeId"],
        "opportunities": ["opportunityId", "name", "stage", "dealValue", "closeProbability"],
        "assignments": ["assignmentId", "employeeId", "allocationFTE", "startDate", "endDate"],
        "competencies": ["competencyId", "name", "domain"],
        "competencyEvidences": ["evidenceId", "employeeId", "competencyId", "level"],
    }

    # 엔터티 간 FK 관계
    FK_RELATIONS = {
        "employees": {"orgUnitId": ("orgUnits", "orgUnitId")},
        "projects": {
            "pmEmployeeId": ("employees", "employeeId"),
            "ownerOrgUnitId": ("orgUnits", "orgUnitId"),
        },
        "assignments": {
            "employeeId": ("employees", "employeeId"),
            "projectId": ("projects", "projectId"),
        },
        "competencyEvidences": {
            "employeeId": ("employees", "employeeId"),
            "competencyId": ("competencies", "competencyId"),
        },
    }

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self.data: dict[str, list[dict]] = {}

    def load_data(self) -> None:
        """Mock 데이터 로드"""
        file_mapping = {
            "orgs.json": ["orgUnits", "jobRoles", "deliveryRoles", "responsibilities"],
            "persons.json": ["employees"],
            "projects.json": ["projects", "workPackages"],
            "opportunities.json": ["opportunities", "demandSignals", "resourceDemands"],
            "skills.json": ["competencies", "competencyEvidences"],
            "assignments.json": ["assignments", "availabilities", "timeBuckets"],
        }

        for filename, entities in file_mapping.items():
            filepath = self.data_dir / filename
            if filepath.exists():
                with open(filepath, encoding="utf-8") as f:
                    content = json.load(f)
                    for entity in entities:
                        if entity in content:
                            self.data[entity] = content[entity]

    def evaluate(self) -> ScorecardResult:
        """데이터 품질 평가 실행"""
        self.load_data()

        result = ScorecardResult(
            generated_at=datetime.now(),
            data_source=str(self.data_dir),
        )

        # 각 엔터티 평가
        for entity_name, records in self.data.items():
            entity_result = self._evaluate_entity(entity_name, records)
            result.entity_results.append(entity_result)

        # 요약 생성
        result.summary = self._generate_summary(result)

        return result

    def _evaluate_entity(self, entity_name: str, records: list[dict]) -> EntityResult:
        """단일 엔터티 평가"""
        entity_result = EntityResult(entity_name=entity_name, record_count=len(records))

        if not records:
            return entity_result

        # 1. 결측률 평가
        missing_metric = self._evaluate_missing_rate(entity_name, records)
        entity_result.metrics.append(missing_metric)

        # 2. 중복률 평가
        duplicate_metric = self._evaluate_duplicate_rate(entity_name, records)
        entity_result.metrics.append(duplicate_metric)

        # 3. 필수 필드 충족률 평가
        required_metric = self._evaluate_required_fields(entity_name, records)
        entity_result.metrics.append(required_metric)

        # 4. FK 매칭률 평가 (관계가 정의된 경우)
        if entity_name in self.FK_RELATIONS:
            fk_metric = self._evaluate_fk_matching(entity_name, records)
            entity_result.metrics.append(fk_metric)

        return entity_result

    def _evaluate_missing_rate(self, entity_name: str, records: list[dict]) -> MetricResult:
        """결측률 평가"""
        required = self.REQUIRED_FIELDS.get(entity_name, [])
        if not required:
            return MetricResult(
                name="missing_rate",
                description="필수 필드 결측 비율",
                value=0.0,
                target=self.TARGETS["missing_rate"],
                unit="%",
                status="PASS",
                details={"message": "필수 필드 정의 없음"},
            )

        total_fields = len(records) * len(required)
        missing_count = 0
        missing_details = {}

        for field_name in required:
            field_missing = sum(1 for r in records if not r.get(field_name))
            if field_missing > 0:
                missing_details[field_name] = field_missing
            missing_count += field_missing

        rate = missing_count / total_fields if total_fields > 0 else 0
        status = "PASS" if rate <= self.TARGETS["missing_rate"] else "FAIL"

        return MetricResult(
            name="missing_rate",
            description="필수 필드 결측 비율",
            value=rate,
            target=self.TARGETS["missing_rate"],
            unit="%",
            status=status,
            details={"missing_fields": missing_details},
        )

    def _evaluate_duplicate_rate(self, entity_name: str, records: list[dict]) -> MetricResult:
        """중복률 평가 (PK 기준)"""
        # PK 필드 추정 (첫 번째 필드가 보통 PK)
        if not records:
            return MetricResult(
                name="duplicate_rate",
                description="키 중복 비율",
                value=0.0,
                target=self.TARGETS["duplicate_rate"],
                unit="%",
                status="PASS",
            )

        pk_field = list(records[0].keys())[0]
        pk_values = [r.get(pk_field) for r in records]
        unique_count = len(set(pk_values))
        duplicate_count = len(pk_values) - unique_count

        rate = duplicate_count / len(pk_values) if pk_values else 0
        status = "PASS" if rate <= self.TARGETS["duplicate_rate"] else "FAIL"

        return MetricResult(
            name="duplicate_rate",
            description="키 중복 비율",
            value=rate,
            target=self.TARGETS["duplicate_rate"],
            unit="%",
            status=status,
            details={"pk_field": pk_field, "duplicates": duplicate_count},
        )

    def _evaluate_required_fields(self, entity_name: str, records: list[dict]) -> MetricResult:
        """필수 필드 충족률 평가"""
        required = self.REQUIRED_FIELDS.get(entity_name, [])
        if not required or not records:
            return MetricResult(
                name="required_field_rate",
                description="필수 필드 충족률",
                value=1.0,
                target=self.TARGETS["required_field_rate"],
                unit="%",
                status="PASS",
            )

        complete_records = 0
        for record in records:
            if all(record.get(field) is not None for field in required):
                complete_records += 1

        rate = complete_records / len(records)
        status = "PASS" if rate >= self.TARGETS["required_field_rate"] else "FAIL"

        return MetricResult(
            name="required_field_rate",
            description="필수 필드 충족률",
            value=rate,
            target=self.TARGETS["required_field_rate"],
            unit="%",
            status=status,
            details={"complete_records": complete_records, "total_records": len(records)},
        )

    def _evaluate_fk_matching(self, entity_name: str, records: list[dict]) -> MetricResult:
        """FK 매칭률 평가"""
        fk_relations = self.FK_RELATIONS.get(entity_name, {})
        if not fk_relations:
            return MetricResult(
                name="key_match_rate",
                description="FK 매칭률",
                value=1.0,
                target=self.TARGETS["key_match_rate"],
                unit="%",
                status="PASS",
            )

        total_fks = 0
        matched_fks = 0
        unmatched_details: dict[str, list[Any]] = {}

        for fk_field, (ref_entity, ref_field) in fk_relations.items():
            ref_records = self.data.get(ref_entity, [])
            ref_values = {r.get(ref_field) for r in ref_records}

            for record in records:
                fk_value = record.get(fk_field)
                if fk_value is not None:
                    total_fks += 1
                    if fk_value in ref_values:
                        matched_fks += 1
                    else:
                        if fk_field not in unmatched_details:
                            unmatched_details[fk_field] = []
                        if len(unmatched_details[fk_field]) < 5:  # 최대 5개만 기록
                            unmatched_details[fk_field].append(fk_value)

        rate = matched_fks / total_fks if total_fks > 0 else 1.0
        status = "PASS" if rate >= self.TARGETS["key_match_rate"] else "FAIL"

        return MetricResult(
            name="key_match_rate",
            description="FK 매칭률",
            value=rate,
            target=self.TARGETS["key_match_rate"],
            unit="%",
            status=status,
            details={"unmatched": unmatched_details} if unmatched_details else {},
        )

    def _generate_summary(self, result: ScorecardResult) -> dict[str, Any]:
        """요약 정보 생성"""
        total_records = sum(e.record_count for e in result.entity_results)
        total_entities = len(result.entity_results)
        passed_entities = sum(1 for e in result.entity_results if e.overall_status == "PASS")

        return {
            "total_entities": total_entities,
            "total_records": total_records,
            "passed_entities": passed_entities,
            "failed_entities": total_entities - passed_entities,
            "readiness_level": result.overall_status,
        }

    def print_report(self, result: ScorecardResult) -> str:
        """콘솔 출력용 리포트 생성"""
        lines = []
        lines.append("=" * 60)
        lines.append("       DATA READINESS SCORECARD")
        lines.append("=" * 60)
        lines.append(f"Generated: {result.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Data Source: {result.data_source}")
        lines.append("")
        lines.append(f"Overall Score: {result.overall_score:.1f}%")
        lines.append(f"Status: {result.overall_status}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("ENTITY DETAILS")
        lines.append("-" * 60)

        for entity in result.entity_results:
            status_icon = "[PASS]" if entity.overall_status == "PASS" else "[FAIL]"
            lines.append(f"\n{status_icon} {entity.entity_name} ({entity.record_count} records)")

            for metric in entity.metrics:
                m_icon = "[OK]" if metric.is_passed else "[NG]"
                if metric.unit == "%":
                    value_str = f"{metric.value * 100:.1f}%"
                    target_str = f"{metric.target * 100:.0f}%"
                else:
                    value_str = f"{metric.value}"
                    target_str = f"{metric.target}"

                lines.append(f"  {m_icon} {metric.name}: {value_str} (target: {target_str})")

        lines.append("")
        lines.append("-" * 60)
        lines.append("SUMMARY")
        lines.append("-" * 60)
        lines.append(f"Total Entities: {result.summary['total_entities']}")
        lines.append(f"Total Records: {result.summary['total_records']}")
        lines.append(
            f"Passed: {result.summary['passed_entities']}/{result.summary['total_entities']}"
        )
        lines.append("=" * 60)

        return "\n".join(lines)


# CLI 실행용
if __name__ == "__main__":
    import sys

    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data/mock"
    scorecard = DataReadinessScorecard(data_dir)
    result = scorecard.evaluate()

    print(scorecard.print_report(result))

    # JSON 결과 저장
    output_path = Path(data_dir) / "scorecard_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)

    print(f"\nJSON result saved to: {output_path}")
