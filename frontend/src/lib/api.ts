import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface PropriedadeResponse {
  id: string;
  numero_car: string;
  municipio: string;
  uf: string;
  area_ha: number;
  status_sicar: string;
  poligono_geojson: Record<string, unknown>;
  dados_adicionais?: Record<string, unknown>;
}

export interface DiagnosticoResponse {
  id: string;
  tarefa_id: string;
  propriedade_id: string;
  risk_level: string;
  prodes_alerts: Record<string, unknown>[];
  deter_alerts: Record<string, unknown>[];
  problem_area_ha: number;
  llm_explanation?: string;
  problem_geojson?: Record<string, unknown>;
  prodes_date_used?: string;
  deter_date_used?: string;
  created_at: string;
}

export const fazendaOkApi = {
  // Propriedades
  buscarPropriedadePorCar: async (numero_car: string): Promise<PropriedadeResponse> => {
    const res = await api.post('/properties/buscar/car', { numero_car });
    return res.data;
  },
  buscarPropriedadePorCoordenadas: async (latitude: number, longitude: number): Promise<PropriedadeResponse> => {
    const res = await api.post('/properties/buscar/coordenadas', { latitude, longitude });
    return res.data;
  },

  // Diagnósticos
  gerarDiagnostico: async (propriedadeId: string) => {
    const res = await api.post(`/diagnostics/gerar/${propriedadeId}`);
    return res.data;
  },
  consultarStatusTarefa: async (tarefaId: string) => {
    const res = await api.get(`/diagnostics/status/${tarefaId}`);
    return res.data;
  },
  obterDiagnostico: async (diagnosticoId: string): Promise<DiagnosticoResponse> => {
    const res = await api.get(`/diagnostics/${diagnosticoId}`);
    return res.data;
  },
  obterHistorico: async (numero_car: string): Promise<DiagnosticoResponse[]> => {
    const res = await api.get(`/diagnostics/historico/${numero_car}`);
    return res.data;
  },

  // Fotos
  uploadFotos: async (formData: FormData) => {
    const res = await api.post('/fotos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },
};
