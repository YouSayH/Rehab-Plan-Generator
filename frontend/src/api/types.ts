// frontend/src/api/types.ts

// Backendの抽出スキーマに対応する型定義

export interface BasicInfo {
  name?: string;
  age?: number;
  gender?: '男' | '女'; // Literalに合わせる
  disease_name?: string; // disease_name
  onset_date?: string;
  history?: string; // 任意フィールド
}

// 複雑なサブスキーマは一旦 Record<string, any> で許容しつつ、主要な構造を定義
export interface PatientExtractionData {
  basic: BasicInfo;
  medical: Record<string, any>;
  function: Record<string, any>;
  basic_movement: Record<string, any>;
  adl: Record<string, any>;
  nutrition: Record<string, any>;
  social: Record<string, any>;
  goals: Record<string, any>;
  signature: Record<string, any>;
}

export interface PlanRead {
  plan_id: number;
  hash_id: string;
  doc_date: string;
  format_version: string;
  raw_data: Record<string, any>;
  created_at: string;
}

// セルマッピング定義
export const CELL_MAPPING: Record<string, { r: number; c: number }> = {
  // 短期目標
  goals_1_month_txt: { r: 11, c: 1 }, 
  // 長期目標
  goals_at_discharge_txt: { r: 13, c: 1 }, 
  // リハビリプログラム (方針 or 具体的内容)
  policy_content_txt: { r: 15, c: 1 }, 
  // リスク管理
  main_risks_txt: { r: 17, c: 1 }, 
};