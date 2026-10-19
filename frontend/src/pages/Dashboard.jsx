
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

import { useUser } from "../context/UserContext";
import { getDashboardStats } from "../api/dashboardApi";

export default function Dashboard() {
  const { user } = useUser();

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

  useEffect(() => {
    let mounted = true;

    const fetchDashboard = async () => {
      try {
        const dashboardData = await getDashboardStats();

        if (!mounted) return;

        setDashboard((prev) => ({
          ...prev,
          totalAnalyses: dashboardData.totalAnalyses,
          verifiedTrue: dashboardData.verifiedTrue,
          verifiedFalse: dashboardData.verifiedFalse,
          ocrUploads: dashboardData.ocrUploads,
          avgConfidence: dashboardData.avgConfidence,
          weeklyAnalysis: dashboardData.weeklyAnalysis,
        }));
      } catch (err) {
        console.error(err);

        if (!mounted) return;

        setError("Failed to load dashboard.");
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    fetchDashboard();

    return () => {
      mounted = false;
    };
  }, []);

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
      valueColor: "text-teal-400",
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
      <div className="min-h-[60vh] w-full flex items-center justify-center px-4">
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
      <div className="min-h-[60vh] w-full flex items-center justify-center px-4">
        <div
          role="alert"
          className="max-w-lg rounded-xl border border-red-500/30 bg-red-500/10 px-6 py-5 text-red-300"
        >
          {error}
        </div>
      </div>
    );
  }

  return (
    <main className="w-full min-h-full min-w-0 bg-transparent px-4 py-6 sm:px-6 sm:py-7 lg:px-8 lg:py-8">
      <div className="w-full min-w-0 space-y-6 lg:space-y-8">
        {/* Dashboard header */}
        <header>
          <DashboardHeader userName={user?.name || "User"} />
        </header>

        {/* Summary statistics */}
        <section
          aria-label="Dashboard statistics"
          className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4 xl:gap-5"
        >
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
        </section>

        {/* Dashboard charts */}
        <section
          aria-label="Analysis charts"
          className="w-full min-w-0"
        >
          <Charts
            fakeNews={dashboard.verifiedFalse}
            realNews={dashboard.verifiedTrue}
            weeklyAnalysis={dashboard.weeklyAnalysis}
          />
        </section>
      </div>
    </main>
  );
}
