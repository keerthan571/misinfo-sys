export default function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  valueColor = "text-slate-900",
}) {
  return (
    <div className="
      bg-slate-100
      rounded-3xl
      border border-slate-200
      shadow-md
      p-6
      hover:shadow-xl
      hover:-translate-y-2
      transition-all
      duration-300
    ">
      <div className="flex items-center justify-between">

        <div className="flex-1">

          <p className="text-sm font-medium text-slate-500">
            {title}
          </p>

          <h2 className={`text-4xl font-bold mt-3 ${valueColor}`}>
            {value}
          </h2>

          <div className="w-16 border-b border-slate-300 mt-3"></div>

          <p className="text-sm text-slate-500 mt-3">
            {subtitle}
          </p>

        </div>

        <div className="
          w-16
          h-16
          rounded-2xl
          bg-white
          shadow-sm
          flex
          items-center
          justify-center
        ">
          <Icon
            size={30}
            className={valueColor}
          />
        </div>

      </div>
    </div>
  );
}