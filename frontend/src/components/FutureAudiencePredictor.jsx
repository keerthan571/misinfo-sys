import { useMemo, useState } from "react";
import {
  Eye,
  Heart,
  MessageCircle,
  Repeat2,
  Share2,
  Bookmark,
  MessageSquareReply,
  Quote,
  TrendingUp,
  Info,
  Users
} from "lucide-react";
const API_BASE_URL = "http://127.0.0.1:8000/api/future-audience";

const numericFields = [
  ["views", "Current views", Eye],
  ["likes", "Likes", Heart],
  ["comments", "Comments", MessageCircle],
  ["shares", "Shares", Share2],
  ["reposts", "Reposts", Repeat2],
  ["bookmarks", "Bookmarks", Bookmark],
  ["replies", "Replies", MessageSquareReply],
  ["quotes", "Quotes", Quote],
];

const metricAliases = {
  views: ["views", "view_count", "video_views", "plays", "views_latest", "current_views"],
  likes: ["likes", "like_count"],
  comments: ["comments", "comment_count"],
  shares: ["shares", "share_count", "shares_count"],
  reposts: ["reposts", "repost_count", "retweets", "retweet_count"],
  bookmarks: ["bookmarks", "bookmark_count", "saves", "saved"],
  replies: ["replies", "reply_count"],
  quotes: ["quotes", "quote_count"],
};

function toNullableNumber(value) {
  if (value === "" || value === null || value === undefined) return null;
  const number = Number(value);
  return Number.isFinite(number) && number >= 0 ? number : null;
}

function formatNumber(value) {
  if (
    value === null ||
    value === undefined ||
    value === "" ||
    !Number.isFinite(Number(value))
  ) {
    return "—";
  }
  return Math.round(Number(value)).toLocaleString();
}

function getFirstAvailable(...values) {
  return values.find(
    (value) => value !== "" && value !== null && value !== undefined
  ) ?? "";
}

function getPlatform(analysis) {
  const raw = analysis?.platform?.platform || analysis?.platform || "";
  const platform = String(raw).trim().toLowerCase();

  if (["x", "twitter", "twitter/x"].includes(platform)) return "X";
  if (platform === "instagram") return "Instagram";
  if (platform === "facebook") return "Facebook";
  return "";
}

function getPostAgeDays(analysis) {
  const postedAt =
    analysis?.postedAt ||
    analysis?.posted_at ||
    analysis?.publication_date ||
    analysis?.post_publication_date;

  const capturedAt =
    analysis?.screenshotCapturedAt ||
    analysis?.screenshot_captured_at ||
    analysis?.screenshot_capture_date;

  if (postedAt && capturedAt) {
    const posted = new Date(postedAt);
    const captured = new Date(capturedAt);

    if (
      !Number.isNaN(posted.getTime()) &&
      !Number.isNaN(captured.getTime()) &&
      captured >= posted
    ) {
      return Math.floor(
        (captured.getTime() - posted.getTime()) / (1000 * 60 * 60 * 24)
      );
    }
  }

  if (analysis?.post_age_days != null) {
    const age = Number(analysis.post_age_days);
    if (Number.isInteger(age) && age >= 0) return age;
  }

  const ageHours = Number(analysis?.post_age_hours);
  if (Number.isFinite(ageHours) && ageHours >= 0) {
    return Math.floor(ageHours / 24);
  }

  return "";
}

function getMetricSources(analysis) {
  const engagement = {
    ...(analysis?.engagement || {}),
    ...(analysis?.verified_engagement || {}),
  };

  const nestedMetrics = {
    ...(analysis?.engagement?.metrics || {}),
    ...(analysis?.verified_engagement?.metrics || {}),
    ...(engagement.metrics || {}),
  };

  return { engagement, nestedMetrics };
}

function getMetricValue(key, analysis) {
  const { engagement, nestedMetrics } = getMetricSources(analysis);

  for (const name of metricAliases[key] || [key]) {
    const value = getFirstAvailable(
      engagement[name],
      nestedMetrics[name],
      analysis?.[name]
    );

    if (
      value !== "" &&
      value !== null &&
      value !== undefined &&
      Number.isFinite(Number(value)) &&
      Number(value) >= 0
    ) {
      return value;
    }
  }

  return "";
}

function getFollowersCount(analysis) {
  const { engagement, nestedMetrics } = getMetricSources(analysis);

  const value = getFirstAvailable(
    engagement.followers_count,
    engagement.follower_count,
    engagement.followers,
    nestedMetrics.followers_count,
    nestedMetrics.follower_count,
    nestedMetrics.followers,
    analysis?.followers_count,
    analysis?.follower_count,
    analysis?.followers,
    analysis?.platform?.followers_count,
    analysis?.platform?.follower_count,
    analysis?.platform?.followers
  );

  if (value === "" || !Number.isFinite(Number(value)) || Number(value) < 0) {
    return null;
  }

  return Number(value);
}

