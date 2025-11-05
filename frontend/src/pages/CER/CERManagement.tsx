/**
 * CER Management Page
 * Migrated from Sentrics, adapted to use API instead of Supabase
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cerService } from '@/services/api/cer.service';
import { logger } from '@/utils/logger';
import { useIsMobile } from '@/hooks/use-mobile';
import type { CER } from '@/services/api/cer.service';

export default function CERManagement() {
  const navigate = useNavigate();
  const isMobile = useIsMobile();
  const [searchTerm, setSearchTerm] = useState('');

  const {
    data: cerList,
    isLoading,
    error,
  } = useQuery<CER[]>({
    queryKey: ['cer', 'list'],
    queryFn: () => cerService.getCERs(),
  });

  const filteredCER =
    cerList?.filter((cer) => cer.name.toLowerCase().includes(searchTerm.toLowerCase())) || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-destructive">Failed to load CER communities</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-responsive-xl font-bold">CER Communities</h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Manage Renewable Energy Communities
          </p>
        </div>
        <Button onClick={() => navigate('/cer/new')} className="w-full sm:w-auto touch-target">
          <Plus className="mr-2 h-4 w-4" />
          New CER
        </Button>
      </div>

      {/* Search */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base sm:text-lg">Search</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search CER communities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8"
            />
          </div>
        </CardContent>
      </Card>

      {/* CER List */}
      <div className="grid gap-3 sm:gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        {filteredCER.map((cer) => (
          <Card
            key={cer.id}
            className="cursor-pointer hover:shadow-lg transition-shadow touch-target"
            onClick={() => navigate(`/cer/${cer.id}`)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between gap-2">
                <CardTitle className="text-base sm:text-lg flex-1 min-w-0 truncate">
                  {cer.name}
                </CardTitle>
                <Badge
                  variant={cer.status === 'active' ? 'default' : 'secondary'}
                  className="shrink-0 text-xs"
                >
                  {cer.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-2">
                <div className="flex justify-between text-xs sm:text-sm">
                  <span className="text-muted-foreground">Legal Type:</span>
                  <span className="font-medium capitalize truncate ml-2">{cer.legal_type}</span>
                </div>
                <div className="flex justify-between text-xs sm:text-sm">
                  <span className="text-muted-foreground">Region:</span>
                  <span className="font-medium truncate ml-2">{cer.region}</span>
                </div>
                <div className="flex justify-between text-xs sm:text-sm">
                  <span className="text-muted-foreground">Capacity:</span>
                  <span className="font-medium">{cer.total_capacity} kW</span>
                </div>
                {cer.pnrr_funding_applied && (
                  <Badge variant="outline" className="mt-2 text-xs">
                    PNRR Funding Applied
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredCER.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">No CER communities found</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
