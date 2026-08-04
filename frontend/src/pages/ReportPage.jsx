import { useEffect, useState } from "react";

import AnalysisReportTable from "../components/reports/AnalysisReportTable";
import AnalysisReportViewer from "../components/reports/AnalysisReportViewer";
import ReportStats from "../components/reports/ReportStats";
import ReportSearch from "../components/reports/ReportSearch";
import RecentReports from "../components/reports/RecentReports";

import {
  getReports,
  getReport,
} from "../services/reportApi";

const ReportPage = () => {
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      const data = await getReports();
      setReports(data.reports || []);
    } catch (error) {
      console.error("Failed to load reports:", error);
    } finally {
      setLoading(false);
    }
  };

  const openReport = async (reportId) => {
    try {
      const report = await getReport(reportId);
      setSelectedReport(report);
    } catch (error) {
      console.error("Failed to load report:", error);
    }
  };

  const filteredReports = reports.filter((report) =>
    report.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8">

      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-white">
          AI Analysis Reports
        </h1>

        <p className="text-slate-400 mt-2">
          View, manage and download generated analysis reports.
        </p>
      </div>

      {/* Statistics */}
      <ReportStats reports={reports} />

      {/* Search */}
      <ReportSearch
        search={search}
        setSearch={setSearch}
      />

      {/* Recent Reports */}
      <RecentReports
        reports={reports}
        openReport={openReport}
      />

      {/* Reports Table */}
      {loading ? (
        <div className="bg-slate-800 rounded-xl p-6">
          <p className="text-white">
            Loading reports...
          </p>
        </div>
      ) : (
        <AnalysisReportTable
          reports={filteredReports}
          refresh={loadReports}
          openReport={openReport}
        />
      )}

      {/* Selected Report */}
      <AnalysisReportViewer
        report={selectedReport}
      />

    </div>
  );
};

export default ReportPage;