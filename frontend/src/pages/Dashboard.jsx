import { useState } from "react";
import Charts from "../components/dashboard/Charts";
import StatCard from "../components/dashboard/StatCard";
import RecentActivity from "../components/dashboard/RecentActivity";
import QuickActions from "../components/dashboard/QuickActions";
import DashboardHeader from "../components/dashboard/DashboardHeader";

export default function Dashboard() {
  
  const [dashboard,setDashboard] = useState({
    totalAnalyses: 0,
    fakeNews: 0,
    realNews: 0,
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

  return (
    <div className="space-y-8">
      <DashboardHeader userName="User" />

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <StatCard
          title="Total Analyses"
          value={dashboard.totalAnalyses}
          subtitle="All analyses performed"
          icon="📊"
        />

        <StatCard
          title="Fake News"
          value={dashboard.fakeNews}
          subtitle="Detected as misinformation"
          icon="🚨"
          valueColor="text-red-500"
        />

        <StatCard
          title="Real News"
          value={dashboard.realNews}
          subtitle="Verified content"
          icon="✅"
          valueColor="text-green-400"
        />

        <StatCard
          title="OCR Uploads"
          value={dashboard.ocrUploads}
          subtitle="Images processed"
          icon="📷"
          valueColor="text-purple-400"
        />

        <StatCard
          title="Reports"
          value={dashboard.reports}
          subtitle="Generated reports"
          icon="📄"
          valueColor="text-blue-400"
        />

        <StatCard
          title="Avg. Confidence"
          value={`${dashboard.avgConfidence}%`}
          subtitle="Prediction confidence"
          icon="🎯"
          valueColor="text-yellow-400"
        />
      </div>

      {/* Charts */}
      <Charts
        fakeNews={dashboard.fakeNews}
        realNews={dashboard.realNews}
        weeklyAnalysis={dashboard.weeklyAnalysis}
      />

      <RecentActivity
        activities={dashboard.recentActivity}
      />
      

      <QuickActions />
    </div>
  );
}