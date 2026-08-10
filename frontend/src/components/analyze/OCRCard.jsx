import {
  ScanText,
  CheckCircle,
  FileText,
  Image as ImageIcon,
} from "lucide-react";

export default function OCRCard({ data }) {
  if (!data) return null;

  const isOCRUsed =
    data.used === true ||
    data.input_type === "Image" ||
    data.status === "OCR Completed";

  const hasText =
    data.extracted_text &&
    data.extracted_text.trim();

  const confidence =
    Number(
      String(data.confidence ?? "0").replace("%", "")
    ) || 0;

  return (
    <div className="mt-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
          <ScanText
            size={21}
            className="text-cyan-400"
          />
        </div>

        <div>
          <h2 className="text-2xl font-bold text-white">
            OCR Analysis
          </h2>

          <p className="text-slate-500 text-sm mt-0.5">
            Optical character recognition from the submitted image
          </p>
        </div>
      </div>

      <div className="space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
            <div className="flex items-center gap-3">
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                  isOCRUsed
                    ? "bg-blue-500/10 border border-blue-500/20"
                    : "bg-green-500/10 border border-green-500/20"
                }`}
              >
                {isOCRUsed ? (
                  <ImageIcon
                    size={19}
                    className="text-blue-400"
                  />
                ) : (
                  <FileText
                    size={19}
                    className="text-green-400"
                  />
                )}
              </div>

              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                  Input Type
                </p>

                <p
                  className={`font-semibold mt-1 ${
                    isOCRUsed
                      ? "text-blue-400"
                      : "text-green-400"
                  }`}
                >
                  {isOCRUsed
                    ? "Image + OCR"
                    : "Direct Text"}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
            <div className="flex items-center gap-3">
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                  isOCRUsed
                    ? "bg-green-500/10 border border-green-500/20"
                    : "bg-slate-500/10 border border-slate-500/20"
                }`}
              >
                <CheckCircle
                  size={19}
                  className={
                    isOCRUsed
                      ? "text-green-400"
                      : "text-slate-500"
                  }
                />
              </div>

              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                  OCR Status
                </p>

                <p
                  className={`font-semibold mt-1 ${
                    isOCRUsed
                      ? "text-green-400"
                      : "text-slate-400"
                  }`}
                >
                  {isOCRUsed
                    ? "Completed"
                    : "Not Required"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {isOCRUsed && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
              <div className="flex justify-between items-center mb-3">
                <div>
                  <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                    OCR Confidence
                  </p>

                  <p className="text-slate-300 text-sm mt-1">
                    Recognition confidence
                  </p>
                </div>

                <span className="text-green-400 text-lg font-bold">
                  {confidence}%
                </span>
              </div>

              <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-green-600 to-emerald-400 transition-all duration-500"
                  style={{
                    width: `${Math.min(
                      confidence,
                      100
                    )}%`,
                  }}
                />
              </div>
            </div>

            <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
              <div className="flex items-center justify-between h-full">
                <div>
                  <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                    Words Extracted
                  </p>

                  <p className="text-slate-300 text-sm mt-1">
                    Text recognized from image
                  </p>
                </div>

                <span className="text-3xl font-bold text-white">
                  {data.word_count ?? 0}
                </span>
              </div>
            </div>
          </div>
        )}

        <div className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <FileText
              size={18}
              className="text-cyan-400"
            />

            <div>
              <h3 className="text-sm font-semibold text-white">
                Extracted Content
              </h3>

              <p className="text-slate-500 text-xs mt-0.5">
                Text detected from the submitted content
              </p>
            </div>
          </div>

          <div
            className="
              bg-slate-950/70
              border
              border-slate-800
              rounded-xl
              p-4
              text-slate-300
              leading-7
              min-h-[180px]
              max-h-72
              overflow-y-auto
              whitespace-pre-wrap
            "
          >
            {hasText ? (
              data.extracted_text
            ) : (
              <span className="text-slate-500 italic">
                {isOCRUsed
                  ? "No readable text was found in the uploaded image."
                  : "User entered text directly. OCR was not required."}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}