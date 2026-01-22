/**
 * HR DSS - Evaluation Dashboard Component (운영자용)
 *
 * 통합 평가 대시보드 - Agent, Ontology, Data Quality 평가 통합
 * 운영자가 시스템 전체 상태를 모니터링하는 메인 화면
 */

import React, { useState, useMemo } from "react";

// ============================================================
// Types
// ============================================================

export interface SystemHealth {
  overall: HealthStatus;
  agents: HealthStatus;
  ontology: HealthStatus;
  dataQuality: HealthStatus;
  lastUpdated: string;
}

export interface HealthStatus {
  status: "HEALTHY" | "WARNING" | "CRITICAL";
  score: number;
  message: string;
}

export interface QuickStats {
  totalQueries: number;
  successRate: number;
  avgResponseTime: number;
  activeWorkflows: number;
  pendingApprovals: number;
  decisionsToday: number;
}

export interface AlertItem {
  id: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  category: "AGENT" | "ONTOLOGY" | "DATA" | "WORKFLOW";
  title: string;
  description: string;
  timestamp: string;
  isResolved: boolean;
}

export interface RecentActivity {
  id: string;
  type: "QUERY" | "DECISION" | "APPROVAL" | "ERROR";
  description: string;
  user: string;
  timestamp: string;
  status: "SUCCESS" | "PENDING" | "FAILED";
}

export interface EvalDashboardProps {
  health: SystemHealth;
  stats: QuickStats;
  alerts: AlertItem[];
  activities: RecentActivity[];
  onNavigate?: (section: string) => void;
  onRefresh?: () => void;
  onResolveAlert?: (alertId: string) => void;
}

// ============================================================
// Constants
// ============================================================

const STATUS_COLORS = {
  HEALTHY: "#4CAF50",
  WARNING: "#FF9800",
  CRITICAL: "#F44336",
  SUCCESS: "#4CAF50",
  PENDING: "#2196F3",
  FAILED: "#F44336",
};

const SEVERITY_COLORS = {
  HIGH: "#F44336",
  MEDIUM: "#FF9800",
  LOW: "#2196F3",
};

const CATEGORY_ICONS = {
  AGENT: "[A]",
  ONTOLOGY: "[O]",
  DATA: "[D]",
  WORKFLOW: "[W]",
};

const ACTIVITY_ICONS = {
  QUERY: "[Q]",
  DECISION: "[D]",
  APPROVAL: "[A]",
  ERROR: "[!]",
};

// ============================================================
// Helper Components
// ============================================================

const HealthCard: React.FC<{
  title: string;
  health: HealthStatus;
  icon: string;
  onClick?: () => void;
}> = ({ title, health, icon, onClick }) => {
  const color = STATUS_COLORS[health.status];

  return (
    <div
      onClick={onClick}
      style={{
        padding: "20px",
        background: "white",
        borderRadius: "12px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
        cursor: onClick ? "pointer" : "default",
        borderTop: `4px solid ${color}`,
        transition: "transform 0.2s",
      }}
      onMouseOver={(e) =>
        onClick && (e.currentTarget.style.transform = "translateY(-2px)")
      }
      onMouseOut={(e) =>
        onClick && (e.currentTarget.style.transform = "translateY(0)")
      }
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "12px",
        }}
      >
        <div>
          <div style={{ fontSize: "14px", color: "#666", marginBottom: "4px" }}>
            {title}
          </div>
          <div style={{ fontSize: "32px", fontWeight: "bold" }}>
            {health.score.toFixed(0)}%
          </div>
        </div>
        <div
          style={{
            width: "48px",
            height: "48px",
            borderRadius: "12px",
            background: `${color}20`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "20px",
            color: color,
          }}
        >
          {icon}
        </div>
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}
      >
        <span
          style={{
            padding: "4px 8px",
            borderRadius: "4px",
            background: color,
            color: "white",
            fontSize: "11px",
            fontWeight: "bold",
          }}
        >
          {health.status}
        </span>
        <span style={{ fontSize: "12px", color: "#666" }}>
          {health.message}
        </span>
      </div>
    </div>
  );
};

const StatCard: React.FC<{
  label: string;
  value: number | string;
  unit?: string;
  trend?: "up" | "down" | "stable";
  trendValue?: string;
}> = ({ label, value, unit, trend, trendValue }) => {
  const trendColors = {
    up: "#4CAF50",
    down: "#F44336",
    stable: "#666",
  };
  const trendIcons = {
    up: "[^]",
    down: "[v]",
    stable: "[-]",
  };

  return (
    <div
      style={{
        padding: "16px",
        background: "white",
        borderRadius: "8px",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: "12px", color: "#666", marginBottom: "8px" }}>
        {label}
      </div>
      <div style={{ fontSize: "28px", fontWeight: "bold" }}>
        {typeof value === "number" ? value.toLocaleString() : value}
        {unit && (
          <span style={{ fontSize: "14px", color: "#666" }}>{unit}</span>
        )}
      </div>
      {trend && trendValue && (
        <div
          style={{
            fontSize: "12px",
            color: trendColors[trend],
            marginTop: "4px",
          }}
        >
          {trendIcons[trend]} {trendValue}
        </div>
      )}
    </div>
  );
};

