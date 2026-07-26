import { useNavigate } from "react-router-dom";
import {
  Newspaper,
  ScanSearch,
  Network,
  TrendingUp,
} from "lucide-react";

export default function QuickActions() {
  const navigate = useNavigate();

  const actions = [
    {
      title: "Analyze News",
      subtitle: "Detect misinformation",
      icon: Newspaper,
      color: "bg-blue-600",
      path: "/analyze",
    },
    {
      title: "OCR Scanner",
      subtitle: "Extract text from images",
      icon: ScanSearch,
      color: "bg-purple-600",
      path: "/ocr",
    },
    {
      title: "Knowledge Graph",
      subtitle: "Visualize relationships",
      icon: Network,
      color: "bg-green-600",
      path: "/graph",
    },
    {
      title: "Spread Prediction",
      subtitle: "Predict misinformation reach",
      icon: TrendingUp,
      color: "bg-red-600",
      path: "/prediction",
    },
  ];

  return (
    <div className="
      bg-slate-100
      rounded-3xl
      border
      border-slate-200
      shadow-md
      p-7
    ">

      <div className="mb-6">

        <h2 className="text-2xl font-bold text-slate-800">
          ⚡ Quick Actions
        </h2>

        <p className="text-slate-500 mt-1">
          Jump directly to the most used modules
        </p>

      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">

        {actions.map((action) => {

          const Icon = action.icon;

          return (
            <button
              key={action.path}
              onClick={() => navigate(action.path)}
              className="
                bg-white
                rounded-2xl
                border
                border-slate-200
                p-5
                text-left
                shadow-sm
                hover:shadow-xl
                hover:-translate-y-2
                transition-all
                duration-300
              "
            >

              <div
                className={`
                  w-14
                  h-14
                  rounded-2xl
                  flex
                  items-center
                  justify-center
                  text-white
                  ${action.color}
                `}
              >
                <Icon size={28} />
              </div>

              <h3 className="mt-5 text-lg font-bold text-slate-800">
                {action.title}
              </h3>

              <p className="mt-2 text-sm text-slate-500">
                {action.subtitle}
              </p>

            </button>
          );

        })}

      </div>

    </div>
  );
}