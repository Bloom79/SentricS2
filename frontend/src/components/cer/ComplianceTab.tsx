/**
 * Compliance Tab Component
 * Manages compliance requirements and records for a CER
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ClipboardCheck,
  AlertCircle,
  CheckCircle2,
  XCircle,
  Loader2,
  Calendar,
  Factory,
  Building2,
  Plus,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
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
import { cerService } from '@/services/api/cer.service';
import { NewComplianceRecord } from '@/components/compliance/NewComplianceRecord';

interface ComplianceTabProps {
  cerId: number;
}

export function ComplianceTab({ cerId }: ComplianceTabProps) {
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showNewRecord, setShowNewRecord] = useState(false);

  const { data: compliance, isLoading: loadingCompliance } = useQuery({
    queryKey: ['cer-compliance', cerId],
    queryFn: () => cerService.getCERCompliance(cerId),
  });

  const { data: requirements, isLoading: loadingRequirements } = useQuery({
    queryKey: ['cer-compliance-requirements', cerId],
    queryFn: () => cerService.getCERComplianceRequirements(cerId, true), // Include plants
  });

  const { data: records, isLoading: loadingRecords } = useQuery({
    queryKey: ['cer-compliance-records', cerId, statusFilter],
    queryFn: () =>
      cerService.getCERComplianceRecords(
        cerId,
        statusFilter === 'all' ? undefined : statusFilter,
        true
      ), // Include plants
  });

  if (loadingCompliance || loadingRequirements || loadingRecords) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

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

  return (
    <div className="space-y-4">
      {/* Compliance Overview */}
      {compliance && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>CER Compliance Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                {compliance.cer_compliance_status === 'compliant' ? (
                  <CheckCircle2 className="h-8 w-8 text-green-500" />
                ) : (
                  <XCircle className="h-8 w-8 text-destructive" />
                )}
                <div>
                  <p className="font-semibold text-lg capitalize">
                    {compliance.cer_compliance_status || 'Unknown'}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {compliance.cer_requirements?.length || 0} requirements,{' '}
                    {compliance.cer_overdue?.length || 0} overdue
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Overall Compliance Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                {compliance.compliance_status === 'compliant' ? (
                  <CheckCircle2 className="h-8 w-8 text-green-500" />
                ) : (
                  <XCircle className="h-8 w-8 text-destructive" />
                )}
                <div>
                  <p className="font-semibold text-lg capitalize">
                    {compliance.compliance_status || 'Unknown'}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {compliance.total_requirements || 0} total requirements,{' '}
                    {compliance.total_overdue || 0} overdue
                    {compliance.linked_plants_count > 0 && (
                      <span className="block mt-1">
                        ({compliance.linked_plants_count} linked plants)
                      </span>
                    )}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Plant Compliance Summary */}
      {compliance?.plant_compliance_summary && compliance.plant_compliance_summary.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Plant Compliance Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
              {compliance.plant_compliance_summary.map((plant: any) => (
                <div
                  key={plant.plant_id}
                  className="flex items-center justify-between p-3 border rounded-md"
                >
                  <div className="flex items-center gap-2">
                    <Factory className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="font-medium text-sm">{plant.plant_name}</p>
                      <p className="text-xs text-muted-foreground">
                        {plant.requirements_count} reqs, {plant.overdue_count} overdue
                      </p>
                    </div>
                  </div>
                  {plant.compliance_status === 'compliant' ? (
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-destructive" />
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Requirements and Records */}
      <Tabs defaultValue="requirements" className="space-y-4">
        <TabsList>
          <TabsTrigger value="requirements">Requirements</TabsTrigger>
          <TabsTrigger value="records">Records</TabsTrigger>
        </TabsList>

        <TabsContent value="requirements" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Requirements ({requirements?.length || 0})</CardTitle>
            </CardHeader>
            <CardContent>
              {requirements && requirements.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Requirement</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Frequency</TableHead>
                      <TableHead>Next Due</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {requirements.map((req: any) => (
                      <TableRow key={req.id}>
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            {req.entity_type === 'plant' ? (
                              <Factory className="h-4 w-4 text-muted-foreground" />
                            ) : (
                              <Building2 className="h-4 w-4 text-muted-foreground" />
                            )}
                            <div>
                              <div>{req.name || req.title || `Requirement #${req.id}`}</div>
                              <div className="text-xs text-muted-foreground">
                                {req.entity_type === 'plant'
                                  ? `Plant: ${req.entity_name}`
                                  : `CER: ${req.entity_name}`}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="capitalize">
                            {req.category || req.authority || 'general'}
                          </Badge>
                        </TableCell>
                        <TableCell className="capitalize">
                          {req.frequency || req.type || 'one-time'}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {req.next_due_date ? (
                            <div className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {new Date(req.next_due_date).toLocaleDateString()}
                            </div>
                          ) : (
                            '-'
                          )}
                        </TableCell>
                        <TableCell>{getStatusBadge(req.status || 'pending')}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <ClipboardCheck className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No compliance requirements defined</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="records" className="space-y-4">
          {showNewRecord && (
            <NewComplianceRecord
              cerId={cerId}
              onSuccess={() => {
                setShowNewRecord(false);
              }}
              onCancel={() => setShowNewRecord(false)}
            />
          )}

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
                      <SelectItem value="compliant">Compliant</SelectItem>
                      <SelectItem value="non_compliant">Non-Compliant</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="overdue">Overdue</SelectItem>
                    </SelectContent>
                  </Select>
                  {!showNewRecord && (
                    <Button onClick={() => setShowNewRecord(true)}>
                      <Plus className="w-4 h-4 mr-2" />
                      New Record
                    </Button>
                  )}
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
                      <TableHead>Notes</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {records.map((record: any) => (
                      <TableRow key={record.id}>
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            {getStatusIcon(record.status)}
                            <div>
                              <div>
                                {record.requirement_name ||
                                  record.requirement?.name ||
                                  `Record #${record.id}`}
                              </div>
                              {record.entity_type && (
                                <div className="text-xs text-muted-foreground flex items-center gap-1">
                                  {record.entity_type === 'plant' ? (
                                    <>
                                      <Factory className="h-3 w-3" />
                                      Plant: {record.entity_name}
                                    </>
                                  ) : (
                                    <>
                                      <Building2 className="h-3 w-3" />
                                      CER: {record.entity_name}
                                    </>
                                  )}
                                </div>
                              )}
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
                        <TableCell className="text-sm max-w-xs truncate">
                          {record.notes || '-'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <ClipboardCheck className="h-12 w-12 mx-auto mb-4 opacity-50" />
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