const AlertList: React.FC<{
  alerts: AlertItem[];
  onResolve?: (alertId: string) => void;
  maxItems?: number;
}> = ({ alerts, onResolve, maxItems = 5 }) => {
  const unresolvedAlerts = alerts.filter((a) => !a.isResolved);
  const displayAlerts = unresolvedAlerts.slice(0, maxItems);

  if (displayAlerts.length === 0) {
    return (
      <div
        style={{
          padding: "24px",
          textAlign: "center",
          color: "#999",
        }}
      >
        [OK] 현재 알림이 없습니다
      </div>
    );
  }

  return (
    <div>
      {displayAlerts.map((alert) => (
        <div
          key={alert.id}
          style={{
            padding: "12px",
            borderLeft: `4px solid ${SEVERITY_COLORS[alert.severity]}`,
            background: "#fafafa",
            borderRadius: "0 8px 8px 0",
            marginBottom: "8px",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              marginBottom: "4px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span
                style={{
                  padding: "2px 6px",
                  borderRadius: "4px",
                  background: SEVERITY_COLORS[alert.severity],
                  color: "white",
                  fontSize: "10px",
                  fontWeight: "bold",
                }}
              >
                {alert.severity}
              </span>
              <span style={{ fontSize: "11px", color: "#666" }}>
                {CATEGORY_ICONS[alert.category]} {alert.category}
              </span>
            </div>
            <span style={{ fontSize: "11px", color: "#999" }}>
              {new Date(alert.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <div
            style={{ fontWeight: "500", fontSize: "13px", marginBottom: "4px" }}
          >
            {alert.title}
          </div>
          <div style={{ fontSize: "12px", color: "#666", marginBottom: "8px" }}>
            {alert.description}
          </div>
          {onResolve && (
            <button
              onClick={() => onResolve(alert.id)}
              style={{
                padding: "4px 12px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                background: "white",
                fontSize: "11px",
                cursor: "pointer",
              }}
            >
              해결됨으로 표시
            </button>
          )}
        </div>
      ))}
      {unresolvedAlerts.length > maxItems && (
        <div style={{ textAlign: "center", fontSize: "12px", color: "#666" }}>
          + {unresolvedAlerts.length - maxItems}개 더 있음
        </div>
      )}
    </div>
  );
};

const ActivityFeed: React.FC<{
  activities: RecentActivity[];
  maxItems?: number;
}> = ({ activities, maxItems = 10 }) => {
  const displayActivities = activities.slice(0, maxItems);

  return (
    <div>
      {displayActivities.map((activity) => (
        <div
          key={activity.id}
          style={{
            padding: "10px 12px",
            borderBottom: "1px solid #f0f0f0",
            display: "flex",
            alignItems: "center",
            gap: "12px",
          }}
        >
          <div
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "50%",
              background:
                activity.status === "SUCCESS"
                  ? "#E8F5E9"
                  : activity.status === "PENDING"
                    ? "#E3F2FD"
                    : "#FFEBEE",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "12px",
              color: STATUS_COLORS[activity.status],
              flexShrink: 0,
            }}
          >
            {ACTIVITY_ICONS[activity.type]}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                fontSize: "13px",
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {activity.description}
            </div>
            <div style={{ fontSize: "11px", color: "#999" }}>
              {activity.user} |{" "}
              {new Date(activity.timestamp).toLocaleTimeString()}
            </div>
          </div>
          <div
            style={{
              padding: "2px 8px",
              borderRadius: "4px",
              background: `${STATUS_COLORS[activity.status]}20`,
              color: STATUS_COLORS[activity.status],
              fontSize: "10px",
              fontWeight: "bold",
              flexShrink: 0,
            }}
          >
            {activity.status}
          </div>
        </div>
      ))}
    </div>
  );
};

const QuickNavigation: React.FC<{
  onNavigate?: (section: string) => void;
}> = ({ onNavigate }) => {
  const navItems = [
    { id: "agents", label: "Agent 평가", icon: "[A]", color: "#9C27B0" },
    { id: "ontology", label: "Ontology 평가", icon: "[O]", color: "#2196F3" },
    { id: "data", label: "데이터 품질", icon: "[D]", color: "#4CAF50" },
    { id: "workflows", label: "워크플로", icon: "[W]", color: "#FF9800" },
    { id: "approvals", label: "승인 대기", icon: "[H]", color: "#F44336" },
    { id: "logs", label: "결정 로그", icon: "[L]", color: "#607D8B" },
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
        gap: "12px",
      }}
    >
      {navItems.map((item) => (
        <button
          key={item.id}
          onClick={() => onNavigate?.(item.id)}
          style={{
            padding: "16px",
            border: "none",
            borderRadius: "8px",
            background: "white",
            cursor: "pointer",
            textAlign: "center",
            transition: "all 0.2s",
            boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = `${item.color}10`;
            e.currentTarget.style.transform = "translateY(-2px)";
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = "white";
            e.currentTarget.style.transform = "translateY(0)";
          }}
        >
          <div
            style={{
              fontSize: "24px",
              color: item.color,
              marginBottom: "8px",
            }}
          >
            {item.icon}
          </div>
          <div style={{ fontSize: "12px", color: "#333" }}>{item.label}</div>
        </button>
      ))}
    </div>
  );
};

