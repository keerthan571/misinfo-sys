export default function AnalyzeInput({
  news,
  setNews,
  image,
  setImage,
  loading,
  onAnalyze,
}) {
  return (
    <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">

      <h2 className="text-2xl font-bold text-white mb-6">
        Analyze News
      </h2>

      {/* Text Input */}
      <div>
        <label className="text-white font-semibold">
          News Text
        </label>

        <textarea
          rows={8}
          value={news}
          onChange={(e) => setNews(e.target.value)}
          placeholder="Paste your news article here..."
          className="w-full mt-3 bg-slate-900 rounded-xl p-4 text-white outline-none resize-none"
        />
      </div>

      {/* Divider */}
      <div className="flex items-center my-6">
        <div className="flex-1 border-t border-slate-600"></div>
        <span className="px-4 text-gray-400 text-sm">OR</span>
        <div className="flex-1 border-t border-slate-600"></div>
      </div>

      {/* Image Upload */}
      <div>
        <label className="text-white font-semibold">
          Upload News Screenshot
        </label>

        <input
          type="file"
          accept="image/*"
          onChange={(e) => setImage(e.target.files[0])}
          className="block mt-3 text-gray-300"
        />

        {image && (
          <p className="mt-3 text-green-400 text-sm">
            Selected: {image.name}
          </p>
        )}
      </div>

      {/* Analyze Button */}
      <button
        onClick={onAnalyze}
        disabled={loading}
        className="mt-8 w-full bg-blue-600 hover:bg-blue-700 py-3 rounded-xl font-bold text-white disabled:opacity-50"
      >
        {loading ? "Analyzing..." : "Analyze"}
      </button>

    </div>
  );
}