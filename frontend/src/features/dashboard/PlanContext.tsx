import React, { createContext, useContext, useState, ReactNode } from 'react';

interface PlanContextType {
  selectedPatientId: string | null;
  setSelectedPatientId: (id: string | null) => void;
  isRightPanelOpen: boolean;
  toggleRightPanel: () => void;
}

const PlanContext = createContext<PlanContextType | undefined>(undefined);

export const PlanProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [isRightPanelOpen, setIsRightPanelOpen] = useState(true);

  const toggleRightPanel = () => setIsRightPanelOpen(prev => !prev);

  return (
    <PlanContext.Provider value={{
      selectedPatientId,
      setSelectedPatientId,
      isRightPanelOpen,
      toggleRightPanel
    }}>
      {children}
    </PlanContext.Provider>
  );
};

export const usePlanContext = () => {
  const context = useContext(PlanContext);
  if (context === undefined) {
    throw new Error('usePlanContext must be used within a PlanProvider');
  }
  return context;
};