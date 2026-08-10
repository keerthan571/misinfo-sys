import { FaUserCircle } from "react-icons/fa";

const DashboardHeader = ({ userName }) => {
  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const hour = new Date().getHours();

  let greeting = "Good Evening";

  if (hour < 12) {
    greeting = "Good Morning";
  } else if (hour < 17) {
    greeting = "Good Afternoon";
  }

  return (
    <div className="relative overflow-hidden rounded-3xl border border-slate-800/80 bg-slate-900/80 px-7 py-7 shadow-lg shadow-black/10">
      <div className="absolute -right-20 -top-24 h-64 w-64 rounded-full bg-violet-500/10 blur-3xl" />
      <div className="absolute -bottom-24 left-1/3 h-40 w-40 rounded-full bg-cyan-500/5 blur-3xl" />

      <div className="relative flex flex-col gap-7 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1.5">
            <span className="h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-300">
              Intelligence Overview
            </span>
          </div>

          <h1 className="text-3xl font-extrabold leading-tight tracking-tight text-white sm:text-4xl">
            AI Misinformation
            <br />
            <span className="text-blue-400">Dashboard</span>
          </h1>

          <p className="mt-3 max-w-xl text-base text-slate-400">
            Monitor and analyse misinformation efficiently with AI-powered
            intelligence.
          </p>

          <p className="mt-4 text-sm font-medium text-slate-500">
            {today}
          </p>
        </div>

        <div className="flex w-full items-center gap-4 rounded-2xl border border-slate-700/70 bg-slate-800/70 px-5 py-4 lg:w-auto lg:min-w-[240px]">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full border border-blue-500/30 bg-blue-500/10">
            <FaUserCircle
              className="text-blue-400"
              size={40}
            />
          </div>

          <div>
            <p className="text-sm font-medium text-slate-500">
              {greeting}
            </p>

            <p className="mt-0.5 text-lg font-bold text-white">
              Welcome back,
            </p>

            <p className="text-sm font-semibold text-blue-400">
              {userName}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardHeader;