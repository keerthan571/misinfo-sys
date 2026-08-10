import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LabelList,
} from "recharts";

export default function Charts({
  fakeNews = 0,
  realNews = 0,
  weeklyAnalysis = [],
}) {
  const pieData = [
    {
      name: "Verified False",
      value: fakeNews || 0,
    },
    {
      name: "Verified True",
      value: realNews || 0,
    },
  ];

  const COLORS = ["#ef4444", "#22c55e"];

  const hasVerificationData =
    (fakeNews || 0) > 0 ||
    (realNews || 0) > 0;

  const totalVerified =
    (fakeNews || 0) +
    (realNews || 0);

  const safeWeeklyData =
    weeklyAnalysis.length > 0
      ? weeklyAnalysis
      : [
          { day: "Mon", count: 0 },
          { day: "Tue", count: 0 },
          { day: "Wed", count: 0 },
          { day: "Thu", count: 0 },
          { day: "Fri", count: 0 },
          { day: "Sat", count: 0 },
          { day: "Sun", count: 0 },
        ];

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
      <div className="group relative overflow-hidden rounded-2xl border border-slate-800/80 bg-slate-900/80 p-6 shadow-lg shadow-black/10 transition-all duration-300 hover:border-slate-700 hover:shadow-xl">
        <div className="absolute -right-16 -top-16 h-40 w-40 rounded-full bg-emerald-500/5 blur-3xl" />

        <div className="relative flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
              <h2 className="text-lg font-bold text-white">
                Fact Verification
              </h2>
            </div>

            <p className="text-sm text-slate-500 mt-1">
              Verified true vs verified false
            </p>
          </div>

          <span className="rounded-full border border-slate-700 bg-slate-800/80 px-3 py-1.5 text-xs font-medium text-slate-400">
            Overall
          </span>
        </div>

        <div className="relative">
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              {hasVerificationData ? (
                <>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={78}
                    outerRadius={108}
                    paddingAngle={4}
                    stroke="none"
                  >
                    {pieData.map((entry, index) => (
                      <Cell
                        key={index}
                        fill={COLORS[index]}
                      />
                    ))}
                  </Pie>

                  <text
                    x="50%"
                    y="46%"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="fill-white text-2xl font-bold"
                  >
                    {totalVerified}
                  </text>

                  <text
                    x="50%"
                    y="54%"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="fill-slate-500 text-xs"
                  >
                    Total Verified
                  </text>
                </>
              ) : (
                <text
                  x="50%"
                  y="50%"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="fill-slate-500 text-sm font-medium"
                >
                  No Verification Data
                </text>
              )}

              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  border: "1px solid #334155",
                  borderRadius: "12px",
                  color: "#fff",
                }}
                itemStyle={{
                  color: "#e2e8f0",
                }}
                labelStyle={{
                  color: "#94a3b8",
                }}
              />

              <Legend
                verticalAlign="bottom"
                iconType="circle"
                wrapperStyle={{
                  color: "#94a3b8",
                  fontSize: "13px",
                  paddingTop: "10px",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="group relative overflow-hidden rounded-2xl border border-slate-800/80 bg-slate-900/80 p-6 shadow-lg shadow-black/10 transition-all duration-300 hover:border-slate-700 hover:shadow-xl">
        <div className="absolute -right-16 -top-16 h-40 w-40 rounded-full bg-blue-500/5 blur-3xl" />

        <div className="relative flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-blue-400" />
              <h2 className="text-lg font-bold text-white">
                Weekly Analysis
              </h2>
            </div>

            <p className="text-sm text-slate-500 mt-1">
              Analyses performed this week
            </p>
          </div>

          <span className="rounded-full border border-slate-700 bg-slate-800/80 px-3 py-1.5 text-xs font-medium text-slate-400">
            This Week
          </span>
        </div>

        <ResponsiveContainer width="100%" height={320}>
          <BarChart
            data={safeWeeklyData}
            margin={{
              top: 20,
              right: 5,
              left: -15,
              bottom: 5,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#1e293b"
            />

            <XAxis
              dataKey="day"
              tickLine={false}
              axisLine={false}
              tick={{
                fill: "#64748b",
                fontSize: 12,
              }}
            />

            <YAxis
              allowDecimals={false}
              tickLine={false}
              axisLine={false}
              tick={{
                fill: "#64748b",
                fontSize: 12,
              }}
            />

            <Tooltip
              cursor={{
                fill: "rgba(59, 130, 246, 0.05)",
              }}
              contentStyle={{
                backgroundColor: "#0f172a",
                border: "1px solid #334155",
                borderRadius: "12px",
                color: "#fff",
              }}
              labelStyle={{
                color: "#94a3b8",
              }}
              itemStyle={{
                color: "#60a5fa",
              }}
            />

            <Bar
              dataKey="count"
              fill="#3b82f6"
              radius={[8, 8, 2, 2]}
              maxBarSize={42}
            >
              <LabelList
                dataKey="count"
                position="top"
                fill="#94a3b8"
                fontSize={12}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}