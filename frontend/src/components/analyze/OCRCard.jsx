export default function OCRCard({ data }) {
  if (!data) return null;

  return (
    <div className="bg-slate-800 rounded-2xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-white mb-6">
        OCR Results
      </h2>

      <div className="space-y-5">
        <div className="flex justify-between">
          <span className="text-gray-400">OCR Used</span>

          <span className="text-white font-semibold">
            {data.used ? "Yes" : "No"}
          </span>
        </div>

        <div className="flex justify-between">
          <span className="text-gray-400">Confidence</span>

          <span className="text-white font-semibold">
            {data.confidence}%
          </span>
        </div>

        <div>
          <p className="text-gray-400 mb-2">
            Extracted Text
          </p>

          <div className="bg-slate-900 rounded-xl p-4 min-h-[120px] text-gray-300">
            {data.extracted_text || "No OCR performed."}
          </div>
        </div>
      </div>
    </div>
  );
}