const ReportStats = ({ reports }) => {

  return (

    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

      <div className="bg-white rounded-xl shadow p-5">

        <h3 className="text-gray-500">
          Total Reports
        </h3>

        <p className="text-3xl font-bold mt-2">
          {reports.length}
        </p>

      </div>

      <div className="bg-white rounded-xl shadow p-5">

        <h3 className="text-gray-500">
          Today's Reports
        </h3>

        <p className="text-3xl font-bold mt-2">
          {reports.length}
        </p>

      </div>

      <div className="bg-white rounded-xl shadow p-5">

        <h3 className="text-gray-500">
          Downloads
        </h3>

        <p className="text-3xl font-bold mt-2">
          --
        </p>

      </div>

    </div>

  );

};

export default ReportStats;