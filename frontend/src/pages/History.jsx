
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  Eye,
  CalendarDays,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  History as HistoryIcon,
  RotateCcw,
} from "lucide-react";
import apiClient from "../api/apiClient";

const PAGE_SIZE = 10;

const PLATFORM_OPTIONS = [
  { value: "", label: "All Platforms" },
  { value: "Instagram", label: "Instagram" },
  { value: "Facebook", label: "Facebook" },
  { value: "X", label: "X / Twitter" },
];

const RESULT_OPTIONS = [
  { value: "", label: "All Verdicts" },
  { value: "verified", label: "Verified Information" },
  { value: "false", label: "False Information" },
  { value: "misinformation", label: "Misinformation" },
  { value: "misleading", label: "Misleading Information" },
  { value: "needs_verification", label: "Needs Verification" },
];

const inputClass =
  "w-full min-w-0 rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15";

function getPlatform(item) {
  const platform = item?.platform;

  const value =
    typeof platform === "string"
      ? platform
      : platform?.platform;

  if (!value) return "Unknown";

  const normalized = String(value).trim().toLowerCase();

  if (normalized === "twitter" || normalized === "twitter/x") {
    return "X";
  }

  if (normalized === "x/twitter") {
    return "X";
  }

  if (normalized === "instagram") return "Instagram";
  if (normalized === "facebook") return "Facebook";

  return String(value);
}

function getValidDate(value) {
  if (!value) return null;

  const date = new Date(value);

  return Number.isNaN(date.getTime()) ? null : date;
}

function getResultStyle(label) {
  const value = String(label || "").toLowerCase();

  if (
    value.includes("verified") ||
    value.includes("reliable")
  ) {
    return "border-emerald-500/25 bg-emerald-500/10 text-emerald-400";
  }

  if (
    value.includes("false") ||
    value.includes("misinformation")
  ) {
    return "border-red-500/25 bg-red-500/10 text-red-400";
  }

  if (
    value.includes("misleading") ||
    value.includes("verification") ||
    value.includes("unverified")
  ) {
    return "border-amber-500/25 bg-amber-500/10 text-amber-400";
  }

  return "border-blue-500/25 bg-blue-500/10 text-blue-400";
}

