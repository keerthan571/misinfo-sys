import {
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
} from "lucide-react";

export default function RecentActivity({ activities }) {

  const formatTime = (time) => {
    if (!time) return "-";

    return new Date(time).toLocaleString("en-IN", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  return (
    <div className="
      bg-slate-100
      rounded-3xl
      border border-slate-200
      shadow-md
      p-7
      hover:shadow-xl
      transition-all
      duration-300
    ">

      {/* Header */}
      <div className="flex items-center justify-between mb-7">

        <div>

          <h2 className="text-xl font-bold text-slate-800">
            Recent Activity
          </h2>

          <p className="text-slate-500 mt-1">
            Your latest misinformation analyses
          </p>

        </div>

        <span className="
          bg-white
          rounded-full
          px-4
          py-2
          shadow-sm
          text-sm
          font-medium
          text-slate-700
        ">
          {activities.length} Records
        </span>

      </div>

      {activities.length === 0 ? (

        <div className="flex flex-col items-center justify-center py-14">

          <AlertTriangle
            size={46}
            className="text-slate-300 mb-4"
          />

          <h3 className="text-xl font-semibold text-slate-700">
            No Recent Activity
          </h3>

          <p className="text-slate-500 mt-2">
            Analyse some news to populate this timeline.
          </p>

        </div>

      ) : (

        <div className="space-y-5">

          {activities.map((activity, index) => (

            <div
              key={index}
              className="
                bg-white
                rounded-2xl
                p-5
                border
                border-slate-200
                hover:shadow-lg
                hover:-translate-y-1
                transition-all
                duration-300
                flex
                justify-between
                items-start
              "
            >

              <div className="flex gap-4">

                <div className="
                  w-12
                  h-12
                  rounded-xl
                  flex
                  items-center
                  justify-center
                  bg-slate-100
                ">

                  {activity.verdict === "True" ? (
                    <ShieldCheck
                      className="text-green-600"
                      size={24}
                    />
                  ) : (
                    <ShieldAlert
                      className="text-red-600"
                      size={24}
                    />
                  )}

                </div>

                <div>

                  <p className="font-semibold text-slate-800 leading-6">
                    {activity.text?.trim()
                      ? activity.text
                      : "Image / OCR Analysis"}
                  </p>

                  <div className="flex flex-wrap gap-5 mt-3 text-sm text-slate-500">

                    <span>
                      Confidence:
                      <span className="font-medium text-slate-700 ml-1">
                        {activity.confidence || "N/A"}
                        {activity.confidence ? "%" : ""}
                      </span>
                    </span>

                    <span>
                      {formatTime(activity.analysis_time)}
                    </span>

                  </div>

                </div>

              </div>

              <span
                className={`px-4 py-2 rounded-full text-xs font-bold ${
                  activity.verdict === "True"
                    ? "bg-green-100 text-green-700"
                    : "bg-red-100 text-red-700"
                }`}
              >
                {activity.verdict === "True"
                  ? "Verified True"
                  : "Verified False"}
              </span>

            </div>

          ))}

        </div>

      )}

    </div>
  );
}