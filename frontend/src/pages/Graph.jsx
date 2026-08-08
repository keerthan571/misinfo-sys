import { useLocation, useNavigate } from "react-router-dom";
import { useAnalysis } from "../context/AnalysisContext";
import GraphViewer from "../components/graph/GraphViewer";

export default function Graph() {
  const location = useLocation();

  const navigate = useNavigate();

  const { analysis: contextAnalysis } =
    useAnalysis();

  const analysis =
    location.state?.analysis ||
    contextAnalysis?.result?.analysis ||
    null;

  /*
   * Graph is available only for social-media
   * screenshot analysis.
   */
  const platform =
    analysis?.platform?.platform ||
    analysis?.platform ||
    "";

  const isTextAnalysis =
    String(platform).toLowerCase() === "text";

  const hasSocialEvidence =
    Boolean(
      analysis?.image?.path ||
      analysis?.vision?.used
    );

  const hasSocialAnalysis =
    Boolean(
      analysis &&
      !isTextAnalysis &&
      hasSocialEvidence
    );

  /*
   * No valid social-media analysis
   */
  if (!hasSocialAnalysis) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">

        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-12 text-center text-white max-w-2xl w-full">

          <div className="text-6xl mb-6">
            🕸️
          </div>

          <h1 className="text-3xl font-bold">
            No Propagation Graph Available
          </h1>

          <p className="text-slate-400 mt-4 leading-7">
            Propagation graph analysis is available
            only for social-media screenshot analysis.
          </p>

          <p className="text-slate-500 mt-2 text-sm">
            Analyze an Instagram, Facebook or Twitter/X
            screenshot first to generate the network.
          </p>

          <button
            onClick={() =>
              navigate("/analyze")
            }
            className="mt-8 bg-blue-600 hover:bg-blue-700 px-7 py-3 rounded-xl text-white font-semibold transition"
          >
            🔍 Go to Analyze
          </button>

        </div>

      </div>
    );
  }

  /*
   * Valid social-media analysis.
   *
   * Existing graph functionality remains untouched.
   */
  return (
    <div className="p-6">

      <div className="space-y-2 mb-6">

        <h1 className="text-4xl font-bold text-white">
          AI Misinformation Propagation Network
        </h1>

        <p className="text-slate-400">
          Network simulation generated using NLP
          classification, propagation modelling and
          PageRank influence analysis.
        </p>

      </div>


      <GraphViewer
        analysis={analysis}
        interactive={true}
        showControls={false}
      />

    </div>
  );
}