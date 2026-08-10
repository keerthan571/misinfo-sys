import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Eye, CalendarDays, SlidersHorizontal } from "lucide-react";
import apiClient from "../api/apiClient";

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchType, setSearchType] = useState("content");
  const [searchValue, setSearchValue] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get("/api/history/");
        setHistory(response.data.history || []);
      } catch (err) {
        console.error(err);
        setError("Failed to load history.");
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const filteredHistory = history.filter((item) => {
    switch (searchType) {
      case "content":
        return (item.text || "")
          .toLowerCase()
          .includes(searchValue.toLowerCase());
      case "platform":
        return (
          item.platform?.platform === searchValue ||
          searchValue === ""
        );
      case "result":
        return (
          item.final_result?.label === searchValue ||
          searchValue === ""
        );
      case "date":
        return (
          new Date(item.analysis_time)
            .toISOString()
            .slice(0, 10) === searchValue ||
          searchValue === ""
        );
      default:
        return true;
    }
  });

  const getResultStyle = (label) => {
    const value = (label || "").toLowerCase();

    if (
      value.includes("verified") ||
      value.includes("reliable")
    ) {
      return "bg-green-500/10 border-green-500/20 text-green-400";
    }

    if (
      value.includes("false") ||
      value.includes("misinformation")
    ) {
      return "bg-red-500/10 border-red-500/20 text-red-400";
    }

    if (
      value.includes("verification") ||
      value.includes("misleading")
    ) {
      return "bg-yellow-500/10 border-yellow-500/20 text-yellow-400";
    }

    return "bg-blue-500/10 border-blue-500/20 text-blue-400";
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
          <p className="text-slate-400 text-sm">
            Loading analysis history...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-7 pb-10">
      <div>
        <div className="flex items-center gap-3">
          <div className="w-1 h-10 rounded-full bg-blue-500" />
          <div>
            <p className="text-blue-400 text-xs font-bold uppercase tracking-wider">
              Analysis Records
            </p>
            <h1 className="text-4xl font-extrabold text-white mt-1">
              Analysis History
            </h1>
          </div>
        </div>
        <p className="text-slate-400 mt-3 ml-4">
          Review and access your previous misinformation analyses.
        </p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-2xl p-4">
          {error}
        </div>
      )}

      <div className="bg-slate-800/80 border border-slate-700/70 rounded-3xl p-6 shadow-xl">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
            <SlidersHorizontal
              size={20}
              className="text-blue-400"
            />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">
              Search & Filter
            </h2>
            <p className="text-sm text-slate-500">
              Find a previous analysis quickly.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[220px_1fr] gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide block mb-2">
              Search By
            </label>

            <select
              value={searchType}
              onChange={(e) => {
                setSearchType(e.target.value);
                setSearchValue("");
              }}
              className="w-full bg-slate-900 text-white border border-slate-700 rounded-xl px-4 py-3 outline-none focus:border-blue-500 transition"
            >
              <option value="content">Content</option>
              <option value="platform">Platform</option>
              <option value="result">Result</option>
              <option value="date">Date</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide block mb-2">
              Search
            </label>

            {searchType === "content" && (
              <div className="relative">
                <Search
                  size={18}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
                />
                <input
                  type="text"
                  placeholder="Search analysis content..."
                  value={searchValue}
                  onChange={(e) =>
                    setSearchValue(e.target.value)
                  }
                  className="w-full bg-slate-900 text-white border border-slate-700 rounded-xl pl-11 pr-4 py-3 outline-none focus:border-blue-500 transition"
                />
              </div>
            )}

            {searchType === "platform" && (
              <select
                value={searchValue}
                onChange={(e) =>
                  setSearchValue(e.target.value)
                }
                className="w-full bg-slate-900 text-white border border-slate-700 rounded-xl px-4 py-3 outline-none focus:border-blue-500 transition"
              >
                <option value="">All Platforms</option>
                <option>Instagram</option>
                <option>Facebook</option>
                <option>Twitter</option>
              </select>
            )}

            {searchType === "result" && (
              <select
                value={searchValue}
                onChange={(e) =>
                  setSearchValue(e.target.value)
                }
                className="w-full bg-slate-900 text-white border border-slate-700 rounded-xl px-4 py-3 outline-none focus:border-blue-500 transition"
              >
                <option value="">All Results</option>
                <option>Verified Information</option>
                <option>False Information</option>
                <option>Potential Misinformation</option>
                <option>Needs Verification</option>
              </select>
            )}

            {searchType === "date" && (
              <div className="relative">
                <CalendarDays
                  size={18}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none"
                />
                <input
                  type="date"
                  value={searchValue}
                  onChange={(e) =>
                    setSearchValue(e.target.value)
                  }
                  className="w-full bg-slate-900 text-white border border-slate-700 rounded-xl pl-11 pr-4 py-3 outline-none focus:border-blue-500 transition"
                />
              </div>
            )}
          </div>
        </div>

        <div className="mt-5 pt-4 border-t border-slate-700/60 flex items-center justify-between">
          <p className="text-sm text-slate-400">
            Showing{" "}
            <span className="text-white font-semibold">
              {filteredHistory.length}
            </span>{" "}
            of{" "}
            <span className="text-white font-semibold">
              {history.length}
            </span>{" "}
            analyses
          </p>

          {searchValue && (
            <button
              onClick={() => setSearchValue("")}
              className="text-sm text-blue-400 hover:text-blue-300 transition"
            >
              Clear filter
            </button>
          )}
        </div>
      </div>

      <div className="bg-slate-800/80 border border-slate-700/70 rounded-3xl shadow-xl overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-700/70 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">
              Previous Analyses
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Select an analysis to view its complete report.
            </p>
          </div>

          <div className="hidden sm:flex items-center gap-2 bg-slate-900 px-3 py-2 rounded-xl border border-slate-700">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            <span className="text-xs text-slate-400">
              {filteredHistory.length} Records
            </span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-white">
            <thead className="bg-slate-900/80">
              <tr className="text-xs uppercase tracking-wider text-slate-500">
                <th className="px-6 py-4 text-left font-semibold">
                  Date
                </th>
                <th className="px-6 py-4 text-left font-semibold">
                  Content
                </th>
                <th className="px-6 py-4 text-left font-semibold">
                  Platform
                </th>
                <th className="px-6 py-4 text-left font-semibold">
                  Result
                </th>
                <th className="px-6 py-4 text-left font-semibold">
                  Confidence
                </th>
                <th className="px-6 py-4 text-right font-semibold">
                  Action
                </th>
              </tr>
            </thead>

            <tbody>
              {filteredHistory.length > 0 ? (
                filteredHistory.map((item) => {
                  const result = item.final_result || {};
                  const platform =
                    item.platform?.platform || "Unknown";

                  return (
                    <tr
                      key={item.analysis_id}
                      className="border-t border-slate-700/60 hover:bg-slate-700/20 transition-colors"
                    >
                      <td className="px-6 py-5 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <CalendarDays
                            size={16}
                            className="text-slate-500"
                          />
                          <div>
                            <p className="text-sm font-medium text-slate-200">
                              {new Date(
                                item.analysis_time
                              ).toLocaleDateString()}
                            </p>
                            <p className="text-xs text-slate-500 mt-1">
                              {new Date(
                                item.analysis_time
                              ).toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </p>
                          </div>
                        </div>
                      </td>

                      <td className="px-6 py-5 max-w-md">
                        <p
                          className="text-sm text-slate-300 leading-6 line-clamp-2"
                          title={item.text || "Image Analysis"}
                        >
                          {item.text
                            ? item.text.length > 100
                              ? `${item.text.substring(
                                  0,
                                  100
                                )}...`
                              : item.text
                            : "Image Analysis"}
                        </p>
                      </td>

                      <td className="px-6 py-5">
                        <span className="inline-flex items-center px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-sm text-slate-300">
                          {platform}
                        </span>
                      </td>

                      <td className="px-6 py-5">
                        <span
                          className={`inline-flex items-center px-3 py-1.5 rounded-full border text-xs font-bold ${getResultStyle(
                            result.label
                          )}`}
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-current mr-2" />
                          {result.label || "Unknown"}
                        </span>
                      </td>

                      <td className="px-6 py-5">
                        <div className="flex items-center gap-3">
                          <span className="text-blue-400 font-bold">
                            {result.confidence ?? 0}%
                          </span>
                          <div className="hidden xl:block w-20 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-500 rounded-full"
                              style={{
                                width: `${Math.min(
                                  Number(result.confidence) || 0,
                                  100
                                )}%`,
                              }}
                            />
                          </div>
                        </div>
                      </td>

                      <td className="px-6 py-5 text-right">
                        <button
                          onClick={() =>
                            navigate(
                              `/history/${item.analysis_id}`
                            )
                          }
                          className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 px-4 py-2.5 rounded-xl text-white text-sm font-semibold transition-all shadow-lg shadow-blue-900/20"
                        >
                          <Eye size={17} />
                          View Report
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td
                    colSpan="6"
                    className="px-6 py-16 text-center"
                  >
                    <div className="flex flex-col items-center">
                      <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-700 flex items-center justify-center mb-4">
                        <Search
                          size={24}
                          className="text-slate-500"
                        />
                      </div>
                      <h3 className="text-white font-semibold text-lg">
                        No matching analyses
                      </h3>
                      <p className="text-slate-500 text-sm mt-2">
                        Try changing your search or filter.
                      </p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}