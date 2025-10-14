import { useState } from 'react';
import { useCompanies } from '../hooks/useCompanies';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import CompanyCard from '../components/CompanyCard';
import { Filter, Plus } from 'lucide-react';
import type { CompaniesListParams } from '../types';

export default function CompaniesPage() {
  const [filters, setFilters] = useState<CompaniesListParams>({
    page: 1,
    page_size: 20,
    status: '',
    industry: '',
    min_score: undefined,
  });

  const { data, isLoading, error, refetch } = useCompanies(filters);

  const handleFilterChange = (key: keyof CompaniesListParams, value: any) => {
    setFilters({ ...filters, [key]: value, page: 1 });
  };

  const handlePageChange = (newPage: number) => {
    setFilters({ ...filters, page: newPage });
  };

  if (isLoading) return <LoadingSpinner text="Loading companies..." />;
  if (error) return <ErrorMessage message="Failed to load companies" onRetry={() => refetch()} />;

  const totalPages = Math.ceil((data?.total || 0) / (filters.page_size || 20));

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Companies</h1>
          <p className="mt-2 text-gray-600">
            Manage and track all your prospect companies
          </p>
        </div>
        <button className="btn-primary flex items-center space-x-2">
          <Plus className="h-5 w-5" />
          <span>Add Company</span>
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="label">Status</label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="input"
            >
              <option value="">All statuses</option>
              <option value="discovered">Discovered</option>
              <option value="profiling">Profiling</option>
              <option value="analyzed">Analyzed</option>
              <option value="contacted">Contacted</option>
            </select>
          </div>

          <div>
            <label className="label">Industry</label>
            <input
              type="text"
              value={filters.industry}
              onChange={(e) => handleFilterChange('industry', e.target.value)}
              placeholder="Filter by industry"
              className="input"
            />
          </div>

          <div>
            <label className="label">Min Lead Score</label>
            <input
              type="number"
              min="0"
              max="100"
              value={filters.min_score || ''}
              onChange={(e) => handleFilterChange('min_score', e.target.value ? parseInt(e.target.value) : undefined)}
              placeholder="0-100"
              className="input"
            />
          </div>

          <div>
            <label className="label">Per Page</label>
            <select
              value={filters.page_size}
              onChange={(e) => handleFilterChange('page_size', parseInt(e.target.value))}
              className="input"
            >
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm text-gray-600">
            Showing {((filters.page || 1) - 1) * (filters.page_size || 20) + 1} to{' '}
            {Math.min((filters.page || 1) * (filters.page_size || 20), data?.total || 0)} of{' '}
            {data?.total || 0} companies
          </p>
        </div>

        {data?.data.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-600">No companies found. Try adjusting your filters.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data?.data.map((company) => (
              <CompanyCard key={company.id} company={company} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center space-x-2 mt-8">
            <button
              onClick={() => handlePageChange((filters.page || 1) - 1)}
              disabled={(filters.page || 1) === 1}
              className="btn-outline"
            >
              Previous
            </button>

            <div className="flex items-center space-x-1">
              {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                const page = i + 1;
                return (
                  <button
                    key={page}
                    onClick={() => handlePageChange(page)}
                    className={`px-3 py-1 rounded ${
                      page === (filters.page || 1)
                        ? 'bg-primary-600 text-white'
                        : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {page}
                  </button>
                );
              })}
            </div>

            <button
              onClick={() => handlePageChange((filters.page || 1) + 1)}
              disabled={(filters.page || 1) === totalPages}
              className="btn-outline"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
