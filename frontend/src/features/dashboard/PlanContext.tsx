import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { PlanRead, PatientExtractionData, CardConfig, stringifyCellAddress, CELL_MAPPING } from '../../api/types';

// デフォルトのカード設定
const DEFAULT_CARDS: CardConfig[] = [
  { 
    id: 'c1', 
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

interface PlanContextType {
  // 生成結果の計画書
  currentPlan: PlanRead | null;
  setCurrentPlan: (plan: PlanRead) => void;

  patientData: PatientExtractionData | null;
  setPatientData: (data: PatientExtractionData) => void;

  // 生成中フラグ
  isGenerating: boolean;
  setIsGenerating: (state: boolean) => void;

  // カード設定管理
  cards: CardConfig[];
  setCards: (cards: CardConfig[]) => void;
  resetCards: () => void;
  saveCardsToStorage: () => void;
}

const PlanContext = createContext<PlanContextType | undefined>(undefined);

export const PlanProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentPlan, setCurrentPlan] = useState<PlanRead | null>(null);
  const [patientData, setPatientData] = useState<PatientExtractionData | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  
  // カード設定のState
  const [cards, setCards] = useState<CardConfig[]>(DEFAULT_CARDS);

  // 初期ロード時にLocalStorageから復元
  useEffect(() => {
    const savedCards = localStorage.getItem('rehab_app_card_config');
    if (savedCards) {
      try {
        setCards(JSON.parse(savedCards));
      } catch (e) {
        console.error('Failed to load card config', e);
      }
    }
  }, []);

  const saveCardsToStorage = () => {
    localStorage.setItem('rehab_app_card_config', JSON.stringify(cards));
  };

  const resetCards = () => {
    setCards(DEFAULT_CARDS);
    localStorage.removeItem('rehab_app_card_config');
  };

  return (
    <PlanContext.Provider value={{ 
      currentPlan, setCurrentPlan, 
      patientData, setPatientData,
      isGenerating, setIsGenerating,
      cards, setCards, resetCards, saveCardsToStorage
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