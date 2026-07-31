import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../api/apiClient";

export default function History() {

  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  const navigate = useNavigate();


  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);

        const response = await apiClient.get("/api/history/");

        setHistory(response.data.history || []);
      } catch (err) {
        console.error(err);
        setError("Failed to load history.");
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();

  }, []);



  const filteredHistory = history.filter((item) => {
    const query = search.toLowerCase();

    return (
      (item.text || "").toLowerCase().includes(query) ||
      (item.platform?.platform || "").toLowerCase().includes(query) ||
      (item.final_result?.label || "").toLowerCase().includes(query) ||
      new Date(item.analysis_time)
        .toLocaleDateString()
        .toLowerCase()
        .includes(query)
    );
  });



  if (loading) {

    return (

      <div className="text-white text-xl">

        Loading history...

      </div>

    );

  }



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



      {
        error && (

          <div className="bg-red-500 text-white p-4 rounded-xl">

            {error}

          </div>

        )
      }
      <div className="bg-slate-800 rounded-2xl p-4">
        <input
          type="text"
          placeholder="🔍 Search by content, platform, result or date..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-slate-900 text-white rounded-xl px-4 py-3 outline-none border border-slate-700 focus:border-blue-500"
        />
      </div>



      <div className="bg-slate-800 rounded-2xl overflow-hidden">


        <table className="w-full text-white">


          <thead className="bg-slate-900">

            <tr>

              <th className="p-4 text-left">
                Date
              </th>

              <th className="p-4 text-left">
                Content
              </th>

              <th className="p-4 text-left">
                Platform
              </th>

              <th className="p-4 text-left">
                Result
              </th>

              <th className="p-4 text-left">
                Confidence
              </th>

              <th className="p-4 text-left">
                Action
              </th>

            </tr>

          </thead>



          <tbody>
            {filteredHistory.length > 0 ? (
              filteredHistory.map((item) => {
                const result = item.final_result || {};
                const label = (result.label || "").toLowerCase();

                return (
                  <tr
                    key={item.analysis_id}
                    className="border-t border-slate-700"
                  >
                    <td className="p-4">
                      {new Date(item.analysis_time).toLocaleDateString()}
                    </td>

                    <td className="p-4 max-w-xs">
                      {item.text
                        ? item.text.substring(0, 50) + "..."
                        : "Image Analysis"}
                    </td>

                    <td className="p-4">
                      {item.platform?.platform || "Unknown"}
                    </td>

                    <td
                      className={`p-4 font-bold ${label.includes("verified") ||
                        label.includes("reliable")
                        ? "text-green-400"
                        : label.includes("false") ||
                          label.includes("misinformation")
                          ? "text-red-400"
                          : label.includes("verification") ||
                            label.includes("misleading")
                            ? "text-yellow-400"
                            : "text-blue-400"
                        }`}
                    >
                      {result.label || "Unknown"}
                    </td>

                    <td className="p-4">
                      {result.confidence ?? 0}%
                    </td>

                    <td className="p-4">
                      <button
                        className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-white font-bold"
                        onClick={() =>
                          navigate(`/history/${item.analysis_id}`)
                        }
                      >
                        👁 View
                      </button>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td
                  colSpan="6"
                  className="text-center text-gray-400 py-8"
                >
                  No matching history found.
                </td>
              </tr>
            )}
          </tbody>


        </table>


      </div>


    </div>

  );

}