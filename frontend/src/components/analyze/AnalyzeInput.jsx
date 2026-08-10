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
  setOcrEngagement,
}) {
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrConfidence, setOcrConfidence] = useState(null);
  const [ocrError, setOcrError] = useState("");
  const [ocrSuccess, setOcrSuccess] = useState("");

  const MAX_FILE_SIZE = 5 * 1024 * 1024;

  const isTextMode = platform === "Text";

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

      console.log("OCR RESPONSE:", data);

      if (data.status === "success") {
        setNews(data.extracted_text || "");

        setOcrEngagement({
          ...(data.ordered_values || {}),
          publisher: data.publisher || null,
          publisher_confidence: data.publisher_confidence || 0,
          publisher_detection_method:
            data.publisher_detection_method || null,
        });

        setOcrConfidence(
          data.confidence ?? 0
        );

        setOcrSuccess(
          "OCR completed successfully."
        );
      } else {
        setOcrError(
          data.message || "OCR failed."
        );
      }
    } catch (err) {
      console.error("OCR ERROR:", err);

      setOcrError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "OCR service unavailable."
      );
    } finally {
      setOcrLoading(false);
    }
  };

  const handlePlatformChange = (e) => {
    const value = e.target.value;

    setPlatform(value);

    /*
     * Text analysis does not use:
     * - uploaded image
     * - OCR engagement
     * - Instagram followers
     */

    if (value === "Text") {
      setImage(null);
      setFollowers("");
      setOcrEngagement({});
      setOcrError("");
      setOcrSuccess("");
      setOcrConfidence(null);
    }

    /*
     * Followers are only relevant to Instagram.
     */
    if (value !== "Instagram") {
      setFollowers("");
    }
  };

  return (
    <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">

      {/* Header */}

      <h2 className="text-2xl font-bold text-white mb-6">
        Analyze News
      </h2>

      {/* Text Input */}

      <label className="text-white font-semibold">
        News Text
      </label>

      <textarea
        rows={10}
        value={news}
        onChange={(e) => setNews(e.target.value)}
        placeholder={
          isTextMode
            ? "Enter the news claim or article text here..."
            : "OCR text will appear here..."
        }
        className="w-full mt-3 bg-slate-900 rounded-xl p-4 text-white outline-none resize-none border border-slate-600 focus:border-blue-500"
      />

      {/* Explanation for text mode */}

      {isTextMode && (
        <div className="mt-4 bg-blue-900/20 border border-blue-500/40 rounded-xl p-4">

          <p className="text-blue-300 font-semibold">
            📝 Text / General Analysis
          </p>

          <p className="text-slate-400 text-sm mt-1 leading-6">
            Text-only analysis performs misinformation
            detection and fact verification. Social-media
            engagement, spread prediction and propagation
            graphs require a social-media screenshot.
          </p>

        </div>
      )}

      {/* Screenshot section */}

      {!isTextMode && (
        <>
          <div className="flex items-center my-6">

            <div className="flex-1 border-t border-slate-600"></div>

            <span className="px-4 text-gray-400 text-sm">
              OR
            </span>

            <div className="flex-1 border-t border-slate-600"></div>

          </div>

          <label className="text-white font-semibold">
            Upload Social Media Screenshot
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
                alt="Uploaded social media screenshot"
                className="w-full max-h-80 object-contain rounded-xl border border-slate-600"
              />

            </div>
          )}

          {/* OCR Loading */}

          {ocrLoading && (
            <div className="mt-4 bg-yellow-900/30 border border-yellow-500 rounded-lg p-3">

              <p className="text-yellow-300">
                ⏳ Extracting text...
              </p>

            </div>
          )}

          {/* OCR Success */}

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

          {/* OCR Error */}

          {ocrError && (
            <div className="mt-4 bg-red-900/30 border border-red-500 rounded-lg p-3">

              <p className="text-red-400">
                ❌ {ocrError}
              </p>

            </div>
          )}
        </>
      )}

      {/* Platform */}

      <div className="mt-6">

        <label className="text-white font-semibold">
          Select Analysis Platform
        </label>

        <select
          value={platform}
          onChange={handlePlatformChange}
          className="w-full mt-3 bg-slate-900 text-white rounded-xl p-3 border border-slate-600 focus:border-blue-500 outline-none"
        >

          <option value="">
            Select Platform
          </option>

          <option value="Text">
            Text / General
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

        {/* Instagram Followers */}

        {platform === "Instagram" && (
          <div className="mt-5">

            <label className="text-white font-semibold">
              Instagram Account Followers
            </label>

            <input
              type="number"
              min="0"
              value={followers}
              onChange={(e) =>
                setFollowers(
                  Number(e.target.value)
                )
              }
              placeholder="Enter followers count"
              className="w-full mt-3 bg-slate-900 text-white rounded-xl p-3 border border-slate-600 outline-none focus:border-blue-500"
            />

          </div>
        )}

      </div>

      {/* Analyze Button */}

      <button
        onClick={onAnalyze}
        disabled={
          loading ||
          ocrLoading
        }
        className="mt-8 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 py-3 rounded-xl font-bold text-white transition"
      >
        {loading
          ? "Analyzing..."
          : "Analyze"}
      </button>

    </div>
  );
}