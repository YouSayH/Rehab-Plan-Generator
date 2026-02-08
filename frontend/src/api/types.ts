// frontend/src/api/types.ts

// ==========================================
// Patient Extraction Data Types
// ==========================================

// 患者一覧取得用の型定義
export interface PatientRead {
  hash_id: string;
  name?: string;
  age?: number;
  gender?: string;
  diagnosis_code?: string;
}

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
  adl: Adl;
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
  r: number; // 0-based index
  c: number; // 0-based index
}

// デフォルトのマッピング設定
export const CELL_MAPPING: Record<string, CellMapping> = {
  main_risks_txt: { r: 17, c: 1 }, // B18
  goals_1_month_txt: { r: 11, c: 1 }, 
  goals_at_discharge_txt: { r: 13, c: 1 }, 
  policy_content_txt: { r: 15, c: 1 }, 
};

// ユーティリティ: A1形式 ("B12") を {r, c} に変換
export const parseCellAddress = (address: string): CellMapping | null => {
  const match = address.toUpperCase().match(/^([A-Z]+)([0-9]+)$/);
  if (!match) return null;

  const colStr = match[1];
  const rowStr = match[2];

  // 列変換 (A->0, B->1, AA->26)
  let col = 0;
  for (let i = 0; i < colStr.length; i++) {
    col = col * 26 + (colStr.charCodeAt(i) - 64);
  }
  col -= 1; // 0-based

  // 行変換 (1->0)
  const row = parseInt(rowStr, 10) - 1;

  return { r: row, c: col };
};

// ユーティリティ: {r, c} を A1形式に変換
export const stringifyCellAddress = (mapping: CellMapping): string => {
  let col = mapping.c + 1;
  let colStr = '';
  while (col > 0) {
    const remainder = (col - 1) % 26;
    colStr = String.fromCharCode(65 + remainder) + colStr;
    col = Math.floor((col - 1) / 26);
  }
  return `${colStr}${mapping.r + 1}`;
};


// ==========================================
// Plan Configuration Types (Hierarchical)
// ==========================================

// パネルの種類を判別するユニオン型
export type PlanNodeType = 'item' | 'group';

/**
 * 単体の生成パネル (Leaf Node)
 * 従来の CardConfig に相当しますが、type プロパティが追加されています。
 */
export interface PlanItem {
  id: string;
  type: 'item';
  title: string;
  description: string;
  prompt: string;
  targetKey: string;      // raw_dataのキー (例: main_risks_txt)
  targetCell?: string;    // ユーザー入力用のセル番号 (例: "B12")
}

/**
 * パネルをまとめるグループ (Container Node)
 * フォルダ機能を提供します。
 */
export interface PlanGroup {
  id: string;
  type: 'group';
  title: string;
  description?: string;
  children: PlanItem[];   // グループ内のアイテムリスト
  isCollapsed?: boolean;  // UI上の開閉状態
}

/**
 * リスト内で扱う要素のユニオン型
 */
export type PlanNode = PlanItem | PlanGroup;

/**
 * 全体の構造定義 (Stateとして保持する型)
 */
export type PlanStructure = PlanNode[];