export interface ChatSessionResponse {
  id: number;
  session_id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatMessageResponse {
  id: number;
  role: "system" | "user" | "assistant";
  content: string;
  order_index: number;
  created_at: string;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: ChatMessageResponse[];
}

export interface ValidationInfo {
  is_valid: boolean;
  stage_results: Record<string, boolean>;
  errors: string[];
  warnings: string[];
}

export interface ClarificationQuestion {
  key: string;
  question: string;
}

export interface TaskContract {
  goal: string;
  inputs: string[];
  outputs: string[];
  constraints: string[];
  assumptions: string[];
  target_runtime: string;
  complexity_note: string;
  task_type: string;
  task_subtype: string;
  risk_flags: string[];
  domain_profile: string;
  profile_rules: string[];
  output_mode: string;
}

export interface ConfidenceInfo {
  score: number;
  reasons: string[];
}

export interface EvaluationReport {
  context_mode: string;
  domain_profile: string;
  task_type: string;
  task_subtype: string;
  selected_templates: string[];
  output_mode: string;
  validation_summary: Record<string, unknown>;
  repair_used: boolean;
  attempts: number;
  confidence_score: number;
  confidence_reasons: string[];
  provider: string;
  model: string;
  has_diff: boolean;
  diff_text: string | null;
  final_status: string;
}

export interface ChatGenerateResponse {
  session_id: string;
  resumed_from_clarification: boolean;
  resumed_from_refinement: boolean;
  status:
    | "completed"
    | "needs_clarification"
    | "completed_with_warnings"
    | "failed_validation";
  code: string;
  output_mode: string;
  wrapped_code: string | null;
  json_output: string | null;
  diff_text: string | null;
  provider: string;
  model: string;
  repaired: boolean;
  attempts: number;
  used_history: boolean;
  validation: ValidationInfo;
  clarification_questions: ClarificationQuestion[];
  task_contract: TaskContract;
  confidence: ConfidenceInfo;
  evaluation_report: EvaluationReport;
  pipeline_steps: Array<Record<string, unknown>>;
}

export interface UiMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
  statusText?: string;
  generated?: ChatGenerateResponse | null;
}

export interface PipelineStepResponse {
  id: number;
  step_name: string;
  status: string;
  duration_ms: number;
  details_json: string | null;
  created_at: string;
}

export interface PipelineRunListItemResponse {
  id: number;
  status: string;
  provider: string | null;
  model: string | null;
  repaired: boolean;
  attempts: number;
  used_history: boolean;
  validate_runtime: boolean;
  confidence_score: number | null;
  created_at: string;
  finished_at: string | null;
}

export interface PipelineRunDetailsResponse {
  id: number;
  session_pk: number | null;
  user_prompt: string;
  status: string;
  provider: string | null;
  model: string | null;
  repaired: boolean;
  attempts: number;
  used_history: boolean;
  validate_runtime: boolean;
  final_code: string | null;
  confidence_score: number | null;
  confidence_reasons_json: string | null;
  task_contract_json: string | null;
  clarification_questions_json: string | null;
  created_at: string;
  finished_at: string | null;
  steps: PipelineStepResponse[];
}