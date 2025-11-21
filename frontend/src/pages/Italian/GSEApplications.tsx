/**
 * GSE Applications Management Page
 * Manage GSE portal applications: TCEC incentives, PNRR funding, RID
 * BUSINESS VALUE: €100-200K/year per CER from TCEC incentives
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Plus,
  FileText,
  Clock,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Calendar,
  Euro,
  Upload,
  ExternalLink,
  RefreshCw,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { italianService } from '@/services/api/italian.service';
import { cerService } from '@/services/api/cer.service';
import { useToast } from '@/hooks/use-toast';

interface GSEApplication {
  tracking_number: string;
  application_type: 'RID' | 'TCEC' | 'PNRR';
  submission_date: string;
  estimated_response_date: string;
  status: 'pending' | 'under_review' | 'approved' | 'rejected';
  deadline_days_remaining?: number;
  cer_id?: number;
  plant_id?: number;
  investment_amount?: number;
}

export default function GSEApplicationsPage() {
  const { cerId } = useParams<{ cerId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [showNewApplicationDialog, setShowNewApplicationDialog] = useState(false);
  const [selectedApplicationType, setSelectedApplicationType] = useState<'RID' | 'TCEC' | 'PNRR'>('TCEC');
  const [showAuthDialog, setShowAuthDialog] = useState(false);
  const [authStatus, setAuthStatus] = useState<'authenticated' | 'not_authenticated'>('not_authenticated');

  // Fetch CER details
  const { data: cer } = useQuery({
    queryKey: ['cer', cerId],
    queryFn: () => cerService.getCER(parseInt(cerId!)),
    enabled: !!cerId,
  });

  // Fetch CER plants
  const { data: plants } = useQuery({
    queryKey: ['cer', cerId, 'plants'],
    queryFn: () => cerService.getCERPlants(parseInt(cerId!)),
    enabled: !!cerId,
  });

  // Mock applications data (in production, this would come from backend)
  const applications: GSEApplication[] = [
    {
      tracking_number: 'TCEC-2024-001234',
      application_type: 'TCEC',
      submission_date: '2024-10-15',
      estimated_response_date: '2024-12-15',
      status: 'under_review',
      deadline_days_remaining: 45,
      cer_id: parseInt(cerId || '0'),
    },
    {
      tracking_number: 'PNRR-2024-005678',
      application_type: 'PNRR',
      submission_date: '2024-09-01',
      estimated_response_date: '2025-11-30',
      status: 'approved',
      cer_id: parseInt(cerId || '0'),
      investment_amount: 150000,
    },
  ];

  // SPID Authentication
  const authenticateMutation = useMutation({
    mutationFn: (fiscalCode: string) => italianService.gse.authenticate(fiscalCode, 'level2'),
    onSuccess: (data) => {
      setAuthStatus('authenticated');
      toast({
        title: 'Authentication Successful',
        description: `SPID Level 2 authenticated. Token expires: ${new Date(data.token_expiry).toLocaleString()}`,
      });
      setShowAuthDialog(false);
    },
    onError: (error: any) => {
      toast({
        title: 'Authentication Failed',
        description: error.message || 'Failed to authenticate with GSE portal',
        variant: 'destructive',
      });
    },
  });

  // Submit TCEC Application
  const submitTCECMutation = useMutation({
    mutationFn: (data: any) =>
      italianService.gse.submitTCECApplication(
        parseInt(cerId!),
        data.cerData,
        data.plants,
        data.members,
        data.documents
      ),
    onSuccess: (data) => {
      toast({
        title: 'TCEC Application Submitted',
        description: `Tracking number: ${data.tracking_number}. Response expected by ${new Date(
          data.estimated_response_date
        ).toLocaleDateString()}`,
      });
      setShowNewApplicationDialog(false);
      queryClient.invalidateQueries({ queryKey: ['gse-applications', cerId] });
    },
    onError: (error: any) => {
      toast({
        title: 'Submission Failed',
        description: error.message || 'Failed to submit TCEC application',
        variant: 'destructive',
      });
    },
  });

  // Submit PNRR Application
  const submitPNRRMutation = useMutation({
    mutationFn: (data: any) =>
      italianService.gse.submitPNRRApplication(
        parseInt(cerId!),
        data.investmentData,
        data.comuneData,
        data.documents
      ),
    onSuccess: (data) => {
      toast({
        title: 'PNRR Application Submitted',
        description: `Tracking number: ${data.tracking_number}. Deadline: November 30, 2025`,
      });
      setShowNewApplicationDialog(false);
      queryClient.invalidateQueries({ queryKey: ['gse-applications', cerId] });
    },
    onError: (error: any) => {
      toast({
        title: 'Submission Failed',
        description: error.message || 'Failed to submit PNRR application',
        variant: 'destructive',
      });
    },
  });

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: any; icon: any }> = {
      pending: { variant: 'secondary', icon: Clock },
      under_review: { variant: 'default', icon: RefreshCw },
      approved: { variant: 'default', icon: CheckCircle },
      rejected: { variant: 'destructive', icon: XCircle },
    };

    const config = variants[status] || variants.pending;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {status.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  const getDeadlineWarning = (daysRemaining?: number) => {
    if (!daysRemaining) return null;

    if (daysRemaining <= 7) {
      return (
        <Badge variant="destructive" className="flex items-center gap-1">
          <AlertTriangle className="h-3 w-3" />
          CRITICAL: {daysRemaining} days left
        </Badge>
      );
    } else if (daysRemaining <= 30) {
      return (
        <Badge variant="default" className="flex items-center gap-1 bg-orange-500">
          <AlertTriangle className="h-3 w-3" />
          URGENT: {daysRemaining} days left
        </Badge>
      );
    } else if (daysRemaining <= 60) {
      return (
        <Badge variant="secondary" className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {daysRemaining} days remaining
        </Badge>
      );
    }

    return (
      <Badge variant="outline" className="flex items-center gap-1">
        <Clock className="h-3 w-3" />
        {daysRemaining} days remaining
      </Badge>
    );
  };

  const getApplicationTypeInfo = (type: string) => {
    const info = {
      TCEC: {
        title: 'TCEC Incentive Application',
        description: 'Tariffa Energia Condivisa - 20-year incentive (€60-120/MWh)',
        deadline: '120 days from plant commissioning',
        value: '€100-200K/year',
        icon: Euro,
        color: 'text-green-600',
      },
      PNRR: {
        title: 'PNRR Funding Application',
        description: '40% funding for CER investments',
        deadline: 'November 30, 2025',
        value: 'Up to 40% of investment',
        icon: Euro,
        color: 'text-blue-600',
      },
      RID: {
        title: 'RID Application',
        description: 'Ritiro Dedicato - Dedicated withdrawal contract',
        deadline: '45 days review period',
        value: 'Grid export contract',
        icon: FileText,
        color: 'text-purple-600',
      },
    };

    return info[type as keyof typeof info];
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">GSE Applications</h1>
          <p className="text-muted-foreground mt-1">
            Manage TCEC incentives, PNRR funding, and RID applications for {cer?.name}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={authStatus === 'authenticated' ? 'outline' : 'default'}
            onClick={() => setShowAuthDialog(true)}
          >
            {authStatus === 'authenticated' ? (
              <>
                <CheckCircle className="mr-2 h-4 w-4" />
                SPID Authenticated
              </>
            ) : (
              <>
                <ExternalLink className="mr-2 h-4 w-4" />
                SPID Login
              </>
            )}
          </Button>
          <Button onClick={() => setShowNewApplicationDialog(true)} disabled={authStatus !== 'authenticated'}>
            <Plus className="mr-2 h-4 w-4" />
            New Application
          </Button>
        </div>
      </div>

      {/* Authentication Warning */}
      {authStatus !== 'authenticated' && (
        <Card className="border-orange-200 bg-orange-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-orange-600 mt-0.5" />
              <div>
                <p className="font-semibold text-orange-900">SPID Authentication Required</p>
                <p className="text-sm text-orange-700 mt-1">
                  You must authenticate with SPID Level 2 to submit applications to the GSE portal. Click "SPID
                  Login" to authenticate.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Critical Deadlines Alert */}
      {applications.some((app) => app.deadline_days_remaining && app.deadline_days_remaining <= 30) && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-semibold text-red-900">CRITICAL DEADLINE APPROACHING</p>
                <p className="text-sm text-red-700 mt-1">
                  You have applications with deadlines within 30 days. Missing the TCEC 120-day deadline will result
                  in loss of €100-200K/year incentives.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Applications</p>
                <p className="text-3xl font-bold">{applications.length}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Under Review</p>
                <p className="text-3xl font-bold">
                  {applications.filter((a) => a.status === 'under_review').length}
                </p>
              </div>
              <RefreshCw className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Approved</p>
                <p className="text-3xl font-bold">{applications.filter((a) => a.status === 'approved').length}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Value</p>
                <p className="text-3xl font-bold">€200K+</p>
              </div>
              <Euro className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Applications Tabs */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">All Applications</TabsTrigger>
          <TabsTrigger value="tcec">TCEC Incentives</TabsTrigger>
          <TabsTrigger value="pnrr">PNRR Funding</TabsTrigger>
          <TabsTrigger value="rid">RID Contracts</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {applications.map((application) => {
            const typeInfo = getApplicationTypeInfo(application.application_type);
            const Icon = typeInfo.icon;

            return (
              <Card key={application.tracking_number} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <Icon className={`h-6 w-6 ${typeInfo.color} mt-1`} />
                      <div>
                        <CardTitle className="text-lg">{typeInfo.title}</CardTitle>
                        <p className="text-sm text-muted-foreground mt-1">{typeInfo.description}</p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      {getStatusBadge(application.status)}
                      {getDeadlineWarning(application.deadline_days_remaining)}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Tracking Number</p>
                      <p className="font-mono font-semibold">{application.tracking_number}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Submitted</p>
                      <p className="font-semibold">
                        {new Date(application.submission_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Response Expected</p>
                      <p className="font-semibold">
                        {new Date(application.estimated_response_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Estimated Value</p>
                      <p className="font-semibold text-green-600">{typeInfo.value}</p>
                    </div>
                  </div>

                  <div className="flex justify-end gap-2 mt-4">
                    <Button variant="outline" size="sm">
                      <FileText className="mr-2 h-4 w-4" />
                      View Details
                    </Button>
                    <Button variant="outline" size="sm">
                      <Upload className="mr-2 h-4 w-4" />
                      Upload Documents
                    </Button>
                    <Button variant="outline" size="sm">
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Check Status
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}

          {applications.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center">
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-lg font-semibold">No Applications Yet</p>
                <p className="text-muted-foreground mt-2">
                  Submit your first GSE application to access incentives and funding
                </p>
                <Button className="mt-4" onClick={() => setShowNewApplicationDialog(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Application
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="tcec">
          <Card>
            <CardHeader>
              <CardTitle>TCEC Incentive Applications</CardTitle>
              <p className="text-sm text-muted-foreground">
                Tariffa Energia Condivisa - 20-year incentive period at €60-120/MWh
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {applications
                  .filter((a) => a.application_type === 'TCEC')
                  .map((app) => (
                    <div key={app.tracking_number} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-semibold">{app.tracking_number}</p>
                          <p className="text-sm text-muted-foreground">
                            Submitted: {new Date(app.submission_date).toLocaleDateString()}
                          </p>
                        </div>
                        {getStatusBadge(app.status)}
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pnrr">
          <Card>
            <CardHeader>
              <CardTitle>PNRR Funding Applications</CardTitle>
              <p className="text-sm text-muted-foreground">40% funding for comuni ≤50,000 population</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {applications
                  .filter((a) => a.application_type === 'PNRR')
                  .map((app) => (
                    <div key={app.tracking_number} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-semibold">{app.tracking_number}</p>
                          <p className="text-sm text-muted-foreground">
                            Investment: €{app.investment_amount?.toLocaleString()}
                          </p>
                        </div>
                        {getStatusBadge(app.status)}
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rid">
          <Card>
            <CardHeader>
              <CardTitle>RID Applications</CardTitle>
              <p className="text-sm text-muted-foreground">Ritiro Dedicato - Dedicated withdrawal contracts</p>
            </CardHeader>
            <CardContent>
              <p className="text-center py-8 text-muted-foreground">No RID applications</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* SPID Authentication Dialog */}
      <Dialog open={showAuthDialog} onOpenChange={setShowAuthDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>SPID Authentication</DialogTitle>
            <DialogDescription>
              Authenticate with SPID Level 2 to access the GSE portal and submit applications.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="fiscal-code">Fiscal Code (Codice Fiscale)</Label>
              <Input id="fiscal-code" placeholder="RSSMRA80A01H501U" maxLength={16} />
            </div>
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="pt-4">
                <p className="text-sm text-blue-900">
                  <strong>Test Mode:</strong> In development, authentication is simulated. Production will use real
                  SPID Level 2 authentication.
                </p>
              </CardContent>
            </Card>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAuthDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => {
                const fiscalCode = (document.getElementById('fiscal-code') as HTMLInputElement)?.value;
                if (fiscalCode) {
                  authenticateMutation.mutate(fiscalCode);
                }
              }}
              disabled={authenticateMutation.isPending}
            >
              {authenticateMutation.isPending ? 'Authenticating...' : 'Authenticate'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* New Application Dialog */}
      <Dialog open={showNewApplicationDialog} onOpenChange={setShowNewApplicationDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>New GSE Application</DialogTitle>
            <DialogDescription>
              Select the type of application you want to submit to the GSE portal.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="app-type">Application Type</Label>
              <Select value={selectedApplicationType} onValueChange={(value: any) => setSelectedApplicationType(value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select application type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="TCEC">
                    <div className="flex items-center gap-2">
                      <Euro className="h-4 w-4 text-green-600" />
                      <span>TCEC Incentive (€100-200K/year, 120-day deadline)</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="PNRR">
                    <div className="flex items-center gap-2">
                      <Euro className="h-4 w-4 text-blue-600" />
                      <span>PNRR Funding (40% of investment, Nov 30, 2025 deadline)</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="RID">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-purple-600" />
                      <span>RID Contract (Grid export, 45-day review)</span>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            {selectedApplicationType === 'TCEC' && (
              <Card className="bg-green-50 border-green-200">
                <CardContent className="pt-4">
                  <div className="space-y-2">
                    <h4 className="font-semibold text-green-900">TCEC Incentive Application</h4>
                    <ul className="text-sm text-green-800 space-y-1 ml-4 list-disc">
                      <li>
                        <strong>Value:</strong> €100-200K/year for 20 years
                      </li>
                      <li>
                        <strong>CRITICAL Deadline:</strong> Must submit within 120 days of plant commissioning
                      </li>
                      <li>
                        <strong>Incentive Rate:</strong> €60-120/MWh based on plant size and zone
                      </li>
                      <li>
                        <strong>Requirements:</strong> CER statute, member list, plant details, POD codes
                      </li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            )}

            {selectedApplicationType === 'PNRR' && (
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="pt-4">
                  <div className="space-y-2">
                    <h4 className="font-semibold text-blue-900">PNRR Funding Application</h4>
                    <ul className="text-sm text-blue-800 space-y-1 ml-4 list-disc">
                      <li>
                        <strong>Funding:</strong> 40% of total investment (up to €400K)
                      </li>
                      <li>
                        <strong>Deadline:</strong> November 30, 2025
                      </li>
                      <li>
                        <strong>Eligibility:</strong> Comuni ≤50,000 population, plants ≤1 MW
                      </li>
                      <li>
                        <strong>Requirements:</strong> Investment breakdown, comune certification, technical specs
                      </li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewApplicationDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => {
                toast({
                  title: 'Application Wizard',
                  description: 'Full application wizard will be available in next phase',
                });
                setShowNewApplicationDialog(false);
              }}
            >
              Continue to Application Form
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
