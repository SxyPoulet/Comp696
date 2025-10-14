# Sales Intelligence Agent - Frontend Guide

## Overview

The frontend is a modern React + TypeScript application built with Vite, providing a user-friendly interface for the Sales Intelligence Agent platform.

## Quick Start

### Option 1: Run with Docker (Recommended)

```bash
# From project root
docker-compose up frontend

# Access the app
open http://localhost:5173
```

### Option 2: Run Locally

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Access the app
open http://localhost:5173
```

## Features

### 1. Dashboard
- Overview of sales pipeline
- Key metrics (total companies, analyzed, avg score, contacted)
- Pipeline status breakdown
- Recent companies
- Top prospects by lead score

### 2. Discover Companies
- Search by industry, location, company size
- Keyword-based discovery
- AI-powered lead scoring
- Adjustable result limit (1-50)
- Real-time search results

### 3. Companies Management
- Paginated company list
- Filter by status, industry, lead score
- Sortable columns
- Company cards with key information
- Quick actions

### 4. Company Profile
- Detailed company overview
- Contacts list with decision makers highlighted
- Email, phone, LinkedIn contact info
- Intelligence analysis view
- Action buttons (Build Profile, Analyze, Generate Content)

### 5. Intelligence Dashboard
- AI-generated executive summary
- Pain points analysis with reasoning and impact
- Business priorities with urgency levels
- Recommended approach strategy
- Confidence scoring

### 6. Content Generation
- Company and contact selection
- Product/service description input
- Tone selection (professional, casual, friendly, formal)
- A/B variant generation
- Multi-channel conversation starters:
  - Email (subject + body + CTA)
  - LinkedIn message
  - Phone opener
  - Connection request
  - Follow-up subject
- Copy to clipboard for all content

## Tech Stack

| Technology | Purpose |
|------------|---------|
| React 18 | UI library |
| TypeScript | Type safety |
| Vite | Build tool and dev server |
| TailwindCSS | Styling framework |
| React Router | Client-side routing |
| TanStack Query | Data fetching and caching |
| Axios | HTTP client |
| Lucide React | Icon library |
| Recharts | Charts and visualizations |

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout.tsx              # Main layout with sidebar
│   │   ├── CompanyCard.tsx         # Company card component
│   │   ├── LoadingSpinner.tsx      # Loading state
│   │   └── ErrorMessage.tsx        # Error state
│   ├── pages/
│   │   ├── Dashboard.tsx           # Dashboard page
│   │   ├── DiscoverPage.tsx        # Discovery page
│   │   ├── CompaniesPage.tsx       # Companies list
│   │   ├── CompanyProfilePage.tsx  # Company detail
│   │   └── ContentGenerationPage.tsx # Content generation
│   ├── hooks/
│   │   └── useCompanies.ts         # React Query hooks
│   ├── services/
│   │   └── api.ts                  # API client
│   ├── types/
│   │   └── index.ts                # TypeScript types
│   ├── App.tsx                     # Main app component
│   ├── main.tsx                    # Entry point
│   └── index.css                   # Global styles with Tailwind
├── public/                         # Static assets
├── .env                            # Environment variables
├── vite.config.ts                  # Vite config
├── tailwind.config.js              # Tailwind config
├── tsconfig.json                   # TypeScript config
└── package.json                    # Dependencies
```

## Configuration

### Environment Variables

Create `.env` file:

```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### Vite Configuration

The `vite.config.ts` includes:
- React plugin
- Dev server on port 5173
- API proxy to backend
- Host mode for Docker

### TailwindCSS

Custom utility classes in `index.css`:
- `.btn-primary` - Primary button style
- `.btn-secondary` - Secondary button style
- `.btn-outline` - Outline button style
- `.card` - Card container
- `.input` - Input field
- `.label` - Form label
- `.badge`, `.badge-success`, `.badge-warning`, etc.

## API Integration

### React Query Hooks

```typescript
// List companies
const { data, isLoading, error } = useCompanies({ page: 1, page_size: 20 });

// Get single company
const { data: company } = useCompany(id);

// Get contacts
const { data: contacts } = useCompanyContacts(id);

