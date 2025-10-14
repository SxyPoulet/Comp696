import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import DiscoverPage from './pages/DiscoverPage';
import CompaniesPage from './pages/CompaniesPage';
import CompanyProfilePage from './pages/CompanyProfilePage';
import ContentGenerationPage from './pages/ContentGenerationPage';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/discover" element={<DiscoverPage />} />
            <Route path="/companies" element={<CompaniesPage />} />
            <Route path="/companies/:id" element={<CompanyProfilePage />} />
            <Route path="/intelligence" element={<Dashboard />} />
            <Route path="/content" element={<ContentGenerationPage />} />
            <Route path="/analytics" element={<Dashboard />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
