
// types based on 'required json response structure' from api_specification.md

/**
 * match status for a single requirement.
 */
export type MatchStatus = "HIGH" | "MEDIUM" | "LOW" | "NONE";

/**
 * general processing status for a candidate.
 */
export type CandidateStatus = "Completed" | "Error" | "Processing";

/**
 * response from the post /api/analyze endpoint.
 */
export interface StartAnalysisResponse {
  analysisId: string;
  status: "Processing";
}

/**
 * structure of a single match analysis item.
 */
export interface MatchAnalysisItem {
  requirement: string;
  matchStatus: MatchStatus;
  aiJustification: string;
  evidence: string[];
}

// --- structures for 'rawextracteddata' ---

export interface RawContactInfo {
  email: string | null;
  phone: string | null;
}

export interface RawEducation {
  degree: string;
  school: string;
}

export interface RawWorkExperience {
  company: string;
  role: string;
  duration: string;
}

/**
 * optional raw data extracted by form recognizer.
 */
export interface RawExtractedData {
  contactInfo: RawContactInfo;
  education: RawEducation[];
  workExperience: RawWorkExperience[];
  skills: string[];
}

// --- main response structures ---

/**
 * detailed report for a single candidate.
 */
export interface DetailedReport {
  aiFullSummary: string;
  matchAnalysis: MatchAnalysisItem[];
  rawExtractedData: RawExtractedData;
}

/**
 * main candidate object.
 */
export interface Candidate {
  candidateId: string;
  fileName: string;
  extractedName: string | null; // null in case of an error
  overallScore: number;
  aiBriefSummary: string;
  status: CandidateStatus;
  detailedReport: DetailedReport | null; // null in case of an error
}

/**
 * details of the analyzed job offer.
 */
export interface JobDetails {
  title: string;
  summary: string;
}

/**
 * main response object from the get /api/results/{analysisid} endpoint.
 */
export interface AnalysisResponse {
  analysisId: string;
  analysisTimestamp: string; // (e.g., "2025-11-05T18:15:00Z")
  jobDetails: JobDetails;
  candidates: Candidate[];
}
