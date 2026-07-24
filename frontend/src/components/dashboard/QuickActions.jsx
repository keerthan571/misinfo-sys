import { useNavigate } from "react-router-dom";

export default function QuickActions() {
  const navigate = useNavigate();

  const actions = [
    {
      title: "📰 Analyze News",
      color: "bg-blue-600 hover:bg-blue-700",
      path: "/analyze",
    },
    {
      title: "📷 OCR Scanner",
      color: "bg-purple-600 hover:bg-purple-700",
      path: "/ocr",
    },
    {
      title: "🌐 View Graph",
      color: "bg-green-600 hover:bg-green-700",
      path: "/graph",
    },
    {
      title: "📈 Prediction",
      color: "bg-red-600 hover:bg-red-700",
      path: "/prediction",
    },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold text-white mb-4">
        ⚡ Quick Actions
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {actions.map((action) => (
          <button
            key={action.path}
            onClick={() => navigate(action.path)}
            className={`${action.color} rounded-xl py-4 font-semibold transition`}
          >
            {action.title}
          </button>
        ))}
      </div>
    </div>
  );
}