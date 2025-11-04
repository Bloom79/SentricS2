/**
 * Compliance Management Dashboard
 * Unified control center for managing plant registrations and compliance documentation
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { 
  AlertTriangle, 
  Clock, 
  CheckCircle2, 
  FileText, 
  Calendar, 
  Upload,
  Play,
  Plus,
  Factory,
  TrendingUp,
  AlertCircle,
  ChevronRight,
  FileCheck,
  Loader2
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { apiClient } from '@/services/api/apiClient';
import { format, addDays, isAfter, isBefore } from 'date-fns';

interface PlantCompliance {
  plant_id: number;
  plant_name: string;
  plant_type: string;
  status: 'compliant' | 'warning' | 'critical';
  active_workflows: number;
  pending_documents: number;
  upcoming_deadlines: number;
  overdue_items: number;
  compliance_score: number;
  next_deadline?: string;
  next_deadline_description?: string;
}

interface ComplianceDeadline {
  id: number;
  plant_id?: number;
  plant_name?: string;
  requirement: string;
  due_date: string;
  status: 'upcoming' | 'due_soon' | 'overdue';
  portal: string;
  documents_required: string[];
  penalty_amount?: number;
  workflow_id?: number;
}

interface ComplianceMetrics {
  total_plants: number;
  compliant_plants: number;
  plants_with_issues: number;
  active_workflows: number;
  pending_submissions: number;
  documents_expiring_soon: number;
  upcoming_deadlines_7d: number;
  overdue_items: number;
}

export default function ComplianceManagement() {
  const navigate = useNavigate();
  const [selectedView, setSelectedView] = useState<'grid' | 'timeline'>('grid');

  // Fetch compliance metrics
  const { data: metrics, isLoading: metricsLoading } = useQuery<ComplianceMetrics>({
    queryKey: ['compliance-metrics'],
    queryFn: async () => {
      // Aggregate data from various endpoints
      const [plants, workflows, documents, compliance] = await Promise.all([
        apiClient.get('/plants'),
        apiClient.get('/workflows', { params: { status: 'In Progress' } }),
        apiClient.get('/documents', { params: { expiring_soon: true } }),
        apiClient.get('/compliance/overdue'),
      ]);

      return {
        total_plants: plants.data?.length || 0,
        compliant_plants: plants.data?.filter((p: any) => p.compliance_status === 'compliant').length || 0,
        plants_with_issues: plants.data?.filter((p: any) => p.compliance_status !== 'compliant').length || 0,
        active_workflows: workflows.data?.length || 0,
        pending_submissions: workflows.data?.filter((w: any) => w.type === 'Document Submission').length || 0,
        documents_expiring_soon: documents.data?.length || 0,
        upcoming_deadlines_7d: 0, // Calculate from compliance records
        overdue_items: compliance.data?.length || 0,
      };
    },
  });

  // Fetch plant compliance status
  const { data: plantCompliance, isLoading: plantsLoading } = useQuery<PlantCompliance[]>({
    queryKey: ['plant-compliance'],
    queryFn: async () => {
      const plants = await apiClient.get('/plants');
      
      // For each plant, fetch compliance data
      const plantComplianceData = await Promise.all(
        plants.data.map(async (plant: any) => {
          const [workflows, compliance] = await Promise.all([
            apiClient.get('/workflows', { params: { plant_id: plant.id } }),
            apiClient.get('/compliance/records', { params: { plant_id: plant.id } }),
          ]);

          const overdueItems = compliance.data?.filter((c: any) => 
            c.status === 'overdue' || (c.due_date && new Date(c.due_date) < new Date())
          ).length || 0;

          const upcomingDeadlines = compliance.data?.filter((c: any) => 
            c.due_date && new Date(c.due_date) > new Date() && new Date(c.due_date) < addDays(new Date(), 30)
          ).length || 0;

          // Calculate compliance score (0-100)
          const complianceScore = overdueItems > 0 ? 40 : upcomingDeadlines > 0 ? 70 : 100;

          return {
            plant_id: plant.id,
            plant_name: plant.name,
            plant_type: plant.type,
            status: overdueItems > 0 ? 'critical' : upcomingDeadlines > 2 ? 'warning' : 'compliant',
            active_workflows: workflows.data?.filter((w: any) => w.status === 'In Progress').length || 0,
            pending_documents: 0, // Calculate from document requirements
            upcoming_deadlines: upcomingDeadlines,
            overdue_items: overdueItems,
            compliance_score: complianceScore,
            next_deadline: compliance.data?.[0]?.due_date,
            next_deadline_description: compliance.data?.[0]?.requirement_name,
          };
        })
      );

      return plantComplianceData;
    },
    enabled: !metricsLoading,
  });

  // Fetch upcoming deadlines
  const { data: deadlines, isLoading: deadlinesLoading } = useQuery<ComplianceDeadline[]>({
    queryKey: ['compliance-deadlines'],
    queryFn: async () => {
      const compliance = await apiClient.get('/compliance/records', {
        params: { status: 'pending' },
      });

      return compliance.data?.map((record: any) => {
        const dueDate = new Date(record.due_date);
        const today = new Date();
        const daysUntilDue = Math.ceil((dueDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

        return {
          id: record.id,
          plant_id: record.plant_id,
          plant_name: record.plant_name || `Plant #${record.plant_id}`,
          requirement: record.requirement_name || record.requirement?.name || 'Compliance Requirement',
          due_date: record.due_date,
          status: daysUntilDue < 0 ? 'overdue' : daysUntilDue <= 7 ? 'due_soon' : 'upcoming',
          portal: record.portal || 'GSE',
          documents_required: record.required_documents || [],
          penalty_amount: record.penalty_amount,
          workflow_id: record.workflow_id,
        };
      }) || [];
    },
  });

  const handleQuickAction = (action: string, plantId?: number) => {
    switch (action) {
      case 'new-registration':
        navigate('/workflow-templates?category=Registration');
        break;
      case 'submit-report':
        navigate('/workflows/new?template=monthly-report');
        break;
      case 'upload-document':
        navigate('/documents/upload');
        break;
      case 'view-plant':
        if (plantId) navigate(`/plants/${plantId}`);
        break;
      default:
        break;
    }
  };

  if (metricsLoading || plantsLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Compliance Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage plant registrations, compliance documentation, and regulatory submissions
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => handleQuickAction('new-registration')}>
            <Plus className="mr-2 h-4 w-4" />
            New Registration
          </Button>
          <Button variant="outline" onClick={() => navigate('/workflow-templates')}>
            <FileText className="mr-2 h-4 w-4" />
            Templates
          </Button>
        </div>
      </div>

      {/* Metrics Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className={metrics?.overdue_items ? 'border-red-500' : ''}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue Items</CardTitle>
            <AlertTriangle className={`h-4 w-4 ${metrics?.overdue_items ? 'text-red-500' : 'text-muted-foreground'}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.overdue_items || 0}</div>
            <p className="text-xs text-muted-foreground">
              Requires immediate attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Workflows</CardTitle>
            <Play className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.active_workflows || 0}</div>
            <p className="text-xs text-muted-foreground">
              {metrics?.pending_submissions || 0} pending submissions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Upcoming Deadlines</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.upcoming_deadlines_7d || 0}</div>
            <p className="text-xs text-muted-foreground">
              Next 7 days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics?.total_plants ? 
                Math.round((metrics.compliant_plants / metrics.total_plants) * 100) : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              {metrics?.compliant_plants || 0} of {metrics?.total_plants || 0} plants
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <Button 
              variant="outline" 
              className="justify-start"
              onClick={() => handleQuickAction('submit-report')}
            >
              <Upload className="mr-2 h-4 w-4" />
              Submit Monthly Report
            </Button>
            <Button 
              variant="outline" 
              className="justify-start"
              onClick={() => handleQuickAction('upload-document')}
            >
              <FileText className="mr-2 h-4 w-4" />
              Upload Document
            </Button>
            <Button 
              variant="outline" 
              className="justify-start"
              onClick={() => navigate('/workflows')}
            >
              <Play className="mr-2 h-4 w-4" />
              View All Workflows
            </Button>
            <Button 
              variant="outline" 
              className="justify-start"
              onClick={() => navigate('/documents')}
            >
              <FileCheck className="mr-2 h-4 w-4" />
              Document Library
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Tabs */}
      <Tabs defaultValue="plants" className="space-y-4">
        <TabsList>
          <TabsTrigger value="plants">Plants Overview</TabsTrigger>
          <TabsTrigger value="deadlines">Upcoming Deadlines</TabsTrigger>
          <TabsTrigger value="workflows">Active Workflows</TabsTrigger>
          <TabsTrigger value="documents">Recent Documents</TabsTrigger>
        </TabsList>

        {/* Plants Overview Tab */}
        <TabsContent value="plants" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {plantCompliance?.map((plant) => (
              <Card 
                key={plant.plant_id}
                className={`cursor-pointer hover:shadow-md transition-shadow ${
                  plant.status === 'critical' ? 'border-red-500' : 
                  plant.status === 'warning' ? 'border-yellow-500' : ''
                }`}
                onClick={() => navigate(`/plants/${plant.plant_id}/compliance`)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <Factory className="h-4 w-4" />
                      <CardTitle className="text-base">{plant.plant_name}</CardTitle>
                    </div>
                    <Badge 
                      variant={
                        plant.status === 'compliant' ? 'default' : 
                        plant.status === 'warning' ? 'secondary' : 'destructive'
                      }
                    >
                      {plant.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Compliance Score</span>
                      <span className="font-medium">{plant.compliance_score}%</span>
                    </div>
                    <Progress value={plant.compliance_score} className="h-2" />
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Active Workflows</p>
                      <p className="font-medium">{plant.active_workflows}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Overdue Items</p>
                      <p className={`font-medium ${plant.overdue_items > 0 ? 'text-red-500' : ''}`}>
                        {plant.overdue_items}
                      </p>
                    </div>
                  </div>

                  {plant.next_deadline && (
                    <div className="pt-2 border-t">
                      <p className="text-xs text-muted-foreground">Next Deadline</p>
                      <p className="text-sm font-medium">
                        {plant.next_deadline_description}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {format(new Date(plant.next_deadline), 'PPP')}
                      </p>
                    </div>
                  )}

                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleQuickAction('view-plant', plant.plant_id);
                    }}
                  >
                    Manage Compliance
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Deadlines Tab */}
        <TabsContent value="deadlines" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Compliance Deadlines</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {deadlines?.sort((a, b) => 
                  new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
                ).map((deadline) => (
                  <div 
                    key={deadline.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 mt-1">
                        {deadline.status === 'overdue' ? (
                          <AlertCircle className="h-5 w-5 text-red-500" />
                        ) : deadline.status === 'due_soon' ? (
                          <Clock className="h-5 w-5 text-yellow-500" />
                        ) : (
                          <Calendar className="h-5 w-5 text-blue-500" />
                        )}
                      </div>
                      <div className="space-y-1">
                        <p className="font-medium">{deadline.requirement}</p>
                        <p className="text-sm text-muted-foreground">
                          {deadline.plant_name} • Portal: {deadline.portal}
                        </p>
                        <div className="flex items-center gap-4 text-xs">
                          <span className={deadline.status === 'overdue' ? 'text-red-500 font-medium' : ''}>
                            Due: {format(new Date(deadline.due_date), 'PPP')}
                          </span>
                          {deadline.penalty_amount && (
                            <span className="text-muted-foreground">
                              Penalty: €{deadline.penalty_amount}
                            </span>
                          )}
                        </div>
                        {deadline.documents_required.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {deadline.documents_required.map((doc, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs">
                                {doc}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {deadline.workflow_id ? (
                        <Button
                          size="sm"
                          onClick={() => navigate(`/workflows/${deadline.workflow_id}`)}
                        >
                          View Workflow
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            // Create workflow for this deadline
                            navigate(`/workflows/new?requirement=${deadline.id}`);
                          }}
                        >
                          Start Workflow
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
                {(!deadlines || deadlines.length === 0) && (
                  <div className="text-center py-8">
                    <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-4" />
                    <p className="text-muted-foreground">No upcoming deadlines</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Active Compliance Workflows</CardTitle>
                <Button onClick={() => navigate('/workflows')}>
                  View All
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Track ongoing registration and compliance workflows
              </p>
              {/* Workflow list would go here */}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Documents Tab */}
        <TabsContent value="documents">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Recent Compliance Documents</CardTitle>
                <Button onClick={() => navigate('/documents')}>
                  Document Library
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Recently uploaded compliance documents
              </p>
              {/* Document list would go here */}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
