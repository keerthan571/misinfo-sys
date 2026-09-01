import { useState } from "react";
import { Upload, Image as ImageIcon, FileImage, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
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
        const extractedText =
          data.extracted_text ||
          data.post_text ||
          "";

        // Put the exact multilingual OCR result
        // into the News Text box.
        setNews(extractedText);

        setOcrEngagement({
          ...(data.ordered_values || {}),
          publisher: data.publisher || null,
          publisher_confidence: data.publisher_confidence || 0,
          publisher_detection_method:
            data.publisher_detection_method || null,
        });
        setOcrConfidence(data.confidence ?? 0);
        setOcrSuccess("OCR completed successfully.");
      } else {
        setOcrError(data.message || "OCR failed.");
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
    if (value === "Text") {
      setImage(null);
      setFollowers("");
      setOcrEngagement({});
      setOcrError("");
      setOcrSuccess("");
      setOcrConfidence(null);
    }
    if (value !== "Instagram") {
      setFollowers("");
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">
            Analyze News
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Enter text directly or analyze a social media screenshot.
          </p>
        </div>
        <div className="hidden sm:flex w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 items-center justify-center">
          <ImageIcon size={20} className="text-blue-400" />
        </div>
      </div>

      <label className="block text-sm font-semibold text-slate-200 mb-3">
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
        className="w-full bg-[#0F172A] rounded-2xl px-4 py-4 text-white placeholder:text-slate-500 outline-none resize-none border border-slate-700/80 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 transition-all"
      />

      {isTextMode && (
        <div className="mt-4 bg-blue-500/5 border border-blue-500/20 rounded-2xl p-4">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
              <FileImage size={18} className="text-blue-400" />
            </div>
            <div>
              <p className="text-blue-300 font-semibold">
                Text / General Analysis
              </p>
              <p className="text-slate-400 text-sm mt-1 leading-6">
                Text-only analysis performs misinformation detection and fact
                verification. Social-media engagement, spread prediction and
                propagation graphs require a social-media screenshot.
              </p>
            </div>
          </div>
        </div>
      )}

      {!isTextMode && (
        <>
          <div className="flex items-center my-7">
            <div className="flex-1 border-t border-slate-700" />
            <span className="px-5 text-slate-500 text-xs font-semibold tracking-widest">
              OR
            </span>
            <div className="flex-1 border-t border-slate-700" />
          </div>

          <label className="block text-sm font-semibold text-slate-200 mb-3">
            Upload Social Media Screenshot
          </label>

          <label
            htmlFor="social-media-image"
            className="
              group
              relative
              flex
              flex-col
              items-center
              justify-center
              w-full
              min-h-[150px]
              rounded-2xl
              border
              border-dashed
              border-slate-600
              bg-[#0F172A]
              hover:border-blue-500/70
              hover:bg-blue-500/[0.03]
              cursor-pointer
              transition-all
              duration-200
            "
          >
            <input
              id="social-media-image"
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="hidden"
            />

            <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center group-hover:bg-blue-500/15 transition">
              <Upload size={22} className="text-blue-400" />
            </div>

            <p className="text-slate-200 font-medium mt-3">
              Click to upload screenshot
            </p>

            <p className="text-slate-500 text-sm mt-1">
              PNG, JPG or JPEG • Maximum 5 MB
            </p>
          </label>

          {image && (
            <div className="mt-4 bg-[#0F172A] border border-slate-700 rounded-2xl p-4">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-9 h-9 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center justify-center">
                  <CheckCircle size={18} className="text-green-400" />
                </div>
                <div className="min-w-0">
                  <p className="text-green-400 text-sm font-semibold">
                    Image selected
                  </p>
                  <p className="text-slate-400 text-xs truncate">
                    {image.name}
                  </p>
                </div>
              </div>

              <img
                src={URL.createObjectURL(image)}
                alt="Uploaded social media screenshot"
                className="w-full max-h-80 object-contain rounded-xl border border-slate-700 bg-slate-950"
              />
            </div>
          )}

          {ocrLoading && (
            <div className="mt-4 flex items-center gap-3 bg-yellow-500/5 border border-yellow-500/20 rounded-xl p-4">
              <Loader2 size={18} className="text-yellow-400 animate-spin" />
              <div>
                <p className="text-yellow-300 font-semibold text-sm">
                  Extracting text...
                </p>
                <p className="text-yellow-400/60 text-xs mt-0.5">
                  Processing the uploaded screenshot
                </p>
              </div>
            </div>
          )}

          {ocrSuccess && (
            <div className="mt-4 flex items-center gap-3 bg-green-500/5 border border-green-500/20 rounded-xl p-4">
              <CheckCircle size={19} className="text-green-400 shrink-0" />
              <div>
                <p className="text-green-300 font-semibold text-sm">
                  {ocrSuccess}
                </p>
                <p className="text-green-400/70 text-xs mt-1">
                  OCR Confidence: {ocrConfidence}%
                </p>
              </div>
            </div>
          )}

          {ocrError && (
            <div className="mt-4 flex items-center gap-3 bg-red-500/5 border border-red-500/20 rounded-xl p-4">
              <AlertCircle size={19} className="text-red-400 shrink-0" />
              <p className="text-red-300 text-sm">
                {ocrError}
              </p>
            </div>
          )}
        </>
      )}

      <div className="mt-6">
        <label className="block text-sm font-semibold text-slate-200 mb-3">
          Select Analysis Platform
        </label>

        <select
          value={platform}
          onChange={handlePlatformChange}
          className="w-full bg-[#0F172A] text-white rounded-2xl px-4 py-3.5 border border-slate-700/80 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 outline-none transition-all"
        >
          <option value="">Select Platform</option>
          <option value="Text">Text / General</option>
          <option value="Instagram">Instagram</option>
          <option value="Facebook">Facebook</option>
          <option value="Twitter">Twitter / X</option>
        </select>

        {platform === "Instagram" && (
          <div className="mt-5">
            <label className="block text-sm font-semibold text-slate-200 mb-3">
              Instagram Account Followers
            </label>

            <input
              type="number"
              min="0"
              value={followers}
              onChange={(e) =>
                setFollowers(Number(e.target.value))
              }
              placeholder="Enter followers count"
              className="w-full bg-[#0F172A] text-white placeholder:text-slate-500 rounded-2xl px-4 py-3.5 border border-slate-700/80 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 outline-none transition-all"
            />
          </div>
        )}
      </div>

      <button
        onClick={onAnalyze}
        disabled={loading || ocrLoading}
        className="
          mt-8
          w-full
          bg-gradient-to-r
          from-blue-600
          to-blue-500
          hover:from-blue-500
          hover:to-blue-400
          disabled:from-slate-700
          disabled:to-slate-700
          disabled:text-slate-400
          py-3.5
          rounded-2xl
          font-bold
          text-white
          shadow-lg
          shadow-blue-600/20
          hover:shadow-blue-500/30
          transition-all
          duration-200
        "
      >
        {loading ? "Analyzing..." : "Analyze"}
      </button>
    </div>
  );
}