// ============================================================
// Main Component
// ============================================================

export const EvalDashboard: React.FC<EvalDashboardProps> = ({
  health,
  stats,
  alerts,
  activities,
  onNavigate,
  onRefresh,
  onResolveAlert,
}) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState<
    "1h" | "24h" | "7d"
  >("24h");

  const criticalAlerts = useMemo(
    () => alerts.filter((a) => a.severity === "HIGH" && !a.isResolved),
    [alerts],
  );

  return (
    <div
      style={{
        padding: "24px",
        background: "#f5f5f5",
        minHeight: "100vh",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "24px",
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: "24px" }}>운영 대시보드</h1>
          <p style={{ margin: "4px 0 0", color: "#666", fontSize: "14px" }}>
            HR 의사결정 지원 시스템 모니터링
          </p>
        </div>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          {/* Time Range Selector */}
          <select
            value={selectedTimeRange}
            onChange={(e) =>
              setSelectedTimeRange(e.target.value as typeof selectedTimeRange)
            }
            style={{
              padding: "8px 12px",
              border: "1px solid #ccc",
              borderRadius: "4px",
              background: "white",
            }}
          >
            <option value="1h">최근 1시간</option>
            <option value="24h">최근 24시간</option>
            <option value="7d">최근 7일</option>
          </select>
          <span style={{ fontSize: "12px", color: "#666" }}>
            업데이트: {new Date(health.lastUpdated).toLocaleTimeString()}
          </span>
          {onRefresh && (
            <button
              onClick={onRefresh}
              style={{
                padding: "8px 16px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                background: "white",
                cursor: "pointer",
              }}
            >
              새로고침
            </button>
          )}
        </div>
      </div>

      {/* Critical Alert Banner */}
      {criticalAlerts.length > 0 && (
        <div
          style={{
            padding: "16px 20px",
            background: "#FFEBEE",
            border: "1px solid #F44336",
            borderRadius: "8px",
            marginBottom: "24px",
            display: "flex",
            alignItems: "center",
            gap: "12px",
          }}
        >
          <span style={{ fontSize: "24px" }}>[!]</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: "bold", color: "#C62828" }}>
              긴급 알림 {criticalAlerts.length}건
            </div>
            <div style={{ fontSize: "13px", color: "#D32F2F" }}>
              {criticalAlerts[0].title}
            </div>
          </div>
          <button
            onClick={() => onNavigate?.("alerts")}
            style={{
              padding: "8px 16px",
              border: "none",
              borderRadius: "4px",
              background: "#F44336",
              color: "white",
              cursor: "pointer",
              fontWeight: "bold",
            }}
          >
            확인하기
          </button>
        </div>
      )}

      {/* Health Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "20px",
          marginBottom: "24px",
        }}
      >
        <HealthCard title="전체 시스템" health={health.overall} icon="[S]" />
        <HealthCard
          title="AI Agent"
          health={health.agents}
          icon="[A]"
          onClick={() => onNavigate?.("agents")}
        />
        <HealthCard
          title="Ontology/KG"
          health={health.ontology}
          icon="[O]"
          onClick={() => onNavigate?.("ontology")}
        />
        <HealthCard
          title="데이터 품질"
          health={health.dataQuality}
          icon="[D]"
          onClick={() => onNavigate?.("data")}
        />
      </div>

      {/* Quick Stats */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
          gap: "12px",
          marginBottom: "24px",
          padding: "16px",
          background: "white",
          borderRadius: "12px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
        }}
      >
        <StatCard
          label="전체 쿼리"
          value={stats.totalQueries}
          trend="up"
          trendValue="+12%"
        />
        <StatCard
          label="성공률"
          value={`${(stats.successRate * 100).toFixed(1)}`}
          unit="%"
          trend={stats.successRate >= 0.9 ? "stable" : "down"}
        />
        <StatCard
          label="평균 응답시간"
          value={`${(stats.avgResponseTime / 1000).toFixed(1)}`}
          unit="s"
          trend="stable"
        />
        <StatCard label="활성 워크플로" value={stats.activeWorkflows} />
        <StatCard
          label="승인 대기"
          value={stats.pendingApprovals}
          trend={stats.pendingApprovals > 5 ? "up" : "stable"}
        />
        <StatCard label="오늘 결정" value={stats.decisionsToday} />
      </div>

      {/* Main Content Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "24px",
          marginBottom: "24px",
        }}
      >
        {/* Activity Feed */}
        <div
          style={{
            background: "white",
            borderRadius: "12px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid #e0e0e0",
              fontWeight: "bold",
              fontSize: "16px",
            }}
          >
            최근 활동
          </div>
          <ActivityFeed activities={activities} maxItems={8} />
        </div>

        {/* Alerts */}
        <div
          style={{
            background: "white",
            borderRadius: "12px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid #e0e0e0",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span style={{ fontWeight: "bold", fontSize: "16px" }}>알림</span>
            <span
              style={{
                padding: "2px 8px",
                borderRadius: "12px",
                background:
                  alerts.filter((a) => !a.isResolved).length > 0
                    ? "#FFEBEE"
                    : "#E8F5E9",
                color:
                  alerts.filter((a) => !a.isResolved).length > 0
                    ? "#F44336"
                    : "#4CAF50",
                fontSize: "12px",
                fontWeight: "bold",
              }}
            >
              {alerts.filter((a) => !a.isResolved).length}
            </span>
          </div>
          <div style={{ padding: "12px" }}>
            <AlertList
              alerts={alerts}
              onResolve={onResolveAlert}
              maxItems={4}
            />
          </div>
        </div>
      </div>

      {/* Quick Navigation */}
      <div
        style={{
          background: "white",
          borderRadius: "12px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          padding: "20px",
        }}
      >
        <div
          style={{
            fontWeight: "bold",
            fontSize: "16px",
            marginBottom: "16px",
          }}
        >
          빠른 이동
        </div>
        <QuickNavigation onNavigate={onNavigate} />
      </div>
    </div>
  );
};