function getInitialForm(analysis) {
  const horizon = Number(
    analysis?.prediction_days ?? analysis?.horizon_days ?? 7
  );

  const form = {
    platform: getPlatform(analysis),
    horizon_days: String(
      Number.isInteger(horizon) ? Math.min(88, Math.max(0, horizon)) : 7
    ),
    post_age_days: String(getPostAgeDays(analysis)),
  };

  for (const [key] of numericFields) {
    const value = getMetricValue(key, analysis);
    form[key] = value === "" ? "" : String(value);
  }

  return form;
}

function getPerformanceTier(data) {
  const candidates = [
    data?.performance_tier,
    data?.tier_classification?.performance_tier,
    data?.tier_classification?.tier,
    data?.spreading_level,
    data?.data?.performance_tier,
    data?.data?.tier_classification?.performance_tier,
    data?.data?.tier_classification?.tier,
    data?.data?.spreading_level,
    data?.future_audience?.performance_tier,
  ];

  for (const candidate of candidates) {
    const value =
      typeof candidate === "string"
        ? candidate
        : candidate?.level || candidate?.tier;

    if (typeof value !== "string") continue;

    const normalized = value.trim().toLowerCase();
    if (["low", "medium", "high"].includes(normalized)) return normalized;
  }

  return null;
}

function getTierStyles(tier) {
  if (tier === "low") {
    return {
      text: "text-sky-300",
      border: "border-sky-400/25",
      background: "bg-sky-500/10",
      dot: "bg-sky-400",
      label: "Low",
    };
  }

  if (tier === "medium") {
    return {
      text: "text-amber-300",
      border: "border-amber-400/25",
      background: "bg-amber-500/10",
      dot: "bg-amber-400",
      label: "Medium",
    };
  }

  return {
    text: "text-rose-300",
    border: "border-rose-400/25",
    background: "bg-rose-500/10",
    dot: "bg-rose-400",
    label: "High",
  };
}

