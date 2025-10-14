// Company Types
export interface Company {
  id?: number; // Optional for discovered companies not yet saved
  name: string;
  domain: string;
  industry?: string;
  size?: string;
  employee_count?: number;
  location?: string;
  description?: string;
  website?: string;
  linkedin_url?: string;
  lead_score: number;
  status?: 'discovered' | 'profiling' | 'analyzed' | 'contacted';
  tech_stack?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
  contacts?: Contact[];
}

export interface Contact {
  id: number;
  company_id: number;
  name: string;
  title?: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
  department?: string;
  seniority_level?: string;
  is_decision_maker: boolean;
  notes?: string;
}

export interface Intelligence {
  id: number;
  company_id: number;
  summary: string;
  pain_points: PainPoint[];
  priorities: Priority[];
  approach_strategy: string;
  confidence_score: number;
  generated_at: string;
}

export interface PainPoint {
  pain_point: string;
  reasoning: string;
  impact: string;
}

export interface Priority {
  priority: string;
  reasoning: string;
  urgency_level: 'low' | 'medium' | 'high';
}

export interface SearchHistory {
  id: number;
  query: string;
  filters: Record<string, any>;
  results_count: number;
  created_at: string;
}

// API Request/Response Types
export interface DiscoveryCriteria {
  industry?: string;
  location?: string;
  size?: string;
  keywords?: string;
  max_results?: number;
}

export interface DiscoveryRequest {
  criteria: DiscoveryCriteria;
  include_scoring?: boolean;
}

export interface DiscoveryResponse {
  total_found: number;
  companies: Company[];
  search_criteria: DiscoveryCriteria;
}

export interface ProfileRequest {
  company_id: number;
  include_contacts?: boolean;
  use_cache?: boolean;
}

export interface ProfileResponse {
  company_id: number;
  status: string;
  lead_score: number;
  contacts_found: number;
  contacts_saved: number;
  sources_used: string[];
  profile: Company;
}

export interface IntelligenceRequest {
  company_id: number;
  force_refresh?: boolean;
}

export interface IntelligenceResponse {
  company_id: number;
  status: string;
  intelligence: Intelligence;
}

export interface ContentRequest {
  company_id: number;
  contact_id?: number;
  contact_name?: string;
  contact_title?: string;
  product_description: string;
  tone?: string;
  include_variants?: boolean;
}

export interface ContentResponse {
  company_id: number;
  email: {
    subject: string;
    body: string;
    cta: string;
  };
  conversation_starters: {
    linkedin_message: string;
    email_subject: string;
    phone_opener: string;
    connection_request: string;
    followup_subject: string;
  };
  variants?: {
    version_a: any;
    version_b: any;
  };
  generated_at: string;
}

export interface TaskStatus {
  task_id: string;
  status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | 'PROGRESS';
  result?: any;
  error?: string;
  progress?: number;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  data: T[];
}

export interface CompaniesListParams {
  page?: number;
  page_size?: number;
  status?: string;
  industry?: string;
  min_score?: number;
}
