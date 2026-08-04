import { useState } from "react";
import apiClient from "../../api/apiClient";

export default function AnalyzeInput({
  news,
  setNews,
  image,
  setImage,
  loading,
  onAnalyze,
  platform,
  setPlatform,
  followers,
  setFollowers,
}) {
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrConfidence, setOcrConfidence] = useState(null);
  const [ocrError, setOcrError] = useState("");
  const [ocrSuccess, setOcrSuccess] = useState("");

  const MAX_FILE_SIZE = 5 * 1024 * 1024;

  const handleImageChange = async (e) => {
    const file = e.target.files?.[0];

    if (!file) return;

    setOcrError("");
    setOcrSuccess("");
    setOcrConfidence(null);

    if (!file.type.startsWith("image/")) {
      setOcrError("Please upload a valid image.");
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setOcrError("Image size must be less than 5 MB.");
      return;
    }

    setImage(file);

    try {
      setOcrLoading(true);

      const formData = new FormData();
      formData.append("file", file);

      const { data } = await apiClient.post(
        "/api/ocr/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      console.log(data);

      if (data.status === "success") {
        setNews(data.extracted_text || "");
        setOcrConfidence(data.confidence ?? 0);
        setOcrSuccess("OCR completed successfully.");
        if (!data.extracted_text) {
          setOcrError("No post text found. Engagement numbers were detected.");
        }
      } else {
        setOcrError(data.message || "OCR failed.");
      }
    } catch (err) {
      setOcrError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "OCR service unavailable."
      );
    } finally {
      setOcrLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">
      <h2 className="text-2xl font-bold text-white mb-6">
        Analyze News
      </h2>

      <div>
        <label className="text-white font-semibold">
          News Text / OCR Edited Text
        </label>

        <textarea
          rows={10}
          value={news}
          onChange={(e) => setNews(e.target.value)}
          placeholder="OCR text will appear here. You can edit it before analysis..."
          className="w-full mt-3 bg-slate-900 rounded-xl p-4 text-white outline-none resize-none"
        />
      </div>

      <div className="flex items-center my-6">
        <div className="flex-1 border-t border-slate-600"></div>
        <span className="px-4 text-gray-400 text-sm">
          OR
        </span>
        <div className="flex-1 border-t border-slate-600"></div>
      </div>

      <div>
        <label className="text-white font-semibold">
          Upload News Screenshot
        </label>

        <input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          className="block mt-3 text-gray-300"
        />

        {image && (
          <div className="mt-5">
            <p className="text-green-400 text-sm mb-3">
              Selected: {image.name}
            </p>

            <img
              src={URL.createObjectURL(image)}
              alt="Uploaded News"
              className="w-full max-h-80 object-contain rounded-xl border border-slate-600"
            />
          </div>
        )}

        {ocrLoading && (
          <div className="mt-4 bg-yellow-900/30 border border-yellow-500 rounded-lg p-3">
            <p className="text-yellow-300">
              ⏳ Extracting text from image...
            </p>
          </div>
        )}

        {ocrSuccess && (
          <div className="mt-4 bg-green-900/30 border border-green-500 rounded-lg p-3">
            <p className="text-green-400 font-semibold">
              ✅ {ocrSuccess}
            </p>
            <p className="text-green-300 text-sm mt-1">
              OCR Confidence: {ocrConfidence}%
            </p>
          </div>
        )}

        {ocrError && (
          <div className="mt-4 bg-red-900/30 border border-red-500 rounded-lg p-3">
            <p className="text-red-400">
              ❌ {ocrError}
            </p>
          </div>
        )}
      </div>

      <div className="mt-6">
        <label className="text-white font-semibold">
          Select Platform
        </label>

        <select
          value={platform}
          onChange={(e) => {
            const value = e.target.value;
            setPlatform(value);

            if (value !== "Instagram") {
              setFollowers("");
            }
          }}
          className="w-full mt-3 bg-slate-900 text-white rounded-xl p-3 outline-none border border-slate-600"
        >
          <option value="">
            Select Platform
          </option>

          <option value="Instagram">
            Instagram
          </option>

          <option value="Facebook">
            Facebook
          </option>

          <option value="Twitter">
            Twitter / X
          </option>
        </select>
        {platform === "Instagram" && (
          <div className="mt-5">
            <label className="text-white font-semibold">
              Instagram Account Followers (Optional)
            </label>

            <input
              type="number"
              value={followers}
              onChange={(e) => setFollowers(e.target.value)}
              placeholder="Enter account followers count"
              className="w-full mt-3 bg-slate-900 text-white rounded-xl p-3 outline-none border border-slate-600"
            />

            <p className="text-gray-400 text-sm mt-2">
              Used only for Instagram spread prediction.
            </p>
          </div>
        )}
      </div>

      <button
        onClick={onAnalyze}
        disabled={loading || ocrLoading}
        className="mt-8 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed py-3 rounded-xl font-bold text-white"
      >
        {loading ? "Analyzing..." : "Analyze"}
      </button>
    </div>
  );
}