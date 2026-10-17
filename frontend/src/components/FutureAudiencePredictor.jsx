import { useMemo, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/api/future-audience";

const numericFields = [
  ["views", "Current views"],
  ["likes", "Likes"],
  ["comments", "Comments"],
  ["shares", "Shares"],
  ["reposts", "Reposts"],
  ["bookmarks", "Bookmarks"],
  ["replies", "Replies"],
  ["quotes", "Quotes"],
];

function toNullableNumber(value) {
  if (value === "" || value === null || value === undefined) return null;

  const number = Number(value);
  return Number.isFinite(number) && number >= 0 ? number : null;
}

function formatNumber(value) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) {
    return "—";
  }

  return Math.round(Number(value)).toLocaleString();
}

function getPlatform(analysis) {
  const raw =
    analysis?.platform?.platform ||
    analysis?.platform ||
    "";

  const platform = String(raw).trim().toLowerCase();

  if (platform === "x" || platform === "twitter" || platform === "twitter/x") {
    return "X";
  }

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

function getInitialForm(analysis) {
  const engagement = {
    ...(analysis?.engagement || {}),
    ...(analysis?.verified_engagement || {}),
  };

  const getFirstAvailable = (...values) => {
    for (const value of values) {
      if (value !== "" && value !== null && value !== undefined) {
        return value;
      }
    }

    return "";
  };

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
    const value =
      key === "views"
        ? getFirstAvailable(
            engagement.views,
            engagement.views_latest,
            engagement.current_views,
            analysis?.views,
            analysis?.views_latest,
            analysis?.current_views
          )
        : getFirstAvailable(engagement[key]);

    form[key] = value === "" ? "" : String(value);
  }

  return form;
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
      !Number.isInteger(horizonDays) ||
      horizonDays < 0 ||
      horizonDays > 88
    ) {
      setError("Choose a prediction horizon between 0 and 88 days.");
      return;
    }

    if (
      form.post_age_days === "" ||
      !Number.isInteger(postAgeDays) ||
      postAgeDays < 0
    ) {
      setError(
        "Post age is unavailable. Enter the post age at the screenshot date."
      );
      return;
    }

    const payload = {
      platform: form.platform,
      horizon_days: horizonDays,
      post_age_days: postAgeDays,
    };

    for (const [key] of numericFields) {
      const raw = form[key];

      if (raw !== "" && toNullableNumber(raw) === null) {
        setError(`Enter a valid non-negative value for ${key}.`);
        return;
      }

      payload[key] = toNullableNumber(raw);
    }

    if (form.platform === "X" && payload.views === null) {
      setError(
        "Current X views are required. Add the observed view count from the screenshot."
      );
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const detail =
          typeof data.detail === "string"
            ? data.detail
            : "The prediction request failed. Check the API and input values.";

        throw new Error(detail);
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

  return (
    <section className="bg-slate-800 border border-cyan-500/20 rounded-3xl p-6 md:p-7 shadow-lg">
      <div className="flex items-center gap-3 mb-2">
        <div className="w-1 h-8 bg-cyan-400 rounded-full" />
        <div>
          <h2 className="text-xl font-bold text-white">
            Future Audience Exposure
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Experimental forecast using the existing audience-exposure API
          </p>
        </div>
      </div>

      <p className="text-sm text-slate-400 leading-6 mb-6">
        Values are prefilled from your analysis wherever available. Correct
        any missing or inaccurate values before forecasting. Views are an
        exposure proxy, not verified unique reach.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid sm:grid-cols-2 gap-5">
          <label className="block">
            <span className="block text-sm text-slate-300 mb-2">
              Platform
            </span>
            <select
              value={form.platform}
              onChange={(event) => update("platform", event.target.value)}
              required
              className="w-full rounded-xl border border-slate-600 bg-slate-900 text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="">Select platform</option>
              <option value="X">X (Twitter)</option>
              <option value="Instagram">Instagram</option>
              <option value="Facebook">Facebook</option>
            </select>
          </label>

          <label className="block">
            <span className="block text-sm text-slate-300 mb-2">
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
              placeholder="Unavailable from analysis"
              className="w-full rounded-xl border border-slate-600 bg-slate-900 text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </label>
        </div>

        <div className="rounded-2xl border border-slate-700 bg-slate-900/70 p-5">
          <div className="flex items-center justify-between gap-4 mb-3">
            <label htmlFor="horizon-days" className="text-sm font-semibold text-white">
              Prediction horizon
            </label>
            <span className="rounded-lg bg-cyan-500/10 border border-cyan-500/20 px-3 py-1.5 text-cyan-300 font-bold">
              {form.horizon_days} days
            </span>
          </div>

          <input
            id="horizon-days"
            type="range"
            min="0"
            max="88"
            step="1"
            value={form.horizon_days}
            onChange={(event) =>
              update("horizon_days", event.target.value)
            }
            className="w-full accent-cyan-400"
          />

          <div className="flex justify-between text-xs text-slate-500 mt-2">
            <span>Day 0 · current baseline</span>
            <span>Day 88</span>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-white mb-3">
            Observed engagement metrics
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Existing values are prefilled when available. Blank fields are
            sent as null, not zero.
          </p>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {numericFields.map(([key, label]) => (
              <label key={key} className="block">
                <span className="block text-sm text-slate-300 mb-2">
                  {label}
                </span>
                <input
                  type="number"
                  min="0"
                  step="any"
                  value={form[key]}
                  onChange={(event) => update(key, event.target.value)}
                  placeholder="Not available"
                  className="w-full rounded-xl border border-slate-600 bg-slate-900 text-white px-3 py-3 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </label>
            ))}
          </div>
        </div>

        {error && (
          <div
            role="alert"
            className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200"
          >
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full sm:w-auto rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-60 disabled:cursor-not-allowed px-7 py-3 text-white font-semibold transition"
        >
          {loading ? "Calculating..." : "Predict Future Exposure"}
        </button>
      </form>

      {result && (
        <div className="mt-7 space-y-4" aria-live="polite">
          <div className="rounded-2xl border border-slate-700 bg-slate-900/90 p-5">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
              <div>
                <p className="text-sm text-slate-400">
                  Predicted views / exposure proxy
                </p>
                <p className="text-3xl md:text-4xl font-bold text-cyan-300 mt-2">
                  {formatNumber(result.predicted_views)}
                </p>
              </div>

              <span className="inline-flex w-fit rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs font-semibold text-amber-300">
                {String(result.status || "result").replaceAll("_", " ")}
              </span>
            </div>

            <div className="grid sm:grid-cols-2 gap-3 mt-5 text-sm">
              <div className="rounded-xl bg-slate-800 p-3">
                <span className="text-slate-500 block">Method</span>
                <span className="text-slate-200">
                  {result.method || "Observed baseline"}
                </span>
              </div>

              <div className="rounded-xl bg-slate-800 p-3">
                <span className="text-slate-500 block">
                  Training examples
                </span>
                <span className="text-slate-200">
                  {result.training_complete_view_pairs ?? "—"}
                </span>
              </div>
            </div>

            <p className="text-sm text-slate-400 mt-4 leading-6">
              {result.message || result.uncertainty}
            </p>
          </div>

          {result.cautions?.length > 0 && (
            <div className="rounded-xl border border-amber-500/25 bg-amber-500/5 p-4">
              <h3 className="font-semibold text-amber-200 mb-2">
                Important limitations
              </h3>
              <ul className="list-disc pl-5 space-y-1 text-sm text-amber-100/80">
                {result.cautions.map((caution, index) => (
                  <li key={index}>{caution}</li>
                ))}
              </ul>
            </div>
          )}

          {result.uncertainty && (
            <p className="text-xs text-slate-500 leading-5">
              {result.uncertainty}
            </p>
          )}

          <p className="text-xs text-slate-500">
            Unique reach is not estimated. The dataset does not contain
            verified unique-reach labels.
          </p>
        </div>
      )}
    </section>
  );
}