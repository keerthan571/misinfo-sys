export default function OCRCard({ data }) {
  if (!data) return null;

  const isOCRUsed = data.used;
  const hasText = data.extracted_text?.trim();

  return (
    <div className="bg-slate-800 rounded-2xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6">
        📝 OCR Analysis
      </h2>

      <div className="space-y-5">
        {/* Input Type */}
        <div className="flex justify-between items-center">
          <span className="text-gray-400">
            Input Type
          </span>

          <span
            className={`font-semibold ${
              isOCRUsed
                ? "text-blue-400"
                : "text-green-400"
            }`}
          >
            {isOCRUsed ? "Image + OCR" : "Direct Text"}
          </span>
        </div>

        {/* OCR Status */}
        <div className="flex justify-between items-center">
          <span className="text-gray-400">
            OCR Status
          </span>

          <span
            className={`font-semibold ${
              isOCRUsed
                ? "text-green-400"
                : "text-gray-400"
            }`}
          >
            {isOCRUsed
              ? "✅ Completed"
              : "Not Required"}
          </span>
        </div>

        {/* Confidence */}
        {isOCRUsed && (
          <div className="flex justify-between items-center">
            <span className="text-gray-400">
              OCR Confidence
            </span>

            <span className="font-semibold text-green-400">
              {data.confidence ?? 0}%
            </span>
          </div>
        )}

        {/* Word Count */}
        {isOCRUsed && (
          <div className="flex justify-between items-center">
            <span className="text-gray-400">
              Words Extracted
            </span>

            <span className="text-white font-semibold">
              {data.word_count ?? 0}
            </span>
          </div>
        )}

        {/* Extracted Text */}
        <div>
          <p className="text-gray-400 mb-2">
            Extracted Content
          </p>

          <div className="bg-slate-900 rounded-xl p-4 text-gray-300 leading-relaxed min-h-[180px] max-h-72 overflow-y-auto whitespace-pre-wrap border border-slate-700">
            {hasText ? (
              data.extracted_text
            ) : (
              <span className="text-gray-500 italic">
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