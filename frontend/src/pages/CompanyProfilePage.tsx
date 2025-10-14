import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import {
  useCompany,
  useCompanyContacts,
  useCompanyIntelligence,
  useBuildProfile,
  useAnalyzeIntelligence
} from '../hooks/useCompanies';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import {
  Building2,
  MapPin,
  Users,
  Globe,
  Linkedin,
  Mail,
  Phone,
  TrendingUp,
  Brain,
  FileText,
  ArrowLeft,
  RefreshCw
} from 'lucide-react';

export default function CompanyProfilePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const companyId = parseInt(id || '0');

  const [activeTab, setActiveTab] = useState<'overview' | 'contacts' | 'intelligence'>('overview');

  // Check if we have a valid company ID
  if (!id || isNaN(companyId) || companyId === 0) {
    return (
      <ErrorMessage
        title="Invalid Company"
        message="This company hasn't been saved yet. Please save the company from the discovery page first."
        onRetry={() => navigate('/discover')}
      />
    );
  }

  const { data: company, isLoading, error, refetch } = useCompany(companyId);
  const { data: contacts, isLoading: contactsLoading } = useCompanyContacts(companyId);
  const { data: intelligence, isLoading: intelligenceLoading, error: intelligenceError } = useCompanyIntelligence(companyId);

  const buildProfile = useBuildProfile();
  const analyzeIntelligence = useAnalyzeIntelligence();

  if (isLoading) return <LoadingSpinner text="Loading company profile..." />;
  if (error || !company) return <ErrorMessage message="Failed to load company" onRetry={() => refetch()} />;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'discovered': return 'bg-blue-100 text-blue-800';
      case 'profiling': return 'bg-yellow-100 text-yellow-800';
      case 'analyzed': return 'bg-green-100 text-green-800';
      case 'contacted': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleBuildProfile = () => {
    buildProfile.mutate({
      company_id: companyId,
      include_contacts: true,
      use_cache: true,
    });
  };

  const handleAnalyze = () => {
    analyzeIntelligence.mutate({
      company_id: companyId,
      force_refresh: false,
    });
  };

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button onClick={() => navigate('/companies')} className="btn-outline flex items-center space-x-2">
        <ArrowLeft className="h-4 w-4" />
        <span>Back to Companies</span>
      </button>

      {/* Header */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4 flex-1">
            <div className="p-3 bg-primary-100 rounded-lg">
              <Building2 className="h-10 w-10 text-primary-600" />
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-3">
                <h1 className="text-3xl font-bold text-gray-900">{company.name}</h1>
                {company.status && (
                  <span className={`badge ${getStatusColor(company.status)}`}>
                    {company.status}
                  </span>
                )}
              </div>
              <p className="mt-1 text-gray-600">{company.domain}</p>

              <div className="mt-4 flex flex-wrap gap-4 text-sm text-gray-600">
                {company.industry && (
                  <div className="flex items-center space-x-1">
                    <Building2 className="h-4 w-4" />
                    <span>{company.industry}</span>
                  </div>
                )}
                {company.location && (
                  <div className="flex items-center space-x-1">
                    <MapPin className="h-4 w-4" />
                    <span>{company.location}</span>
                  </div>
                )}
                {company.employee_count && (
                  <div className="flex items-center space-x-1">
                    <Users className="h-4 w-4" />
                    <span>{company.employee_count} employees</span>
                  </div>
                )}
              </div>

              {company.website && (
                <div className="mt-3 flex space-x-4">
                  {company.website && (
                    <a
                      href={company.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary-600 hover:text-primary-700 flex items-center space-x-1"
                    >
                      <Globe className="h-4 w-4" />
                      <span>Website</span>
                    </a>
                  )}
                  {company.linkedin_url && (
                    <a
                      href={company.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary-600 hover:text-primary-700 flex items-center space-x-1"
                    >
                      <Linkedin className="h-4 w-4" />
                      <span>LinkedIn</span>
                    </a>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-col items-end space-y-3 ml-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-gray-400" />
              <div className="text-right">
                <div className="text-sm text-gray-600">Lead Score</div>
                <div className="text-2xl font-bold text-primary-600">
                  {company.lead_score?.toFixed(0) || 'N/A'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {company.description && (
          <p className="mt-6 text-gray-700 leading-relaxed">{company.description}</p>
        )}

        {/* Actions */}
        <div className="mt-6 flex space-x-3">
          <button
            onClick={handleBuildProfile}
            disabled={buildProfile.isPending}
            className="btn-primary flex items-center space-x-2"
          >
            <RefreshCw className={`h-4 w-4 ${buildProfile.isPending ? 'animate-spin' : ''}`} />
            <span>{buildProfile.isPending ? 'Building...' : 'Build Profile'}</span>
          </button>

          <button
            onClick={handleAnalyze}
            disabled={analyzeIntelligence.isPending}
            className="btn-outline flex items-center space-x-2"
          >
            <Brain className={`h-4 w-4 ${analyzeIntelligence.isPending ? 'animate-spin' : ''}`} />
            <span>{analyzeIntelligence.isPending ? 'Analyzing...' : 'Analyze Intelligence'}</span>
          </button>

          <button
            onClick={() => navigate(`/content?company=${companyId}`)}
            className="btn-outline flex items-center space-x-2"
          >
            <FileText className="h-4 w-4" />
            <span>Generate Content</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex space-x-8">
          {['overview', 'contacts', 'intelligence'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as typeof activeTab)}
              className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Company Overview</h2>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-600">Domain</p>
                <p className="mt-1 text-gray-900">{company.domain}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Industry</p>
                <p className="mt-1 text-gray-900">{company.industry || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Size</p>
                <p className="mt-1 text-gray-900">{company.size || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Employee Count</p>
                <p className="mt-1 text-gray-900">{company.employee_count || 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'contacts' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Contacts</h2>
          {contactsLoading ? (
            <LoadingSpinner size="sm" text="Loading contacts..." />
          ) : !contacts || contacts.length === 0 ? (
            <p className="text-gray-600 text-center py-8">
              No contacts found. Build profile to discover contacts.
            </p>
          ) : (
            <div className="space-y-4">
              {contacts.map((contact) => (
                <div key={contact.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <h3 className="font-semibold text-gray-900">{contact.name}</h3>
                        {contact.is_decision_maker && (
                          <span className="badge badge-success">Decision Maker</span>
                        )}
                      </div>
                      {contact.title && (
                        <p className="text-sm text-gray-600 mt-1">{contact.title}</p>
                      )}
                      <div className="mt-2 space-y-1">
                        {contact.email && (
                          <div className="flex items-center space-x-2 text-sm text-gray-600">
                            <Mail className="h-4 w-4" />
                            <a href={`mailto:${contact.email}`} className="hover:text-primary-600">
                              {contact.email}
                            </a>
                          </div>
                        )}
                        {contact.phone && (
                          <div className="flex items-center space-x-2 text-sm text-gray-600">
                            <Phone className="h-4 w-4" />
                            <span>{contact.phone}</span>
                          </div>
                        )}
                        {contact.linkedin_url && (
                          <div className="flex items-center space-x-2 text-sm text-gray-600">
                            <Linkedin className="h-4 w-4" />
                            <a
                              href={contact.linkedin_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="hover:text-primary-600"
                            >
                              LinkedIn Profile
                            </a>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'intelligence' && (
        <div className="space-y-6">
          {intelligenceLoading ? (
            <LoadingSpinner text="Loading intelligence..." />
          ) : intelligenceError ? (
            <div className="card text-center py-8">
              <p className="text-gray-600 mb-4">
                No intelligence analysis available yet.
              </p>
              <button onClick={handleAnalyze} className="btn-primary">
                Analyze Now
              </button>
            </div>
          ) : intelligence ? (
            <>
              {/* Summary */}
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Executive Summary</h2>
                <p className="text-gray-700 leading-relaxed">{intelligence.summary}</p>
                <div className="mt-4 flex items-center space-x-2 text-sm">
                  <span className="text-gray-600">Confidence Score:</span>
                  <span className="font-semibold text-primary-600">
                    {(intelligence.confidence_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              {/* Pain Points */}
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Pain Points</h2>
                <div className="space-y-4">
                  {intelligence.pain_points.map((pp, index) => (
                    <div key={index} className="border-l-4 border-red-400 pl-4">
                      <h3 className="font-medium text-gray-900">{pp.pain_point}</h3>
                      <p className="text-sm text-gray-600 mt-1">{pp.reasoning}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        <span className="font-medium">Impact:</span> {pp.impact}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Priorities */}
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Business Priorities</h2>
                <div className="space-y-4">
                  {intelligence.priorities.map((priority, index) => (
                    <div key={index} className="border-l-4 border-blue-400 pl-4">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-medium text-gray-900">{priority.priority}</h3>
                        <span className={`badge ${
                          priority.urgency_level === 'high' ? 'badge-danger' :
                          priority.urgency_level === 'medium' ? 'badge-warning' :
                          'badge-info'
                        }`}>
                          {priority.urgency_level} urgency
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{priority.reasoning}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Approach Strategy */}
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Recommended Approach</h2>
                <p className="text-gray-700 leading-relaxed">{intelligence.approach_strategy}</p>
              </div>
            </>
          ) : null}
        </div>
      )}
    </div>
  );
}
