/**
 * Compliance Page
 * Comprehensive compliance management across all CERs and Plants
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  AlertCircle,
  CheckCircle2,
  XCircle,
  Loader2,
  Calendar,
  Factory,
  Building2,
  FileText,
} from 'lucide-react';
import { apiClient } from '@/services/api/apiClient';
import { cerService } from '@/services/api/cer.service';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useNavigate } from 'react-router-dom';

export default function Compliance() {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [entityFilter, setEntityFilter] = useState<string>('all'); // all, cer, plant

  // Get all CERs for entity filtering
  const { data: cers } = useQuery({
    queryKey: ['cers'],
    queryFn: () => cerService.getCERs(),
  });

  // Get overdue records
  const { data: overdue, isLoading: loadingOverdue } = useQuery({
    queryKey: ['compliance', 'overdue'],
    queryFn: async () => {
      const response = await apiClient.get('/compliance/overdue');
      return response.data || [];
    },
  });

  // Get all requirements
  const { data: requirements, isLoading: loadingRequirements } = useQuery({
    queryKey: ['compliance', 'requirements', entityFilter],
    queryFn: async () => {
      const params: any = {};
      if (entityFilter === 'cer') {
        params.cer_id = null; // Will be filtered client-side
      } else if (entityFilter === 'plant') {
        params.plant_id = null; // Will be filtered client-side
      }
      const response = await apiClient.get('/compliance/requirements', { params });
      return response.data || [];
    },
  });

  // Get all records
  const { data: records, isLoading: loadingRecords } = useQuery({
    queryKey: ['compliance', 'records', statusFilter, entityFilter],
    queryFn: async () => {
      // Fetch records from all CERs
      if (!cers || cers.length === 0) return [];

      const allRecords: any[] = [];
      for (const cer of cers) {
        try {
          const cerRecords = await cerService.getCERComplianceRecords(
            cer.id,
            statusFilter === 'all' ? undefined : statusFilter,
            true // Include plants
          );
          allRecords.push(...cerRecords);
        } catch (error) {
          console.error(`Error fetching records for CER ${cer.id}:`, error);
        }
      }
      return allRecords;
    },
    enabled: !!cers,
  });

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'compliant':
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'non_compliant':
      case 'overdue':
        return <XCircle className="h-4 w-4 text-destructive" />;
      case 'pending':
        return <AlertCircle className="h-4 w-4 text-orange-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      compliant: 'default',
      completed: 'default',
      non_compliant: 'destructive',
      overdue: 'destructive',
      pending: 'secondary',
    };
    return (
      <Badge variant={variants[status?.toLowerCase()] || 'outline'} className="capitalize">
        {status?.replace('_', ' ') || 'unknown'}
      </Badge>
    );
  };

  if (loadingOverdue || loadingRequirements || loadingRecords) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Compliance Management</h1>
          <p className="text-muted-foreground">
            Track and manage compliance requirements across all CERs and Plants
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Requirements</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{requirements?.length || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Records</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{records?.length || 0}</div>
          </CardContent>
        </Card>
        <Card className={overdue && overdue.length > 0 ? 'border-destructive' : ''}>
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <AlertCircle
                className={
                  overdue && overdue.length > 0
                    ? 'h-5 w-5 text-destructive'
                    : 'h-5 w-5 text-muted-foreground'
                }
              />
              Overdue Items
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div
              className={`text-2xl font-bold ${overdue && overdue.length > 0 ? 'text-destructive' : ''}`}
            >
              {overdue?.length || 0}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Overdue Alert */}
      {overdue && overdue.length > 0 && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              Overdue Items ({overdue.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {overdue.map((record: any) => (
                <div
                  key={record.id}
                  className="flex justify-between items-center p-3 border border-destructive rounded"
                >
                  <div>
                    <p className="font-medium">
                      {record.requirement?.name || `Requirement #${record.requirement_id}`}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Due:{' '}
                      {record.due_date ? new Date(record.due_date).toLocaleDateString() : 'N/A'}
                      {record.entity_type && (
                        <span className="ml-2">
                          • {record.entity_type === 'plant' ? 'Plant' : 'CER'}:{' '}
                          {record.entity_name || 'Unknown'}
                        </span>
                      )}
                    </p>
                  </div>
                  <Badge variant="destructive">Overdue</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Requirements and Records Tabs */}
      <Tabs defaultValue="requirements" className="space-y-4">
        <TabsList>
          <TabsTrigger value="requirements">Requirements</TabsTrigger>
          <TabsTrigger value="records">Records</TabsTrigger>
        </TabsList>

        <TabsContent value="requirements" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Compliance Requirements ({requirements?.length || 0})</CardTitle>
                <Select value={entityFilter} onValueChange={setEntityFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filter by entity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Entities</SelectItem>
                    <SelectItem value="cer">CER Only</SelectItem>
                    <SelectItem value="plant">Plant Only</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent>
              {requirements && requirements.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Requirement</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Frequency</TableHead>
                      <TableHead>Entity</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {requirements.map((req: any) => (
                      <TableRow key={req.id}>
                        <TableCell className="font-medium">
                          {req.name || `Requirement #${req.id}`}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="capitalize">
                            {req.authority || req.category || 'general'}
                          </Badge>
                        </TableCell>
                        <TableCell className="capitalize">
                          {req.frequency_days
                            ? `Every ${req.frequency_days} days`
                            : req.type || 'one-time'}
                        </TableCell>
                        <TableCell>
                          {req.cer_id ? (
                            <div className="flex items-center gap-1">
                              <Building2 className="h-3 w-3" />
                              <Button
                                variant="link"
                                className="h-auto p-0"
                                onClick={() => navigate(`/cer/${req.cer_id}`)}
                              >
                                CER #{req.cer_id}
                              </Button>
                            </div>
                          ) : req.plant_id ? (
                            <div className="flex items-center gap-1">
                              <Factory className="h-3 w-3" />
                              <Button
                                variant="link"
                                className="h-auto p-0"
                                onClick={() => navigate(`/plants/${req.plant_id}`)}
                              >
                                Plant #{req.plant_id}
                              </Button>
                            </div>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No compliance requirements found</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="records" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Compliance Records ({records?.length || 0})</CardTitle>
                <div className="flex items-center gap-2">
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Filter by status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                      <SelectItem value="overdue">Overdue</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {records && records.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Requirement</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Due Date</TableHead>
                      <TableHead>Completed Date</TableHead>
                      <TableHead>Entity</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {records.map((record: any) => (
                      <TableRow key={record.id}>
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            {getStatusIcon(record.status)}
                            <div>
                              {record.requirement_name ||
                                record.requirement?.name ||
                                `Record #${record.id}`}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>{getStatusBadge(record.status || 'pending')}</TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {record.due_date ? (
                            <div className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {new Date(record.due_date).toLocaleDateString()}
                            </div>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {record.completed_date
                            ? new Date(record.completed_date).toLocaleDateString()
                            : '-'}
                        </TableCell>
                        <TableCell>
                          {record.entity_type === 'plant' ? (
                            <div className="flex items-center gap-1">
                              <Factory className="h-3 w-3" />
                              <Button
                                variant="link"
                                className="h-auto p-0"
                                onClick={() => navigate(`/plants/${record.entity_id}`)}
                              >
                                {record.entity_name || `Plant #${record.entity_id}`}
                              </Button>
                            </div>
                          ) : record.entity_type === 'cer' ? (
                            <div className="flex items-center gap-1">
                              <Building2 className="h-3 w-3" />
                              <Button
                                variant="link"
                                className="h-auto p-0"
                                onClick={() => navigate(`/cer/${record.entity_id}`)}
                              >
                                {record.entity_name || `CER #${record.entity_id}`}
                              </Button>
                            </div>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No compliance records found</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
