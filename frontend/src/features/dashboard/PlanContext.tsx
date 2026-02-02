import React, { createContext, useContext, useState, ReactNode } from 'react';
import { PlanRead, PatientExtractionData } from '../../api/types';

interface PlanContextType {
  // 生成結果の計画書
  currentPlan: PlanRead | null;
  setCurrentPlan: (plan: PlanRead) => void;

  patientData: PatientExtractionData | null;
  setPatientData: (data: PatientExtractionData) => void;

  // 生成中フラグ
  isGenerating: boolean;
  setIsGenerating: (state: boolean) => void;
}

const PlanContext = createContext<PlanContextType | undefined>(undefined);

export const PlanProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentPlan, setCurrentPlan] = useState<PlanRead | null>(null);
  
  const [patientData, setPatientData] = useState<PatientExtractionData | null>(null);
  
  const [isGenerating, setIsGenerating] = useState(false);

  return (
    <PlanContext.Provider value={{ 
      currentPlan, setCurrentPlan, 
      patientData, setPatientData,
      isGenerating, setIsGenerating 
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