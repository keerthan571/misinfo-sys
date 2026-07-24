import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

export default function Charts({
  fakeNews,
  realNews,
  weeklyAnalysis,
}) {
  const pieData = [
    { name: "Fake", value: fakeNews },
    { name: "Real", value: realNews },
  ];

  const COLORS = ["#ef4444", "#22c55e"];

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

      {/* Pie Chart */}
      <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">
        <h2 className="text-xl font-bold text-white mb-4">
          Fake vs Real
        </h2>

        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              dataKey="value"
              outerRadius={90}
              label
            >
              {pieData.map((_, index) => (
                <Cell
                  key={index}
                  fill={COLORS[index]}
                />
              ))}
            </Pie>

            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Weekly Chart */}
      <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">
        <h2 className="text-xl font-bold text-white mb-4">
          Weekly Analyses
        </h2>

        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={weeklyAnalysis}>
            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="day" />

            <YAxis />

            <Tooltip />

            <Bar
              dataKey="count"
              fill="#3b82f6"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
}