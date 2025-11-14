
// comment style according to user instructions

import axios from 'axios';
import { AnalysisResponse, StartAnalysisResponse } from '../types/apiTypes';

// configure a base instance of axios
// assumes the backend api is served from '/api'
// update 'baseurl' if your backend is on a different port (e.g., 'http://localhost:8000/api')
const apiClient = axios.create({
  baseURL: '/api',
});

/**
 * starts the analysis process.
 * sends job description and cv files as 'multipart/form-data'.
 *
 *
 * @param jobDescription - the full text of the job offer.
 * @param cvFiles - an array of file objects from the uploader.
 * @returns a promise with the initial analysis status and id.
 */
const startAnalysis = async (
  jobDescription: string,
  cvFiles: File[]
): Promise<StartAnalysisResponse> => {
  
  // create a formdata object to send 'multipart/form-data'
  const formData = new FormData();
  
  // append the job description string
  formData.append('jobDescription', jobDescription);
  
  // append each file
  // the key 'cvfiles' must match the api specification
  cvFiles.forEach((file) => {
    formData.append('cvFiles', file);
  });

  // make the post request
  // we must set the 'content-type' header manually for form-data
  const response = await apiClient.post<StartAnalysisResponse>(
    '/analyze', //
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  
  // return the json response (e.g., { analysisid: '...', status: 'processing' })
  return response.data;
};

/**
 * polls for the final analysis results.
 *
 *
 * @param analysisId - the id received from the startanalysis call.
 * @returns a promise with the full analysis report.
 */
const getAnalysisResults = async (
  analysisId: string
): Promise<AnalysisResponse> => {
  
  // make the get request to the dynamic endpoint
  const response = await apiClient.get<AnalysisResponse>(
    `/results/${analysisId}` //
  );
  
  // return the full json report
  return response.data;
};

// export functions for use in components or hooks
export const analysisApi = {
  startAnalysis,
  getAnalysisResults,
};
