import {
  Globe2,
  CheckCircle,
  Signal,
} from "lucide-react";

export default function PlatformCard({ data }) {
  if (!data) return null;

  const confidence =
    Number(
      String(data.confidence ?? "0").replace("%", "")
    ) || 0;

  return (
    <div className="mt-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
          <Globe2
            size={21}
            className="text-indigo-400"
          />
        </div>

        <div>
          <h2 className="text-2xl font-bold text-white">
            Platform Detection
          </h2>

          <p className="text-slate-500 text-sm mt-0.5">
            Detected social media platform and matching signals
          </p>
        </div>
      </div>

      <div className="space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-green-500/10 border border-green-500/20 flex items-center justify-center">
                <CheckCircle
                  size={19}
                  className="text-green-400"
                />
              </div>

              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                  Platform
                </p>

                <p className="text-green-400 font-semibold mt-1">
                  {data.platform || "Unknown"}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
            <div className="flex justify-between items-center mb-3">
              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                  Detection Confidence
                </p>

                <p className="text-slate-300 text-sm mt-1">
                  Confidence in platform detection
                </p>
              </div>

              <span className="text-blue-400 font-bold text-lg">
                {confidence}%
              </span>
            </div>

            <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-blue-600 to-blue-400 transition-all duration-500"
                style={{
                  width: `${Math.min(confidence, 100)}%`,
                }}
              />
            </div>
          </div>
        </div>

        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Signal
              size={18}
              className="text-indigo-400"
            />

            <div>
              <h3 className="text-sm font-semibold text-white">
                Matched Signals
              </h3>

              <p className="text-slate-500 text-xs mt-0.5">
                Indicators used to identify the platform
              </p>
            </div>
          </div>

          {data.matched_signals?.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {data.matched_signals.map(
                (signal, index) => (
                  <span
                    key={index}
                    className="
                      bg-indigo-500/10
                      border
                      border-indigo-500/20
                      text-indigo-300
                      text-sm
                      px-3
                      py-1.5
                      rounded-lg
                    "
                  >
                    {signal}
                  </span>
                )
              )}
            </div>
          ) : (
            <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4">
              <p className="text-slate-500 text-sm">
                No matching signals available.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}