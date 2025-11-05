/**
 * Sites Page
 * List all sites with filtering and search
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, MapPin, Battery, Users, Zap, Building2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/services/api/apiClient';

interface Site {
  id: number;
  name: string;
  code?: string;
  site_type: string;
  status: string;
  location?: string;
  region?: string;
  capacity?: number;
  plants_count?: number;
  storage_units_count?: number;
  consumers_count?: number;
  total_capacity_kw?: number;
}

export default function Sites() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<{
    status?: string;
    site_type?: string;
    region?: string;
  }>({});

  const { data: sites, isLoading } = useQuery<Site[]>({
    queryKey: ['sites', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.site_type) params.append('site_type', filters.site_type);
      if (filters.region) params.append('region', filters.region);

      const response = await apiClient.get(`/sites?${params.toString()}`);
      return response.data;
    },
  });

  const filteredSites =
    sites?.filter(
      (site) =>
        site.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        site.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        site.location?.toLowerCase().includes(searchTerm.toLowerCase())
    ) || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Sites</h1>
          <p className="text-muted-foreground">
            Manage physical locations containing multiple plants
          </p>
        </div>
        <Button onClick={() => navigate('/sites/new')}>
          <Plus className="mr-2 h-4 w-4" />
          Add Site
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Search & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search sites by name, code, or location..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <select
              className="px-3 py-2 border rounded-md"
              value={filters.status || ''}
              onChange={(e) => setFilters({ ...filters, status: e.target.value || undefined })}
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="maintenance">Maintenance</option>
              <option value="under_construction">Under Construction</option>
            </select>
            <select
              className="px-3 py-2 border rounded-md"
              value={filters.site_type || ''}
              onChange={(e) => setFilters({ ...filters, site_type: e.target.value || undefined })}
            >
              <option value="">All Types</option>
              <option value="industrial">Industrial</option>
              <option value="commercial">Commercial</option>
              <option value="residential">Residential</option>
              <option value="mixed">Mixed</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Sites Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredSites.map((site) => (
          <Card
            key={site.id}
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/sites/${site.id}`)}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">{site.name}</CardTitle>
                  {site.code && <p className="text-sm text-muted-foreground">{site.code}</p>}
                </div>
                <Badge variant={site.status === 'active' ? 'default' : 'secondary'}>
                  {site.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {site.location && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <MapPin className="h-4 w-4" />
                    <span>{site.location}</span>
                  </div>
                )}

                {site.total_capacity_kw && site.total_capacity_kw > 0 && (
                  <div className="flex items-center gap-2 text-sm">
                    <Zap className="h-4 w-4 text-yellow-500" />
                    <span className="font-medium">
                      {(site.total_capacity_kw / 1000).toFixed(2)} MW
                    </span>
                  </div>
                )}

                <div className="flex gap-4 pt-2 border-t">
                  <div className="flex items-center gap-1 text-sm">
                    <Building2 className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{site.plants_count || 0}</span>
                    <span className="text-muted-foreground">Plants</span>
                  </div>
                  {site.storage_units_count && site.storage_units_count > 0 && (
                    <div className="flex items-center gap-1 text-sm">
                      <Battery className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{site.storage_units_count}</span>
                      <span className="text-muted-foreground">Storage</span>
                    </div>
                  )}
                  {site.consumers_count && site.consumers_count > 0 && (
                    <div className="flex items-center gap-1 text-sm">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{site.consumers_count}</span>
                      <span className="text-muted-foreground">Consumers</span>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredSites.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">No sites found</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
