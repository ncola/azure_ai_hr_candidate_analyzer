
// main application component

import React, { useState } from 'react';
import UploadForm from './components/UploadForm';
import ResultsDashboard from './components/ResultsDashboard';

// simple styling for layout
// replace with tailwind classes (e..g, 'container mx-auto p-4')
const appStyle: React.CSSProperties = {
  maxWidth: '900px',
  margin: '20px auto',
  padding: '1rem',
  fontFamily: 'Arial, sans-serif'
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  borderBottom: '2px solid #f0f0f0',
  paddingBottom: '10px'
};

const App: React.FC = () => {
  // state to manage which view is active
  // null = show upload form
  // string = show results dashboard for that id
  const [currentAnalysisId, setCurrentAnalysisId] = useState<string | null>(null);

  /**
   * this function is passed as a prop to uploadform
   * it gets called when the api /analyze call is successful
   */
  const handleAnalysisStart = (analysisId: string) => {
    setCurrentAnalysisId(analysisId);
  };

  /**
   * allows the user to go back to the upload form
   */
  const startNewAnalysis = () => {
    setCurrentAnalysisId(null);
  };

  return (
    <div style={appStyle}>
      {/* main header */}
      <header style={headerStyle}>
        <h1>HR Candidate Analyzer</h1>
        {/* show 'new analysis' button only when viewing results */}
        {currentAnalysisId && (
          <button onClick={startNewAnalysis}>
            Rozpocznij nową analizę
          </button>
        )}
      </header>

      {/* main content area */}
      <main style={{ marginTop: '20px' }}>
        {/* conditional rendering */}
        {/* if we don't have an id, show the upload form */}
        {!currentAnalysisId && (
          <UploadForm onAnalysisStart={handleAnalysisStart} />
        )}
        
        {/* if we have an id, show the results dashboard */}
        {currentAnalysisId && (
          <ResultsDashboard analysisId={currentAnalysisId} />
        )}
      </main>
    </div>
  );
};

export default App;