export default function FutureAudiencePredictor({ analysis }) {
  const initialForm = useMemo(() => getInitialForm(analysis), [analysis]);

  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
    setResult(null);
  };

  const availableMetrics = numericFields.filter(([key]) => {
    return form[key] !== "" && toNullableNumber(form[key]) !== null;
  });

  const followersCount = getFollowersCount(analysis);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!form.platform) {
      setError("The platform could not be identified from the analysis.");
      return;
    }

    const horizonDays = Number(form.horizon_days);
    const postAgeDays = Number(form.post_age_days);

    if (
      form.horizon_days === "" ||
      !Number.isInteger(horizonDays) ||
      horizonDays < 0 ||
      horizonDays > 88
    ) {
      setError("Enter a whole-number prediction horizon from 0 to 88 days.");
      return;
    }

    if (
      form.post_age_days === "" ||
      !Number.isInteger(postAgeDays) ||
      postAgeDays < 0
    ) {
      setError(
        "Post age is unavailable. Check the publication and screenshot dates in the analysis."
      );
      return;
    }

    const analysisId = analysis?.analysis_id;
    const token = localStorage.getItem("token");

    if (!analysisId) {
      setError(
        "Analysis ID is missing. Return to History or reopen the selected analysis."
      );
      return;
    }

    if (!token) {
      setError("Your login session is missing. Please log in again.");
      return;
    }

    const payload = {
      analysis_id: analysisId,
      platform: form.platform,
      horizon_days: horizonDays,
      post_age_days: postAgeDays,
      followers_count: getFollowersCount(analysis),
    };

    for (const [key] of numericFields) {
      payload[key] = toNullableNumber(form[key]);
    }

    if (form.platform === "X" && payload.views === null) {
      setError(
        "Current X views were not extracted. Return to the analysis and check the screenshot."
      );
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Your login session has expired. Please log in again.");
        }

        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "The prediction request failed. Check the API and input values."
        );
      }

      setResult(data);
    } catch (err) {
      if (err instanceof TypeError) {
        setError(
          "Cannot reach FastAPI at http://127.0.0.1:8000. Check that the backend is running and CORS is enabled."
        );
      } else {
        setError(
          err.message || "Something went wrong while requesting the forecast."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  const performanceTier =
    getPerformanceTier(result) ||
    getPerformanceTier(analysis?.future_audience);

  const tierStyles = performanceTier
    ? getTierStyles(performanceTier)
    : null;

  return (
    <section className="min-w-0 space-y-6">
      <div className="min-w-0 rounded-2xl border border-slate-700/70 bg-[#1B293F] p-5 shadow-lg sm:p-6 md:p-7">
        <div className="mb-5 flex items-center gap-3">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-blue-500/20 bg-blue-500/10">
            <TrendingUp size={22} className="text-blue-400" />
          </div>

          <div className="min-w-0">
            <h2 className="text-xl font-bold text-white">Forecast Settings</h2>
            <p className="mt-1 text-sm text-slate-400">
              Configure the forecast period for this post.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid min-w-0 grid-cols-1 gap-5 sm:grid-cols-2">
            <label className="block min-w-0">
              <span className="mb-2 block text-sm font-semibold text-slate-300">
                Platform
              </span>

              <select
                value={form.platform}
                onChange={(event) => update("platform", event.target.value)}
                required
                className="w-full min-w-0 rounded-xl border border-slate-700 bg-[#0F172A] px-4 py-3 text-white outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-400/15"
              >
                <option value="">Select platform</option>
                <option value="X">X (Twitter)</option>
                <option value="Instagram">Instagram</option>
                <option value="Facebook">Facebook</option>
              </select>
            </label>

            <label className="block min-w-0">
              <span className="mb-2 block text-sm font-semibold text-slate-300">
                Post age at screenshot (days)
              </span>

              <input
                type="number"
                min="0"
                step="1"
                required
                value={form.post_age_days}
                onChange={(event) =>
                  update("post_age_days", event.target.value)
                }
                placeholder="Post age in days"
                className="w-full min-w-0 rounded-xl border border-slate-700 bg-[#0F172A] px-4 py-3 text-white outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-400/15"
              />
            </label>
          </div>

          <div className="rounded-2xl border border-slate-700/70 bg-[#0F172A] p-5">
            <label
              htmlFor="horizon-days"
              className="mb-3 block text-sm font-semibold text-white"
            >
              Prediction horizon
            </label>

            <div className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-center">
              <input
                id="horizon-days"
                type="number"
                min="0"
                max="88"
                step="1"
                required
                value={form.horizon_days}
                onChange={(event) =>
                  update("horizon_days", event.target.value)
                }
                className="w-full min-w-0 rounded-xl border border-slate-700 bg-[#1B293F] px-4 py-3 text-lg font-semibold text-white outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-400/15 sm:max-w-xs"
              />

              <span className="text-sm text-slate-400">
                Enter a whole number from 0 to 88 days.
              </span>
            </div>
          </div>

          <div>
            <div className="mb-4">
              <h3 className="text-base font-bold text-white">
                Extracted Engagement
              </h3>
            </div>
            {followersCount !== null && (
              <div className="mb-4 max-w-xs rounded-xl border border-slate-700/70 bg-[#0F172A] p-4">
                <div className="flex items-center gap-2">
                  <Users size={17} className="text-blue-400" />
                  <span className="text-sm font-medium text-slate-400">
                    Account Followers
                  </span>
                </div>
                <p className="mt-3 text-2xl font-bold text-white">
                  {formatNumber(followersCount)}
                </p>
              </div>
            )}
            {availableMetrics.length > 0 ? (
              <div className="grid min-w-0 grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {availableMetrics.map(([key, label, Icon]) => (
                  <div
                    key={key}
                    className="min-w-0 rounded-xl border border-slate-700/70 bg-[#0F172A] p-4"
                  >
                    <div className="flex items-center gap-2">
                      <Icon size={17} className="shrink-0 text-blue-400" />
                      <span className="text-sm font-medium text-slate-400">
                        {label}
                      </span>
                    </div>

                    <p className="mt-3 break-words text-2xl font-bold text-white">
                      {formatNumber(form[key])}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm leading-6 text-slate-300">
                No numeric engagement metrics were extracted. Return to the
                analysis page and check the screenshot.
              </div>
            )}
          </div>

          {error && (
            <div
              role="alert"
              className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm leading-6 text-red-200"
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="inline-flex min-h-12 w-full min-w-0 items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto sm:min-w-[240px]"
          >
            <TrendingUp size={18} />
            {loading ? "Calculating..." : "Predict Future Exposure"}
          </button>
        </form>
      </div>

      {result && (
        <div className="space-y-5" aria-live="polite">
          <section className="rounded-2xl border border-slate-700/70 bg-[#1B293F] p-5 sm:p-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm font-medium text-slate-400">
                  Predicted views / exposure proxy
                </p>

                <p className="mt-2 break-words text-3xl font-extrabold text-blue-300 sm:text-4xl">
                  {formatNumber(result.predicted_views)}
                </p>
              </div>

              <span className="inline-flex w-fit rounded-lg border border-slate-600 bg-[#0F172A] px-3 py-1.5 text-xs font-semibold capitalize text-slate-300">
                {String(result.status || "result").replaceAll("_", " ")}
              </span>
            </div>

            {performanceTier && (
              <div
                className={`mt-5 rounded-xl border p-4 ${tierStyles.border} ${tierStyles.background}`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${tierStyles.dot}`}
                  />
                  <p className="text-sm font-semibold text-slate-200">
                    Observed Engagement Growth Tier
                  </p>
                </div>

                <p className={`mt-2 text-2xl font-extrabold ${tierStyles.text}`}>
                  {tierStyles.label}
                </p>

                <p className="mt-1 text-xs leading-5 text-slate-400">
                  This classification describes relative engagement growth,
                  not verified reach or misinformation truthfulness.
                </p>
              </div>
            )}
            {(result.message || result.uncertainty) && (
              <p className="mt-4 text-sm leading-6 text-slate-400">
                {result.message || result.uncertainty}
              </p>
            )}
          </section>

          <p className="text-xs leading-5 text-slate-500">
            Estimated views are an audience-exposure proxy, not verified unique
            reach. The dataset does not contain verified unique-reach labels.
          </p>
        </div>
      )}
    </section>
  );
}
