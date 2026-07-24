export default function StatCard({
  title,
  value,
  subtitle,
  icon,
  valueColor = "text-white",
}) {
  return (
    <div className="bg-slate-800 rounded-2xl p-6 shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
      <div className="flex items-center justify-between">
        <p className="text-gray-400 text-lg font-medium">{title}</p>

        <span className="text-3xl">{icon}</span>
      </div>

      <h2 className={`text-4xl font-bold mt-5 ${valueColor}`}>
        {value}
      </h2>

      {subtitle && (
        <p className="text-sm text-gray-400 mt-3">
          {subtitle}
        </p>
      )}
    </div>
  );
}