// ============================================================
// Mock Data Generator
// ============================================================

export const generateMockEvalDashboardData = (): {
  health: SystemHealth;
  stats: QuickStats;
  alerts: AlertItem[];
  activities: RecentActivity[];
} => {
  return {
    health: {
      overall: {
        status: "HEALTHY",
        score: 94,
        message: "모든 시스템 정상 운영 중",
      },
      agents: { status: "HEALTHY", score: 96, message: "5/5 에이전트 정상" },
      ontology: { status: "HEALTHY", score: 92, message: "KG 품질 양호" },
      dataQuality: {
        status: "WARNING",
        score: 88,
        message: "일부 데이터 갱신 필요",
      },
      lastUpdated: new Date().toISOString(),
    },
    stats: {
      totalQueries: 1247,
      successRate: 0.94,
      avgResponseTime: 2350,
      activeWorkflows: 3,
      pendingApprovals: 2,
      decisionsToday: 8,
    },
    alerts: [
      {
        id: "ALT-001",
        severity: "MEDIUM",
        category: "DATA",
        title: "데이터 갱신 지연",
        description: "assignments.json 파일이 24시간 이상 갱신되지 않음",
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        isResolved: false,
      },
      {
        id: "ALT-002",
        severity: "LOW",
        category: "AGENT",
        title: "응답 시간 증가",
        description: "Impact Simulator 평균 응답 시간이 20% 증가",
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        isResolved: false,
      },
    ],
    activities: [
      {
        id: "ACT-001",
        type: "DECISION",
        description: "AI팀 가동률 분석 결정 완료",
        user: "김팀장",
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        status: "SUCCESS",
      },
      {
        id: "ACT-002",
        type: "APPROVAL",
        description: "Go/No-go 승인 대기 중",
        user: "이부장",
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        status: "PENDING",
      },
      {
        id: "ACT-003",
        type: "QUERY",
        description: "역량 갭 분석 요청",
        user: "박과장",
        timestamp: new Date(Date.now() - 5400000).toISOString(),
        status: "SUCCESS",
      },
      {
        id: "ACT-004",
        type: "ERROR",
        description: "KG 쿼리 타임아웃",
        user: "시스템",
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        status: "FAILED",
      },
    ],
  };
};

export default EvalDashboard;
