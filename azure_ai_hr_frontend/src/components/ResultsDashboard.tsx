import React, { useState, useEffect, useRef } from 'react';
import { analysisApi } from '../api/analysisApi';
import { AnalysisResponse, Candidate } from '../types/apiTypes';

// component properties
interface ResultsDashboardProps {
  /**
   * the id returned from the initial /api/analyze call
   */
  analysisId: string;
}

// polling interval (e.g., every 3 seconds)
const POLLING_INTERVAL_MS = 3000;

const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ analysisId }) => {
  // state for api data
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);

  // state for ui feedback
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // ref to hold the interval id
  // this allows us to clear it from anywhere
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    // reset state when a new analysisid is provided
    setIsLoading(true);
    setError(null);
    setAnalysisData(null);

    // function to fetch data from the api
    const fetchData = async () => {
      try {
        const data = await analysisApi.getAnalysisResults(analysisId);
        
        // success(:3) set data, stop loading, and clear the interval
        setAnalysisData(data);
        setIsLoading(false);
        
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }

      } catch (err) {
        // a 404 might mean 'still processing'
        // for this example, we assume any error is final
        console.error('blad podczas pobierania wynikow:', err);
        setError('nie udalo sie pobrac wynikow   sproboj ponownie pozniej');
        setIsLoading(false);

        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    };

    // --- polling logic ---
    
    // 1. fetch immediately on component mount
    fetchData();

    // 2. then, set up an interval to poll
    // (window.setinterval is used to avoid node.js vs browser type conflicts)
    intervalRef.current = window.setInterval(fetchData, POLLING_INTERVAL_MS);

    // 3. cleanup function
    // this runs when the component unmounts or analysisid changes
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };

  }, [analysisId]); // re-run this entire effect if analysisid changes

  
  // --- rendering logic ---

  if (isLoading) {
    return (
      <div>
        <h2>Analizuję kandydatów...</h2>
        <p>to moze potrwac chwile   proszę czekać</p>
        {/* todo: add a spinner component */}
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ color: 'red' }}>
        <h2>Wystąpił błąd</h2>
        <p>{error}</p>
      </div>
    );
  }

  if (!analysisData) {
    // this case should rarely be seen, at least i hope so lol
    return <div>brak danych</div>;
  }

  // --- successful data render ---
  //
  return (
    <div className="results-dashboard">
      <header className="dashboard-header">
        <h1>Wyniki analizy</h1>
        <h2>{analysisData.jobDetails.title}</h2>
        <p>{analysisData.jobDetails.summary}</p>
        <small>analiza z {new Date(analysisData.analysisTimestamp).toLocaleString('pl-PL')}</small>
      </header>

      <hr />

      <section className="candidate-list">
        <h3>Lista Kandydatów</h3>
        {/* render candidates, backend should have sorted them by overallscore */}
        {analysisData.candidates.map((candidate) => (
          <CandidateCard key={candidate.candidateId} candidate={candidate} />
        ))}
      </section>
    </div>
  );
};

/**
 * sub-component to render a single candidate's summary
 */
const CandidateCard: React.FC<{ candidate: Candidate }> = ({ candidate }) => {
  
  const isError = candidate.status === 'Error';

  // example tailwind classes
  // const cardClasses = `p-4 mb-4 border rounded-lg ${isError ? 'bg-red-50 border-red-300' : 'bg-white shadow'}`;
  
  return (
    <div className="candidate-card" style={{
      padding: '1rem',
      marginBottom: '1rem',
      border: '1px solid #ddd',
      borderRadius: '8px',
      backgroundColor: isError ? '#fff0f0' : '#ffffff'
    }}>
      
      {/* card header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h4 style={{ margin: 0 }}>
          {/* handle missing name on error */}
          {candidate.extractedName || candidate.fileName}
        </h4>
        {!isError && (
          <span style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
            {candidate.overallScore}%
          </span>
        )}
      </div>
      
      {/* file name (if different from extracted name) */}
      {candidate.extractedName && (
        <small style={{ color: '#555' }}>{candidate.fileName}</small>
      )}
      
      {/* summary or error message */}
      <p style={{ color: isError ? '#c00' : '#333' }}>
        {candidate.aiBriefSummary}
      </p>

      {!isError && (
        <button
          onClick={() => alert(`todo: otworz szczegolowy raport dla ${candidate.candidateId}`)}
          // example tailwind: "bg-blue-100 text-blue-800 px-3 py-1 rounded"
        >
          Zobacz pełny raport
        </button>
      )}
    </div>
  );
};

export default ResultsDashboard;
