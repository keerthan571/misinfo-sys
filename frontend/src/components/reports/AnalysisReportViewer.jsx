const AnalysisReportViewer = ({ report }) => {

  if (!report) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold">
          Select a report to view details.
        </h2>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-6">

      <h2 className="text-2xl font-bold">
        Analysis Report
      </h2>

      {/* Analysis Summary */}

      <section>

        <h3 className="text-lg font-semibold mb-2">
          Analysis Summary
        </h3>

        <div className="grid grid-cols-2 gap-4">

          <p>
            <strong>Label:</strong>{" "}
            {report.analysis?.label}
          </p>

          <p>
            <strong>Confidence:</strong>{" "}
            {report.analysis?.confidence}
          </p>

          <p>
            <strong>Risk:</strong>{" "}
            {report.analysis?.risk_level}
          </p>

        </div>

        <p className="mt-3">
          {report.analysis?.summary}
        </p>

      </section>

      {/* Engagement */}

      <section>

        <h3 className="text-lg font-semibold mb-2">
          Engagement
        </h3>

        <div className="grid grid-cols-3 gap-3">

          <p>Likes : {report.engagement?.likes}</p>

          <p>Shares : {report.engagement?.shares}</p>

          <p>Comments : {report.engagement?.comments}</p>

          <p>Views : {report.engagement?.views}</p>

          <p>Bookmarks : {report.engagement?.bookmarks}</p>

        </div>

      </section>

      {/* Spread Prediction */}

      <section>

        <h3 className="text-lg font-semibold mb-2">
          Spread Prediction
        </h3>

        <p>
          Predicted Reach :
          {" "}
          {report.prediction?.predicted_reach}
        </p>

        <p>
          Spread Probability :
          {" "}
          {report.prediction?.spread_probability}
        </p>

        <p>
          Virality Score :
          {" "}
          {report.prediction?.virality_score}
        </p>

      </section>

      {/* Fact Verification */}

      <section>

        <h3 className="text-lg font-semibold mb-2">
          Fact Verification
        </h3>

        <p>
          Verdict :
          {" "}
          {report.fact_verification?.verdict}
        </p>

        <p>
          Confidence :
          {" "}
          {report.fact_verification?.confidence}
        </p>

        <p>
          {report.fact_verification?.reason}
        </p>

      </section>

      {/* Graph */}

      <section>

        <h3 className="text-lg font-semibold mb-2">
          Graph Statistics
        </h3>

        <p>
          Nodes :
          {" "}
          {report.graph_statistics?.node_count}
        </p>

        <p>
          Edges :
          {" "}
          {report.graph_statistics?.edge_count}
        </p>

        <p>
          Density :
          {" "}
          {report.graph_statistics?.density}
        </p>

      </section>

      {/* Influencers */}

      <section>

        <h3 className="text-lg font-semibold mb-2">
          Top Influencers
        </h3>

        <ul className="list-disc ml-6">

          {report.top_influencers?.map((item) => (

            <li key={item.id}>

              {item.label}
              {" - "}
              Score :
              {" "}
              {item.score}

            </li>

          ))}

        </ul>

      </section>

      {/* Communities */}

      <section>

        <h3 className="text-lg font-semibold mb-2">
          Communities
        </h3>

        <ul className="list-disc ml-6">

          {report.communities?.map((item) => (

            <li key={item.community_id}>

              Community
              {" "}
              {item.community_id}
              {" | "}
              Risk :
              {" "}
              {item.risk_score}

            </li>

          ))}

        </ul>

      </section>

    </div>
  );

};

export default AnalysisReportViewer;