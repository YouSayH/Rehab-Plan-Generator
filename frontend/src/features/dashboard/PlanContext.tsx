// frontend/src/features/dashboard/PlanContext.tsx
import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { PlanRead, PatientExtractionData, PlanStructure, stringifyCellAddress, CELL_MAPPING, PatientRead, FieldConfigMap, FieldConfig } from '../../api/types';
import { ApiClient } from '../../api/client';

// 簡易的なDeep Cloneと削除関数
const deepClone = <T,>(obj: T): T => JSON.parse(JSON.stringify(obj));
const deleteValue = (obj: any, path: string) => {
  const parts = path.split('.');
  let current = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    if (!current[parts[i]]) return;
    current = current[parts[i]];
  }
  if (current && parts.length > 0) {
    delete current[parts[parts.length - 1]];
  }
};

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
const STORAGE_KEY_FIELD_CONFIG = 'rehab_app_field_config_v1';

interface PlanContextType {
  // 生成結果の計画書
  currentPlan: PlanRead | null;
  setCurrentPlan: (plan: PlanRead) => void;

  // 患者選択機能
  patientList: PatientRead[];
  currentHashId: string | null;
  setCurrentHashId: (hashId: string) => void;
  loadPatientList: () => Promise<void>;

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
  registerPatientName: (hashId: string, name: string) => void;
  getPatientName: (hashId: string) => string | null;

  // フィールド設定関連
  fieldConfigs: FieldConfigMap;
  updateFieldConfig: (path: string, diff: Partial<FieldConfig>) => void;
  getFilteredPatientData: () => PatientExtractionData | null;
}

const PlanContext = createContext<PlanContextType | undefined>(undefined);

export const PlanProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentPlan, setCurrentPlan] = useState<PlanRead | null>(null);
  const [patientData, setPatientData] = useState<PatientExtractionData | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // 患者リストと選択IDのState
  const [patientList, setPatientList] = useState<PatientRead[]>([]);
  const [currentHashId, setCurrentHashId] = useState<string | null>(null);
  
  // 患者リスト取得関数 (useCallbackでメモ化)
  // currentHashIdの更新ロジックを含むため、依存配列は空にして内部でstate setterを使用
  const loadPatientList = useCallback(async () => {
    try {
      const list = await ApiClient.getPatients();
      setPatientList(list);
      // リストがあり、未選択なら先頭をデフォルト選択（任意）
      // Stateの更新関数内で現在の値を確認して更新する
      // 関数アップデートを使って currentHashId への依存を排除（初期選択ロジック）
      setCurrentHashId(prev => {
        if (list.length > 0 && !prev) {
          return list[0].hash_id;
        }
        return prev;
      });
    } catch (e) {
      console.error("Failed to load patient list", e);
    }
  }, []);

// パネル構造のState (初期値はデフォルト設定)
  const [planStructure, setPlanStructure] = useState<PlanStructure>(DEFAULT_PLAN_STRUCTURE);
  
  // 実名マッピング（メモリ上）
  const [nameMap, setNameMap] = useState<Record<string, string>>({});

  // フィールド設定の状態
  const [fieldConfigs, setFieldConfigs] = useState<FieldConfigMap>({});

  // 初期ロード時にLocalStorageから復元
  useEffect(() => {
    // 初回マウント時に患者リストを取得
    loadPatientList();

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

    // 3. フィールド設定の復元
    const savedFieldConfig = localStorage.getItem(STORAGE_KEY_FIELD_CONFIG);
    if (savedFieldConfig) {
      try {
        setFieldConfigs(JSON.parse(savedFieldConfig));
      } catch (e) { console.error('Failed to load field config', e); }
    }
  }, [loadPatientList]); // loadPatientListを依存に追加

  const saveStructureToStorage = useCallback(() => {
    localStorage.setItem(STORAGE_KEY_PLAN_STRUCTURE, JSON.stringify(planStructure));
    localStorage.setItem(STORAGE_KEY_FIELD_CONFIG, JSON.stringify(fieldConfigs)); // 設定も保存
  }, [planStructure, fieldConfigs]);

  const resetPlanStructure = useCallback(() => {
    if (window.confirm('パネル設定を初期状態に戻しますか？')) {
      setPlanStructure(DEFAULT_PLAN_STRUCTURE);
      localStorage.removeItem(STORAGE_KEY_PLAN_STRUCTURE);
      localStorage.removeItem('rehab_app_card_config'); // 旧設定削除
    }
  }, []);

  // 実名マッピング管理ロジック (useCallbackでメモ化 + 関数型更新)
  // nameMapを依存配列から外すことで、この関数の参照を安定させる（無限ループ防止の要）
  const registerPatientName = useCallback((hashId: string, name: string) => {
    setNameMap(prev => {
      // 変更がない場合は更新しない（無駄なレンダリング防止）
      if (prev[hashId] === name) return prev;
      
      const newMap = { ...prev, [hashId]: name };
      localStorage.setItem(STORAGE_KEY_NAME_MAP, JSON.stringify(newMap));
      return newMap;
    });
  }, []); // 依存配列は空！

const getPatientName = useCallback((hashId: string): string | null => {
    return nameMap[hashId] || null;
  }, [nameMap]); // nameMapが変わった時のみ再生成

  // フィールド設定更新関数
  const updateFieldConfig = useCallback((path: string, diff: Partial<FieldConfig>) => {
    setFieldConfigs(prev => {
      const current = prev[path] || { 
        path, 
        targetCell: '', 
        format: 'text', 
        includeInPrompt: true 
      };
      const updated = { ...current, ...diff };
      return { ...prev, [path]: updated };
    });
  }, []);

  // フィルタリングされたPatientDataを取得する関数
  // includeInPromptがfalseの項目を削除して返します
  const getFilteredPatientData = useCallback((): PatientExtractionData | null => {
    if (!patientData) return null;
    
    // データ自体がない場合はnull
    if (Object.keys(fieldConfigs).length === 0) return patientData;

    const filtered = deepClone(patientData);

    // 設定をループして、includeInPromptがfalseのものを削除
    Object.keys(fieldConfigs).forEach(path => {
      const config = fieldConfigs[path];
      if (config.includeInPrompt === false) {
        deleteValue(filtered, path);
      }
    });

    return filtered;
  }, [patientData, fieldConfigs]);

  return (
    <PlanContext.Provider value={{ 
      currentPlan, setCurrentPlan, 
      patientData, setPatientData,
      isGenerating, setIsGenerating,
      planStructure, setPlanStructure, 
      resetPlanStructure, saveStructureToStorage,
      registerPatientName, getPatientName,
      patientList, currentHashId,
      setCurrentHashId, loadPatientList,
      fieldConfigs, updateFieldConfig, getFilteredPatientData
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