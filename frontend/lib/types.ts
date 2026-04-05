export interface Question {
  id: string;
  text: string;
}

export interface CareerMatch {
  role: string;
  score: number;
}

export interface TraitState {
  analytical: number;
  creativity: number;
  social: number;
  risk: number;
  discipline: number;
}

export interface AssessmentResult {
  best_match: CareerMatch;
  alternatives: CareerMatch[];
  confidence: number;
  state: TraitState;
}

export interface ResultResponse extends AssessmentResult {
  session_id: string;
  questions_answered: number;
}

export interface StartResponse {
  session_id: string;
  question: Question;
  message?: string;
}

export interface NextResponse {
  session_id: string;
  question?: Question | null;
  result?: AssessmentResult | null;
  message: string;
  state: TraitState;
}

export interface AdviceRequest {
  analytical: number;
  creativity: number;
  social: number;
  risk: number;
  discipline: number;
  career: string;
}

export interface AdviceResponse {
  explanation: string;
  skill_gap: string[];
  roadmap: string[];
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}
