import { PatientExtractionData, PlanRead, PatientRead } from './types';

// 環境に合わせてURLを変更してください
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const ApiClient = {
  getPatients: async (): Promise<PatientRead[]> => {
    const response = await fetch(`${API_BASE_URL}/patients/`);
    if (!response.ok) {
      throw new Error(`Failed to fetch patients: ${response.statusText}`);
    }
    return response.json();
  },
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

  // 計画書の新規作成 (空の計画書または初期データ付きを作成)
  createPlan: async (hashId: string, rawData: Record<string, any> = {}): Promise<PlanRead> => {
    const response = await fetch(`${API_BASE_URL}/plans/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        hash_id: hashId,
        raw_data: rawData
      }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },

  // カスタム部分生成
  generateCustom: async (
    patientData: PatientExtractionData, 
    prompt: string, 
    targetKey?: string,
    currentPlan?: Record<string, any>
  ): Promise<{ result: string }> => {
    const response = await fetch(`${API_BASE_URL}/plans/generate/custom`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        patient_data: patientData,
        prompt: prompt,
        target_key: targetKey,
        current_plan: currentPlan
      }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },

  // バッチ生成 (グループ単位の一括生成)
  generateBatch: async (
    patientData: PatientExtractionData, 
    items: { targetKey: string; prompt: string }[],
    currentPlan?: Record<string, any>
  ): Promise<Record<string, string>> => {
    
    // backendの期待する target_key (スネークケース) に変換
    const mappedItems = items.map(item => ({
      target_key: item.targetKey,
      prompt: item.prompt
    }));

    const response = await fetch(`${API_BASE_URL}/plans/generate/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        patient_data: patientData,
        items: mappedItems,
        current_plan: currentPlan
      }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },
  
  // 計画書の更新
  updatePlan: async (planId: number, rawData: Record<string, any>): Promise<PlanRead> => {
     const response = await fetch(`${API_BASE_URL}/plans/${planId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ raw_data: rawData }),
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