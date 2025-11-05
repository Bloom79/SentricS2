/**
 * Dashboard Page
 */
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
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
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/services/api/apiClient';
import { logger } from '@/utils/logger';
import { useIsMobile } from '@/hooks/use-mobile';
import {
  Activity,
  TrendingUp,
  AlertCircle,
  FileText,
  CheckCircle2,
  FileWarning,
  Calendar,
  ChevronRight,
  AlertTriangle,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface DashboardStats {
  plants: {
    total: number;
    active: number;
    total_capacity_kw: number;
  };
  cer: {
    total: number;
    active: number;
  };
  assets: {
    total: number;
    operational: number;
  };
  workflows: {
    total: number;
    active: number;
  };
  compliance: {
    overdue: number;
  };
  documents: {
    total: number;
    expiring_soon: number;
  };
}

interface WorkflowSummary {
  id: number;
  name: string;
  status?: string;
  type?: string;
  plant_id?: number;
  plant_name?: string;
  due_date?: string;
  start_date?: string;
  progress_percentage?: number;
}

interface WorkflowRow extends WorkflowSummary {
  daysRemaining?: number;
}

interface ComplianceAlert {
  id: number;
  requirement_name?: string;
  due_date?: string;
  status?: string;
  plant_name?: string;
  cer_name?: string;
  requirement?: {
    authority?: string;
    portal_name?: string;
  };
}

interface ComplianceAlertItem extends ComplianceAlert {
  daysOverdue?: number;
}

interface DocumentWatchItem {
  id: number;
  name: string;
  type?: string;
  status?: string;
  plant_name?: string;
  cer_name?: string;
  expiry_date?: string;
  days_until_expiry?: number;
}

interface DocumentWatchlistItem extends DocumentWatchItem {
  computedDaysUntilExpiry?: number;
}

interface InsightCardConfig {
  title: string;
  icon: LucideIcon;
  value: string;
  helper: string;
  badgeLabel?: string;
  badgeVariant?: 'default' | 'secondary' | 'destructive' | 'outline';
  progress?: number;
  progressLabel?: string;
}

interface AnalyticsSection {
  title: string;
  description: string;
  href: string;
  icon: LucideIcon;
  stat?: string;
}

const DAY_IN_MS = 1000 * 60 * 60 * 24;

const clampProgress = (value?: number) => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return 0;
  }
  return Math.min(100, Math.max(0, value));
};

const computeDaysUntil = (value?: string) => {
  if (!value) {
    return undefined;
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return undefined;
  }
  return Math.round((parsed.getTime() - Date.now()) / DAY_IN_MS);
};

const formatRelativeLabel = (days?: number) => {
  if (days === undefined) {
    return 'No due date';
  }
  if (days < 0) {
    return `Overdue by ${Math.abs(days)}d`;
  }
  if (days === 0) {
    return 'Due today';
  }
  return `Due in ${days}d`;
};

const formatDate = (value?: string) => {
  if (!value) {
    return '—';
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return '—';
  }
  return parsed.toLocaleDateString();
};

