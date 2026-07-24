export default function History() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-white">
          Analysis History
        </h1>

        <p className="text-gray-400 mt-2">
          View previous misinformation analyses.
        </p>
      </div>

      <div className="bg-slate-800 rounded-2xl overflow-hidden">

        <table className="w-full text-white">
          <thead className="bg-slate-900">
            <tr>
              <th className="p-4 text-left">Date</th>
              <th className="p-4 text-left">Title</th>
              <th className="p-4 text-left">Result</th>
              <th className="p-4 text-left">Confidence</th>
            </tr>
          </thead>

          <tbody>

            <tr className="border-t border-slate-700">
              <td className="p-4">24-07-2026</td>
              <td className="p-4">Sample News</td>
              <td className="p-4 text-red-400">FAKE</td>
              <td className="p-4">97%</td>
            </tr>

            <tr className="border-t border-slate-700">
              <td className="p-4">23-07-2026</td>
              <td className="p-4">Economic Update</td>
              <td className="p-4 text-green-400">REAL</td>
              <td className="p-4">94%</td>
            </tr>

          </tbody>
        </table>

      </div>
    </div>
  );
}