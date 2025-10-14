import { Building2, MapPin, Users, TrendingUp, Save } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import type { Company } from '../types';

interface CompanyCardProps {
  company: Company;
  onSave?: (company: Company) => void;
}

export default function CompanyCard({ company, onSave }: CompanyCardProps) {
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (onSave) {
      setIsSaving(true);
      try {
        await onSave(company);
      } finally {
        setIsSaving(false);
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'discovered':
        return 'bg-blue-100 text-blue-800';
      case 'profiling':
        return 'bg-yellow-100 text-yellow-800';
      case 'analyzed':
        return 'bg-green-100 text-green-800';
      case 'contacted':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-gray-600';
  };

  // If company doesn't have an ID yet (discovered but not saved), render as non-clickable card
  const CardWrapper = company.id ? Link : 'div';
  const cardProps = company.id
    ? { to: `/companies/${company.id}`, className: "card hover:shadow-md transition-shadow cursor-pointer" }
    : { className: "card" };

  return (
    <CardWrapper {...cardProps as any}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <div className="p-2 bg-primary-100 rounded-lg">
            <Building2 className="h-6 w-6 text-primary-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {company.name}
            </h3>
            <p className="text-sm text-gray-500 truncate">{company.domain}</p>
          </div>
        </div>

        <div className="flex flex-col items-end space-y-2 ml-4">
          {company.status && (
            <span className={`badge ${getStatusColor(company.status)}`}>
              {company.status}
            </span>
          )}
          <div className="flex items-center space-x-1">
            <TrendingUp className="h-4 w-4 text-gray-400" />
            <span className={`text-sm font-semibold ${getScoreColor(company.lead_score)}`}>
              {company.lead_score.toFixed(0)}
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4 space-y-2">
        {company.industry && (
          <div className="flex items-center text-sm text-gray-600">
            <span className="font-medium mr-2">Industry:</span>
            <span>{company.industry}</span>
          </div>
        )}

        <div className="flex items-center space-x-4 text-sm text-gray-600">
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

        {company.description && (
          <p className="text-sm text-gray-600 line-clamp-2 mt-2">
            {company.description}
          </p>
        )}
      </div>

      {!company.id && onSave && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="w-full btn-primary flex items-center justify-center space-x-2"
          >
            <Save className={`h-4 w-4 ${isSaving ? 'animate-spin' : ''}`} />
            <span>{isSaving ? 'Saving...' : 'Save to Database'}</span>
          </button>
        </div>
      )}
    </CardWrapper>
  );
}
