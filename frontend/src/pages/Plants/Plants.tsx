/**
 * Plants Page - Enhanced
 * Comprehensive renewable energy plant management
 */

import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Plus,
  Search,
  Filter,
  MapPin,
  Zap,
  Activity,
  Building2,
  Sun,
  Wind,
  Battery,
  AlertCircle,
  CheckCircle2,
  Clock,
  TrendingUp,
  FileText,
  Users,
  Calendar,
  MoreVertical,
  ArrowUpRight,
  Gauge,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiClient } from '@/services/api/apiClient';
import { logger } from '@/utils/logger';
import { useIsMobile } from '@/hooks/use-mobile';
import { getPlantStatusLabel, getPlantTypeLabel, getPlantStatusVariant } from '@/utils/plantUtils';

interface Plant {
  id: number;
  name: string;
  code: string;
  power: string;
  power_kw: number;
  status: string;
  type: string;
  location: string;
  region: string;
  cer_id?: number;
  cer_name?: string;
  site_id?: number;
  site_name?: string;
  commissioning_date?: string;
  asset_count?: number;
  active_workflows?: number;
  compliance_score?: number;
  document_count?: number;
  last_maintenance?: string;
  efficiency?: number;
  production_mtd?: number;
  availability?: number;
}

interface PlantStats {
  total: number;
  operational: number;
  maintenance: number;
  offline: number;
  total_capacity_mw: number;
  average_efficiency: number;
  total_production_mwh: number;
}

const getPlantIcon = (type: string) => {
  const typeMap: Record<string, React.ElementType> = {
    photovoltaic: Sun,
    wind: Wind,
    battery: Battery,
    hydroelectric: Activity,
  };
  return typeMap[type?.toLowerCase()] || Zap;
};

const calculateDaysSince = (date?: string) => {
  if (!date) return null;
  const days = Math.floor((Date.now() - new Date(date).getTime()) / (1000 * 60 * 60 * 24));
  return days;
};

const formatPower = (kw: number) => {
  if (kw >= 1000) {
    return `${(kw / 1000).toFixed(1)} MW`;
  }
  return `${kw.toFixed(0)} kW`;
};

