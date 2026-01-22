"use client";

import React, { useState } from "react";
import {
  EvalDashboard,
  generateMockEvalDashboardData,
} from "../../components/EvalDashboard";

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState(
    generateMockEvalDashboardData,
  );

  const handleRefresh = () => {
    setDashboardData(generateMockEvalDashboardData());
  };

  const handleNavigate = (section: string) => {
    console.log("Navigate to:", section);
    alert(
      `"${section}" 섹션으로 이동합니다.\n\n(상세 페이지는 추후 구현 예정)`,
    );
  };

  const handleResolveAlert = (alertId: string) => {
    setDashboardData((prev) => ({
      ...prev,
      alerts: prev.alerts.map((alert) =>
        alert.id === alertId ? { ...alert, isResolved: true } : alert,
      ),
    }));
  };

  return (
    <div style={{ margin: "-32px -24px" }}>
      <EvalDashboard
        health={dashboardData.health}
        stats={dashboardData.stats}
        alerts={dashboardData.alerts}
        activities={dashboardData.activities}
        onNavigate={handleNavigate}
        onRefresh={handleRefresh}
        onResolveAlert={handleResolveAlert}
      />
    </div>
  );
}
