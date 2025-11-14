import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone'; //
import { analysisApi } from '../api/analysisApi';

// component properties
interface UploadFormProps {
  /**
   * callback function executed on successful analysis start
   * it passes the new analysisid to the parent component
   */
  onAnalysisStart: (analysisId: string) => void;
}

const UploadForm: React.FC<UploadFormProps> = ({ onAnalysisStart }) => {
  // state for form fields
  const [jobDescription, setJobDescription] = useState<string>('');
  const [cvFiles, setCvFiles] = useState<File[]>([]);

  // state for ui feedback
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // setup dropzone handler
  // usecallback ensures this function isn't recreated on every render
  const onDrop = useCallback((acceptedFiles: File[]) => {
    // this replaces files (you can also append if you prefer)
    setCvFiles(acceptedFiles);
    setError(null); // clear file error if files are added
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      // define accepted mime types based on your needs
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    }
  });

  // handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // prevent default html form submission
    setError(null);

    // --- simple validation ---
    if (!jobDescription.trim()) {
      setError('opis stanowiska jest wymagany');
      return;
    }
    if (cvFiles.length === 0) {
      setError('przeslij przynajmniej jedno cv');
      return;
    }

    setIsLoading(true);

    try {
      // call the api function we defined earlier
      // it sends data as 'multipart/form-data'
      const response = await analysisApi.startAnalysis(jobDescription, cvFiles);
      
      // on success, call the parent callback with the new id
      onAnalysisStart(response.analysisId);

    } catch (apiError) {
      console.error('blad podczas rozpoczynania analizy:', apiError);
      setError('nie udalo sie rozpoczac analizy   sproboj ponownie');
      setIsLoading(false);
    }
    // 'isloading' remains true on success because we expect a page navigation
  };
  
  // helper to render the list of selected files
  const fileList = cvFiles.map(file => (
    <li key={file.path}>
      {file.name} - {(file.size / 1024).toFixed(2)} KB
    </li>
  ));

  // simple inline style for dropzone
  // replace with tailwind classes (e.g., 'border-2 border-dashed border-gray-400')
  const dropzoneStyle: React.CSSProperties = {
    border: '2px dashed #ccc',
    borderRadius: '4px',
    padding: '20px',
    textAlign: 'center',
    cursor: 'pointer',
    backgroundColor: isDragActive ? '#f0f0f0' : '#ffffff',
  };

  return (
    <div className="upload-container">
      
      {/* job description text area */}
      <div className="form-group">
        <label htmlFor="jobDescription">Opis Stanowiska</label>
        <textarea
          id="jobDescription"
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
          disabled={isLoading}
          rows={10}
          placeholder="wklej pelny opis stanowiska tutaj..."
          // example tailwind: "w-full p-2 border rounded"
        />
      </div>

      {/* cv dropzone */}
      <div className="form-group">
        <label>Pliki CV (.pdf, .docx)</label>
        <div {...getRootProps()} style={dropzoneStyle}>
          <input {...getInputProps()} />
          {isDragActive ?
            <p>upusc pliki tutaj ...</p> :
            <p>przeciagnij i upusc pliki cv tutaj, lub kliknij aby wybrac</p>
          }
        </div>
        
        {/* selected files list */}
        {fileList.length > 0 && (
          <aside>
            <h4>Wybrane pliki:</h4>
            <ul>{fileList}</ul>
          </aside>
        )}
      </div>
      
      {/* error display */}
      {error && (
        <div style={{ color: 'red' }}>
          {error}
        </div>
      )}

      {/* submit button */}
      <button 
        type="button" 
        onClick={handleSubmit} 
        disabled={isLoading}
        // example tailwind: "w-full bg-blue-500 text-white p-2 rounded disabled:bg-gray-400"
      >
        {isLoading ? 'Analizuję...' : 'Rozpocznij Analizę'}
      </button>

    </div>
  );
};

export default UploadForm;
