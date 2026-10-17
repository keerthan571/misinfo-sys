import { useLocation, useNavigate } from "react-router-dom";
import { useAnalysis } from "../context/AnalysisContext";
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
      <div className="space-y-4 p-6">
        <h1 className="text-2xl font-bold">
          Future Audience Exposure
        </h1>

        <p>
          No eligible social-media analysis was found.
          Analyze a supported social-media post first.
        </p>

        <button
          type="button"
          onClick={() => navigate("/analyze")}
          className="rounded-lg bg-blue-600 px-4 py-2 text-white"
        >
          Go to Analyze
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-10">
      <div>
        <h1 className="text-2xl font-bold">
          Future Audience Exposure
        </h1>

        <p className="mt-2 text-sm text-gray-500">
          Estimate future views or audience exposure using
          the experimental forecasting methods.
        </p>
      </div>

      <FutureAudiencePredictor
        key={analysis.analysis_id || platform}
        analysis={analysis}
      />

      <div className="rounded-xl border p-5">
        <h2 className="text-lg font-semibold">
          Propagation Network
        </h2>

        <p className="mt-2 text-sm text-gray-500">
          Explore the simulated propagation network,
          influential nodes, and detected communities.
          Graph values are simulated and should not be
          interpreted as verified real-world reach.
        </p>

        <button
          type="button"
          onClick={() =>
            navigate("/graph", { state: { analysis } })
          }
          className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-white"
        >
          View Propagation Graph
        </button>
      </div>
    </div>
  );
}
