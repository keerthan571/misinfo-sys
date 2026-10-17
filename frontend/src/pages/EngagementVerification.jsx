
import { useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  BarChart3,
  Users,
  MessageCircle,
  Repeat2,
  Share2,
  Bookmark,
  Eye,
  CheckCircle2,
  Pencil,
} from "lucide-react";
import apiClient from "../api/apiClient";

function getDateValue(...values) {
  const value = values.find(
    (item) => typeof item === "string" && item.trim()
  );
  return value ? value.slice(0, 10) : "";
}

function getPlatformName(platform) {
  const value = String(platform || "Instagram").toLowerCase();

  if (value === "twitter" || value === "x") return "X";
  if (value === "instagram") return "Instagram";
  if (value === "facebook") return "Facebook";

  return platform || "Instagram";
}

function getMetricIcon(key) {
  const value = key.toLowerCase();

  if (value.includes("comment") || value.includes("reply")) {
    return MessageCircle;
  }
  if (value.includes("repost") || value.includes("retweet")) {
    return Repeat2;
  }
  if (value.includes("share")) return Share2;
  if (value.includes("bookmark") || value.includes("save")) {
    return Bookmark;
  }
  if (value.includes("view") || value.includes("play")) return Eye;

  return BarChart3;
}

function getMetricColor(key) {
  const value = key.toLowerCase();

  if (value.includes("comment") || value.includes("reply")) {
    return {
      text: "text-cyan-400",
      bg: "bg-cyan-500/10",
      border: "border-cyan-500/20",
    };
  }
  if (value.includes("repost") || value.includes("retweet")) {
    return {
      text: "text-purple-400",
      bg: "bg-purple-500/10",
      border: "border-purple-500/20",
    };
  }
  if (value.includes("share")) {
    return {
      text: "text-green-400",
      bg: "bg-green-500/10",
      border: "border-green-500/20",
    };
  }
  if (value.includes("bookmark") || value.includes("save")) {
    return {
      text: "text-pink-400",
      bg: "bg-pink-500/10",
      border: "border-pink-500/20",
    };
  }
  if (value.includes("view") || value.includes("play")) {
    return {
      text: "text-indigo-400",
      bg: "bg-indigo-500/10",
      border: "border-indigo-500/20",
    };
  }

  return {
    text: "text-blue-400",
    bg: "bg-blue-500/10",
    border: "border-blue-500/20",
  };
}

