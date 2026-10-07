import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  BarChart3,
  CheckCircle2,
  ShieldCheck,
  Brain,
  FileSearch,
  Image as ImageIcon,
  ArrowRight,
  Sparkles,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import apiClient from "../api/apiClient";
import { useAnalysis } from "../context/AnalysisContext";
import AnalyzeInput from "../components/analyze/AnalyzeInput";
import DetectionCard from "../components/analyze/DetectionCard";
import FactVerificationCard from "../components/analyze/FactVerificationCard";
export default function Analyze() {
  const { analysis, setAnalysis } = useAnalysis();
  const [news, setNews] = useState(
    analysis?.news || ""
  );
  const [image, setImage] = useState(null);
  const [platform, setPlatform] = useState(
    analysis?.platform || ""
  );
  const [followers, setFollowers] = useState("");
  const [ocrEngagement, setOcrEngagement] =
    useState({});
  const [imagePreview, setImagePreview] =
    useState(
      analysis?.imagePreview || null
    );
  const [result, setResult] =
    useState(
      analysis?.result || null
    );
  const [loading, setLoading] =
    useState(false);
  const [error, setError] =
    useState("");
  const navigate = useNavigate();
  // =========================================================
  // MODE
  // =========================================================
  const isTextMode =
    platform === "Text";
  const isImageMode =
    Boolean(image);
  const hasSocialAnalysis =
    Boolean(
      result?.analysis &&
      isImageMode &&
      !isTextMode
    );
  // =========================================================
  // ANALYZE
  // =========================================================
  const handleAnalyze = async () => {
    if (!news.trim() && !image) {
      setError(
        "Please enter news text or upload a social media screenshot."
      );
      return;
    }
    if (!platform) {
      setError(
        "Please select the platform."
      );
      return;
    }
    if (
      isTextMode &&
      !news.trim()
    ) {
      setError(
        "Please enter text for Text / General analysis."
      );
      return;
    }
    if (
      !isTextMode &&
      !image
    ) {
      setError(
        "Please upload a social media screenshot for complete analysis."
      );
      return;
    }
    try {
      setLoading(true);
      setError("");
      setResult(null);
      const formData =
        new FormData();
      formData.append(
        "platform",
        platform
      );
      if (
        platform === "Instagram" &&
        followers
      ) {
        formData.append(
          "followers",
          followers
        );
      }
      if (news.trim()) {
        formData.append(
          "text",
          news
        );
      }
      if (image) {
        formData.append(
          "image",
          image
        );
      }
      formData.append(
        "ocr_engagement",
        JSON.stringify(
          isTextMode
            ? {}
            : ocrEngagement
        )
      );
      const response = await apiClient.post(
        "/api/analyze/",
        formData
      );
      setResult(
        response.data
      );
      // =====================================================
      // IMAGE PREVIEW
      // =====================================================
      let preview = null;
      const savedImage =
        response.data
          ?.analysis
          ?.image
          ?.path;
      if (savedImage) {
          const normalizedPath = String(savedImage).replace(/\\/g, "/");
          preview = `${apiClient.defaults.baseURL}/${normalizedPath}`;
          setImagePreview(preview);
      } else {
        setImagePreview(null);
      }
      // =====================================================
      // SAVE ANALYSIS CONTEXT
      // =====================================================
      setAnalysis({
        result:
          response.data,
        imagePreview:
          preview,
        news,
        platform,
        followers,
      });
      // =====================================================
      // OCR TEXT
      // =====================================================
      if (
        response.data
          ?.analysis
          ?.vision
          ?.post_text &&
        !news.trim()
      ) {
        setNews(
          response.data
            .analysis
            .vision
            .post_text
        );
      }
    } catch (err) {
      console.error(
        "ANALYSIS ERROR:",
        err
      );
      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Analysis failed."
      );
    } finally {
      setLoading(false);
    }
  };
  // =========================================================
  // RESULT DATA
  // =========================================================
  const prediction =
    result
      ?.analysis
      ?.final_result
      ?.label || "";
  const confidence =
    result
      ?.analysis
      ?.final_result
      ?.confidence;
  const riskLevel =
    result
      ?.analysis
      ?.final_result
      ?.risk_level;
  const summary =
    result
      ?.analysis
      ?.final_result
      ?.summary ||
    "No analysis summary available.";
  // =========================================================
  // PREDICTION COLOR
  // =========================================================
  const getPredictionStyle = () => {
    const label =
      prediction.toLowerCase();
    if (
      label.includes("verified") ||
      label.includes("reliable")
    ) {
      return {
        text:
          "text-emerald-400",
        bg:
          "bg-emerald-500/10",
        border:
          "border-emerald-500/20",
        icon:
          CheckCircle2,
      };
    }
    if (
      label.includes("false") ||
      label.includes("misinformation")
    ) {
      return {
        text:
          "text-red-400",
        bg:
          "bg-red-500/10",
        border:
          "border-red-500/20",
        icon:
          AlertTriangle,
      };
    }
    if (
      label.includes("verification") ||
      label.includes("misleading")
    ) {
      return {
        text:
          "text-yellow-400",
        bg:
          "bg-yellow-500/10",
        border:
          "border-yellow-500/20",
        icon:
          AlertTriangle,
      };
    }
    return {
      text:
        "text-blue-400",
      bg:
        "bg-blue-500/10",
      border:
        "border-blue-500/20",
      icon:
        ShieldCheck,
    };
  };
  const predictionStyle =
    getPredictionStyle();
  const PredictionIcon =
    predictionStyle.icon;
  // =========================================================
  // PIPELINE
  // =========================================================
  const pipelineSteps = [
    {
      label:
        "Content analyzed",
      done:
        Boolean(result),
    },
    {
      label:
        "Misinformation detection",
      done:
        Boolean(
          result?.analysis?.detection
        ),
    },
    {
      label:
        "Fact verification",
      done:
        Boolean(
          result?.analysis
            ?.fact_verification
        ),
    },
    {
      label:
        "Engagement detected",
      done:
        Boolean(
          result?.analysis
            ?.engagement
        ),
    },
  ];
  // =========================================================
  // UI
  // =========================================================
  return (
    <div className="max-w-[1500px] mx-auto space-y-7 pb-10">
      {/* =====================================================
          PAGE HEADER
      ===================================================== */}
      <div>
        <div className="flex items-center gap-3">
          <div
            className="
              w-11 h-11
              rounded-xl
              bg-indigo-500/10
              border border-indigo-500/20
              flex items-center justify-center
            "
          >
            <Sparkles
              size={22}
              className="text-indigo-400"
            />
          </div>
          <div>
            <h1
              className="
                text-3xl md:text-4xl
                font-extrabold
                text-white
                tracking-tight
              "
            >
              Analyze Content
            </h1>
            <p
              className="
                text-slate-400
                mt-1
                text-sm md:text-base
              "
            >
              Detect misinformation, verify claims,
              and analyze social-media propagation.
            </p>
          </div>
        </div>
      </div>
      {/* =====================================================
          INPUT SECTION
      ===================================================== */}
      <section
        className="
          bg-[#1B293F]
          border border-slate-700/50
          rounded-3xl
          p-5 md:p-7
          shadow-xl
        "
      >
        <div
          className="
            flex items-center justify-between
            mb-5
          "
        >
          <div>
            <div
              className="
                flex items-center gap-2
              "
            >
              <FileSearch
                size={19}
                className="text-blue-400"
              />
              <h2
                className="
                  text-lg
                  font-bold
                  text-white
                "
              >
                Content Input
              </h2>
            </div>
            <p
              className="
                text-slate-500
                text-sm
                mt-1
              "
            >
              Paste text or upload a
              social-media screenshot.
            </p>
          </div>
        </div>
        <AnalyzeInput
          news={news}
          setNews={setNews}
          image={image}
          setImage={setImage}
          loading={loading}
          onAnalyze={handleAnalyze}
          platform={platform}
          setPlatform={setPlatform}
          followers={followers}
          setFollowers={setFollowers}
          setOcrEngagement={
            setOcrEngagement
          }
        />
      </section>
      {/* =====================================================
          ERROR
      ===================================================== */}
      {error && (
        <div
          className="
            flex items-start gap-3
            bg-red-500/10
            border border-red-500/20
            rounded-2xl
            px-5 py-4
            text-red-300
          "
        >
          <AlertTriangle
            size={20}
            className="shrink-0 mt-0.5"
          />
          <div>
            <p
              className="
                font-semibold
                text-red-200
              "
            >
              Analysis Error
            </p>
            <p
              className="
                text-sm
                mt-1
                text-red-300/80
              "
            >
              {error}
            </p>
          </div>
        </div>
      )}
      {/* =====================================================
          ANALYSIS PIPELINE
      ===================================================== */}
      {result?.analysis && (
        <section
          className="
            bg-[#111D30]
            border border-slate-700/50
            rounded-2xl
            px-5 py-4
          "
        >
          <div
            className="
              flex flex-wrap
              items-center
              gap-x-6
              gap-y-3
            "
          >
            {pipelineSteps.map(
              (step, index) => (
                <div
                  key={step.label}
                  className="
                    flex items-center
                    gap-2
                  "
                >
                  <div
                    className={`
                      w-6 h-6
                      rounded-full
                      flex items-center justify-center
                      ${
                        step.done
                          ? "bg-emerald-500/15 text-emerald-400"
                          : "bg-slate-700 text-slate-500"
                      }
                    `}
                  >
                    {step.done ? (
                      <CheckCircle2
                        size={15}
                      />
                    ) : (
                      <span
                        className="
                          text-[10px]
                          font-bold
                        "
                      >
                        {index + 1}
                      </span>
                    )}
                  </div>
                  <span
                    className={`
                      text-sm
                      ${
                        step.done
                          ? "text-slate-200"
                          : "text-slate-500"
                      }
                    `}
                  >
                    {step.label}
                  </span>
                  {index <
                    pipelineSteps.length - 1 && (
                    <ArrowRight
                      size={14}
                      className="
                        text-slate-700
                        ml-2
                      "
                    />
                  )}
                </div>
              )
            )}
          </div>
        </section>
      )}
      {/* =====================================================
          HERO ANALYSIS SECTION
      ===================================================== */}
      {result?.analysis && (
        <section
          className={`grid grid-cols-1 ${
            isImageMode && imagePreview
              ? "xl:grid-cols-[360px_1fr]"
              : ""
          } gap-6`}
        >
          {/* -------------------------------------------------
              IMAGE
          ------------------------------------------------- */}
          {isImageMode && imagePreview && (
            <div
              className="
                bg-[#1B293F]
                border border-slate-700/50
                rounded-3xl
                p-5
                shadow-xl
              "
            >
              <div
                className="
                  flex items-center
                  justify-between
                  mb-4
                "
              >
                <div
                  className="
                    flex items-center
                    gap-2
                  "
                >
                  <ImageIcon
                    size={18}
                    className="
                      text-indigo-400
                    "
                  />
                  <h2
                    className="
                      text-base
                      font-bold
                      text-white
                    "
                  >
                    Source Screenshot
                  </h2>
                </div>
                <span
                  className="
                    text-[11px]
                    px-2.5 py-1
                    rounded-full
                    bg-slate-800
                    text-slate-400
                    border border-slate-700
                  "
                >
                  {platform}
                </span>
              </div>
              <div
                className="
                  bg-[#080F1D]
                  rounded-2xl
                  p-3
                  min-h-[420px]
                  flex items-center
                  justify-center
                  overflow-hidden
                "
              >
                <img
                  src={imagePreview}
                  alt="Uploaded social media screenshot"
                  className="
                    max-h-[520px]
                    max-w-full
                    object-contain
                    rounded-xl
                  "
                />
              </div>
              <div
                className="
                  flex items-center
                  gap-2
                  mt-4
                  text-xs
                  text-emerald-400
                "
              >
                <CheckCircle2
                  size={15}
                />
                Screenshot processed
                successfully
              </div>
            </div>
          )}
          {/* -------------------------------------------------
              RESULT
          ------------------------------------------------- */}
          <div
            className="
              bg-[#1B293F]
              border border-slate-700/50
              rounded-3xl
              p-6 md:p-7
              shadow-xl
            "
          >
            <div
              className="
                flex items-center
                justify-between
                gap-4
                mb-6
              "
            >
              <div>
                <div
                  className="
                    flex items-center
                    gap-2
                  "
                >
                  <Brain
                    size={20}
                    className="
                      text-purple-400
                    "
                  />
                  <h2
                    className="
                      text-xl
                      font-bold
                      text-white
                    "
                  >
                    Analysis Result
                  </h2>
                </div>
                <p
                  className="
                    text-slate-500
                    text-sm
                    mt-1
                  "
                >
                  AI-assisted misinformation
                  and claim analysis.
                </p>
              </div>
              <div
                className={`
                  hidden sm:flex
                  items-center gap-2
                  px-3 py-2
                  rounded-xl
                  border
                  ${predictionStyle.bg}
                  ${predictionStyle.border}
                  ${predictionStyle.text}
                `}
              >
                <PredictionIcon
                  size={16}
                />
                <span
                  className="
                    text-xs
                    font-semibold
                  "
                >
                  Analysis Complete
                </span>
              </div>
            </div>
            {/* =================================================
                MAIN VERDICT
            ================================================= */}
            <div
              className={`
                rounded-2xl
                border
                ${predictionStyle.bg}
                ${predictionStyle.border}
                p-6
                mb-5
              `}
            >
              <p
                className="
                  text-xs
                  uppercase
                  tracking-[0.16em]
                  font-semibold
                  text-slate-500
                  mb-3
                "
              >
                Final Assessment
              </p>
              <div
                className="
                  flex flex-col
                  md:flex-row
                  md:items-end
                  justify-between
                  gap-5
                "
              >
                <div>
                  <div
                    className="
                      flex items-center
                      gap-3
                    "
                  >
                    <PredictionIcon
                      size={27}
                      className={
                        predictionStyle.text
                      }
                    />
                    <h3
                      className={`
                        text-2xl md:text-3xl
                        font-extrabold
                        ${predictionStyle.text}
                      `}
                    >
                      {prediction ||
                        "Analysis Pending"}
                    </h3>
                  </div>
                </div>
                <div
                  className="
                    flex gap-8
                  "
                >
                  <div>
                    <p
                      className="
                        text-xs
                        text-slate-500
                        uppercase
                        tracking-wider
                      "
                    >
                      Confidence
                    </p>
                    <p
                      className="
                        text-2xl
                        font-extrabold
                        text-emerald-400
                        mt-1
                      "
                    >
                      {confidence != null
                        ? `${Math.round(
                            confidence
                          )}%`
                        : "N/A"}
                    </p>
                  </div>
                  {!isTextMode && (
                    <div>
                      <p
                        className="
                          text-xs
                          text-slate-500
                          uppercase
                          tracking-wider
                        "
                      >
                        Risk
                      </p>
                      <p
                        className="
                          text-2xl
                          font-extrabold
                          text-yellow-400
                          mt-1
                        "
                      >
                        {riskLevel ||
                          "N/A"}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
            {/* =================================================
                SUMMARY
            ================================================= */}
            <div>
              <div
                className="
                  flex items-center
                  gap-2
                  mb-2
                "
              >
                <ShieldCheck
                  size={17}
                  className="
                    text-blue-400
                  "
                />
                <h3
                  className="
                    text-sm
                    font-bold
                    text-slate-200
                  "
                >
                  Assessment Summary
                </h3>
              </div>
              <p
                className="
                  text-slate-400
                  text-sm
                  leading-7
                "
              >
                {summary}
              </p>
            </div>
          </div>
        </section>
      )}
      {/* =====================================================
          NLP + FACT VERIFICATION
      ===================================================== */}
      {result?.analysis && (
        <section>
          <div
            className="
              flex items-end
              justify-between
              mb-4
            "
          >
            <div>
              <p
                className="
                  text-xs
                  uppercase
                  tracking-[0.15em]
                  text-slate-500
                  font-semibold
                "
              >
                Detailed Analysis
              </p>
              <h2
                className="
                  text-xl
                  font-bold
                  text-white
                  mt-1
                "
              >
                Detection & Verification
              </h2>
            </div>
          </div>
          <div
            className="
              grid
              grid-cols-1
              lg:grid-cols-2
              gap-6
            "
          >
            <DetectionCard
              data={
                result.analysis.detection
              }
            />
            <FactVerificationCard
              data={
                result.analysis
                  .fact_verification
              }
            />
          </div>
        </section>
      )}
      {/* =====================================================
          PROPAGATION CTA
      ===================================================== */}
      {hasSocialAnalysis && (
        <section
          className="
            relative
            overflow-hidden
            bg-gradient-to-r
            from-blue-600/10
            via-indigo-500/10
            to-purple-500/10
            border border-blue-500/20
            rounded-3xl
            p-6 md:p-8
          "
        >
          <div
            className="
              absolute
              -right-20
              -top-20
              w-56 h-56
              rounded-full
              bg-blue-500/10
              blur-3xl
            "
          />
          <div
            className="
              relative
              flex flex-col
              md:flex-row
              md:items-center
              justify-between
              gap-6
            "
          >
            <div>
              <div
                className="
                  flex items-center
                  gap-2
                  mb-2
                "
              >
                <BarChart3
                  size={20}
                  className="
                    text-blue-400
                  "
                />
                <span
                  className="
                    text-xs
                    uppercase
                    tracking-[0.15em]
                    text-blue-400
                    font-bold
                  "
                >
                  Next Stage
                </span>
              </div>
              <h2
                className="
                  text-xl md:text-2xl
                  font-bold
                  text-white
                "
              >
                Analyze Content Propagation
              </h2>
              <p
                className="
                  text-slate-400
                  text-sm
                  mt-2
                  max-w-2xl
                  leading-6
                "
              >
                Verify the detected engagement
                metrics before generating spread
                prediction and propagation analysis.
              </p>
            </div>
            <button
              onClick={() => {
                navigate(
                  "/engagement-verification",
                  {
                    state: {
                      analysis: {
                        ...result.analysis,
                        engagement: {
                          ...result
                            .analysis
                            .engagement,
                          followers:
                            Number(
                              followers
                            ) || 0,
                        },
                      },
                    },
                  }
                );
              }}
              className="
                shrink-0
                flex items-center
                justify-center
                gap-2
                bg-blue-600
                hover:bg-blue-500
                active:bg-blue-700
                text-white
                font-bold
                px-7 py-3.5
                rounded-xl
                transition-all
                shadow-lg
                shadow-blue-600/20
              "
            >
              <BarChart3
                size={18}
              />
              Review Engagement
              <ArrowRight
                size={17}
              />
            </button>
          </div>
        </section>
      )}
      {/* =====================================================
          TEXT MODE NOTICE
      ===================================================== */}
      {isTextMode && result?.analysis && (
        <section
          className="
            bg-[#111D30]
            border border-slate-700/50
            rounded-2xl
            p-5
          "
        >
          <div
            className="
              flex items-start
              gap-3
            "
          >
            <div
              className="
                w-9 h-9
                rounded-lg
                bg-slate-800
                flex items-center
                justify-center
                shrink-0
              "
            >
              <FileSearch
                size={17}
                className="
                  text-slate-400
                "
              />
            </div>
            <div>
              <h3
                className="
                  text-sm
                  font-bold
                  text-slate-200
                "
              >
                Text Analysis
              </h3>
              <p
                className="
                  text-slate-500
                  text-sm
                  leading-6
                  mt-1
                "
              >
                This analysis is based on the
                submitted text. Social-media
                engagement, spread prediction,
                and propagation graph analysis
                are not generated because no
                social-media evidence was provided.
              </p>
            </div>
          </div>
        </section>
      )}
      {/* =====================================================
          LOADING OVERLAY MESSAGE
      ===================================================== */}
      {loading && (
        <div
          className="
            fixed
            bottom-6
            right-6
            z-50
            flex items-center
            gap-3
            bg-[#172238]
            border border-blue-500/20
            rounded-2xl
            px-5 py-4
            shadow-2xl
          "
        >
          <Loader2
            size={20}
            className="
              text-blue-400
              animate-spin
            "
          />
          <div>
            <p
              className="
                text-sm
                font-semibold
                text-white
              "
            >
              Analyzing content...
            </p>
            <p
              className="
                text-xs
                text-slate-500
                mt-0.5
              "
            >
              Processing OCR, NLP and
              verification data
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
