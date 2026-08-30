import {
  Brain,
  AlertTriangle,
  CheckCircle,
  FileText,
  Globe,
  KeyRound,
  ShieldAlert,
} from "lucide-react";

export default function DetectionCard({ data }) {
  if (!data) return null;

  const getPredictionStyle = (prediction) => {
    const value = prediction?.toLowerCase() || "";

    if (value.includes("misinformation") || value.includes("false")) {
      return {
        bg: "bg-red-500/10",
        border: "border-red-500/20",
        text: "text-red-400",
        icon: AlertTriangle,
      };
    }

    if (value.includes("verification") || value.includes("verify")) {
      return {
        bg: "bg-yellow-500/10",
        border: "border-yellow-500/20",
        text: "text-yellow-400",
        icon: ShieldAlert,
      };
    }

    if (value.includes("reliable") || value.includes("true")) {
      return {
        bg: "bg-green-500/10",
        border: "border-green-500/20",
        text: "text-green-400",
        icon: CheckCircle,
      };
    }

    return {
      bg: "bg-blue-500/10",
      border: "border-blue-500/20",
      text: "text-blue-400",
      icon: Brain,
    };
  };

  const predictionStyle = getPredictionStyle(data.prediction);
  const PredictionIcon = predictionStyle.icon;

  return (
    <div className="mt-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
          <Brain size={21} className="text-purple-400" />
        </div>

        <div>
          <h2 className="text-2xl font-bold text-white">
            NLP Analysis
          </h2>

          <p className="text-slate-500 text-sm mt-0.5">
            Natural language analysis of the submitted content
          </p>
        </div>
      </div>

      <div className="space-y-5">
        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                NLP Assessment
              </p>

              <p className="text-slate-300 text-sm mt-1">
                Factual claim assessment
              </p>
            </div>

            <div
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl border ${predictionStyle.bg} ${predictionStyle.border}`}
            >
              <PredictionIcon
                size={17}
                className={predictionStyle.text}
              />

              <span
                className={`text-sm font-semibold ${predictionStyle.text}`}
              >
                {data.prediction || "Needs Verification"}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <FileText size={18} className="text-blue-400" />

            <h3 className="text-sm font-semibold text-white">
              Detected Claim
            </h3>
          </div>

          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
            <p className="text-slate-300 leading-7">
              {data.claim || "Unknown"}
            </p>
          </div>
        </div>

        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4">
              <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                Claim Type
              </p>

              <p className="text-white font-semibold mt-2">
                {data.claim_type || "Unknown"}
              </p>
            </div>

            <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4">
              <div className="flex items-center gap-2">
                <Globe size={15} className="text-blue-400" />

                <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                  Language
                </p>
              </div>

              <p className="text-white font-semibold mt-2">
                {data.language || "Unknown"}
              </p>
            </div>
          </div>
        </div>

        {data.keywords?.length > 0 && (
          <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <KeyRound size={18} className="text-yellow-400" />

              <h3 className="text-sm font-semibold text-white">
                Keywords
              </h3>
            </div>

            <div className="flex flex-wrap gap-2">
              {data.keywords.map((item, index) => (
                <span
                  key={index}
                  className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 text-sm"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        )}

        {data.manipulation_signals?.length > 0 && (
          <div className="bg-[#0F172A] border border-yellow-500/10 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle
                size={18}
                className="text-yellow-400"
              />

              <h3 className="text-sm font-semibold text-white">
                Manipulation Signals
              </h3>
            </div>

            <div className="space-y-2">
              {data.manipulation_signals.map((item, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 bg-yellow-500/5 border border-yellow-500/10 rounded-xl p-3"
                >
                  <span className="text-yellow-400 mt-0.5">
                    •
                  </span>

                  <p className="text-slate-300 text-sm leading-6">
                    {item}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {data.entities?.length > 0 && (
          <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <Globe size={18} className="text-cyan-400" />

              <h3 className="text-sm font-semibold text-white">
                Extracted Entities
              </h3>
            </div>

            <div className="space-y-2">
              {data.entities.map((entity, index) => (
                <div
                  key={index}
                  className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 flex justify-between items-center gap-4"
                >
                  <span className="text-slate-300">
                    {entity.name}
                  </span>

                  <span className="px-2.5 py-1 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold">
                    {entity.type}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div>
            <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
              Similar Claim
            </p>

            <p className="text-slate-300 text-sm mt-1">
              Previously detected matching claim
            </p>
          </div>

          <span
            className={`px-3 py-1.5 rounded-lg text-sm font-semibold ${
              data.similar_claim
                ? "bg-yellow-500/10 border border-yellow-500/20 text-yellow-400"
                : "bg-green-500/10 border border-green-500/20 text-green-400"
            }`}
          >
            {data.similar_claim
              ? "Detected"
              : "Not Detected"}
          </span>
        </div>
      </div>
    </div>
  );
}