import { createContext, useContext, useState } from "react";


const AnalysisContext = createContext();


export function AnalysisProvider({ children }) {

  const [analysisData, setAnalysisData] = useState(null);


  return (

    <AnalysisContext.Provider

      value={{
        analysisData,
        setAnalysisData
      }}

    >

      {children}

    </AnalysisContext.Provider>

  );

}



export function useAnalysis() {

  return useContext(AnalysisContext);

}