const getWorkflowStatusVariant = (
  status?: string
): 'default' | 'secondary' | 'destructive' | 'outline' => {
  if (!status) {
    return 'outline';
  }
  const normalized = status.toLowerCase();
  if (normalized.includes('progress')) {
    return 'secondary';
  }
  if (normalized.includes('complete')) {
    return 'default';
  }
  if (normalized.includes('cancel')) {
    return 'outline';
  }
  if (normalized.includes('hold')) {
    return 'outline';
  }
  return 'outline';
};

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const isMobile = useIsMobile();

  const {
    data: stats,
    isLoading: statsLoading,
    isError: statsError,
  } = useQuery<DashboardStats>({
    queryKey: ['dashboard', 'stats'],
    queryFn: async () => {
      const response = await apiClient.get('/dashboard/stats');
      return response.data;
    },
    retry: false,
  });

  const {
    data: activity,
    isError: activityError,
    isLoading: activityLoading,
  } = useQuery({
    queryKey: ['dashboard', 'activity'],
    queryFn: async () => {
      const response = await apiClient.get('/dashboard/activity?limit=10');
      return response.data;
    },
    retry: false,
    staleTime: 2 * 60 * 1000, // 2 minutes - activity changes frequently
  });

  const {
    data: workflowsData,
    isLoading: workflowsLoading,
    isError: workflowsError,
  } = useQuery<WorkflowSummary[]>({
    queryKey: ['dashboard', 'workflows', 'in-progress'],
    queryFn: async () => {
      const response = await apiClient.get('/workflows', {
        params: { limit: 6, status: 'in_progress' },
      });
      return response.data || [];
    },
    retry: false,
  });

  const {
    data: overdueComplianceData,
    isLoading: complianceLoading,
    isError: complianceError,
  } = useQuery<ComplianceAlert[]>({
    queryKey: ['dashboard', 'compliance', 'overdue'],
    queryFn: async () => {
      const response = await apiClient.get('/compliance/overdue');
      return response.data || [];
    },
    retry: false,
  });

  const {
    data: documentData,
    isLoading: documentsLoading,
    isError: documentsError,
  } = useQuery<DocumentWatchItem[]>({
    queryKey: ['dashboard', 'documents', 'expiring'],
    queryFn: async () => {
      const response = await apiClient.get('/documents', {
        params: { limit: 50 },
      });
      return response.data || [];
    },
    retry: false,
  });

  // All hooks must be called before any conditional returns
  const workflowRows: WorkflowRow[] = React.useMemo(() => {
    if (!workflowsData) {
      return [];
    }
    return workflowsData.slice(0, 6).map((workflow) => ({
      ...workflow,
      daysRemaining: computeDaysUntil(workflow.due_date),
    }));
  }, [workflowsData]);

  const complianceAlerts: ComplianceAlertItem[] = React.useMemo(() => {
    if (!overdueComplianceData) {
      return [];
    }
    return overdueComplianceData
      .map((record) => {
        const daysRemaining = computeDaysUntil(record.due_date);
        return {
          ...record,
          daysOverdue: daysRemaining !== undefined ? Math.max(0, -daysRemaining) : undefined,
        };
      })
      .sort((a, b) => (b.daysOverdue ?? 0) - (a.daysOverdue ?? 0))
      .slice(0, 5);
  }, [overdueComplianceData]);

  const documentWatchlist: DocumentWatchlistItem[] = React.useMemo(() => {
    if (!documentData) {
      return [];
    }
    return documentData
      .map((doc) => {
        const computed =
          typeof doc.days_until_expiry === 'number'
            ? doc.days_until_expiry
            : computeDaysUntil(doc.expiry_date);
        return {
          ...doc,
          computedDaysUntilExpiry: computed,
        };
      })
      .filter(
        (doc) => doc.computedDaysUntilExpiry !== undefined && doc.computedDaysUntilExpiry <= 45
      )
      .sort((a, b) => (a.computedDaysUntilExpiry ?? 999) - (b.computedDaysUntilExpiry ?? 999))
      .slice(0, 5);
  }, [documentData]);

  const totalWorkflows = stats?.workflows.total ?? 0;
  const activeWorkflows = stats?.workflows.active ?? 0;
  const workflowActiveRatio = totalWorkflows
    ? Math.round((activeWorkflows / totalWorkflows) * 100)
    : 0;

  const totalAssets = stats?.assets.total ?? 0;
  const operationalAssets = stats?.assets.operational ?? 0;
  const assetAvailability = totalAssets ? Math.round((operationalAssets / totalAssets) * 100) : 0;

  const overdueCount = complianceAlerts.length;
  const expiringSoonCount = documentWatchlist.length;

  // Error logging (non-blocking)
  if (statsError) {
    logger.error('Failed to load dashboard stats', statsError);
  }
  if (workflowsError) {
    logger.error('Failed to load workflow snapshot', workflowsError);
  }
  if (complianceError) {
    logger.error('Failed to load compliance alerts', complianceError);
  }
  if (documentsError) {
    logger.error('Failed to load document watchlist', documentsError);
  }
  if (activityError) {
    logger.error('Failed to load dashboard activity', activityError);
  }

  // Early return after all hooks - only show loading if critical data is loading
  // Don't block on secondary data like activity or documents
  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
        <p className="ml-4 text-muted-foreground">Loading dashboard...</p>
      </div>
    );
  }

  const insightCards: InsightCardConfig[] = [
    {
      title: 'Workflow Execution',
      icon: Activity,
      value: `${activeWorkflows}`,
      helper: totalWorkflows ? `active of ${totalWorkflows} workflows` : 'No workflows created yet',
      badgeLabel: totalWorkflows ? `${workflowActiveRatio}% active` : undefined,
      badgeVariant: 'outline',
      progress: clampProgress(workflowActiveRatio),
      progressLabel: totalWorkflows
        ? `${workflowActiveRatio}% of workflows currently in progress`
        : 'Create workflows to orchestrate operations',
    },
    {
      title: 'Compliance Risk',
      icon: AlertCircle,
      value: `${overdueCount}`,
      helper: 'overdue obligations needing action',
      badgeLabel: overdueCount > 0 ? 'Action required' : 'On track',
      badgeVariant: overdueCount > 0 ? 'destructive' : 'secondary',
    },
    {
      title: 'Documents Expiring',
      icon: FileWarning,
      value: `${expiringSoonCount}`,
      helper: 'expiring within the next 45 days',
      badgeLabel: expiringSoonCount > 0 ? 'Review soon' : 'All healthy',
      badgeVariant: expiringSoonCount > 0 ? 'destructive' : 'secondary',
    },
    {
      title: 'Asset Availability',
      icon: TrendingUp,
      value: totalAssets ? `${operationalAssets}` : '0',
      helper: totalAssets ? `operational of ${totalAssets}` : 'No assets registered',
      badgeLabel: totalAssets ? `${assetAvailability}% availability` : undefined,
      badgeVariant: 'outline',
      progress: clampProgress(assetAvailability),
      progressLabel: totalAssets
        ? `${assetAvailability}% of assets are currently operational`
        : 'Add assets to monitor availability',
    },
  ];

  const analyticsSections: AnalyticsSection[] = [
    {
      title: 'Compliance Performance',
      description:
        overdueCount > 0
          ? `${overdueCount} compliance obligations are overdue across your portfolio.`
          : 'All compliance obligations are currently on track.',
      href: '/compliance',
      icon: AlertTriangle,
      stat: overdueCount > 0 ? `${overdueCount} overdue` : undefined,
    },
    {
      title: 'Workflow Pipeline',
      description: totalWorkflows
        ? `${activeWorkflows} workflows are in progress and ${totalWorkflows - activeWorkflows} are waiting to start.`
        : 'Create workflows to orchestrate activation, compliance, and fiscal processes.',
      href: '/workflows',
      icon: Activity,
      stat: totalWorkflows ? `${workflowActiveRatio}% active` : undefined,
    },
    {
      title: 'Document Lifecycle',
      description:
        expiringSoonCount > 0
          ? `${expiringSoonCount} documents require renewal within the next 45 days.`
          : 'No documents are approaching expiration.',
      href: '/documents',
      icon: FileText,
      stat: expiringSoonCount ? `${expiringSoonCount} expiring soon` : undefined,
    },
    {
      title: 'CER Communities',
      description: stats?.cer.total
        ? `${stats.cer.active} active communities out of ${stats.cer.total}.`
        : 'Set up CER communities to track shared energy initiatives.',
      href: '/cer',
      icon: CheckCircle2,
      stat: stats?.cer.total ? `${stats.cer.active}/${stats.cer.total} active` : undefined,
    },
  ];

  return (
    <div className="space-y-4 sm:space-y-6">
      <div>
        <h1 className="text-responsive-xl font-bold">Dashboard</h1>
        <p className="text-xs sm:text-sm text-muted-foreground">
          Cross-module overview of operations, compliance, documents, and assets
        </p>
      </div>

      <div className="grid gap-3 sm:gap-4 grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs sm:text-sm font-medium">Plants</CardTitle>
            <Activity className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-xl sm:text-2xl font-bold">{stats?.plants.total ?? 0}</div>
            <p className="text-[10px] sm:text-xs text-muted-foreground">
              {stats?.plants.active ?? 0} active •{' '}
              {(stats?.plants.total_capacity_kw ?? 0).toFixed(1)} kW
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs sm:text-sm font-medium">CER</CardTitle>
            <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-xl sm:text-2xl font-bold">{stats?.cer.total ?? 0}</div>
            <p className="text-[10px] sm:text-xs text-muted-foreground">
              {stats?.cer.active ?? 0} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs sm:text-sm font-medium">Assets</CardTitle>
            <Activity className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-xl sm:text-2xl font-bold">{stats?.assets.total ?? 0}</div>
            <p className="text-[10px] sm:text-xs text-muted-foreground">
              {stats?.assets.operational ?? 0} operational
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs sm:text-sm font-medium">Compliance</CardTitle>
            <AlertCircle className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-xl sm:text-2xl font-bold">{stats?.compliance.overdue ?? 0}</div>
            <p className="text-[10px] sm:text-xs text-muted-foreground">Overdue</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Cross-Module Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4">
            {insightCards.map((card) => (
              <div key={card.title} className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <div className="rounded-md bg-primary/10 p-2 text-primary">
                    <card.icon className="h-4 w-4" />
                  </div>
                  {card.badgeLabel ? (
                    <Badge variant={card.badgeVariant ?? 'outline'}>{card.badgeLabel}</Badge>
                  ) : null}
                </div>
                <div className="mt-4 text-2xl font-semibold">{card.value}</div>
                <p className="text-sm text-muted-foreground">{card.helper}</p>
                {card.progress !== undefined ? (
                  <div className="mt-3 space-y-1">
                    <Progress value={card.progress} className="h-2" />
                    {card.progressLabel ? (
                      <p className="text-xs text-muted-foreground">{card.progressLabel}</p>
                    ) : null}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <div>
                <CardTitle className="text-lg font-semibold">Workflows in Progress</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Monitor execution across plants and programs
                </p>
              </div>
              <Badge variant="outline">{activeWorkflows} active</Badge>
            </div>
          </CardHeader>
          <CardContent>
            {workflowsLoading ? (
              <div className="flex h-32 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary" />
              </div>
            ) : workflowsError ? (
              <div className="flex h-32 items-center justify-center text-muted-foreground">
                <p className="text-sm">Unable to load workflows. Data may be unavailable.</p>
              </div>
            ) : workflowRows.length > 0 ? (
              isMobile ? (
                // Mobile: Card-based layout
                <div className="space-y-3">
                  {workflowRows.map((workflow) => (
                    <div key={workflow.id} className="rounded-lg border p-3 space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-sm truncate">{workflow.name}</h4>
                          <p className="text-xs text-muted-foreground">
                            {workflow.plant_name ?? 'Unassigned'} • {workflow.type ?? 'Workflow'}
                          </p>
                        </div>
                        <Badge
                          variant={getWorkflowStatusVariant(workflow.status)}
                          className="shrink-0 text-xs"
                        >
                          {workflow.status ?? 'Unknown'}
                        </Badge>
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-muted-foreground">Progress</span>
                          <span className="font-medium">
                            {Math.round(workflow.progress_percentage ?? 0)}%
                          </span>
                        </div>
                        <Progress
                          value={clampProgress(workflow.progress_percentage)}
                          className="h-2"
                        />
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">Due Date</span>
                        <span
                          className={
                            workflow.daysRemaining !== undefined && workflow.daysRemaining < 0
                              ? 'text-destructive font-medium'
                              : 'text-muted-foreground'
                          }
                        >
                          {formatRelativeLabel(workflow.daysRemaining)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                // Desktop: Table layout
                <div className="overflow-x-auto -mx-6 sm:mx-0">
                  <div className="inline-block min-w-full align-middle px-6 sm:px-0">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="min-w-[200px]">Workflow</TableHead>
                          <TableHead className="min-w-[100px]">Status</TableHead>
                          <TableHead className="min-w-[120px]">Progress</TableHead>
                          <TableHead className="text-right min-w-[100px]">Due</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {workflowRows.map((workflow) => (
                          <TableRow key={workflow.id}>
                            <TableCell>
                              <div className="flex flex-col">
                                <span className="font-medium">{workflow.name}</span>
                                <span className="text-xs text-muted-foreground">
                                  {workflow.plant_name ?? 'Unassigned'} •{' '}
                                  {workflow.type ?? 'Workflow'}
                                </span>
                              </div>
                            </TableCell>
                            <TableCell>
                              <Badge variant={getWorkflowStatusVariant(workflow.status)}>
                                {workflow.status ?? 'Unknown'}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <div className="space-y-1">
                                <Progress
                                  value={clampProgress(workflow.progress_percentage)}
                                  className="h-2 w-24"
                                />
                                <span className="text-xs text-muted-foreground">
                                  {Math.round(workflow.progress_percentage ?? 0)}%
                                </span>
                              </div>
                            </TableCell>
                            <TableCell className="text-right">
                              <div className="flex flex-col items-end">
                                <span
                                  className={`text-xs ${
                                    workflow.daysRemaining !== undefined &&
                                    workflow.daysRemaining < 0
                                      ? 'text-destructive'
                                      : 'text-muted-foreground'
                                  }`}
                                >
                                  {formatRelativeLabel(workflow.daysRemaining)}
                                </span>
                                <span className="text-xs text-muted-foreground">
                                  {formatDate(workflow.due_date)}
                                </span>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              )
            ) : (
              <p className="text-sm text-muted-foreground">
                No workflows are currently in progress. Launch a new workflow to get started.
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <div>
                <CardTitle className="text-lg font-semibold">Compliance Alerts</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Overdue obligations requiring attention
                </p>
              </div>
              <Badge variant={overdueCount > 0 ? 'destructive' : 'secondary'}>
                {overdueCount > 0 ? `${overdueCount} overdue` : 'On track'}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {complianceLoading ? (
              <div className="flex h-32 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary" />
              </div>
            ) : complianceError ? (
              <div className="flex h-32 items-center justify-center text-muted-foreground">
                <p>Unable to load compliance alerts. Data may be unavailable.</p>
              </div>
            ) : complianceAlerts.length > 0 ? (
              <div className="space-y-3">
                {complianceAlerts.map((alert) => (
                  <div key={alert.id} className="rounded-lg border p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-1">
                        <p className="text-sm font-semibold">
                          {alert.requirement_name ?? 'Compliance obligation'}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {alert.plant_name ?? alert.cer_name ?? 'General'} •{' '}
                          {formatDate(alert.due_date)}
                        </p>
                        {alert.requirement?.authority ? (
                          <p className="text-xs text-muted-foreground">
                            Authority: {alert.requirement.authority}
                          </p>
                        ) : null}
                      </div>
                      <Badge variant="destructive">
                        {alert.daysOverdue !== undefined
                          ? `Overdue ${alert.daysOverdue}d`
                          : 'Overdue'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                All compliance obligations are currently on track.
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 sm:gap-6 grid-cols-1 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-start justify-between gap-3">
              <div>
                <CardTitle className="text-lg font-semibold">Document Watchlist</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Expiring documents within the next 45 days
                </p>
              </div>
              <Badge variant={expiringSoonCount > 0 ? 'destructive' : 'secondary'}>
                {expiringSoonCount > 0 ? `${expiringSoonCount} to review` : 'All clear'}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {documentsLoading ? (
              <div className="flex h-32 items-center justify-center">
                <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary" />
              </div>
            ) : documentsError ? (
              <div className="flex h-32 items-center justify-center text-muted-foreground">
                <p className="text-sm">Unable to load documents. Data may be unavailable.</p>
              </div>
            ) : documentWatchlist.length > 0 ? (
              isMobile ? (
                // Mobile: Card-based layout
                <div className="space-y-3">
                  {documentWatchlist.map((doc) => (
                    <div key={doc.id} className="rounded-lg border p-3 space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-sm truncate">{doc.name}</h4>
                          <p className="text-xs text-muted-foreground">{doc.type ?? 'Document'}</p>
                        </div>
                        <Badge variant="outline" className="shrink-0 text-xs">
                          {doc.status ?? 'Draft'}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">Linked to</span>
                        <span className="font-medium">
                          {doc.plant_name ?? doc.cer_name ?? 'General'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">Expires</span>
                        <span
                          className={
                            doc.computedDaysUntilExpiry !== undefined &&
                            doc.computedDaysUntilExpiry < 0
                              ? 'text-destructive font-medium'
                              : 'text-muted-foreground'
                          }
                        >
                          {formatRelativeLabel(doc.computedDaysUntilExpiry)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                // Desktop: Table layout
                <div className="overflow-x-auto -mx-6 sm:mx-0">
                  <div className="inline-block min-w-full align-middle px-6 sm:px-0">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="min-w-[200px]">Document</TableHead>
                          <TableHead className="min-w-[120px]">Linked To</TableHead>
                          <TableHead className="min-w-[100px]">Expiry</TableHead>
                          <TableHead className="text-right min-w-[80px]">Status</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {documentWatchlist.map((doc) => (
                          <TableRow key={doc.id}>
                            <TableCell>
                              <div className="flex flex-col">
                                <span className="font-medium">{doc.name}</span>
                                <span className="text-xs text-muted-foreground">
                                  {doc.type ?? 'Document'}
                                </span>
                              </div>
                            </TableCell>
                            <TableCell>
                              <span className="text-xs text-muted-foreground">
                                {doc.plant_name ?? doc.cer_name ?? 'General'}
                              </span>
                            </TableCell>
                            <TableCell>
                              <div className="flex flex-col">
                                <span
                                  className={`text-xs ${
                                    doc.computedDaysUntilExpiry !== undefined &&
                                    doc.computedDaysUntilExpiry < 0
                                      ? 'text-destructive'
                                      : 'text-muted-foreground'
                                  }`}
                                >
                                  {formatRelativeLabel(doc.computedDaysUntilExpiry)}
                                </span>
                                <span className="text-xs text-muted-foreground">
                                  {formatDate(doc.expiry_date)}
                                </span>
                              </div>
                            </TableCell>
                            <TableCell className="text-right">
                              <Badge variant="outline">{doc.status ?? 'Draft'}</Badge>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              )
            ) : (
              <p className="text-sm text-muted-foreground">
                No documents are approaching expiration. Great job keeping documentation current!
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Reports & Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analyticsSections.map((section) => (
                <div
                  key={section.title}
                  className="rounded-lg border p-4 transition-colors hover:bg-muted/40"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <section.icon className="h-4 w-4 text-primary" />
                      <h3 className="text-sm font-semibold">{section.title}</h3>
                    </div>
                    {section.stat ? <Badge variant="outline">{section.stat}</Badge> : null}
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">{section.description}</p>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="mt-4 px-0 text-primary hover:text-primary"
                    onClick={() => navigate(section.href)}
                  >
                    Explore <ChevronRight className="ml-1 h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          {activity && activity.length > 0 ? (
            <div className="space-y-4">
              {activity.map((item: any, index: number) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="font-medium capitalize">{item.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {item.type} • {item.action}
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <Badge variant="outline" className="capitalize">
                      {item.type}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      {item.date ? new Date(item.date).toLocaleDateString() : ''}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">No recent activity</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
