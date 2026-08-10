import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import {
  BarChart3,
  Users,
  MessageCircle,
  Reply,
  Repeat2,
  Share2,
  Bookmark,
  Eye,
  CheckCircle2,
  Pencil,
} from "lucide-react";
import apiClient from "../api/apiClient";

export default function EngagementVerification() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const analysis = state?.analysis || {};
  const originalEngagement = analysis.engagement || {};
  const platform = (analysis.platform?.platform || "").toLowerCase();
  const showFollowers = platform === "instagram";
  const followers = Number(originalEngagement.followers || 0);
  const [editMode, setEditMode] = useState(false);
  const [engagement, setEngagement] = useState(() => {
    const data = {};
    Object.entries(originalEngagement)
      .filter(
        ([key]) =>
          key !== "followers" &&
          key !== "metrics"
      )
      .forEach(([key, value]) => {
        data[key] = Number(value);
      });
    return data;
  });

  const continuePrediction = async () => {
    const verifiedEngagement = {};
    Object.entries(engagement).forEach(([key, value]) => {
      verifiedEngagement[key] = Number(value);
    });

    try {
      const response = await apiClient.post(
        "/api/predict/",
        {
          analysis_id: analysis.analysis_id,
          engagement: verifiedEngagement,
          detection: analysis.detection || {},
          platform:
            analysis.platform?.platform ||
            "Instagram",
        }
      );

      const updatedAnalysis = {
        ...analysis,
        engagement: {
          ...originalEngagement,
          ...verifiedEngagement,
          ...(showFollowers && {
            followers,
          }),
        },
        verified_engagement: verifiedEngagement,
        prediction: response.data.prediction,
        spread_analysis:
          response.data.spread_analysis,
        graph: response.data.graph,
      };

      navigate("/prediction", {
        state: {
          analysis: updatedAnalysis,
        },
      });
    } catch (error) {
      console.log(
        "Prediction Error:",
        error
      );
    }
  };

  const handleChange = (key, value) => {
    setEngagement({
      ...engagement,
      [key]: Number(value),
    });
  };

  const getMetricIcon = (key) => {
    const value = key.toLowerCase();

    if (value.includes("like")) {
      return BarChart3;
    }

    if (
      value.includes("comment") ||
      value.includes("reply")
    ) {
      return MessageCircle;
    }

    if (
      value.includes("repost") ||
      value.includes("retweet")
    ) {
      return Repeat2;
    }

    if (value.includes("share")) {
      return Share2;
    }

    if (value.includes("bookmark")) {
      return Bookmark;
    }

    if (value.includes("view")) {
      return Eye;
    }

    return BarChart3;
  };

  const getMetricColor = (key) => {
    const value = key.toLowerCase();

    if (value.includes("like")) {
      return {
        text: "text-blue-400",
        bg: "bg-blue-500/10",
        border: "border-blue-500/20",
      };
    }

    if (
      value.includes("comment") ||
      value.includes("reply")
    ) {
      return {
        text: "text-cyan-400",
        bg: "bg-cyan-500/10",
        border: "border-cyan-500/20",
      };
    }

    if (
      value.includes("repost") ||
      value.includes("retweet")
    ) {
      return {
        text: "text-purple-400",
        bg: "bg-purple-500/10",
        border: "border-purple-500/20",
      };
    }

    if (value.includes("share")) {
      return {
        text: "text-green-400",
        bg: "bg-green-500/10",
        border: "border-green-500/20",
      };
    }

    if (value.includes("bookmark")) {
      return {
        text: "text-pink-400",
        bg: "bg-pink-500/10",
        border: "border-pink-500/20",
      };
    }

    if (value.includes("view")) {
      return {
        text: "text-indigo-400",
        bg: "bg-indigo-500/10",
        border: "border-indigo-500/20",
      };
    }

    return {
      text: "text-blue-400",
      bg: "bg-blue-500/10",
      border: "border-blue-500/20",
    };
  };

  return (
    <div className="max-w-[1500px] mx-auto">
      <div className="bg-[#1B293F] border border-slate-700/50 rounded-3xl p-7 md:p-9 shadow-xl">
        <div className="flex items-start gap-4 mb-2">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0">
            <BarChart3
              size={24}
              className="text-indigo-400"
            />
          </div>

          <div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-white">
              Engagement Verification
            </h1>

            <p className="text-slate-400 mt-2">
              Verify detected engagement values before spread prediction.
            </p>
          </div>
        </div>

        <div className="h-px bg-slate-700/60 my-7" />

        {showFollowers && (
          <div className="mb-6 bg-[#0F172A] border border-purple-500/20 rounded-2xl p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                  <Users
                    size={20}
                    className="text-purple-400"
                  />
                </div>

                <div>
                  <p className="text-slate-500 text-xs uppercase tracking-wider font-semibold">
                    Account Followers
                  </p>

                  <p className="text-slate-400 text-sm mt-1">
                    Instagram audience size
                  </p>
                </div>
              </div>

              <span className="text-2xl font-bold text-purple-400">
                {followers.toLocaleString()}
              </span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(engagement).map(
            ([key, value]) => {
              const Icon = getMetricIcon(key);
              const color = getMetricColor(key);

              return (
                <div
                  key={key}
                  className="bg-[#0F172A] border border-slate-700/70 rounded-2xl p-5 transition-all duration-200 hover:border-slate-600 hover:-translate-y-0.5"
                >
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-slate-400 capitalize font-medium">
                      {key.replace(/_/g, " ")}
                    </p>

                    <div
                      className={`w-9 h-9 rounded-lg ${color.bg} ${color.border} border flex items-center justify-center`}
                    >
                      <Icon
                        size={17}
                        className={color.text}
                      />
                    </div>
                  </div>

                  {editMode ? (
                    <input
                      type="number"
                      min="0"
                      value={value}
                      onChange={(e) =>
                        handleChange(
                          key,
                          e.target.value
                        )
                      }
                      className="mt-5 w-full bg-slate-800 border border-slate-600 focus:border-blue-500 outline-none rounded-xl px-3 py-3 text-white font-semibold"
                    />
                  ) : (
                    <h2
                      className={`text-3xl font-bold mt-5 ${color.text}`}
                    >
                      {Number(
                        value
                      ).toLocaleString()}
                    </h2>
                  )}

                  <div className="w-full h-px bg-slate-700/70 mt-4" />

                  <p className="text-slate-600 text-xs mt-3">
                    Detected value
                  </p>
                </div>
              );
            }
          )}
        </div>

        <div className="h-px bg-slate-700/60 my-7" />

        <div className="flex flex-col md:flex-row gap-4">
          <button
            onClick={continuePrediction}
            className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 px-8 py-3.5 rounded-xl font-bold text-white transition-all duration-200 shadow-lg shadow-blue-600/10"
          >
            <CheckCircle2 size={19} />
            Continue to Prediction
          </button>

          <button
            onClick={() =>
              setEditMode(!editMode)
            }
            className={`flex-1 flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl font-bold transition-all duration-200 ${
              editMode
                ? "bg-green-600 hover:bg-green-500 text-white"
                : "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600"
            }`}
          >
            <Pencil size={18} />
            {editMode
              ? "Save Changes"
              : "Edit Values"}
          </button>
        </div>
      </div>
    </div>
  );
}