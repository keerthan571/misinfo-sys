import { useState, useEffect } from "react";
import {
  BarChart3,
  ShieldCheck,
  ShieldAlert,
  Target,
} from "lucide-react";

import Charts from "../components/dashboard/Charts";
import StatCard from "../components/dashboard/StatCard";
import DashboardHeader from "../components/dashboard/DashboardHeader";

import { getCurrentUser } from "../api/authApi";
import { getDashboardStats } from "../api/dashboardApi";

export default function Dashboard() {
  const [dashboard, setDashboard] = useState({
    totalAnalyses: 0,
    verifiedTrue: 0,
    verifiedFalse: 0,
    ocrUploads: 0,
    avgConfidence: 0,
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
      const [dashboardData, userData] = await Promise.all([
        getDashboardStats(),
        getCurrentUser(),
      ]);

      setDashboard((prev) => ({
        ...prev,
        totalAnalyses: dashboardData.totalAnalyses,
        verifiedTrue: dashboardData.verifiedTrue,
        verifiedFalse: dashboardData.verifiedFalse,
        ocrUploads: dashboardData.ocrUploads,
        avgConfidence: dashboardData.avgConfidence,
        weeklyAnalysis: dashboardData.weeklyAnalysis,
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
      valueColor: "text-blue-400",
    },
    {
      title: "Verified True",
      value: dashboard.verifiedTrue,
      subtitle: "Claims verified as true",
      icon: ShieldCheck,
      valueColor: "text-emerald-400",
    },
    {
      title: "Verified False",
      value: dashboard.verifiedFalse,
      subtitle: "Claims verified as false",
      icon: ShieldAlert,
      valueColor: "text-red-400",
    },
    {
      title: "AI Confidence",
      value: `${dashboard.avgConfidence}%`,
      subtitle: "Average AI confidence",
      icon: Target,
      valueColor: "text-amber-400",
    },
  ];

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 rounded-full border-4 border-slate-700 border-t-blue-500 animate-spin" />
          <p className="text-slate-400 text-sm">
            Loading dashboard...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="bg-red-500/10 border border-red-500/20 rounded-2xl px-6 py-5 text-red-300">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="mb-7">
        <DashboardHeader userName={userName} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5 mb-7">
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

      <div className="w-full">
        <Charts
          fakeNews={dashboard.verifiedFalse}
          realNews={dashboard.verifiedTrue}
          weeklyAnalysis={dashboard.weeklyAnalysis}
        />
      </div>
    </div>
  );
}