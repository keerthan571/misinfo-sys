import {
  deleteReport,
  downloadCSV,
  downloadPDF,
} from "../../services/reportApi";

const AnalysisReportTable = ({
  reports,
  refresh,
  openReport,
}) => {

  const handleDelete = async (id) => {

    if (!window.confirm("Delete this report?")) {
      return;
    }

    try {

      await deleteReport(id);

      refresh();

    } catch (error) {

      console.error(error);

      alert("Unable to delete report.");

    }

  };

  const handlePDF = async (id) => {

    try {

      const result = await downloadPDF(id);

      alert(
        `PDF generated successfully.\n\n${result.file}`
      );

    } catch (error) {

      console.error(error);

      alert("Failed to generate PDF.");

    }

  };

  const handleCSV = async (id) => {

    try {

      const result = await downloadCSV(id);

      alert(
        `CSV generated successfully.\n\n${result.file}`
      );

    } catch (error) {

      console.error(error);

      alert("Failed to generate CSV.");

    }

  };

  return (

    <div className="bg-white rounded-xl shadow-lg overflow-hidden">

      <table className="min-w-full">

        <thead className="bg-slate-100">

          <tr>

            <th className="px-6 py-4 text-left font-semibold">
              Report ID
            </th>

            <th className="px-6 py-4 text-center font-semibold">
              Actions
            </th>

          </tr>

        </thead>

        <tbody>

          {reports.length === 0 ? (

            <tr>

              <td
                colSpan={2}
                className="text-center py-8 text-gray-500"
              >
                No reports available.
              </td>

            </tr>

          ) : (

            reports.map((report) => {

              const id = report.replace(".json", "");

              return (

                <tr
                  key={id}
                  className="border-t hover:bg-slate-50 transition"
                >

                  <td className="px-6 py-4 font-medium">

                    {id}

                  </td>

                  <td className="px-6 py-4">

                    <div className="flex flex-wrap justify-center gap-2">

                      <button
                        onClick={() => openReport(id)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2 rounded-lg"
                      >
                        View
                      </button>

                      <button
                        onClick={() => handlePDF(id)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg"
                      >
                        PDF
                      </button>

                      <button
                        onClick={() => handleCSV(id)}
                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg"
                      >
                        CSV
                      </button>

                      <button
                        onClick={() => handleDelete(id)}
                        className="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-lg"
                      >
                        Delete
                      </button>

                    </div>

                  </td>

                </tr>

              );

            })

          )}

        </tbody>

      </table>

    </div>

  );

};

export default AnalysisReportTable;