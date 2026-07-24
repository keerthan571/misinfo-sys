import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

const pieData = [
  { name: "Fake", value: 412 },
  { name: "Real", value: 833 },
];

const barData = [
  { day: "Mon", analyses: 120 },
  { day: "Tue", analyses: 180 },
  { day: "Wed", analyses: 240 },
  { day: "Thu", analyses: 150 },
  { day: "Fri", analyses: 280 },
];

const COLORS = ["#ef4444", "#22c55e"];

export default function Charts() {
  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

      {/* Pie Chart */}
      <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">
        <h2 className="text-2xl font-bold text-white mb-6">
          Fake vs Real News
        </h2>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                outerRadius={90}
                label
              >
                {pieData.map((entry, index) => (
                  <Cell key={index} fill={COLORS[index]} />
                ))}
              </Pie>

              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bar Chart */}
      <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">
        <h2 className="text-2xl font-bold text-white mb-6">
          Weekly Analyses
        </h2>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="analyses" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}