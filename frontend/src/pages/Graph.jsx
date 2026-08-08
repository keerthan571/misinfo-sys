import { useLocation, useNavigate } from "react-router-dom";
import { useAnalysis } from "../context/AnalysisContext";
import GraphViewer from "../components/graph/GraphViewer";

export default function Graph() {

    const location = useLocation();

    const navigate = useNavigate();

    const { analysis: contextAnalysis } = useAnalysis();

    const analysis =
        location.state?.analysis ||
        contextAnalysis?.result?.analysis ||
        null;

    if (!analysis) {

        return (

            <div className="flex flex-col items-center justify-center h-[70vh]">

                <h1 className="text-4xl font-bold text-white mb-4">

                    No Propagation Graph

                </h1>

                <p className="text-slate-400 mb-8 text-lg">

                    Analyze a post to generate a misinformation propagation graph.

                </p>

                <button
                    onClick={() => navigate("/analyze")}
                    className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-xl text-white font-semibold"
                >

                    Analyze Post

                </button>

            </div>

        );

    }

    return (

        <div className="p-6">

            <div className="space-y-2 mb-6">

                <h1 className="text-4xl font-bold text-white">

                    AI Misinformation Propagation Network

                </h1>

                <p className="text-slate-400">

                    Network simulation generated using NLP classification,
                    propagation modelling and PageRank influence analysis.

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