export default function Plants() {
  const navigate = useNavigate();
  const isMobile = useIsMobile();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedRegion, setSelectedRegion] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const {
    data: plants,
    isLoading,
    isError,
    error,
  } = useQuery<Plant[]>({
    queryKey: ['plants', selectedType, selectedStatus, selectedRegion],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (selectedType && selectedType !== 'all') params.append('type', selectedType);
      if (selectedStatus && selectedStatus !== 'all') params.append('status', selectedStatus);
      if (selectedRegion && selectedRegion !== 'all') params.append('region', selectedRegion);

      const response = await apiClient.get(`/plants?${params.toString()}`);
      return response.data;
    },
    retry: false,
  });

  // Calculate statistics
  const stats = useMemo<PlantStats>(() => {
    if (!plants || plants.length === 0) {
      return {
        total: 0,
        operational: 0,
        maintenance: 0,
        offline: 0,
        total_capacity_mw: 0,
        average_efficiency: 0,
        total_production_mwh: 0,
      };
    }

    const operational = plants.filter((p) => p.status?.toLowerCase() === 'in_operation').length;
    const maintenance = plants.filter(
      (p) => p.status?.toLowerCase() === 'under_maintenance'
    ).length;
    const offline = plants.filter((p) => p.status?.toLowerCase() === 'offline').length;
    const total_capacity_kw = plants.reduce((sum, p) => sum + (p.power_kw || 0), 0);
    const efficiencies = plants.filter((p) => p.efficiency).map((p) => p.efficiency || 0);
    const average_efficiency =
      efficiencies.length > 0 ? efficiencies.reduce((a, b) => a + b, 0) / efficiencies.length : 0;
    const total_production_mwh = plants.reduce((sum, p) => sum + (p.production_mtd || 0), 0);

    return {
      total: plants.length,
      operational,
      maintenance,
      offline,
      total_capacity_mw: total_capacity_kw / 1000,
      average_efficiency,
      total_production_mwh,
    };
  }, [plants]);

  // Get unique regions for filter
  const regions = useMemo(() => {
    if (!plants) return [];
    const uniqueRegions = [...new Set(plants.map((p) => p.region).filter(Boolean))];
    return uniqueRegions.sort();
  }, [plants]);

  const filteredPlants = useMemo(() => {
    if (!plants) return [];

    return plants.filter((plant) => {
      const matchesSearch =
        !searchTerm ||
        plant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        plant.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        plant.location?.toLowerCase().includes(searchTerm.toLowerCase());

      return matchesSearch;
    });
  }, [plants, searchTerm]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (isError) {
    logger.error('Failed to load plants', error);
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">
            Failed to load plants. Please try again or log in.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-responsive-xl font-bold">Plants</h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Manage your renewable energy portfolio
          </p>
        </div>
        <Button onClick={() => navigate('/plants/new')} className="w-full sm:w-auto touch-target">
          <Plus className="mr-2 h-4 w-4" />
          Add Plant
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-3 grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs sm:text-sm font-medium">Total Plants</CardTitle>
            <Building2 className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-xl sm:text-2xl font-bold">{stats.total}</div>
            <div className="flex items-center gap-1 sm:gap-2 text-[10px] sm:text-xs text-muted-foreground">
              <CheckCircle2 className="h-3 w-3 text-green-500" />
              <span>{stats.operational} operational</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs sm:text-sm font-medium">Capacity</CardTitle>
            <Zap className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-xl sm:text-2xl font-bold">
              {stats.total_capacity_mw.toFixed(1)} MW
            </div>
            <Progress value={75} className="h-2 mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs sm:text-sm font-medium">Efficiency</CardTitle>
            <Gauge className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-xl sm:text-2xl font-bold">
              {stats.average_efficiency.toFixed(1)}%
            </div>
            <div className="flex items-center gap-1 text-[10px] sm:text-xs">
              <TrendingUp className="h-3 w-3 text-green-500" />
              <span className="text-green-500">+2.5%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs sm:text-sm font-medium">Production</CardTitle>
            <Activity className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-xl sm:text-2xl font-bold">
              {stats.total_production_mwh.toFixed(0)} MWh
            </div>
            <div className="text-[10px] sm:text-xs text-muted-foreground">MTD</div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Search & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4 sm:flex-row">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search plants, codes, locations..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>

            <Select value={selectedType || 'all'} onValueChange={setSelectedType}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="All Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="photovoltaic">Photovoltaic</SelectItem>
                <SelectItem value="wind">Wind</SelectItem>
                <SelectItem value="hydroelectric">Hydroelectric</SelectItem>
                <SelectItem value="battery">Battery Storage</SelectItem>
              </SelectContent>
            </Select>

            <Select value={selectedStatus || 'all'} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="All Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="in_operation">In Operation</SelectItem>
                <SelectItem value="under_maintenance">Under Maintenance</SelectItem>
                <SelectItem value="offline">Offline</SelectItem>
                <SelectItem value="commissioning">Commissioning</SelectItem>
              </SelectContent>
            </Select>

            {regions.length > 0 && (
              <Select value={selectedRegion || 'all'} onValueChange={setSelectedRegion}>
                <SelectTrigger className="w-full sm:w-[180px]">
                  <SelectValue placeholder="All Regions" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Regions</SelectItem>
                  {regions.map((region) => (
                    <SelectItem key={region} value={region}>
                      {region}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Plants Grid/List */}
      <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as 'grid' | 'list')}>
        <TabsList className="grid w-full max-w-[400px] grid-cols-2">
          <TabsTrigger value="grid">Grid View</TabsTrigger>
          <TabsTrigger value="list">List View</TabsTrigger>
        </TabsList>

        <TabsContent value="grid" className="mt-4 sm:mt-6">
          <div className="grid gap-3 sm:gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {filteredPlants.map((plant) => {
              const Icon = getPlantIcon(plant.type);
              const daysSinceCommissioning = calculateDaysSince(plant.commissioning_date);

              return (
                <Card
                  key={plant.id}
                  className="cursor-pointer hover:shadow-lg transition-all duration-200 group touch-target"
                  onClick={() => navigate(`/plants/${plant.id}`)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-start gap-2 flex-1 min-w-0">
                        <div className="p-1.5 sm:p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors shrink-0">
                          <Icon className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <CardTitle className="text-base sm:text-lg truncate">
                            {plant.name}
                          </CardTitle>
                          <p className="text-xs sm:text-sm text-muted-foreground truncate">
                            {plant.code}
                          </p>
                        </div>
                      </div>
                      {!isMobile && (
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                            <Button variant="ghost" size="icon">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Actions</DropdownMenuLabel>
                            <DropdownMenuItem
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/plants/${plant.id}`);
                              }}
                            >
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/plants/${plant.id}/edit`);
                              }}
                            >
                              Edit Plant
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/workflows/new?plant_id=${plant.id}`);
                              }}
                            >
                              Start Workflow
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-2 sm:space-y-3">
                      {/* Status Badge */}
                      <div className="flex items-center justify-between">
                        <Badge variant={getPlantStatusVariant(plant.status)} className="text-xs">
                          {getPlantStatusLabel(plant.status)}
                        </Badge>
                        <span className="text-sm font-medium">{formatPower(plant.power_kw)}</span>
                      </div>

                      {/* Key Metrics */}
                      <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-0.5">
                          <p className="text-[10px] sm:text-xs text-muted-foreground">Location</p>
                          <p className="text-xs sm:text-sm font-medium flex items-center gap-1 truncate">
                            <MapPin className="h-3 w-3 shrink-0" />
                            <span className="truncate">
                              {plant.location || plant.region || 'Not set'}
                            </span>
                          </p>
                        </div>
                        {plant.efficiency && (
                          <div className="space-y-0.5">
                            <p className="text-[10px] sm:text-xs text-muted-foreground">
                              Efficiency
                            </p>
                            <p className="text-xs sm:text-sm font-medium">
                              {plant.efficiency.toFixed(1)}%
                            </p>
                          </div>
                        )}
                      </div>

                      {/* Additional Info - Hide on mobile if not critical */}
                      {(!isMobile || plant.active_workflows || plant.cer_id) && (
                        <div className="flex items-center gap-2 sm:gap-4 pt-1 sm:pt-2 border-t flex-wrap">
                          {plant.active_workflows !== undefined && plant.active_workflows > 0 && (
                            <div className="flex items-center gap-1 text-[10px] sm:text-xs">
                              <Activity className="h-3 w-3 text-blue-500" />
                              <span>{plant.active_workflows} workflows</span>
                            </div>
                          )}
                          {!isMobile && plant.document_count !== undefined && (
                            <div className="flex items-center gap-1 text-xs">
                              <FileText className="h-3 w-3 text-gray-500" />
                              <span>{plant.document_count} docs</span>
                            </div>
                          )}
                          {plant.cer_id && (
                            <Badge variant="outline" className="text-[10px] sm:text-xs">
                              <Users className="h-3 w-3 mr-1" />
                              CER
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        <TabsContent value="list" className="mt-6">
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-4 font-medium">Plant</th>
                      <th className="text-left p-4 font-medium">Type</th>
                      <th className="text-left p-4 font-medium">Power</th>
                      <th className="text-left p-4 font-medium">Status</th>
                      <th className="text-left p-4 font-medium">Location</th>
                      <th className="text-left p-4 font-medium">Efficiency</th>
                      <th className="text-left p-4 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPlants.map((plant) => {
                      const Icon = getPlantIcon(plant.type);
                      return (
                        <tr
                          key={plant.id}
                          className="border-b hover:bg-muted/50 cursor-pointer"
                          onClick={() => navigate(`/plants/${plant.id}`)}
                        >
                          <td className="p-4">
                            <div className="flex items-center gap-3">
                              <div className="p-2 bg-primary/10 rounded-lg">
                                <Icon className="h-4 w-4 text-primary" />
                              </div>
                              <div>
                                <p className="font-medium">{plant.name}</p>
                                <p className="text-sm text-muted-foreground">{plant.code}</p>
                              </div>
                            </div>
                          </td>
                          <td className="p-4">
                            <span className="text-sm">{getPlantTypeLabel(plant.type)}</span>
                          </td>
                          <td className="p-4">
                            <span className="font-medium">{formatPower(plant.power_kw)}</span>
                          </td>
                          <td className="p-4">
                            <Badge variant={getPlantStatusVariant(plant.status)}>
                              {getPlantStatusLabel(plant.status)}
                            </Badge>
                          </td>
                          <td className="p-4">
                            <div className="flex items-center gap-1 text-sm">
                              <MapPin className="h-3 w-3" />
                              {plant.location || plant.region || 'Not set'}
                            </div>
                          </td>
                          <td className="p-4">
                            {plant.efficiency ? (
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-medium">
                                  {plant.efficiency.toFixed(1)}%
                                </span>
                                <Progress value={plant.efficiency} className="w-16 h-2" />
                              </div>
                            ) : (
                              <span className="text-sm text-muted-foreground">—</span>
                            )}
                          </td>
                          <td className="p-4">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/plants/${plant.id}`);
                              }}
                            >
                              View
                              <ArrowUpRight className="ml-1 h-3 w-3" />
                            </Button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {filteredPlants.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No plants found matching your criteria</p>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => {
                setSearchTerm('');
                setSelectedType('all');
                setSelectedStatus('all');
                setSelectedRegion('all');
              }}
            >
              Clear Filters
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
