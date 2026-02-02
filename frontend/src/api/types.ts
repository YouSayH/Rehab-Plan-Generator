// frontend/src/api/types.ts

// ==========================================
// Patient Extraction Data Types
// ==========================================

export interface BasicInfo {
  name: string | null;
  age: number | null;
  gender: '男' | '女' | null;
  age_display?: string;
  disease_name?: string | null;
  onset_date?: string | null;
  history?: string | null;
}

// ADLの各項目（FIM/BI）
export interface AdlItem {
  fim_start?: number | null;
  fim_current?: number | null;
  bi_start?: number | null;
  bi_current?: number | null;
}

// ADL全体
export interface Adl {
  eating: AdlItem;
  grooming: AdlItem;
  bathing: AdlItem;
  dressing_upper: AdlItem;
  dressing_lower: AdlItem;
  toileting: AdlItem;
  bladder: AdlItem;
  bowel: AdlItem;
  transfer_bed: AdlItem;
  transfer_toilet: AdlItem;
  transfer_tub: AdlItem;
  locomotion_walk: AdlItem;
  locomotion_stairs: AdlItem;
  comprehension: AdlItem;
  expression: AdlItem;
  social: AdlItem;
  problem_solving: AdlItem;
  memory: AdlItem;
}

export interface Goals {
  short_term_goal?: string | null;
  long_term_goal?: string | null;
}

// データ全体のルート型
export interface PatientExtractionData {
  basic: BasicInfo;
  medical: Record<string, any>;
  function: Record<string, any>;
  basic_movement: Record<string, any>;
  adl: Adl; // 詳細型を適用
  nutrition: Record<string, any>;
  social: Record<string, any>;
  goals: Goals;
  signature: Record<string, any>;
}

// ==========================================
// Plan / Mapping Types
// ==========================================

export interface PlanRead {
  plan_id: number;
  hash_id: string;
  doc_date: string;
  format_version: string;
  raw_data: Record<string, any>;
  created_at: string;
}

export interface CellMapping {
  r: number;
  c: number;
}

export const CELL_MAPPING: Record<string, CellMapping> = {
  goals_1_month_txt: { r: 11, c: 1 }, 
  goals_at_discharge_txt: { r: 13, c: 1 }, 
  policy_content_txt: { r: 15, c: 1 }, 
  main_risks_txt: { r: 17, c: 1 }, 
};