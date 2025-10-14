import axios, { type AxiosInstance } from 'axios';
import type {
  Company,
  Contact,
  Intelligence,
  DiscoveryRequest,
  DiscoveryResponse,
  ProfileRequest,
  ProfileResponse,
  IntelligenceRequest,
  IntelligenceResponse,
  ContentRequest,
  ContentResponse,
  TaskStatus,
  PaginatedResponse,
  CompaniesListParams,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 300000, // 5 minutes for long-running operations
    });

    // Request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('[API Error]', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Company endpoints
  async getCompanies(params?: CompaniesListParams): Promise<PaginatedResponse<Company>> {
    const response = await this.client.get('/companies', { params });
    return {
      total: response.data.total,
      page: response.data.page,
      page_size: response.data.page_size,
      data: response.data.companies,
    };
  }

  async getCompany(id: number): Promise<Company> {
    const response = await this.client.get(`/companies/${id}`);
    return response.data;
  }

  async createCompany(company: Partial<Company>): Promise<Company> {
    const response = await this.client.post('/companies', company);
    return response.data;
  }

  async updateCompany(id: number, company: Partial<Company>): Promise<Company> {
    const response = await this.client.put(`/companies/${id}`, company);
    return response.data;
  }

  async deleteCompany(id: number): Promise<void> {
    await this.client.delete(`/companies/${id}`);
  }

  async getCompanyContacts(id: number, decisionMakersOnly = false): Promise<Contact[]> {
    const response = await this.client.get(`/companies/${id}/contacts`, {
      params: { decision_makers_only: decisionMakersOnly },
    });
    return response.data;
  }

  async getCompanyIntelligence(id: number): Promise<Intelligence> {
    const response = await this.client.get(`/companies/${id}/intelligence`);
    return response.data;
  }

  // Discovery endpoints
  async discoverCompanies(request: DiscoveryRequest): Promise<DiscoveryResponse> {
    const response = await this.client.post('/discover/sync', request);
    return response.data;
  }

  async discoverCompaniesAsync(request: DiscoveryRequest): Promise<TaskStatus> {
    const response = await this.client.post('/discover', request);
    return response.data;
  }

  // Profile endpoints
  async buildProfile(request: ProfileRequest): Promise<ProfileResponse> {
    const response = await this.client.post('/profiles/sync', request);
    return response.data;
  }

  async buildProfileAsync(request: ProfileRequest): Promise<TaskStatus> {
    const response = await this.client.post('/profiles', request);
    return response.data;
  }

  // Intelligence endpoints
  async analyzeIntelligence(request: IntelligenceRequest): Promise<IntelligenceResponse> {
    const response = await this.client.post('/intelligence/sync', request);
    return response.data;
  }

  async analyzeIntelligenceAsync(request: IntelligenceRequest): Promise<TaskStatus> {
    const response = await this.client.post('/intelligence', request);
    return response.data;
  }

  // Content generation endpoints
  async generateContent(request: ContentRequest): Promise<ContentResponse> {
    const response = await this.client.post('/content/sync', request);
    return response.data;
  }

  async generateContentAsync(request: ContentRequest): Promise<TaskStatus> {
    const response = await this.client.post('/content', request);
    return response.data;
  }

  async generateEmailOnly(request: ContentRequest): Promise<{ subject: string; body: string; cta: string }> {
    const response = await this.client.post('/content/email-only', request);
    return response.data;
  }

  // Task endpoints
  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    const response = await this.client.get(`/tasks/${taskId}`);
    return response.data;
  }

  async cancelTask(taskId: string): Promise<void> {
    await this.client.delete(`/tasks/${taskId}`);
  }

  // Health check
  async checkHealth(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const api = new ApiService();
export default api;
