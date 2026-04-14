export interface ModelCheckResponse {
  ok: boolean;
  provider: string;
  model: string;
  preview: string;
}

export interface ValidateCodeResponse {
  is_valid: boolean;
  stage_results: Record<string, boolean>;
  errors: string[];
  warnings: string[];
}

export interface EvaluateCodeResponse {
  validation: {
    is_valid: boolean;
    stage_results: Record<string, boolean>;
    errors?: string[];
    warnings?: string[];
  };
  confidence: {
    score: number;
    reasons: string[];
  };
  evaluation_report: {
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
  };
}