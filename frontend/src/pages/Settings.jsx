export default function Settings() {
  return (
    <div className="space-y-6">

      <div>
        <h1 className="text-4xl font-bold text-white">
          Settings
        </h1>

        <p className="text-gray-400 mt-2">
          Configure your AI Misinformation Analysis System.
        </p>
      </div>

      <div className="bg-slate-800 rounded-2xl p-8 space-y-6">

        <div>
          <label className="text-white font-semibold">
            User Name
          </label>

          <input
            type="text"
            defaultValue="Mahesha"
            className="w-full mt-2 bg-slate-900 p-3 rounded-lg text-white outline-none"
          />
        </div>

        <div>
          <label className="text-white font-semibold">
            Email
          </label>

          <input
            type="email"
            defaultValue="mahesha@example.com"
            className="w-full mt-2 bg-slate-900 p-3 rounded-lg text-white outline-none"
          />
        </div>

        <button className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold">
          Save Settings
        </button>

      </div>

    </div>
  );
}