function formatDate(value) {
  const date = getValidDate(value);

  if (!date) return "Date unavailable";

  return date.toLocaleDateString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatTime(value) {
  const date = getValidDate(value);

  if (!date) return "";

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getConfidence(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return null;
  }

  const confidence = Number(value);

  if (!Number.isFinite(confidence)) return null;

  return Math.min(100, Math.max(0, confidence));
}

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [searchValue, setSearchValue] = useState("");
  const [platformFilter, setPlatformFilter] = useState("");
  const [resultFilter, setResultFilter] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;

    const fetchHistory = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await apiClient.get("/api/history/");
        const records = response.data?.history;

        if (!Array.isArray(records)) {
          throw new Error(
            "The history API returned an unexpected response."
          );
        }

        if (!cancelled) {
          setHistory(records);
        }
      } catch (err) {
        console.error("Failed to load analysis history:", err);

        if (!cancelled) {
          setError(
            "Failed to load analysis history. Please try again."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchHistory();

    return () => {
      cancelled = true;
    };
  }, []);

  const filteredHistory = useMemo(() => {
    const query = searchValue.trim().toLowerCase();

    return history
      .filter((item) => {
        const text = String(item?.text || "");
        const platform = getPlatform(item);
        const resultLabel = String(
          item?.final_result?.label || ""
        );

        const matchesSearch =
          !query ||
          text.toLowerCase().includes(query) ||
          platform.toLowerCase().includes(query) ||
          resultLabel.toLowerCase().includes(query) ||
          String(item?.analysis_id || "")
            .toLowerCase()
            .includes(query);

        const matchesPlatform =
          !platformFilter ||
          platform.toLowerCase() ===
          platformFilter.toLowerCase();

        const normalizedResult = resultLabel.toLowerCase();

        const matchesResult =
          !resultFilter ||
          (resultFilter === "verified" &&
            (normalizedResult.includes("verified") ||
              normalizedResult.includes("reliable")) &&
            !normalizedResult.includes("unverified")) ||
          (resultFilter === "false" &&
            normalizedResult.includes("false")) ||
          (resultFilter === "misinformation" &&
            normalizedResult.includes("misinformation")) ||
          (resultFilter === "misleading" &&
            normalizedResult.includes("misleading")) ||
          (resultFilter === "needs_verification" &&
            normalizedResult.includes("verification"));

        const date = getValidDate(item?.analysis_time);

        const matchesStartDate =
          !startDate ||
          (date &&
            date >= new Date(`${startDate}T00:00:00`));

        const matchesEndDate =
          !endDate ||
          (date &&
            date <= new Date(`${endDate}T23:59:59.999`));

        return (
          matchesSearch &&
          matchesPlatform &&
          matchesResult &&
          matchesStartDate &&
          matchesEndDate
        );
      })
      .sort((a, b) => {
        const dateA =
          getValidDate(a?.analysis_time)?.getTime() || 0;
        const dateB =
          getValidDate(b?.analysis_time)?.getTime() || 0;

        return dateB - dateA;
      });
  }, [
    history,
    searchValue,
    platformFilter,
    resultFilter,
    startDate,
    endDate,
  ]);

  const totalPages = Math.max(
    1,
    Math.ceil(filteredHistory.length / PAGE_SIZE)
  );

  const safePage = Math.min(currentPage, totalPages);

  const paginatedHistory = filteredHistory.slice(
    (safePage - 1) * PAGE_SIZE,
    safePage * PAGE_SIZE
  );

  useEffect(() => {
    setCurrentPage(1);
  }, [
    searchValue,
    platformFilter,
    resultFilter,
    startDate,
    endDate,
  ]);

  const clearFilters = () => {
    setSearchValue("");
    setPlatformFilter("");
    setResultFilter("");
    setStartDate("");
    setEndDate("");
    setCurrentPage(1);
  };

  const hasActiveFilters = Boolean(
    searchValue.trim() ||
    platformFilter ||
    resultFilter ||
    startDate ||
    endDate
  );

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500/20 border-t-blue-500" />
          <p className="text-sm text-slate-400">
            Loading analysis history...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-7 pb-10">
      {/* Page heading */}

      <header className="!ml-0 !mr-auto !w-full text-left">
        <div className="flex items-center justify-start gap-4 text-left">
          <div className="h-12 w-1 shrink-0 rounded-full bg-blue-500" />

          <div className="min-w-0 text-left">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-blue-400">
              Analysis Records
            </p>

            <h1 className="mt-1 text-3xl font-extrabold leading-tight tracking-tight text-white sm:text-4xl">
              Analysis History
            </h1>
          </div>
        </div>

        <p className="!ml-5 mt-3 text-left text-sm leading-6 text-slate-400 sm:text-base">
          Review and access your previous misinformation analyses.
        </p>
      </header>


      {/* Error state */}
      {error && (
        <div
          role="alert"
          className="flex flex-col gap-3 rounded-2xl border border-red-500/25 bg-red-500/10 p-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <p className="text-sm text-red-400">{error}</p>

          <button
            type="button"
            onClick={() => window.location.reload()}
            className="inline-flex items-center gap-2 self-start rounded-lg border border-red-500/30 px-3 py-2 text-sm font-semibold text-red-300 transition hover:bg-red-500/10"
          >
            <RotateCcw size={15} />
            Retry
          </button>
        </div>
      )}

      {/* Search and filters */}
      <section className="rounded-3xl border border-slate-700/70 bg-slate-800/80 p-4 shadow-xl sm:p-6">
        <div className="mb-5 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-blue-500/20 bg-blue-500/10">
            <SlidersHorizontal
              size={20}
              className="text-blue-400"
            />
          </div>

          <div>
            <h2 className="text-lg font-bold text-white">
              Search & Filters
            </h2>
            <p className="text-sm text-slate-500">
              Search content and narrow down your records.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {/* Search */}
          <div className="lg:col-span-2">
            <label
              htmlFor="history-search"
              className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-400"
            >
              Search content, platform, verdict or record ID
            </label>

            <div className="relative">
              <Search
                size={18}
                className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
              />

              <input
                id="history-search"
                type="search"
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                placeholder="Search your previous analyses..."
                className={`${inputClass} pl-11`}
              />
            </div>
          </div>

          {/* Platform */}
          <div>
            <label
              htmlFor="history-platform"
              className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-400"
            >
              Platform
            </label>

            <select
              id="history-platform"
              value={platformFilter}
              onChange={(e) =>
                setPlatformFilter(e.target.value)
              }
              className={inputClass}
            >
              {PLATFORM_OPTIONS.map((option) => (
                <option
                  key={option.value}
                  value={option.value}
                >
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Verdict */}
          <div>
            <label
              htmlFor="history-verdict"
              className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-400"
            >
              Verdict
            </label>

            <select
              id="history-verdict"
              value={resultFilter}
              onChange={(e) =>
                setResultFilter(e.target.value)
              }
              className={inputClass}
            >
              {RESULT_OPTIONS.map((option) => (
                <option
                  key={option.value}
                  value={option.value}
                >
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Start date */}
          <div>
            <label
              htmlFor="history-start-date"
              className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-400"
            >
              From Date
            </label>

            <div className="relative">
              <CalendarDays
                size={17}
                className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
              />

              <input
                id="history-start-date"
                type="date"
                value={startDate}
                max={endDate || undefined}
                onChange={(e) => setStartDate(e.target.value)}
                className={`${inputClass} pl-11`}
              />
            </div>
          </div>

          {/* End date */}
          <div>
            <label
              htmlFor="history-end-date"
              className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-400"
            >
              To Date
            </label>

            <div className="relative">
              <CalendarDays
                size={17}
                className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
              />

              <input
                id="history-end-date"
                type="date"
                value={endDate}
                min={startDate || undefined}
                onChange={(e) => setEndDate(e.target.value)}
                className={`${inputClass} pl-11`}
              />
            </div>
          </div>
        </div>

        <div className="mt-5 flex flex-col gap-3 border-t border-slate-700/60 pt-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-slate-400">
            Showing{" "}
            <span className="font-semibold text-white">
              {filteredHistory.length}
            </span>{" "}
            of{" "}
            <span className="font-semibold text-white">
              {history.length}
            </span>{" "}
            analyses
          </p>

          {hasActiveFilters && (
            <button
              type="button"
              onClick={clearFilters}
              className="inline-flex items-center gap-2 self-start text-sm font-semibold text-blue-400 transition hover:text-blue-300"
            >
              <RotateCcw size={15} />
              Clear filters
            </button>
          )}
        </div>
      </section>

      {/* History table */}
      <section className="overflow-hidden rounded-3xl border border-slate-700/70 bg-slate-800/80 shadow-xl">
        <div className="flex flex-col gap-3 border-b border-slate-700/70 px-4 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div>
            <h2 className="text-xl font-bold text-white">
              Previous Analyses
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Select a record to view its complete report.
            </p>
          </div>

          <div className="inline-flex items-center gap-2 self-start rounded-xl border border-slate-700 bg-slate-900 px-3 py-2">
            <HistoryIcon
              size={15}
              className="text-blue-400"
            />
            <span className="text-xs text-slate-400">
              {filteredHistory.length}{" "}
              {filteredHistory.length === 1
                ? "Record"
                : "Records"}
            </span>
          </div>
        </div>

        {filteredHistory.length === 0 ? (
          <div className="flex flex-col items-center px-5 py-16 text-center">
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-slate-700 bg-slate-900">
              <Search
                size={24}
                className="text-slate-500"
              />
            </div>

            <h3 className="text-lg font-semibold text-white">
              {history.length === 0
                ? "No analysis history yet"
                : "No matching analyses"}
            </h3>

            <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
              {history.length === 0
                ? "Your previous analyses will appear here after you analyze content."
                : "Try changing your search terms or filters to find a record."}
            </p>

            {hasActiveFilters && (
              <button
                type="button"
                onClick={clearFilters}
                className="mt-5 rounded-xl border border-blue-500/30 px-4 py-2.5 text-sm font-semibold text-blue-400 transition hover:bg-blue-500/10"
              >
                Clear all filters
              </button>
            )}
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[850px] text-left text-white">
                <thead className="bg-slate-900/80">
                  <tr className="text-xs uppercase tracking-wider text-slate-500">
                    <th className="px-5 py-4 font-semibold">
                      Date
                    </th>
                    <th className="px-5 py-4 font-semibold">
                      Content
                    </th>
                    <th className="px-5 py-4 font-semibold">
                      Platform
                    </th>
                    <th className="px-5 py-4 font-semibold">
                      Verdict
                    </th>
                    <th className="px-5 py-4 font-semibold">
                      Confidence
                    </th>
                    <th className="px-5 py-4 text-right font-semibold">
                      Action
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {paginatedHistory.map((item, index) => {
                    const result = item?.final_result || {};
                    const platform = getPlatform(item);
                    const confidence = getConfidence(
                      result.confidence
                    );

                    const content = item?.text
                      ? String(item.text)
                      : "Image Analysis";

                    const recordKey =
                      item?.analysis_id ??
                      `${item?.analysis_time || "record"}-${index}`;

                    return (
                      <tr
                        key={recordKey}
                        className="border-t border-slate-700/60 transition-colors hover:bg-slate-700/20"
                      >
                        {/* Date */}
                        <td className="whitespace-nowrap px-5 py-5">
                          <div className="flex items-start gap-2.5">
                            <CalendarDays
                              size={16}
                              className="mt-0.5 shrink-0 text-slate-500"
                            />

                            <div>
                              <p className="text-sm font-medium text-slate-200">
                                {formatDate(item?.analysis_time)}
                              </p>

                              <p className="mt-1 text-xs text-slate-500">
                                {formatTime(item?.analysis_time)}
                              </p>
                            </div>
                          </div>
                        </td>

                        {/* Content */}
                        <td className="max-w-sm px-5 py-5">
                          <p
                            className="line-clamp-2 text-sm leading-6 text-slate-300"
                            title={content}
                          >
                            {content}
                          </p>
                        </td>

                        {/* Platform */}
                        <td className="px-5 py-5">
                          <span className="inline-flex whitespace-nowrap rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm text-slate-300">
                            {platform}
                          </span>
                        </td>

                        {/* Verdict */}
                        <td className="px-5 py-5">
                          <span
                            className={`inline-flex max-w-[220px] items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-bold ${getResultStyle(
                              result.label
                            )}`}
                          >
                            <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-current" />
                            <span className="whitespace-normal">
                              {result.label || "Unknown"}
                            </span>
                          </span>
                        </td>

                        {/* Confidence */}
                        <td className="px-5 py-5">
                          {confidence === null ? (
                            <span className="text-sm text-slate-500">
                              N/A
                            </span>
                          ) : (
                            <div className="flex items-center gap-3">
                              <span className="font-bold tabular-nums text-blue-400">
                                {confidence}%
                              </span>

                              <div className="hidden h-1.5 w-16 overflow-hidden rounded-full bg-slate-700 xl:block">
                                <div
                                  className="h-full rounded-full bg-blue-500"
                                  style={{
                                    width: `${confidence}%`,
                                  }}
                                />
                              </div>
                            </div>
                          )}
                        </td>

                        {/* Action */}
                        <td className="whitespace-nowrap px-5 py-5 text-right">
                          {item?.analysis_id ? (
                            <button
                              type="button"
                              onClick={() =>
                                navigate(
                                  `/history/${item.analysis_id}`
                                )
                              }
                              className="inline-flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-900/20 transition hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-slate-800"
                            >
                              <Eye size={16} />
                              View Report
                            </button>
                          ) : (
                            <span className="text-xs text-slate-500">
                              Unavailable
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex flex-col gap-4 border-t border-slate-700/70 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
              <p className="text-sm text-slate-400">
                Showing{" "}
                <span className="font-semibold text-white">
                  {(safePage - 1) * PAGE_SIZE + 1}
                </span>
                {"–"}
                <span className="font-semibold text-white">
                  {Math.min(
                    safePage * PAGE_SIZE,
                    filteredHistory.length
                  )}
                </span>{" "}
                of{" "}
                <span className="font-semibold text-white">
                  {filteredHistory.length}
                </span>
              </p>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={safePage <= 1}
                  onClick={() =>
                    setCurrentPage((page) =>
                      Math.max(1, page - 1)
                    )
                  }
                  className="inline-flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm font-semibold text-slate-300 transition hover:border-blue-500/50 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <ChevronLeft size={16} />
                  Previous
                </button>

                <span className="min-w-[90px] text-center text-sm text-slate-400">
                  Page{" "}
                  <span className="font-semibold text-white">
                    {safePage}
                  </span>{" "}
                  of{" "}
                  <span className="font-semibold text-white">
                    {totalPages}
                  </span>
                </span>

                <button
                  type="button"
                  disabled={safePage >= totalPages}
                  onClick={() =>
                    setCurrentPage((page) =>
                      Math.min(totalPages, page + 1)
                    )
                  }
                  className="inline-flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm font-semibold text-slate-300 transition hover:border-blue-500/50 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </>
        )}
      </section>
    </div>
  );
}
