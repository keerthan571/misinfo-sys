import { useLocation, useNavigate } from "react-router-dom";
import { useAnalysis } from "../context/AnalysisContext";
import GraphViewer from "../components/graph/GraphViewer";

export default function Graph() {

    const location = useLocation();
    const navigate = useNavigate();

    const {
        analysis: contextAnalysis
    } = useAnalysis();


    /*
    ============================================================
    GET EXISTING ANALYSIS
    ============================================================
    */

    const analysis =
        location.state?.analysis ||
        contextAnalysis?.result?.analysis ||
        null;


    /*
    ============================================================
    PLATFORM VALIDATION
    ============================================================
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
    ============================================================
    NO GRAPH AVAILABLE
    ============================================================
    */

    if (!hasSocialAnalysis) {

        return (

            <div className="min-h-[70vh] flex items-center justify-center">

                <div className="max-w-xl w-full bg-slate-800 border border-slate-700 rounded-3xl p-10 text-center text-white">

                    <h1 className="text-3xl font-bold">
                        No Propagation Graph Available
                    </h1>

                    <p className="text-slate-400 mt-4 leading-7">
                        Propagation graph analysis is available
                        only for social-media screenshot analysis.
                    </p>

                    <p className="text-slate-500 mt-2 text-sm leading-6">
                        Analyze an Instagram, Facebook or
                        Twitter/X screenshot first to generate
                        the propagation network.
                    </p>

                    <button
                        type="button"
                        onClick={() =>
                            navigate("/analyze")
                        }
                        className="!w-auto mt-8 bg-blue-600 hover:bg-blue-500 px-7 py-3 rounded-xl text-white font-semibold transition"
                        style={{
                            width: "fit-content"
                        }}
                    >
                        Go to Analyze
                    </button>

                </div>

            </div>

        );

    }


    /*
    ============================================================
    GRAPH PAGE
    ============================================================
    */

    return (

        <div className="space-y-6">

            {/* =================================================
                HEADER
            ================================================= */}

            <section className="bg-slate-800 border border-slate-700 rounded-3xl p-7">

                <p className="text-blue-400 text-xs font-semibold uppercase tracking-wider">
                    Network Intelligence
                </p>

                <h1 className="text-4xl font-bold text-white mt-2">
                    Propagation Graph
                </h1>

                <p className="text-slate-400 mt-3 leading-7">
                    Visual representation of how the analyzed
                    content propagates through users, influencers,
                    communities and automated accounts.
                </p>

            </section>


            {/* =================================================
                GRAPH VIEWER
            ================================================= */}

            <GraphViewer
                analysis={analysis}
            />

        </div>

    );
}