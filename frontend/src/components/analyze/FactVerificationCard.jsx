import {
  CheckCircle,
  FileCheck2,
  ExternalLink,
  AlertTriangle,
  Search,
} from "lucide-react";

export default function FactVerificationCard({ data }) {
  if (!data) return null;

  const verdict = data.verdict || "Not Available";

  const getVerdictStyle = () => {
    if (verdict === "Verified Information") {
      return {
        text: "text-green-400",
        bg: "bg-green-500/10",
        border: "border-green-500/20",
        icon: CheckCircle,
      };
    }

    if (verdict === "False Information") {
      return {
        text: "text-red-400",
        bg: "bg-red-500/10",
        border: "border-red-500/20",
        icon: AlertTriangle,
      };
    }

    if (verdict === "Misleading Information") {
      return {
        text: "text-orange-400",
        bg: "bg-orange-500/10",
        border: "border-orange-500/20",
        icon: AlertTriangle,
      };
    }

    return {
      text: "text-yellow-400",
      bg: "bg-yellow-500/10",
      border: "border-yellow-500/20",
      icon: Search,
    };
  };

  const verdictStyle = getVerdictStyle();
  const VerdictIcon = verdictStyle.icon;

  const confidence = Number(
    String(data.confidence ?? "0").replace("%", "")
  ) || 0;

  return (
    <div className="mt-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-green-500/10 border border-green-500/20 flex items-center justify-center">
          <FileCheck2
            size={21}
            className="text-green-400"
          />
        </div>

        <div>
          <h2 className="text-2xl font-bold text-white">
            Fact Verification
          </h2>

          <p className="text-slate-500 text-sm mt-0.5">
            Evidence-based verification of the detected claim
          </p>
        </div>
      </div>

      <div className="space-y-5">
        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Search
              size={18}
              className="text-blue-400"
            />

            <h3 className="text-sm font-semibold text-white">
              Claim
            </h3>
          </div>

          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 min-h-[80px]">
            <p className="text-slate-300 leading-7">
              {data.claim || "No claim extracted."}
            </p>
          </div>
        </div>

        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                Verdict
              </p>

              <p className="text-slate-300 text-sm mt-1">
                Fact verification result
              </p>
            </div>

            <div
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl border ${verdictStyle.bg} ${verdictStyle.border}`}
            >
              <VerdictIcon
                size={17}
                className={verdictStyle.text}
              />

              <span
                className={`text-sm font-semibold ${verdictStyle.text}`}
              >
                {verdict}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex justify-between items-center mb-3">
            <div>
              <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                Verification Confidence
              </p>

              <p className="text-slate-300 text-sm mt-1">
                Confidence in the verification result
              </p>
            </div>

            <span className="text-blue-400 font-bold text-lg">
              {confidence}%
            </span>
          </div>

          <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-600 to-blue-400 h-full rounded-full transition-all duration-500"
              style={{
                width: `${Math.min(confidence, 100)}%`,
              }}
            />
          </div>
        </div>

        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <FileCheck2
              size={18}
              className="text-purple-400"
            />

            <h3 className="text-sm font-semibold text-white">
              Verification Reason
            </h3>
          </div>

          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 min-h-[80px]">
            <p className="text-slate-300 leading-7">
              {data.reason ||
                "No verification explanation available."}
            </p>
          </div>
        </div>

        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">
                Verification Sources
              </h3>

              <p className="text-slate-500 text-xs mt-1">
                Sources used for fact verification
              </p>
            </div>

            <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
              <ExternalLink
                size={17}
                className="text-blue-400"
              />
            </div>
          </div>

          {data.sources && data.sources.length > 0 ? (
            <div className="space-y-2">
              {data.sources.map((source, index) => (
                <a
                  key={index}
                  href={source}
                  target="_blank"
                  rel="noreferrer"
                  className="
                    flex
                    items-center
                    gap-3
                    bg-slate-950/70
                    border
                    border-slate-800
                    rounded-xl
                    p-3
                    text-sm
                    text-blue-400
                    hover:text-blue-300
                    hover:border-blue-500/30
                    transition-all
                    break-all
                  "
                >
                  <ExternalLink
                    size={15}
                    className="shrink-0"
                  />

                  <span>{source}</span>
                </a>
              ))}
            </div>
          ) : (
            <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
              <p className="text-slate-500 text-sm">
                No sources available.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}