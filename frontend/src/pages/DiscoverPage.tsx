import { useState } from 'react';
import { useDiscoverCompanies, useCreateCompany } from '../hooks/useCompanies';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import CompanyCard from '../components/CompanyCard';
import { Search, Filter } from 'lucide-react';
import type { DiscoveryCriteria, Company } from '../types';

export default function DiscoverPage() {
  const [criteria, setCriteria] = useState<DiscoveryCriteria>({
    industry: '',
    location: '',
    size: '',
    keywords: '',
    max_results: 10,
  });

  const { mutate: discover, data, isPending, error, reset } = useDiscoverCompanies();
  const createCompany = useCreateCompany();

  const handleSaveCompany = async (company: Company) => {
    createCompany.mutate({
      name: company.name,
      domain: company.domain,
      industry: company.industry,
      size: company.size,
      employee_count: company.employee_count,
      location: company.location,
      description: company.description,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    discover({
      criteria,
      include_scoring: true,
    });
  };

  const handleReset = () => {
    setCriteria({
      industry: '',
      location: '',
      size: '',
      keywords: '',
      max_results: 10,
    });
    reset();
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Discover Companies</h1>
        <p className="mt-2 text-gray-600">
          Search for and qualify potential prospects using AI
        </p>
      </div>

      {/* Search Form */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <Filter className="h-5 w-5 text-gray-500" />
          <h2 className="text-lg font-semibold text-gray-900">Search Criteria</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Industry */}
            <div>
              <label className="label">Industry</label>
              <input
                type="text"
                value={criteria.industry}
                onChange={(e) => setCriteria({ ...criteria, industry: e.target.value })}
                placeholder="e.g., AI/ML, SaaS, FinTech"
                className="input"
              />
              <p className="mt-1 text-xs text-gray-500">Target industry or sector</p>
            </div>

            {/* Location */}
            <div>
              <label className="label">Location</label>
              <input
                type="text"
                value={criteria.location}
                onChange={(e) => setCriteria({ ...criteria, location: e.target.value })}
                placeholder="e.g., San Francisco, New York"
                className="input"
              />
              <p className="mt-1 text-xs text-gray-500">City or region</p>
            </div>

            {/* Company Size */}
            <div>
              <label className="label">Company Size</label>
              <select
                value={criteria.size}
                onChange={(e) => setCriteria({ ...criteria, size: e.target.value })}
                className="input"
              >
                <option value="">Any size</option>
                <option value="1-10">1-10 employees</option>
                <option value="11-50">11-50 employees</option>
                <option value="51-200">51-200 employees</option>
                <option value="201-500">201-500 employees</option>
                <option value="501-1000">501-1000 employees</option>
                <option value="1001+">1001+ employees</option>
              </select>
              <p className="mt-1 text-xs text-gray-500">Filter by employee count</p>
            </div>

            {/* Max Results */}
            <div>
              <label className="label">Max Results</label>
              <input
                type="number"
                min="1"
                max="50"
                value={criteria.max_results}
                onChange={(e) => setCriteria({ ...criteria, max_results: parseInt(e.target.value) || 10 })}
                className="input"
              />
              <p className="mt-1 text-xs text-gray-500">Number of companies to find (1-50)</p>
            </div>
          </div>

          {/* Keywords */}
          <div>
            <label className="label">Keywords</label>
            <textarea
              value={criteria.keywords}
              onChange={(e) => setCriteria({ ...criteria, keywords: e.target.value })}
              placeholder="e.g., machine learning, cloud infrastructure, B2B SaaS"
              rows={3}
              className="input"
            />
            <p className="mt-1 text-xs text-gray-500">
              Keywords to search for in company descriptions and profiles
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-4">
            <button
              type="submit"
              disabled={isPending}
              className="btn-primary flex items-center space-x-2"
            >
              <Search className="h-5 w-5" />
              <span>{isPending ? 'Searching...' : 'Search Companies'}</span>
            </button>

            <button
              type="button"
              onClick={handleReset}
              className="btn-outline"
              disabled={isPending}
            >
              Reset
            </button>
          </div>
        </form>
      </div>

      {/* Loading State */}
      {isPending && (
        <LoadingSpinner text="Discovering companies... This may take a moment." />
      )}

      {/* Error State */}
      {error && (
        <ErrorMessage
          title="Discovery Failed"
          message={error.message || 'Failed to discover companies. Please try again.'}
          onRetry={() => discover({ criteria, include_scoring: true })}
        />
      )}

      {/* Results */}
      {data && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Results</h2>
              <p className="text-sm text-gray-600 mt-1">
                Found {data.total_found} companies matching your criteria
              </p>
            </div>
          </div>

          {data.companies.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-gray-600">
                No companies found matching your criteria. Try adjusting your search parameters.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {data.companies.map((company, index) => (
                <CompanyCard
                  key={index}
                  company={company}
                  onSave={handleSaveCompany}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
