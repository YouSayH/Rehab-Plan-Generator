import { PatientExtractionData, PlanRead } from './types';

// 環境に合わせてURLを変更してください
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const ApiClient = {
  // 計画書生成
  generatePlan: async (hashId: string, patientData: PatientExtractionData): Promise<PlanRead> => {
    const response = await fetch(`${API_BASE_URL}/plans/generate/${hashId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(patientData),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },

  getLatestState: async (hashId: string): Promise<PatientExtractionData> => {
    console.log(`[ApiClient] Fetching latest state for ${hashId}...`);
    const response = await fetch(`${API_BASE_URL}/patients/${hashId}/latest-state`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch patient data: ${response.statusText}`);
    }
    return response.json();
  }
};