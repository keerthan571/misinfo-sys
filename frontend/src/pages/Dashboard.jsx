import { useState, useEffect } from "react";
import {
  BarChart3,
  ShieldCheck,
  ShieldAlert,
  ScanLine,
  FileText,
  Target,
} from "lucide-react";

import Charts from "../components/dashboard/Charts";
import StatCard from "../components/dashboard/StatCard";
import RecentActivity from "../components/dashboard/RecentActivity";
import QuickActions from "../components/dashboard/QuickActions";
import DashboardHeader from "../components/dashboard/DashboardHeader";

import { getCurrentUser } from "../api/authApi";
import {
  getDashboardStats,
  getRecentActivity,
} from "../api/dashboardApi";
export default function Dashboard() {
  const [dashboard, setDashboard] = useState({
    totalAnalyses: 0,
    verifiedTrue: 0,
    verifiedFalse: 0,
    ocrUploads: 0,
    reports: 0,
    avgConfidence: 0,
    recentActivity: [],
    weeklyAnalysis: [
      { day: "Mon", count: 0 },
      { day: "Tue", count: 0 },
      { day: "Wed", count: 0 },
      { day: "Thu", count: 0 },
      { day: "Fri", count: 0 },
      { day: "Sat", count: 0 },
      { day: "Sun", count: 0 },
    ],
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [userName, setUserName] = useState("User");
  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const [
        dashboardData,
        userData,
        recentActivity,
      ] = await Promise.all([
        getDashboardStats(),
        getCurrentUser(),
        getRecentActivity(),
      ]);

      setDashboard((prev) => ({
        ...prev,
        totalAnalyses: dashboardData.totalAnalyses,
        verifiedTrue: dashboardData.verifiedTrue,
        verifiedFalse: dashboardData.verifiedFalse,
        ocrUploads: dashboardData.ocrUploads,
        reports: dashboardData.reports,
        avgConfidence: dashboardData.avgConfidence,
        weeklyAnalysis: dashboardData.weeklyAnalysis,
        recentActivity: recentActivity,
      }));

      setUserName(userData.name);

    } catch (err) {
      console.error(err);
      setError("Failed to load dashboard.");
    } finally {
      setLoading(false);
    }
  };
  const stats = [
    {
      title: "Total Analyses",
      value: dashboard.totalAnalyses,
      subtitle: "All analyses performed",
      icon: BarChart3,
      valueColor: "text-blue-500",
    },
    {
      title: "Verified True",
      value: dashboard.verifiedTrue,
      subtitle: "Claims verified as true",
      icon: ShieldCheck,
      valueColor: "text-green-500",
    },
    {
      title: "Verified False",
      value: dashboard.verifiedFalse,
      subtitle: "Claims verified as false",
      icon: ShieldAlert,
      valueColor: "text-red-500",
    },
    {
      title: "OCR Uploads",
      value: dashboard.ocrUploads,
      subtitle: "Images processed",
      icon: ScanLine,
      valueColor: "text-purple-500",
    },
    {
      title: "Reports",
      value: dashboard.reports,
      subtitle: "Generated reports",
      icon: FileText,
      valueColor: "text-indigo-500",
    },
    {
      title: "AI Confidence",
      value: `${dashboard.avgConfidence}%`,
      subtitle: "Average AI confidence",
      icon: Target,
      valueColor: "text-yellow-500",
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <h2 className="text-xl font-semibold text-gray-600">
          Loading Dashboard...
        </h2>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <h2 className="text-xl font-semibold text-red-500">
          {error}
        </h2>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <DashboardHeader userName={userName} />

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {stats.map((stat) => (
          <StatCard
            key={stat.title}
            title={stat.title}
            value={stat.value}
            subtitle={stat.subtitle}
            icon={stat.icon}
            valueColor={stat.valueColor}
          />
        ))}
      </div>

      {/* Charts */}
      <Charts
        fakeNews={dashboard.verifiedFalse}
        realNews={dashboard.verifiedTrue}
        weeklyAnalysis={dashboard.weeklyAnalysis}
      />

      {/* Recent Activity */}
      <RecentActivity activities={dashboard.recentActivity} />

      {/* Quick Actions */}
      <QuickActions />
    </div>
  );
}