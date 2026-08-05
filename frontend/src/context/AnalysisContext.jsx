import { createContext, useContext, useState } from "react";

const AnalysisContext = createContext();

export function AnalysisProvider({ children }) {

    const [analysis, setAnalysis] = useState(null);

    return (
        <AnalysisContext.Provider
            value={{
                analysis,
                setAnalysis,
            }}
        >
            {children}
        </AnalysisContext.Provider>
    );
}

export function useAnalysis() {
    return useContext(AnalysisContext);
}