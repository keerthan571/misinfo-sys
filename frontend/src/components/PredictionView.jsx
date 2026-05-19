import React from 'react';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';


const PredictionView = ({ data }) => {

  if (!data) return null;

  // Extract prediction data
  const predictionData = data?.data || {};

  // Reach chart data
  const reachChartData = [
    {
      name: 'Reach',
      value:
        predictionData.predicted_reach || 0
    }
  ];

  // Pie chart data
  const pieData = [
    {
      name: 'Likes',
      value:
        predictionData.engagement_breakdown?.likes || 0
    },

    {
      name: 'Shares',
      value:
        predictionData.engagement_breakdown?.shares || 0
    },

    {
      name: 'Comments',
      value:
        predictionData.engagement_breakdown?.comments || 0
    }
  ];

  // Pie chart colors
  const COLORS = [
    '#4f46e5',
    '#10b981',
    '#f59e0b'
  ];

  return (

    <div className="card">

      <h2>Spread Prediction</h2>

      {/* Predicted Reach */}

      <div className="result-item">

        <strong>Predicted Reach:</strong>

        {' '}

        {
          predictionData.predicted_reach
        } users

      </div>

      {/* Risk Level */}

      <div className="result-item">

        <strong>Risk Level:</strong>

        <span
          style={{

            color:
              predictionData.risk_level ===
              'Very High'

                ? 'red'

                : predictionData.risk_level ===
                  'High'

                ? 'orange'

                : predictionData.risk_level ===
                  'Medium'

                ? '#f59e0b'

                : 'green',

            fontWeight: 'bold',

            marginLeft: '5px'
          }}
        >

          {
            predictionData.risk_level
          }

        </span>

      </div>

      {/* Virality Score */}

      <div className="result-item">

        <strong>Virality Score:</strong>

        {' '}

        {
          predictionData.virality_score
        }%

      </div>

      {/* Analysis Summary */}

      <div className="result-item">

        <strong>Analysis Summary:</strong>

        {' '}

        {
          data.analysis_summary
        }

      </div>

      {/* Reach Bar Chart */}

      <div
        style={{
          width: '100%',
          height: 250,
          marginTop: '20px'
        }}
      >

        <ResponsiveContainer>

          <BarChart
            data={reachChartData}
          >

            <XAxis dataKey="name" />

            <YAxis />

            <Tooltip />

            <Bar
              dataKey="value"
              fill="#4f46e5"
              radius={[10, 10, 0, 0]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

      {/* Virality Progress Bar */}

      <div
        style={{
          marginTop: '30px'
        }}
      >

        <h3
          style={{
            marginBottom: '10px'
          }}
        >

          Virality Meter

        </h3>

        <div
          style={{
            width: '100%',
            background: '#e5e7eb',
            borderRadius: '20px',
            overflow: 'hidden',
            height: '28px'
          }}
        >

          <div
            style={{

              width:
                `${predictionData.virality_score}%`,

              background: '#4f46e5',

              height: '100%',

              borderRadius: '20px',

              textAlign: 'center',

              color: 'white',

              fontWeight: 'bold',

              lineHeight: '28px',

              transition: '0.5s ease'
            }}
          >

            {
              predictionData.virality_score
            }%

          </div>

        </div>

      </div>

      {/* Pie Chart */}

      <div
        style={{
          width: '100%',
          height: 320,
          marginTop: '40px'
        }}
      >

        <ResponsiveContainer>

          <PieChart>

            <Pie
              data={pieData}

              cx="50%"

              cy="50%"

              outerRadius={100}

              dataKey="value"

              label
            >

              {

                pieData.map(

                  (entry, index) => (

                    <Cell
                      key={index}

                      fill={
                        COLORS[
                          index % COLORS.length
                        ]
                      }
                    />
                  )
                )
              }

            </Pie>

            <Tooltip />

          </PieChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
};

export default PredictionView;