import {
  CheckCircle,
  FileCheck2,
  ExternalLink,
  AlertTriangle,
  Search,
  ShieldCheck,
  ArrowUpRight,
} from "lucide-react";

export default function FactVerificationCard({ data }) {
  if (!data) return null;

  const verdict = data.verdict || "Not Available";

  const getVerdictStyle = () => {
    if (verdict === "Verified Information") {
      return {
        text: "text-green-400",
        bg: "bg-green-500/10",
        border: "border-green-500/30",
        icon: CheckCircle,
        label: "Verified",
      };
    }

    if (verdict === "False Information") {
      return {
        text: "text-red-400",
        bg: "bg-red-500/10",
        border: "border-red-500/30",
        icon: AlertTriangle,
        label: "False",
      };
    }

    if (verdict === "Misleading Information") {
      return {
        text: "text-orange-400",
        bg: "bg-orange-500/10",
        border: "border-orange-500/30",
        icon: AlertTriangle,
        label: "Misleading",
      };
    }

    return {
      text: "text-yellow-400",
      bg: "bg-yellow-500/10",
      border: "border-yellow-500/30",
      icon: Search,
      label: "Needs Review",
    };
  };

  const verdictStyle = getVerdictStyle();
  const VerdictIcon = verdictStyle.icon;

  const sources = Array.isArray(data.sources) ? data.sources : [];

  return (
    <section className="mt-8">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-green-500/10 border border-green-500/20 flex items-center justify-center">
            <FileCheck2 size={21} className="text-green-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Fact Verification</h2>
            <p className="text-slate-500 text-sm mt-0.5">Evidence-based verification of the detected claim</p>
          </div>
        </div>
        <div className={`hidden sm:flex items-center gap-2 px-3 py-2 rounded-xl border ${verdictStyle.bg} ${verdictStyle.border}`}>
          <ShieldCheck size={16} className={verdictStyle.text} />
          <span className={`text-xs font-semibold ${verdictStyle.text}`}>{verdictStyle.label}</span>
        </div>
      </div>
      <div className={`rounded-2xl border ${verdictStyle.border} ${verdictStyle.bg} p-5 mb-5`}>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className={`w-11 h-11 rounded-xl bg-slate-950/40 border ${verdictStyle.border} flex items-center justify-center`}>
              <VerdictIcon size={22} className={verdictStyle.text} />
            </div>
            <div>
              <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">Verification Verdict</p>
              <h3 className={`text-xl font-bold mt-1 ${verdictStyle.text}`}>{verdict}</h3>
            </div>
          </div>
          <div className={`px-4 py-2 rounded-xl border ${verdictStyle.border} bg-slate-950/30`}>
            <span className={`text-sm font-semibold ${verdictStyle.text}`}>Fact Check Result</span>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
              <Search size={16} className="text-blue-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Detected Claim</h3>
              <p className="text-slate-600 text-xs mt-0.5">Claim extracted from the submitted content</p>
            </div>
          </div>
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 min-h-[150px]">
            <p className="text-slate-300 leading-7 text-sm">
              {data.claim || "No claim extracted."}
            </p>
          </div>
        </div>
        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
              <FileCheck2 size={16} className="text-purple-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Verification Reason</h3>
              <p className="text-slate-600 text-xs mt-0.5">Why this verdict was assigned</p>
            </div>
          </div>
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 min-h-[150px]">
            <p className="text-slate-300 leading-7 text-sm">
              {data.reason || "No verification explanation available."}
            </p>
          </div>
        </div>
      </div>
      <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5 mt-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center">
              <ExternalLink size={17} className="text-blue-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Verification Sources</h3>
              <p className="text-slate-500 text-xs mt-0.5">Sources used to verify the claim</p>
            </div>
          </div>
          <span className="text-xs text-slate-500 bg-slate-800/60 px-2.5 py-1 rounded-lg">
            {sources.length} {sources.length === 1 ? "Source" : "Sources"}
          </span>
        </div>
        {sources.length > 0 ? (
          <div className="space-y-2">
            {sources.map((source, index) => (
              <a
                key={index}
                href={source}
                target="_blank"
                rel="noreferrer"
                className="group flex items-center gap-3 bg-slate-950/60 border border-slate-800 hover:border-blue-500/30 hover:bg-blue-500/5 rounded-xl px-4 py-3 transition-all"
              >
                <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center shrink-0">
                  <span className="text-xs font-semibold text-slate-400">{index + 1}</span>
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-blue-400 group-hover:text-blue-300 truncate transition-colors">
                    {source}
                  </p>
                </div>
                <ArrowUpRight size={16} className="text-slate-600 group-hover:text-blue-400 shrink-0 transition-colors" />
              </a>
            ))}
          </div>
        ) : (
          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 text-center">
            <ExternalLink size={22} className="text-slate-600 mx-auto mb-2" />
            <p className="text-slate-500 text-sm">No verification sources available.</p>
          </div>
        )}
      </div>
    </section>
  );
}