export default function RecentActivity({ activities }) {
  return (
    <div className="bg-slate-800 rounded-2xl p-6 shadow-lg">
      <h2 className="text-2xl font-bold text-white mb-4">
        📰 Recent Activity
      </h2>

      {activities.length === 0 ? (
        <p className="text-gray-400">
          No recent activity available.
        </p>
      ) : (
        <div className="space-y-3">
          {activities.map((activity, index) => (
            <div
              key={index}
              className="bg-slate-900 p-4 rounded-lg text-white"
            >
              {activity}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}