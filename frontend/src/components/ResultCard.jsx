import React from 'react';

const ResultCard = ({ title, data }) => {

  if (!data) return null;

  return (

    <div className="card">

      <h2>{title}</h2>

      {

        Object.entries(data).map(

          ([key, value]) => {

            // -----------------------------------
            // Array Rendering (Tags/Badges)
            // -----------------------------------

            if (Array.isArray(value)) {

              return (

                <div
                  key={key}
                  className="result-item"
                >

                  <strong>
                    {
                      key.replaceAll('_', ' ')
                    }:
                  </strong>

                  <div
                    style={{
                      marginTop: '10px'
                    }}
                  >

                    {

                      value.length === 0

                        ? (

                          <span
                            style={{
                              color: '#666'
                            }}
                          >

                            No suspicious terms detected

                          </span>
                        )

                        : (

                          value.map(

                            (item, index) => (

                              <span
                                key={index}

                                style={{
                                  display: 'inline-block',
                                  background:
                                    '#4f46e5',

                                  color: 'white',

                                  padding:
                                    '6px 14px',

                                  borderRadius:
                                    '20px',

                                  marginRight:
                                    '8px',

                                  marginTop:
                                    '6px',

                                  fontSize:
                                    '14px',

                                  fontWeight:
                                    'bold',

                                  boxShadow:
                                    '0 2px 6px rgba(0,0,0,0.2)'
                                }}
                              >

                                {item}

                              </span>
                            )
                          )
                        )
                    }

                  </div>

                </div>
              );
            }

            // -----------------------------------
            // Object Rendering
            // -----------------------------------

            if (
              typeof value === 'object' &&
              value !== null
            ) {

              return (

                <div
                  key={key}
                  className="result-item"
                >

                  <strong>
                    {
                      key.replaceAll('_', ' ')
                    }:
                  </strong>

                  <pre
                    style={{
                      fontSize: '0.8rem',
                      marginTop: '0.5rem',
                      background: '#f5f5f5',
                      padding: '10px',
                      borderRadius: '8px'
                    }}
                  >

                    {
                      JSON.stringify(
                        value,
                        null,
                        2
                      )
                    }

                  </pre>

                </div>
              );
            }

            // -----------------------------------
            // Normal Text Rendering
            // -----------------------------------

            return (

              <div
                key={key}
                className="result-item"
              >

                <strong>
                  {
                    key.replaceAll('_', ' ')
                  }:
                </strong>

                {' '}

                {String(value)}

              </div>
            );
          }
        )
      }

    </div>
  );
};

export default ResultCard;