export default function EngagementVerification() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const analysis = state?.analysis || {};

  const originalEngagement = useMemo(
    () => analysis.engagement || {},
    [analysis.engagement]
  );

  const platformName = getPlatformName(
    analysis.platform?.platform || analysis.platform
  );

  const showFollowers = platformName === "Instagram";

  const followers = Number(
    originalEngagement.followers ??
      originalEngagement.followers_count ??
      analysis.follower_count ??
      0
  );

  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const [postedAt, setPostedAt] = useState(() =>
    getDateValue(
      analysis.postedAt,
      analysis.posted_at,
      analysis.publication_date,
      analysis.post_publication_date
    )
  );

  const [screenshotCapturedAt, setScreenshotCapturedAt] = useState(() =>
    getDateValue(
      analysis.screenshotCapturedAt,
      analysis.screenshot_captured_at,
      analysis.screenshot_capture_date
    )
  );

  const [engagement, setEngagement] = useState(() => {
    const source = {
      ...(analysis.engagement || {}),
      ...(analysis.verified_engagement || {}),
    };

    const data = {};

    Object.entries(source).forEach(([key, value]) => {
      if (
        key !== "followers" &&
        key !== "followers_count" &&
        key !== "metrics" &&
        value !== null &&
        value !== undefined &&
        value !== "" &&
        Number.isFinite(Number(value))
      ) {
        data[key] = Math.max(0, Number(value));
      }
    });

    if (source.metrics && typeof source.metrics === "object") {
      Object.entries(source.metrics).forEach(([key, value]) => {
        if (
          key !== "followers" &&
          key !== "followers_count" &&
          data[key] === undefined &&
          value !== null &&
          value !== undefined &&
          value !== "" &&
          Number.isFinite(Number(value))
        ) {
          data[key] = Math.max(0, Number(value));
        }
      });
    }

    return data;
  });

  const handleChange = (key, value) => {
    setEngagement((previous) => ({
      ...previous,
      [key]: value === "" ? "" : Number(value),
    }));
  };

  const continuePrediction = async () => {
    setErrorMessage("");

    if (!analysis.analysis_id) {
      setErrorMessage(
        "Analysis ID is missing. Return to the analysis page and try again."
      );
      return;
    }

    if (!postedAt || !screenshotCapturedAt) {
      setErrorMessage(
        "Enter both the post publication date and screenshot capture date."
      );
      return;
    }

    if (screenshotCapturedAt < postedAt) {
      setErrorMessage(
        "The screenshot capture date cannot be earlier than the publication date."
      );
      return;
    }

    const verifiedEngagement = {};

    for (const [key, value] of Object.entries(engagement)) {
      const number = Number(value);

      if (
        value === "" ||
        !Number.isFinite(number) ||
        number < 0
      ) {
        setErrorMessage(
          `${key.replace(/_/g, " ")} must be a valid non-negative number.`
        );
        return;
      }

      verifiedEngagement[key] = number;
    }

    setLoading(true);

    try {
      const response = await apiClient.post("/api/predict/", {
        analysis_id: analysis.analysis_id,
        engagement: verifiedEngagement,
        detection: analysis.detection || {},
        platform: platformName,
        follower_count: Number.isFinite(followers) ? followers : null,
        posted_at: postedAt,
        screenshot_captured_at: screenshotCapturedAt,
      });

      const data = response.data || {};

      const postAgeDays = Math.floor(
        (
          new Date(`${screenshotCapturedAt}T00:00:00`) -
          new Date(`${postedAt}T00:00:00`)
        ) / 86400000
      );

      const updatedAnalysis = {
        ...analysis,

        postedAt,
        posted_at: postedAt,
        screenshotCapturedAt,
        screenshot_captured_at: screenshotCapturedAt,
        post_age_days: postAgeDays,

        engagement: {
          ...originalEngagement,
          ...verifiedEngagement,
          ...(showFollowers ? { followers } : {}),
        },

        verified_engagement: verifiedEngagement,
        follower_count: Number.isFinite(followers) ? followers : null,

        spreading_level: data.spreading_level ?? null,
        engagement_observations: data.engagement_observations ?? [],

        graph: data.graph ?? null,
        prediction: data.prediction ?? null,
        spread_analysis: data.spread_analysis ?? null,
        post_age_hours: data.post_age_hours ?? null,
      };

      navigate("/prediction", {
        state: { analysis: updatedAnalysis },
      });
    } catch (error) {
      const detail = error?.response?.data?.detail;

      setErrorMessage(
        typeof detail === "string"
          ? detail
          : "Unable to save engagement observations. Check the backend and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-[1500px]">
      <div className="rounded-3xl border border-slate-700/50 bg-[#1B293F] p-7 shadow-xl md:p-9">
        <div className="mb-2 flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-indigo-500/20 bg-indigo-500/10">
            <BarChart3 size={24} className="text-indigo-400" />
          </div>

          <div>
            <h1 className="text-3xl font-extrabold text-white md:text-4xl">
              Engagement Verification
            </h1>
            <p className="mt-2 text-slate-400">
              Verify engagement values and record the screenshot date before
              continuing.
            </p>
          </div>
        </div>

        <div className="my-7 h-px bg-slate-700/60" />

        {/* Publication and screenshot dates */}
        <section className="mb-7 rounded-2xl border border-cyan-500/20 bg-[#0F172A] p-5">
          <h2 className="mb-4 text-lg font-semibold text-white">
            Post and screenshot dates
          </h2>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label
                htmlFor="posted-at"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Post publication date
              </label>

              <input
                id="posted-at"
                type="date"
                value={postedAt}
                max={screenshotCapturedAt || undefined}
                onChange={(event) => setPostedAt(event.target.value)}
                required
                className="w-full rounded-xl border border-slate-600 bg-slate-800 px-4 py-3 text-white outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label
                htmlFor="screenshot-captured-at"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Screenshot capture date
              </label>

              <input
                id="screenshot-captured-at"
                type="date"
                value={screenshotCapturedAt}
                min={postedAt || undefined}
                onChange={(event) =>
                  setScreenshotCapturedAt(event.target.value)
                }
                required
                className="w-full rounded-xl border border-slate-600 bg-slate-800 px-4 py-3 text-white outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <p className="mt-3 text-xs leading-5 text-slate-500">
            Publication date must be on or before the screenshot date. Each
            screenshot date identifies an engagement observation.
          </p>
        </section>

        {/* Instagram follower count */}
        {showFollowers && (
          <div className="mb-6 rounded-2xl border border-purple-500/20 bg-[#0F172A] p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-purple-500/20 bg-purple-500/10">
                  <Users size={20} className="text-purple-400" />
                </div>

                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Account Followers
                  </p>
                  <p className="mt-1 text-sm text-slate-400">
                    Instagram audience size
                  </p>
                </div>
              </div>

              <span className="text-2xl font-bold text-purple-400">
                {followers.toLocaleString()}
              </span>
            </div>
          </div>
        )}

        {/* Engagement metrics */}
        {Object.keys(engagement).length === 0 ? (
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/10 p-4 text-sm text-amber-200">
            No numeric engagement metrics were found. Return to the analysis
            step and confirm that the metrics were extracted.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(engagement).map(([key, value]) => {
              const Icon = getMetricIcon(key);
              const color = getMetricColor(key);

              return (
                <div
                  key={key}
                  className="rounded-2xl border border-slate-700/70 bg-[#0F172A] p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-600"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium capitalize text-slate-400">
                      {key.replace(/_/g, " ")}
                    </p>

                    <div
                      className={`flex h-9 w-9 items-center justify-center rounded-lg border ${color.bg} ${color.border}`}
                    >
                      <Icon size={17} className={color.text} />
                    </div>
                  </div>

                  {editMode ? (
                    <input
                      type="number"
                      min="0"
                      step="any"
                      value={value}
                      onChange={(event) =>
                        handleChange(key, event.target.value)
                      }
                      className="mt-5 w-full rounded-xl border border-slate-600 bg-slate-800 px-3 py-3 font-semibold text-white outline-none focus:border-blue-500"
                    />
                  ) : (
                    <h2 className={`mt-5 text-3xl font-bold ${color.text}`}>
                      {Number(value || 0).toLocaleString()}
                    </h2>
                  )}

                  <div className="mt-4 h-px w-full bg-slate-700/70" />

                  <p className="mt-3 text-xs text-slate-600">
                    {editMode ? "Editable value" : "Detected value"}
                  </p>
                </div>
              );
            })}
          </div>
        )}

        {errorMessage && (
          <div
            role="alert"
            className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200"
          >
            {errorMessage}
          </div>
        )}

        <div className="my-7 h-px bg-slate-700/60" />

        <div className="flex flex-col gap-4 md:flex-row">
          <button
            type="button"
            onClick={continuePrediction}
            disabled={loading}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-blue-600 px-8 py-3.5 font-bold text-white shadow-lg shadow-blue-600/10 transition-all duration-200 hover:bg-blue-500 active:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <CheckCircle2 size={19} />
            {loading ? "Saving observations..." : "Continue to Prediction"}
          </button>

          <button
            type="button"
            onClick={() => setEditMode((previous) => !previous)}
            className={`flex flex-1 items-center justify-center gap-2 rounded-xl px-8 py-3.5 font-bold transition-all duration-200 ${
              editMode
                ? "bg-green-600 text-white hover:bg-green-500"
                : "border border-slate-600 bg-slate-800 text-slate-200 hover:bg-slate-700"
            }`}
          >
            <Pencil size={18} />
            {editMode ? "Finish Editing" : "Edit Values"}
          </button>
        </div>
      </div>
    </div>
  );
}
