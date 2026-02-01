import React from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import LeftPanel from './LeftPanel';
import RightPanel from './RightPanel';
import UniverSheet from './UniverSheet';
import { PlanProvider, usePlanContext } from './PlanContext';

const DashboardContent: React.FC = () => {
  const { isRightPanelOpen } = usePlanContext();

  return (
// styleに width: '100vw', height: '100vh', overflow: 'hidden' があるか確認
    <div style={{ height: '100vh', width: '100vw', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      
      {/* Header */}
      <header style={{ height: '48px', backgroundColor: '#1f2937', color: 'white', display: 'flex', alignItems: 'center', padding: '0 16px', flexShrink: 0 }}>
        <h1 style={{ fontSize: '1rem', fontWeight: 'bold' }}>Rehab Plan Generator (Phase 1)</h1>
      </header>

      {/* Main Content Area */}
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex' }}>
        <PanelGroup direction="horizontal">
          <Panel defaultSize={20} minSize={15} maxSize={30} style={{ overflow: 'hidden' }}>
            <LeftPanel />
          </Panel>
          <PanelResizeHandle style={{ width: '4px', backgroundColor: '#e5e7eb', cursor: 'col-resize' }} />
          <Panel minSize={30} style={{ overflow: 'hidden' }}>
            <UniverSheet />
          </Panel>
          {isRightPanelOpen && (
            <>
              <PanelResizeHandle style={{ width: '4px', backgroundColor: '#e5e7eb', cursor: 'col-resize' }} />
              <Panel defaultSize={25} minSize={20} maxSize={40} style={{ overflow: 'hidden' }}>
                <RightPanel />
              </Panel>
            </>
          )}
        </PanelGroup>
      </div>
    </div>
  );
};

const DashboardLayout: React.FC = () => {
  return (
    <PlanProvider>
      <DashboardContent />
    </PlanProvider>
  );
};

export default DashboardLayout;