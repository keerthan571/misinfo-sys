
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAnalysis } from "../context/AnalysisContext";
import apiClient from "../api/apiClient";
import GraphViewer from "../components/graph/GraphViewer";

export default function Graph() {
    const location = useLocation();
    const navigate = useNavigate();

    const { analysis: contextAnalysis } = useAnalysis();

    const initialAnalysis =
        location.state?.analysis ||
        contextAnalysis?.result?.analysis ||
        null;

    const [analysis, setAnalysis] = useState(initialAnalysis);
    const [loading, setLoading] = useState(false);

    // Refresh the saved analysis when an analysis ID is available.
    useEffect(() => {
        const candidate =
            location.state?.analysis ||
            contextAnalysis?.result?.analysis ||
            null;

        const analysisId = candidate?.analysis_id;

        if (!analysisId) {
            setAnalysis(candidate);
            return;
        }

        let cancelled = false;

        const refreshAnalysis = async () => {
            setLoading(true);

            try {
                const response = await apiClient.get(
                    `/api/history/${analysisId}`
                );

                if (!cancelled) {
                    const savedAnalysis = response.data?.analysis;
                    setAnalysis(savedAnalysis || candidate);
                }
            } catch (error) {
                console.error(
                    "Unable to refresh saved analysis:",
                    error
                );

                if (!cancelled) {
                    setAnalysis(candidate);
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        };

        refreshAnalysis();

        return () => {
            cancelled = true;
        };
    }, [
        location.state?.analysis,
        contextAnalysis?.result?.analysis,
    ]);

    // Exit fullscreen if this page unmounts.
    useEffect(() => {
        return () => {
            if (document.fullscreenElement) {
                document.exitFullscreen().catch(() => {});
            }
        };
    }, []);

    const platform =
        analysis?.platform?.platform ||
        analysis?.platform ||
        "";

    const isTextAnalysis =
        String(platform).toLowerCase() === "text";

    const hasSocialEvidence = Boolean(
        analysis?.image?.path ||
        analysis?.vision?.used
    );

    const hasSocialAnalysis = Boolean(
        analysis &&
        !isTextAnalysis &&
        hasSocialEvidence
    );

    if (loading && !analysis) {
        return (
            <div className="min-h-[70vh] flex items-center justify-center text-white">
                Loading saved analysis...
            </div>
        );
    }

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
                        onClick={() => navigate("/analyze")}
                        className="!w-auto mt-8 bg-blue-600 hover:bg-blue-500 px-7 py-3 rounded-xl text-white font-semibold transition"
                    >
                        Go to Analyze
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
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

            {/* Keep the graph panel and its own fullscreen button. */}
            <GraphViewer analysis={analysis} />
        </div>
    );
}