// Get intelligence
const { data: intelligence } = useCompanyIntelligence(id);

// Create company
const { mutate: createCompany } = useCreateCompany();
createCompany({ name: 'Acme', domain: 'acme.com' });

// Build profile
const { mutate: buildProfile } = useBuildProfile();
buildProfile({ company_id: 1, include_contacts: true });

// Analyze intelligence
const { mutate: analyze } = useAnalyzeIntelligence();
analyze({ company_id: 1 });

// Generate content
const { mutate: generate } = useGenerateContent();
generate({
  company_id: 1,
  contact_name: 'John Doe',
  product_description: 'AI platform...'
});
```

### API Service

The `api.ts` service provides methods for all endpoints:
- Company CRUD operations
- Discovery
- Profile building
- Intelligence analysis
- Content generation
- Task status tracking

## Development

### Adding a New Page

1. Create component in `src/pages/`:
```typescript
export default function NewPage() {
  return <div>New Page</div>;
}
```

2. Add route in `App.tsx`:
```typescript
<Route path="/new" element={<NewPage />} />
```

3. Add navigation item in `Layout.tsx`:
```typescript
{ name: 'New', href: '/new', icon: Icon },
```

### Adding a New API Hook

1. Add function in `src/hooks/useCompanies.ts`:
```typescript
export function useNewFeature() {
  return useQuery({
    queryKey: ['feature'],
    queryFn: () => api.getFeature(),
  });
}
```

2. Use in component:
```typescript
const { data, isLoading } = useNewFeature();
```

## Building for Production

### Build

```bash
npm run build
```

Output in `dist/` directory.

### Preview

```bash
npm run preview
```

### Deploy

**Vercel:**
```bash
npm install -g vercel
vercel --prod
```

**Netlify:**
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

**Docker:**
```bash
# Build static files
docker run --rm -v $(pwd):/app -w /app node:20-alpine sh -c "npm install && npm run build"

# Serve with nginx
docker run -d -p 80:80 -v $(pwd)/dist:/usr/share/nginx/html nginx:alpine
```

## Styling Guide

### Colors

Primary colors (blue):
- `primary-50` to `primary-900`
- Main: `primary-600`

### Common Patterns

**Button:**
```tsx
<button className="btn-primary">Click me</button>
```

**Card:**
```tsx
<div className="card">
  <h2>Title</h2>
  <p>Content</p>
</div>
```

**Input:**
```tsx
<label className="label">Name</label>
<input type="text" className="input" />
```

**Badge:**
```tsx
<span className="badge badge-success">Active</span>
```

**Loading:**
```tsx
<LoadingSpinner text="Loading..." />
```

**Error:**
```tsx
<ErrorMessage message="Error occurred" onRetry={() => refetch()} />
```

## Best Practices

### State Management
- Use React Query for server state
- Use useState for local UI state
- Avoid prop drilling with context if needed

### Error Handling
- Always show user-friendly error messages
- Provide retry options
- Log errors to console in development

### Loading States
- Show loading spinners for async operations
- Disable buttons during mutations
- Indicate progress for long operations

### Type Safety
- Define all types in `src/types/`
- Use TypeScript strict mode
- Avoid `any` types

### Performance
- Use React Query caching
- Lazy load heavy components
- Optimize images and assets
- Minimize bundle size

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5173
npx kill-port 5173

# Or use different port
npm run dev -- --port 3000
```

### API Connection Issues
- Check backend is running on `http://localhost:8000`
- Verify VITE_API_URL in `.env`
- Check browser console for CORS errors
- Try accessing API directly: `http://localhost:8000/docs`

### Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite
```

### Type Errors
```bash
# Regenerate types
npm run build

# Check TypeScript
npx tsc --noEmit
```

## Testing

```bash
# Unit tests (if configured)
npm test

# E2E tests (if configured)
npm run test:e2e

# Type checking
npm run type-check
```

## Contributing

1. Follow existing code style
2. Use TypeScript for all new code
3. Add types for all API responses
4. Test thoroughly before committing
5. Update this guide for major changes

## Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)
- [TanStack Query](https://tanstack.com/query/latest)
- [React Router](https://reactrouter.com/)

## License

MIT License
