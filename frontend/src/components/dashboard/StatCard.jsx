export default function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  valueColor = "text-blue-400",
}) {
  return (
    <div className="group relative overflow-hidden rounded-2xl border border-slate-800/80 bg-slate-900/80 p-6 shadow-lg shadow-black/10 transition-all duration-300 hover:-translate-y-1 hover:border-slate-700 hover:bg-slate-900 hover:shadow-xl">
      <div className="absolute -right-10 -top-10 h-28 w-28 rounded-full bg-blue-500/5 blur-2xl transition-all duration-300 group-hover:bg-blue-500/10" />

      <div className="relative flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-400">
            {title}
          </p>

          <h2
            className={`mt-3 text-4xl font-bold tracking-tight ${valueColor}`}
          >
            {value}
          </h2>

          <div className="mt-4 h-px w-12 bg-slate-700" />

          <p className="mt-3 text-sm text-slate-500">
            {subtitle}
          </p>
        </div>

        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-slate-700/80 bg-slate-800/80 shadow-inner">
          <Icon
            size={27}
            strokeWidth={2}
            className={valueColor}
          />
        </div>
      </div>
    </div>
  );
}