import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useCompanies, useGenerateContent } from '../hooks/useCompanies';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { FileText, Copy, Check, Sparkles } from 'lucide-react';
import type { ContentRequest } from '../types';

export default function ContentGenerationPage() {
  const [searchParams] = useSearchParams();
  const companyIdParam = searchParams.get('company');

  const [request, setRequest] = useState<ContentRequest>({
    company_id: companyIdParam ? parseInt(companyIdParam) : 0,
    contact_name: '',
    contact_title: '',
    product_description: '',
    tone: 'professional',
    include_variants: true,
  });

  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [activeVariant, setActiveVariant] = useState<'main' | 'version_a' | 'version_b'>('main');

  const { data: companies } = useCompanies({ page_size: 100 });
  const { mutate: generate, data, isPending, error, reset } = useGenerateContent();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (request.company_id && request.product_description) {
      generate(request);
    }
  };

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Content Generation</h1>
        <p className="mt-2 text-gray-600">
          Generate personalized outreach content powered by AI
        </p>
      </div>

      {/* Form */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-6">
          <Sparkles className="h-5 w-5 text-primary-600" />
          <h2 className="text-lg font-semibold text-gray-900">Generation Settings</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Company Selection */}
          <div>
            <label className="label">Company *</label>
            <select
              value={request.company_id}
              onChange={(e) => setRequest({ ...request, company_id: parseInt(e.target.value) })}
              className="input"
              required
            >
              <option value={0}>Select a company</option>
              {companies?.data.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.name} ({company.domain})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Contact Name */}
            <div>
              <label className="label">Contact Name</label>
              <input
                type="text"
                value={request.contact_name}
                onChange={(e) => setRequest({ ...request, contact_name: e.target.value })}
                placeholder="e.g., Jane Smith"
                className="input"
              />
              <p className="mt-1 text-xs text-gray-500">Optional: Personalize for specific contact</p>
            </div>

            {/* Contact Title */}
            <div>
              <label className="label">Contact Title</label>
              <input
                type="text"
                value={request.contact_title}
                onChange={(e) => setRequest({ ...request, contact_title: e.target.value })}
                placeholder="e.g., CTO, VP Engineering"
                className="input"
              />
              <p className="mt-1 text-xs text-gray-500">Optional: Contact's job title</p>
            </div>
          </div>

          {/* Product Description */}
          <div>
            <label className="label">Product/Service Description *</label>
            <textarea
              value={request.product_description}
              onChange={(e) => setRequest({ ...request, product_description: e.target.value })}
              placeholder="Describe your product or service that you want to pitch..."
              rows={4}
              className="input"
              required
            />
            <p className="mt-1 text-xs text-gray-500">
              Provide details about what you're offering and how it helps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Tone */}
            <div>
              <label className="label">Tone</label>
              <select
                value={request.tone}
                onChange={(e) => setRequest({ ...request, tone: e.target.value })}
                className="input"
              >
                <option value="professional">Professional</option>
                <option value="casual">Casual</option>
                <option value="friendly">Friendly</option>
                <option value="formal">Formal</option>
              </select>
            </div>

            {/* Include Variants */}
            <div className="flex items-center space-x-3 pt-6">
              <input
                type="checkbox"
                id="variants"
                checked={request.include_variants}
                onChange={(e) => setRequest({ ...request, include_variants: e.target.checked })}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="variants" className="text-sm text-gray-700">
                Generate A/B test variants
              </label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            <button
              type="submit"
              disabled={isPending || !request.company_id || !request.product_description}
              className="btn-primary flex items-center space-x-2"
            >
              <Sparkles className="h-5 w-5" />
              <span>{isPending ? 'Generating...' : 'Generate Content'}</span>
            </button>

            <button
              type="button"
              onClick={() => {
                setRequest({
                  ...request,
                  contact_name: '',
                  contact_title: '',
                  product_description: '',
                });
                reset();
              }}
              className="btn-outline"
              disabled={isPending}
            >
              Reset
            </button>
          </div>
        </form>
      </div>

      {/* Loading */}
      {isPending && (
        <LoadingSpinner text="Generating personalized content... This may take up to a minute." />
      )}

      {/* Error */}
      {error && (
        <ErrorMessage
          title="Generation Failed"
          message={error.message || 'Failed to generate content. Please try again.'}
          onRetry={() => generate(request)}
        />
      )}

      {/* Results */}
      {data && (
        <div className="space-y-6">
          {/* Variant Tabs */}
          {data.variants && (
            <div className="border-b border-gray-200">
              <div className="flex space-x-4">
                {['main', 'version_a', 'version_b'].map((variant) => (
                  <button
                    key={variant}
                    onClick={() => setActiveVariant(variant as typeof activeVariant)}
                    className={`pb-3 px-3 border-b-2 font-medium text-sm transition-colors ${
                      activeVariant === variant
                        ? 'border-primary-600 text-primary-600'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    {variant === 'main' ? 'Main Version' :
                     variant === 'version_a' ? 'Variant A' : 'Variant B'}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Email Content */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Email</h2>
              <button
                onClick={() => copyToClipboard(
                  `Subject: ${data.email.subject}\n\n${data.email.body}\n\n${data.email.cta}`,
                  'email'
                )}
                className="btn-outline flex items-center space-x-2"
              >
                {copiedField === 'email' ? (
                  <Check className="h-4 w-4 text-green-600" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
                <span>{copiedField === 'email' ? 'Copied!' : 'Copy Email'}</span>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Subject</label>
                <div className="mt-1 p-3 bg-gray-50 rounded-lg">
                  <p className="text-gray-900">{data.email.subject}</p>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Body</label>
                <div className="mt-1 p-4 bg-gray-50 rounded-lg">
                  <p className="text-gray-900 whitespace-pre-wrap leading-relaxed">
                    {data.email.body}
                  </p>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Call to Action</label>
                <div className="mt-1 p-3 bg-primary-50 rounded-lg">
                  <p className="text-gray-900">{data.email.cta}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Conversation Starters */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Multi-Channel Conversation Starters
            </h2>

            <div className="space-y-4">
              {/* LinkedIn Message */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">LinkedIn Message</h3>
                  <button
                    onClick={() => copyToClipboard(data.conversation_starters.linkedin_message, 'linkedin')}
                    className="text-sm text-primary-600 hover:text-primary-700 flex items-center space-x-1"
                  >
                    {copiedField === 'linkedin' ? (
                      <Check className="h-4 w-4 text-green-600" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                    <span>{copiedField === 'linkedin' ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                  {data.conversation_starters.linkedin_message}
                </p>
              </div>

              {/* Phone Opener */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">Phone Opener</h3>
                  <button
                    onClick={() => copyToClipboard(data.conversation_starters.phone_opener, 'phone')}
                    className="text-sm text-primary-600 hover:text-primary-700 flex items-center space-x-1"
                  >
                    {copiedField === 'phone' ? (
                      <Check className="h-4 w-4 text-green-600" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                    <span>{copiedField === 'phone' ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                  {data.conversation_starters.phone_opener}
                </p>
              </div>

              {/* Connection Request */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">Connection Request</h3>
                  <button
                    onClick={() => copyToClipboard(data.conversation_starters.connection_request, 'connection')}
                    className="text-sm text-primary-600 hover:text-primary-700 flex items-center space-x-1"
                  >
                    {copiedField === 'connection' ? (
                      <Check className="h-4 w-4 text-green-600" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                    <span>{copiedField === 'connection' ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                  {data.conversation_starters.connection_request}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
