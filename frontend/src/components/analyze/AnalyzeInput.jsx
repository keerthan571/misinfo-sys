import { useState } from "react";
import {
  Upload,
  Image as ImageIcon,
  FileImage,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";
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
  const [instagramContentType, setInstagramContentType] = useState("");
  const [detectedInstagramLayout, setDetectedInstagramLayout] = useState("");
  const [showReelForm, setShowReelForm] = useState(false);
  const [manualEngagement, setManualEngagement] = useState({
    likes: "",
    comments: "",
    reposts: "",
    shares: "",
  });
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
      formData.append("platform", platform);
      const response = await apiClient.post("/api/ocr/", formData);
      const data = response.data;
      console.log("OCR RESPONSE:", data);
      if (!data || typeof data !== "object") {
        throw new Error("OCR returned an empty or invalid response.");
      }
      if (
        data &&
        typeof data === "object" &&
        (
          data.status === "success" ||
          data.post_text ||
          data.extracted_text
        )
      ) {
        // ---------------------------------------------------------
        // IMPORTANT OCR TEXT SELECTION
        // ---------------------------------------------------------
        //
        // raw_text is the ORIGINAL Tesseract OCR output.
        //
        // Example:
        //
        // raw_text:
        //   ಅಶೋಕ್‌ ಅಣ್ಣಾ, ೧೫೮ ಕುರಿತು ಮರಿ ಖರ್ಗೆ ಪ್ರಶ್ನೆ ...
        //
        // post_text:
        //   ಅಶ ಕ ಅಣ ಣ , ೧5೮ ಕ ರ ತ ...
        //
        // We MUST prefer raw_text.
        //
        // This prevents the coordinate/processed post_text from
        // damaging Kannada/Hindi characters before NLP.
        //
        const extractedText =
          data.post_text ||
          data.extracted_text ||
          "";
        setNews(extractedText);
        const detectedLayout = data.instagram_layout || "";
        setDetectedInstagramLayout(detectedLayout);
        // The user explicitly chooses Post or Reel. Only Reel opens
        // the manual engagement form; Post keeps the existing flow.
        setShowReelForm(
          platform === "Instagram" &&
          instagramContentType === "reel"
        );
        setManualEngagement({
          likes: "",
          comments: "",
          reposts: "",
          shares: "",
        });
        setOcrEngagement({
          ...(data.ordered_values || {}),
          // Preserve the layout detected by the existing OCR flow for Posts.
          // Only the explicitly selected Reel uses the vertical Reel layout.
          instagram_layout:
            platform === "Instagram" && instagramContentType === "reel"
              ? "vertical"
              : detectedLayout,
          // IMPORTANT:
          // Always send CLEAN OCR post text to analysis.
          // NEVER send raw_text.
          post_text: extractedText,
          publisher:
            data.publisher || null,
          publisher_confidence:
            data.publisher_confidence || 0,
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
          data.message ||
          "OCR failed."
        );
      }
    } catch (err) {
      console.error("OCR ERROR:", err);
      console.error("OCR RESPONSE DATA:", err.response?.data);
      setOcrError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        "Unknown OCR error"
      );
    } finally {
      setOcrLoading(false);
    }
  };
  const handlePlatformChange = (e) => {
    const value = e.target.value;
    setPlatform(value);
    setShowReelForm(false);
    setInstagramContentType("");
    setDetectedInstagramLayout("");
    setManualEngagement({
      likes: "",
      comments: "",
      reposts: "",
      shares: "",
    });
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
  const handleInstagramContentTypeChange = (e) => {
    const value = e.target.value;
    setInstagramContentType(value);
    setOcrError("");
    setManualEngagement({
      likes: "",
      comments: "",
      reposts: "",
      shares: "",
    });
    setOcrEngagement((prev) => ({
      ...prev,
      ...(value === "reel"
        ? { instagram_layout: "vertical" }
        : value === "post"
          ? { instagram_layout: detectedInstagramLayout }
          : {}),
      manual_engagement: {},
    }));
    setShowReelForm(
      value === "reel" && Boolean(image) && Boolean(ocrSuccess)
    );
  };
  const handleAnalyzeClick = () => {
    if (platform === "Instagram" && !instagramContentType) {
      setOcrError("Please select Instagram Post or Instagram Reel.");
      return;
    }
    if (
      ["Instagram", "Facebook", "Twitter"].includes(platform) &&
      !String(followers ?? "").trim()
    ) {
      setOcrError("Please enter the follower count for the selected platform.");
      return;
    }
    if (platform === "Instagram" && instagramContentType === "reel") {
      if (image && ocrSuccess) {
        setShowReelForm(true);
      } else {
        setOcrError("Upload the Instagram Reel screenshot and wait for OCR to finish.");
      }
      return;
    }
    onAnalyze();
  };
  return (
    <div className="space-y-5 text-slate-100">
      {showReelForm ? (
        <div className="space-y-4">
          <h2 className="text-xl md:text-2xl font-bold tracking-tight text-white no-underline decoration-transparent">
            Instagram Reel Engagement
          </h2>
          {ocrError && (
            <p className="text-sm text-red-300" role="alert">{ocrError}</p>
          )}
          {["likes", "comments", "reposts", "shares"].map((key) => (
            <div key={key}>
              <label className="mb-2 block capitalize text-sm font-semibold text-slate-200">
                {key}
              </label>
              <input
                type="number"
                min="0"
                value={manualEngagement[key]}
                onChange={(e) => {
                  const value = e.target.value;
                  setManualEngagement((prev) => ({
                    ...prev,
                    [key]: value,
                  }));
                  setOcrEngagement((prev) => ({
                    ...prev,
                    manual_engagement: {
                      ...(prev.manual_engagement || {}),
                      [key]: value,
                    },
                  }));
                }}
                placeholder={`Enter ${key}`}
                className="w-full rounded-xl border border-slate-700/80 bg-[#0F172A] px-4 py-3 text-sm text-white placeholder:text-slate-500 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10"
              />
            </div>
          ))}
          <button
            type="button"
            onClick={onAnalyze}
            className="w-full rounded-xl bg-blue-600 py-3 font-bold text-white"
          >
            Continue to Analysis
          </button>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between gap-4 mb-5">
            <div>
              <h2 className="text-xl md:text-2xl font-bold tracking-tight text-white no-underline decoration-transparent">
                Analyze News
              </h2>
              <p className="mt-1 text-sm text-slate-400 leading-6 max-w-2xl">
                Enter text directly or analyze a social media screenshot.
              </p>
            </div>
            <div className="hidden sm:flex w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 items-center justify-center">
              <ImageIcon
                size={20}
                className="text-blue-400"
              />
            </div>
          </div>
          <label className="mb-2 block text-sm font-semibold text-slate-200">
            News Text
          </label>
          <textarea
            rows={10}
            value={news}
            onChange={(e) =>
              setNews(e.target.value)
            }
            placeholder={
              isTextMode
                ? "Enter the news claim or article text here..."
                : "OCR text will appear here..."
            }
            className="w-full resize-none rounded-2xl border border-slate-700/80 bg-[#0F172A] px-4 py-4 text-sm leading-6 text-white placeholder:text-slate-500 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10"
          />
          {isTextMode && (
            <div className="mt-4 bg-blue-500/5 border border-blue-500/20 rounded-2xl p-4">
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                  <FileImage
                    size={18}
                    className="text-blue-400"
                  />
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
          <div className="mt-6">
          <label className="mb-2 block text-sm font-semibold text-slate-200">
            Select Analysis Platform
          </label>
          <select
            value={platform}
            onChange={handlePlatformChange}
            className="w-full rounded-xl border border-slate-700/80 bg-[#0F172A] px-4 py-3.5 text-sm text-white outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10"
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
          {["Instagram", "Facebook", "Twitter"].includes(platform) && (
            <div className="mt-4 space-y-4">
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-200">
                  {platform === "Instagram"
                    ? "Instagram Followers"
                    : platform === "Facebook"
                      ? "Facebook Page Followers"
                      : "Twitter/X Followers"}
                  <span className="text-red-400"> *</span>
                </label>
                <input
                  type="number"
                  min="0"
                  required
                  value={followers}
                  onChange={(e) => {
                    setFollowers(e.target.value);
                    setOcrError("");
                  }}
                  placeholder="Enter follower count"
                  className="w-full rounded-xl border border-slate-700/80 bg-[#0F172A] px-4 py-3.5 text-sm text-white outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10"
                />
              </div>
              {platform === "Instagram" && (
                <>
                  <div>
                    <label className="mb-2 block text-sm font-semibold text-slate-200">
                      Instagram Content Type
                    </label>
                    <select
                      value={instagramContentType}
                      onChange={handleInstagramContentTypeChange}
                      className="w-full rounded-xl border border-slate-700/80 bg-[#0F172A] px-4 py-3.5 text-sm text-white outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10"
                    >
                      <option value="">Select Instagram Content Type</option>
                      <option value="post">Instagram Post</option>
                      <option value="reel">Instagram Reel</option>
                    </select>
                  </div>
                  <div className="flex items-start gap-3 rounded-xl border border-blue-500/20 bg-blue-500/5 p-4">
                    <AlertCircle
                      size={20}
                      className="mt-0.5 shrink-0 text-blue-400"
                    />
                    <div>
                      <p className="text-sm font-semibold text-blue-300">
                        Instagram Post and Reel Note
                      </p>
                      <p className="mt-1 text-sm leading-6 text-slate-400">
                        Feed posts use a horizontal engagement row, while Reels
                        usually display engagement metrics vertically on the right.
                        Please verify extracted values in the Engagement Verification
                        screen before proceeding with analysis.
                      </p>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
          {!isTextMode && (
            <>
              <div className="flex items-center my-7">
                <div className="flex-1 border-t border-slate-700" />
                <span className="px-5 text-slate-500 text-xs font-semibold tracking-widest">
                  OR
                </span>
                <div className="flex-1 border-t border-slate-700" />
              </div>
              <label className="mb-2 block text-sm font-semibold text-slate-200">
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
                  <Upload
                    size={22}
                    className="text-blue-400"
                  />
                </div>
                <p className="text-slate-200 font-medium mt-3">
                  Click to upload screenshot
                </p>
                <p className="text-slate-500 text-sm mt-1">
                  PNG, JPG or JPEG • Maximum 5 MB
                </p>
              </label>
              {image && (
                <div className="mt-4 rounded-2xl border border-slate-700/80 bg-[#0F172A] p-4">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-9 h-9 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center justify-center">
                      <CheckCircle
                        size={18}
                        className="text-green-400"
                      />
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
                    className="w-full max-h-80 rounded-xl border border-slate-700/80 bg-slate-950 object-contain"
                  />
                </div>
              )}
              {ocrLoading && (
                <div className="mt-4 flex items-center gap-3 bg-yellow-500/5 border border-yellow-500/20 rounded-xl p-4">
                  <Loader2
                    size={18}
                    className="text-yellow-400 animate-spin"
                  />
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
                <div className="mt-4 flex items-center gap-3 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
                  <CheckCircle
                    size={19}
                    className="text-green-400 shrink-0"
                  />
                  <div>
                    <p className="text-green-300 font-semibold text-sm">
                      {ocrSuccess}
                    </p>
                    
                  </div>
                </div>
              )}
              {ocrError && (
                <div className="mt-4 flex items-center gap-3 rounded-xl border border-red-500/20 bg-red-500/5 p-4">
                  <AlertCircle
                    size={19}
                    className="text-red-400"
                  />
                  <p className="text-red-300 text-sm">
                    {ocrError}
                  </p>
                </div>
              )}
            </>
          )}
      <button
        onClick={handleAnalyzeClick}
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
        {loading
          ? "Analyzing..."
          : "Analyze"}
      </button>
      </>
      )}
  </div>
  );
}
