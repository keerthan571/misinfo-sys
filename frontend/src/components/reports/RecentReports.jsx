import { FileText } from "lucide-react";

const RecentReports = ({ reports, openReport }) => {

  const latestReports = reports.slice(0, 5);

  return (

    <div className="bg-white rounded-xl shadow-lg p-6">

      <h2 className="text-xl font-bold mb-4">

        Recent Reports

      </h2>

      {latestReports.length === 0 ? (

        <p className="text-gray-500">

          No reports available.

        </p>

      ) : (

        <div className="space-y-3">

          {latestReports.map((report) => {

            const id = report.replace(".json", "");

            return (

              <button
                key={id}
                onClick={() => openReport(id)}
                className="
                  w-full
                  flex
                  items-center
                  justify-between
                  p-3
                  rounded-lg
                  border
                  hover:bg-blue-50
                  transition
                "
              >

                <div className="flex items-center gap-3">

                  <FileText
                    size={20}
                    className="text-blue-600"
                  />

                  <span>

                    {id}

                  </span>

                </div>

                <span className="text-blue-600">

                  View →

                </span>

              </button>

            );

          })}

        </div>

      )}

    </div>

  );

};

export default RecentReports;