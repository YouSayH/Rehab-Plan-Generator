// frontend/src/features/dashboard/PlanContext.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { PlanRead, PatientExtractionData, PlanStructure, stringifyCellAddress, CELL_MAPPING } from '../../api/types';


// デフォルトのパネル設定（階層構造）
const DEFAULT_PLAN_STRUCTURE: PlanStructure = [
  { 
    id: 'c1', 
    type: 'item',
    title: '現状評価（リスク・禁忌）', 
    description: 'バイタル、リスク管理、痛みの状態を生成',
    prompt: `患者データに基づき、現状の問題点、リスク管理事項、禁忌事項を箇条書きでまとめてください。
【制約事項】
・マークダウン記法（**太字**や##見出し等）は使用しないでください。
・箇条書きの行頭文字は「・」を使用してください。
・スプレッドシートのセルに見やすく表示できるプレーンテキスト形式で出力してください。`,
    targetKey: 'main_risks_txt',
    targetCell: stringifyCellAddress(CELL_MAPPING['main_risks_txt']) // "B18"
  },
  { 
    id: 'c2', 
    type: 'item',
    title: '目標設定（短期）', 
    description: 'FIM予測に基づいた短期SMARTゴール',
    prompt: `患者の現在のADL能力と予後予測に基づき、1ヶ月後の短期目標をSMARTの法則に従って3つ提案してください。
【制約事項】
・マークダウン記法は使用せず、プレーンテキストで出力してください。
・各目標の文頭は「・」としてください。`,
    targetKey: 'goals_1_month_txt',
    targetCell: stringifyCellAddress(CELL_MAPPING['goals_1_month_txt']) // "B12"
  },
  { 
    id: 'c3', 
    type: 'item',
    title: '治療方針', 
    description: '具体的な訓練内容と頻度',
    prompt: `目標達成に向けた具体的なリハビリテーション治療プログラム、頻度、留意点を提案してください。
【制約事項】
・マークダウン記法は使用せず、シンプルなテキスト形式にしてください。
・項目等は隅付き括弧【 】などで区切り、視認性を高めてください。`,
    targetKey: 'policy_content_txt',
    targetCell: stringifyCellAddress(CELL_MAPPING['policy_content_txt']) // "B16"
  },
];

// ローカルストレージのキー定数
const STORAGE_KEY_PLAN_STRUCTURE = 'rehab_app_plan_structure';
const STORAGE_KEY_NAME_MAP = 'rehab_app_patient_name_map';

interface PlanContextType {
  // 生成結果の計画書
  currentPlan: PlanRead | null;
  setCurrentPlan: (plan: PlanRead) => void;

  patientData: PatientExtractionData | null;
  setPatientData: (data: PatientExtractionData) => void;

  // 生成中フラグ
  isGenerating: boolean;
  setIsGenerating: (state: boolean) => void;

  // パネル構造管理 (階層構造対応)
  planStructure: PlanStructure;
  setPlanStructure: (structure: PlanStructure) => void;
  
  // 設定のリセット・保存
  resetPlanStructure: () => void;
  saveStructureToStorage: () => void;

  // プライバシー保護対応（ハッシュIDと実名のマッピング）
  /**
   * ハッシュIDに対応する実名をブラウザ内に登録します。
   * (計画書生成開始時や、ファイルアップロード時に呼び出してください)
   */
  registerPatientName: (hashId: string, name: string) => void;

  /**
   * ハッシュIDから実名を取得します。
   * (ヘッダー表示時などに使用してください)
   */
  getPatientName: (hashId: string) => string | null;
}

const PlanContext = createContext<PlanContextType | undefined>(undefined);

export const PlanProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentPlan, setCurrentPlan] = useState<PlanRead | null>(null);
  const [patientData, setPatientData] = useState<PatientExtractionData | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  
  // パネル構造のState (初期値はデフォルト設定)
  const [planStructure, setPlanStructure] = useState<PlanStructure>(DEFAULT_PLAN_STRUCTURE);
  
  // 実名マッピング（メモリ上）
  const [nameMap, setNameMap] = useState<Record<string, string>>({});

  // 初期ロード時にLocalStorageから復元
  useEffect(() => {
    // 1. パネル構造の復元
    const savedConfig = localStorage.getItem(STORAGE_KEY_PLAN_STRUCTURE);
    if (savedConfig) {
      try {
        const parsed = JSON.parse(savedConfig);
        if (Array.isArray(parsed)) setPlanStructure(parsed);
      } catch (e) { console.error('Failed to load plan structure', e); }
    }

    // 2. 実名マッピングの復元
    const savedMap = localStorage.getItem(STORAGE_KEY_NAME_MAP);
    if (savedMap) {
      try {
        const parsed = JSON.parse(savedMap);
        setNameMap(parsed);
      } catch (e) { console.error('Failed to load name map', e); }
    }
  }, []);

  const saveStructureToStorage = () => {
    localStorage.setItem(STORAGE_KEY_PLAN_STRUCTURE, JSON.stringify(planStructure));
  };

  const resetPlanStructure = () => {
    if (window.confirm('パネル設定を初期状態に戻しますか？')) {
      setPlanStructure(DEFAULT_PLAN_STRUCTURE);
      localStorage.removeItem(STORAGE_KEY_PLAN_STRUCTURE);
      localStorage.removeItem('rehab_app_card_config'); // 旧設定削除
    }
  };

  // 実名マッピング管理ロジック
  const registerPatientName = (hashId: string, name: string) => {
    const newMap = { ...nameMap, [hashId]: name };
    setNameMap(newMap);
    localStorage.setItem(STORAGE_KEY_NAME_MAP, JSON.stringify(newMap));
  };

  const getPatientName = (hashId: string): string | null => {
    return nameMap[hashId] || null;
  };

  return (
    <PlanContext.Provider value={{ 
      currentPlan, setCurrentPlan, 
      patientData, setPatientData,
      isGenerating, setIsGenerating,
      planStructure, setPlanStructure, 
      resetPlanStructure, saveStructureToStorage,
      registerPatientName, getPatientName
    }}>
      {children}
    </PlanContext.Provider>
  );
};

export const usePlanContext = () => {
  const context = useContext(PlanContext);
  if (!context) {
    throw new Error('usePlanContext must be used within a PlanProvider');
  }
  return context;
};