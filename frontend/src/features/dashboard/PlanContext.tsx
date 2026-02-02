import React, { createContext, useContext, useState, ReactNode } from 'react';
import { PlanRead } from '../../api/types';

interface PlanContextType {
  currentPlan: PlanRead | null;
  setCurrentPlan: (plan: PlanRead) => void;
  isGenerating: boolean;
  setIsGenerating: (state: boolean) => void;
}

const PlanContext = createContext<PlanContextType | undefined>(undefined);

export const PlanProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentPlan, setCurrentPlan] = useState<PlanRead | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  return (
    <PlanContext.Provider value={{ currentPlan, setCurrentPlan, isGenerating, setIsGenerating }}>
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