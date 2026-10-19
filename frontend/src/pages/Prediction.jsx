import { useLocation, useNavigate } from "react-router-dom";
import { useAnalysis } from "../context/AnalysisContext";
import { BarChart3, Network, ArrowRight, ShieldAlert } from "lucide-react";
import FutureAudiencePredictor from "../components/FutureAudiencePredictor";

export default function Prediction() {
  const navigate = useNavigate();
  const { state } = useLocation();
  const { analysis: contextAnalysis } = useAnalysis();

  const analysis =
    state?.analysis ||
    contextAnalysis?.result?.analysis ||
    null;

  const platformValue =
    analysis?.platform?.platform ||
    analysis?.platform ||
    "";

  const platform = String(platformValue).toLowerCase();

  const hasSocialEvidence = Boolean(
    analysis?.image?.path ||
    analysis?.vision?.used
  );

  const hasSocialAnalysis = Boolean(
    analysis &&
    ["x", "twitter", "instagram", "facebook"].includes(platform) &&
    hasSocialEvidence
  );

  if (!hasSocialAnalysis) {
    return (
      <div className="mx-auto max-w-5xl p-5 sm:p-8">
        <div className="rounded-3xl border border-slate-700/70 bg-[#1B293F] p-6 sm:p-8">
          <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl border border-amber-500/20 bg-amber-500/10">
            <ShieldAlert size={24} className="text-amber-400" />
          </div>

          <h1 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
            Future Audience Exposure
          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">
            No eligible social-media analysis was found.
            Analyze a supported social-media post with a screenshot first.
          </p>

          <button
            type="button"
            onClick={() => navigate("/analyze")}
            className="mt-6 inline-flex min-h-12 items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-500"
          >
            Go to Analyze
            <ArrowRight size={17} />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto min-w-0 max-w-[1500px] space-y-6 pb-10">
      {/* Page header */}
      <header className="px-1">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-blue-500/20 bg-blue-500/10">
            <BarChart3 size={23} className="text-blue-400" />
          </div>

          <div className="min-w-0">
            <h1 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
              Future Audience Exposure
            </h1>
            <p className="mt-1 text-sm leading-6 text-slate-400">
              Explore estimated future views and engagement performance.
            </p>
          </div>
        </div>
      </header>

      {/* Forecast form and results */}
      <FutureAudiencePredictor
        key={analysis.analysis_id || platform}
        analysis={analysis}
      />

      {/* Propagation network */}
      <section className="min-w-0 rounded-2xl border border-slate-700/70 bg-[#1B293F] p-5 sm:p-6">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-indigo-500/20 bg-indigo-500/10">
            <Network size={21} className="text-indigo-400" />
          </div>

          <div className="min-w-0 flex-1">
            <h2 className="text-lg font-bold text-white sm:text-xl">
              Propagation Network
            </h2>

            <p className="mt-2 text-sm leading-6 text-slate-400">
              Explore the propagation graph, influential nodes, and detected
              communities. Simulated graph values should not be interpreted
              as verified real-world reach.
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={() =>
            navigate("/graph", { state: { analysis } })
          }
          className="mt-5 inline-flex min-h-12 w-full min-w-0 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 text-center font-semibold text-white transition hover:bg-blue-500 sm:w-auto sm:min-w-[240px]"
        >
          <Network size={18} />
          View Propagation Graph
          <ArrowRight size={17} />
        </button>
      </section>
    </div>
  );
}
