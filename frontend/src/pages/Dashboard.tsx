import { useCompanies } from '../hooks/useCompanies';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import CompanyCard from '../components/CompanyCard';
import { Building2, TrendingUp, Users, CheckCircle } from 'lucide-react';

export default function Dashboard() {
  const { data: companies, isLoading, error, refetch } = useCompanies({ page_size: 50 });

  if (isLoading) return <LoadingSpinner text="Loading dashboard..." />;
  if (error) return <ErrorMessage message="Failed to load dashboard data" onRetry={() => refetch()} />;

  const stats = {
    total: companies?.total || 0,
    discovered: companies?.data.filter(c => c.status === 'discovered').length || 0,
    profiling: companies?.data.filter(c => c.status === 'profiling').length || 0,
    analyzed: companies?.data.filter(c => c.status === 'analyzed').length || 0,
    contacted: companies?.data.filter(c => c.status === 'contacted').length || 0,
    avgScore: companies?.data.length
      ? (companies.data.reduce((sum, c) => sum + c.lead_score, 0) / companies.data.length).toFixed(1)
      : '0',
  };

  const recentCompanies = companies?.data.slice(0, 6) || [];
  const highScoreCompanies = [...(companies?.data || [])]
    .sort((a, b) => b.lead_score - a.lead_score)
    .slice(0, 6);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Overview of your sales intelligence pipeline
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card bg-gradient-to-br from-blue-50 to-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Companies</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Building2 className="h-8 w-8 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-green-50 to-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Analyzed</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{stats.analyzed}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-yellow-50 to-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Lead Score</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{stats.avgScore}</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <TrendingUp className="h-8 w-8 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-50 to-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Contacted</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{stats.contacted}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Users className="h-8 w-8 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Pipeline Status */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Pipeline Status</h2>
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.discovered}</div>
            <div className="text-sm text-gray-600 mt-1">Discovered</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{stats.profiling}</div>
            <div className="text-sm text-gray-600 mt-1">Profiling</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{stats.analyzed}</div>
            <div className="text-sm text-gray-600 mt-1">Analyzed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{stats.contacted}</div>
            <div className="text-sm text-gray-600 mt-1">Contacted</div>
          </div>
        </div>
      </div>

      {/* Recent Companies */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Companies</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recentCompanies.map((company) => (
            <CompanyCard key={company.id} company={company} />
          ))}
        </div>
      </div>

      {/* High Score Companies */}
      {highScoreCompanies.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Prospects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {highScoreCompanies.map((company) => (
              <CompanyCard key={company.id} company={company} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
