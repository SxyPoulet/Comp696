import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import type {
  Company,
  CompaniesListParams,
  DiscoveryRequest,
  ProfileRequest,
  IntelligenceRequest,
  ContentRequest,
} from '../types';

// Query keys
export const companyKeys = {
  all: ['companies'] as const,
  lists: () => [...companyKeys.all, 'list'] as const,
  list: (params: CompaniesListParams) => [...companyKeys.lists(), params] as const,
  details: () => [...companyKeys.all, 'detail'] as const,
  detail: (id: number) => [...companyKeys.details(), id] as const,
  contacts: (id: number) => [...companyKeys.detail(id), 'contacts'] as const,
  intelligence: (id: number) => [...companyKeys.detail(id), 'intelligence'] as const,
};

// List companies
export function useCompanies(params?: CompaniesListParams) {
  return useQuery({
    queryKey: companyKeys.list(params || {}),
    queryFn: () => api.getCompanies(params),
  });
}

// Get single company
export function useCompany(id: number) {
  return useQuery({
    queryKey: companyKeys.detail(id),
    queryFn: () => api.getCompany(id),
    enabled: !!id,
  });
}

// Get company contacts
export function useCompanyContacts(id: number, decisionMakersOnly = false) {
  return useQuery({
    queryKey: [...companyKeys.contacts(id), decisionMakersOnly],
    queryFn: () => api.getCompanyContacts(id, decisionMakersOnly),
    enabled: !!id,
  });
}

// Get company intelligence
export function useCompanyIntelligence(id: number) {
  return useQuery({
    queryKey: companyKeys.intelligence(id),
    queryFn: () => api.getCompanyIntelligence(id),
    enabled: !!id,
    retry: false, // Don't retry if intelligence doesn't exist yet
  });
}

// Create company
export function useCreateCompany() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (company: Partial<Company>) => api.createCompany(company),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: companyKeys.lists() });
    },
  });
}

// Update company
export function useUpdateCompany() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Company> }) =>
      api.updateCompany(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: companyKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: companyKeys.lists() });
    },
  });
}

// Delete company
export function useDeleteCompany() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => api.deleteCompany(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: companyKeys.lists() });
    },
  });
}

// Discover companies
export function useDiscoverCompanies() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: DiscoveryRequest) => api.discoverCompanies(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: companyKeys.lists() });
    },
  });
}

// Build profile
export function useBuildProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ProfileRequest) => api.buildProfile(request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: companyKeys.detail(variables.company_id) });
      queryClient.invalidateQueries({ queryKey: companyKeys.contacts(variables.company_id) });
    },
  });
}

// Analyze intelligence
export function useAnalyzeIntelligence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: IntelligenceRequest) => api.analyzeIntelligence(request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: companyKeys.intelligence(variables.company_id) });
    },
  });
}

// Generate content
export function useGenerateContent() {
  return useMutation({
    mutationFn: (request: ContentRequest) => api.generateContent(request),
  });
}

// Generate email only (faster)
export function useGenerateEmail() {
  return useMutation({
    mutationFn: (request: ContentRequest) => api.generateEmailOnly(request),
  });
}
