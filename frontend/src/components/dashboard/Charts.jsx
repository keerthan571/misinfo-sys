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
  fakeNews,
  realNews,
  weeklyAnalysis,
}) {

  const pieData = [
    {
      name: "Verified False",
      value: fakeNews,
    },
    {
      name: "Verified True",
      value: realNews,
    },
  ];

  const COLORS = [
    "#ef4444",
    "#22c55e",
  ];

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">

      {/* Pie Chart */}

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

        <div className="flex justify-between items-center mb-6">

          <div>

            <h2 className="text-xl font-bold text-slate-800">
              Fact Verification Results
            </h2>

            <p className="text-slate-500 mt-1">
              Verified True vs Verified False
            </p>

          </div>

          <span className="
            bg-white
            shadow-sm
            rounded-full
            px-4
            py-2
            text-sm
            font-medium
            text-slate-700
          ">
            Overall
          </span>

        </div>

        <ResponsiveContainer width="100%" height={320}>

          <PieChart>

            <Pie
              data={pieData}
              dataKey="value"
              nameKey="name"
              innerRadius={75}
              outerRadius={105}
              paddingAngle={5}
            >

              {pieData.map((entry, index) => (
                <Cell
                  key={index}
                  fill={COLORS[index]}
                />
              ))}

            </Pie>

            <Tooltip />

            <Legend verticalAlign="bottom" />

          </PieChart>

        </ResponsiveContainer>

      </div>

      {/* Weekly Chart */}

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

        <div className="flex justify-between items-center mb-6">

          <div>

            <h2 className="text-xl font-bold text-slate-800">
              Weekly Analysis
            </h2>

            <p className="text-slate-500 mt-1">
              Analyses performed this week
            </p>

          </div>

          <span className="
            bg-white
            shadow-sm
            rounded-full
            px-4
            py-2
            text-sm
            font-medium
            text-slate-700
          ">
            This Week
          </span>

        </div>

        <ResponsiveContainer width="100%" height={320}>

          <BarChart data={weeklyAnalysis}>

            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#d1d5db"
            />

            <XAxis
              dataKey="day"
              tickLine={false}
              axisLine={false}
            />

            <YAxis
              allowDecimals={false}
              tickLine={false}
              axisLine={false}
            />

            <Tooltip />

            <Bar
              dataKey="count"
              fill="#2563eb"
              radius={[10, 10, 0, 0]}
            >

              <LabelList
                dataKey="count"
                position="top"
              />

            </Bar>

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}