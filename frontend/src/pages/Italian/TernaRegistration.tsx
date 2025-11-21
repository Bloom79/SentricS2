/**
 * Terna GAUDÌ Registration Page
 * Manage producer and plant registrations in Terna GAUDÌ system
 * CRITICAL: Plant registration must be completed within 30 days of grid connection
 * PENALTY: €1,000-10,000 for late registration
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import {
  Plus,
  Building2,
  Zap,
  CheckCircle,
  AlertTriangle,
  Clock,
  FileText,
  ExternalLink,
  Shield,
  Calendar,
  Hash,
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
import { Progress } from '@/components/ui/progress';
import { italianService } from '@/services/api/italian.service';
import { cerService } from '@/services/api/cer.service';
import { useToast } from '@/hooks/use-toast';

interface TernaProducer {
  producer_id: string;
  name: string;
  fiscal_code: string;
  registration_date: string;
  status: 'active' | 'pending';
}

interface TernaPlant {
  censimp_code: string;
  plant_id: number;
  plant_name: string;
  power_kw: number;
  grid_connection_date: string;
  registration_date: string;
  deadline_date: string;
  days_remaining: number;
  dso_validation_status: 'pending' | 'validated' | 'discrepancies';
  producer_id: string;
}

export default function TernaRegistrationPage() {
  const { cerId } = useParams<{ cerId: string }>();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [showProducerDialog, setShowProducerDialog] = useState(false);
  const [showPlantDialog, setShowPlantDialog] = useState(false);
  const [selectedPlant, setSelectedPlant] = useState<any>(null);

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

  // Mock data (in production, fetch from backend)
  const producers: TernaProducer[] = [
    {
      producer_id: 'PROD-2024-001',
      name: 'Cooperativa Energia Solare',
      fiscal_code: '12345678901',
      registration_date: '2024-01-15',
      status: 'active',
    },
  ];

  const ternaPlants: TernaPlant[] = [
    {
      censimp_code: '12345678901234',
      plant_id: 1,
      plant_name: 'Impianto FV Comunale',
      power_kw: 150,
      grid_connection_date: '2024-11-01',
      registration_date: '2024-11-05',
      deadline_date: '2024-12-01',
      days_remaining: 15,
      dso_validation_status: 'pending',
      producer_id: 'PROD-2024-001',
    },
    {
      censimp_code: '98765432109876',
      plant_id: 2,
      plant_name: 'Impianto FV Industriale',
      power_kw: 500,
      grid_connection_date: '2024-10-01',
      registration_date: '2024-10-10',
      deadline_date: '2024-10-31',
      days_remaining: -20,
      dso_validation_status: 'validated',
      producer_id: 'PROD-2024-001',
    },
  ];

  // Register Producer Mutation
  const registerProducerMutation = useMutation({
    mutationFn: (data: any) => italianService.terna.registerProducer(data),
    onSuccess: (data) => {
      toast({
        title: 'Producer Registered',
        description: `Producer ID: ${data.producer_id}`,
      });
      setShowProducerDialog(false);
      queryClient.invalidateQueries({ queryKey: ['terna-producers', cerId] });
    },
    onError: (error: any) => {
      toast({
        title: 'Registration Failed',
        description: error.message || 'Failed to register producer',
        variant: 'destructive',
      });
    },
  });

  // Register Plant Mutation
  const registerPlantMutation = useMutation({
    mutationFn: (data: any) =>
      italianService.terna.registerPlant(data.producerId, data.plantData, data.gridConnectionDate),
    onSuccess: (data) => {
      toast({
        title: 'Plant Registered',
        description: `CENSIMP code: ${data.censimp_code}. DSO validation pending (15 working days).`,
      });
      setShowPlantDialog(false);
      queryClient.invalidateQueries({ queryKey: ['terna-plants', cerId] });
    },
    onError: (error: any) => {
      toast({
        title: 'Registration Failed',
        description: error.message || 'Failed to register plant',
        variant: 'destructive',
      });
    },
  });

  // Check DSO Validation
  const checkValidationMutation = useMutation({
    mutationFn: (censimpCode: string) => italianService.terna.checkValidationStatus(censimpCode),
    onSuccess: (data) => {
      toast({
        title: 'Validation Status Updated',
        description: `Status: ${data.validation_status}`,
      });
      queryClient.invalidateQueries({ queryKey: ['terna-plants', cerId] });
    },
  });

  const getDeadlineStatus = (daysRemaining: number) => {
    if (daysRemaining < 0) {
      return {
        color: 'bg-red-500',
        text: 'OVERDUE',
        variant: 'destructive' as const,
        icon: AlertTriangle,
        message: `${Math.abs(daysRemaining)} days overdue - PENALTY RISK €1,000-10,000`,
      };
    } else if (daysRemaining <= 7) {
      return {
        color: 'bg-red-500',
        text: 'CRITICAL',
        variant: 'destructive' as const,
        icon: AlertTriangle,
        message: `${daysRemaining} days left - URGENT ACTION REQUIRED`,
      };
    } else if (daysRemaining <= 15) {
      return {
        color: 'bg-orange-500',
        text: 'URGENT',
        variant: 'default' as const,
        icon: Clock,
        message: `${daysRemaining} days remaining`,
      };
    } else {
      return {
        color: 'bg-green-500',
        text: 'ON TIME',
        variant: 'secondary' as const,
        icon: CheckCircle,
        message: `${daysRemaining} days remaining`,
      };
    }
  };

  const getDSOValidationBadge = (status: string) => {
    const variants: Record<string, { variant: any; icon: any; text: string }> = {
      pending: { variant: 'secondary', icon: Clock, text: 'DSO Validation Pending' },
      validated: { variant: 'default', icon: CheckCircle, text: 'DSO Validated' },
      discrepancies: { variant: 'destructive', icon: AlertTriangle, text: 'Discrepancies Found' },
    };

    const config = variants[status] || variants.pending;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {config.text}
      </Badge>
    );
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Terna GAUDÌ Registration</h1>
          <p className="text-muted-foreground mt-1">
            Manage producer and plant registrations for {cer?.name}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowProducerDialog(true)}>
            <Building2 className="mr-2 h-4 w-4" />
            Register Producer
          </Button>
          <Button onClick={() => setShowPlantDialog(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Register Plant
          </Button>
        </div>
      </div>

      {/* Critical Deadline Alert */}
      {ternaPlants.some((plant) => plant.days_remaining <= 15 && plant.days_remaining >= 0) && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-semibold text-red-900">CRITICAL DEADLINE APPROACHING</p>
                <p className="text-sm text-red-700 mt-1">
                  You have plants with registration deadlines within 15 days. Late registration results in penalties
                  of €1,000-10,000. Complete registration immediately.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Overdue Alert */}
      {ternaPlants.some((plant) => plant.days_remaining < 0) && (
        <Card className="border-red-500 bg-red-100">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-6 w-6 text-red-700 mt-0.5" />
              <div>
                <p className="font-bold text-red-900 text-lg">REGISTRATION OVERDUE - PENALTY RISK</p>
                <p className="text-sm text-red-800 mt-1">
                  <strong>IMMEDIATE ACTION REQUIRED:</strong> You have overdue plant registrations. Penalties range
                  from €1,000 to €10,000. Contact your technical office immediately to complete registration and
                  minimize penalties.
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
                <p className="text-sm font-medium text-muted-foreground">Registered Producers</p>
                <p className="text-3xl font-bold">{producers.length}</p>
              </div>
              <Building2 className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Registered Plants</p>
                <p className="text-3xl font-bold">{ternaPlants.length}</p>
              </div>
              <Zap className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">DSO Validated</p>
                <p className="text-3xl font-bold">
                  {ternaPlants.filter((p) => p.dso_validation_status === 'validated').length}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Pending Deadlines</p>
                <p className="text-3xl font-bold">
                  {ternaPlants.filter((p) => p.days_remaining > 0 && p.dso_validation_status !== 'validated').length}
                </p>
              </div>
              <Clock className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="plants" className="space-y-4">
        <TabsList>
          <TabsTrigger value="plants">Plant Registrations</TabsTrigger>
          <TabsTrigger value="producers">Producers</TabsTrigger>
          <TabsTrigger value="help">Registration Guide</TabsTrigger>
        </TabsList>

        {/* Plants Tab */}
        <TabsContent value="plants" className="space-y-4">
          {ternaPlants.map((plant) => {
            const deadlineStatus = getDeadlineStatus(plant.days_remaining);
            const DeadlineIcon = deadlineStatus.icon;
            const progressPercentage = Math.min(100, Math.max(0, (30 - plant.days_remaining) / 30 * 100));

            return (
              <Card
                key={plant.censimp_code}
                className={`hover:shadow-lg transition-shadow ${
                  plant.days_remaining <= 7 ? 'border-red-300' : ''
                }`}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <Zap className="h-6 w-6 text-green-600 mt-1" />
                      <div>
                        <CardTitle className="text-lg">{plant.plant_name}</CardTitle>
                        <p className="text-sm text-muted-foreground mt-1">
                          {plant.power_kw} kW • Grid connected:{' '}
                          {new Date(plant.grid_connection_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <Badge variant={deadlineStatus.variant} className="flex items-center gap-1">
                        <DeadlineIcon className="h-3 w-3" />
                        {deadlineStatus.text}
                      </Badge>
                      {getDSOValidationBadge(plant.dso_validation_status)}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {/* Deadline Progress Bar */}
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="font-medium">Registration Deadline Progress</span>
                      <span className={`font-semibold ${plant.days_remaining < 0 ? 'text-red-600' : ''}`}>
                        {deadlineStatus.message}
                      </span>
                    </div>
                    <Progress
                      value={progressPercentage}
                      className="h-2"
                      indicatorClassName={deadlineStatus.color}
                    />
                    <div className="flex justify-between text-xs text-muted-foreground mt-1">
                      <span>Grid Connection: {new Date(plant.grid_connection_date).toLocaleDateString()}</span>
                      <span>Deadline: {new Date(plant.deadline_date).toLocaleDateString()}</span>
                    </div>
                  </div>

                  {/* Plant Details */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm mb-4">
                    <div>
                      <p className="text-muted-foreground flex items-center gap-1">
                        <Hash className="h-3 w-3" />
                        CENSIMP Code
                      </p>
                      <p className="font-mono font-semibold">{plant.censimp_code}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Registration Date</p>
                      <p className="font-semibold">{new Date(plant.registration_date).toLocaleDateString()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Producer ID</p>
                      <p className="font-semibold">{plant.producer_id}</p>
                    </div>
                  </div>

                  {/* DSO Validation Info */}
                  {plant.dso_validation_status === 'pending' && (
                    <Card className="bg-blue-50 border-blue-200 mb-4">
                      <CardContent className="pt-4">
                        <p className="text-sm text-blue-900">
                          <Clock className="inline h-4 w-4 mr-1" />
                          <strong>DSO Validation Pending:</strong> The DSO has 15 working days to validate your
                          registration. Current status will be checked automatically.
                        </p>
                      </CardContent>
                    </Card>
                  )}

                  {plant.dso_validation_status === 'validated' && (
                    <Card className="bg-green-50 border-green-200 mb-4">
                      <CardContent className="pt-4">
                        <p className="text-sm text-green-900">
                          <CheckCircle className="inline h-4 w-4 mr-1" />
                          <strong>DSO Validated:</strong> Your plant registration has been validated by the DSO.
                          Registration complete.
                        </p>
                      </CardContent>
                    </Card>
                  )}

                  {/* Actions */}
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => checkValidationMutation.mutate(plant.censimp_code)}
                      disabled={checkValidationMutation.isPending}
                    >
                      <Shield className="mr-2 h-4 w-4" />
                      Check DSO Status
                    </Button>
                    <Button variant="outline" size="sm">
                      <FileText className="mr-2 h-4 w-4" />
                      View Details
                    </Button>
                    <Button variant="outline" size="sm">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Open in GAUDÌ
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </TabsContent>

        {/* Producers Tab */}
        <TabsContent value="producers" className="space-y-4">
          {producers.map((producer) => (
            <Card key={producer.producer_id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <Building2 className="h-6 w-6 text-blue-600 mt-1" />
                    <div>
                      <CardTitle className="text-lg">{producer.name}</CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">
                        Fiscal Code: {producer.fiscal_code}
                      </p>
                    </div>
                  </div>
                  <Badge variant="default">
                    <CheckCircle className="mr-1 h-3 w-3" />
                    Active
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Producer ID</p>
                    <p className="font-semibold">{producer.producer_id}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Registration Date</p>
                    <p className="font-semibold">{new Date(producer.registration_date).toLocaleDateString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Help Tab */}
        <TabsContent value="help">
          <Card>
            <CardHeader>
              <CardTitle>Terna GAUDÌ Registration Guide</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold text-lg mb-2">Registration Process</h3>
                <ol className="list-decimal list-inside space-y-2 text-sm">
                  <li>
                    <strong>Step 1: Register Producer</strong> - Register the legal entity that owns the plant
                  </li>
                  <li>
                    <strong>Step 2: Register Plant</strong> - Register the plant within 30 days of grid connection
                  </li>
                  <li>
                    <strong>Step 3: DSO Validation</strong> - Wait for DSO validation (15 working days)
                  </li>
                  <li>
                    <strong>Step 4: CENSIMP Code</strong> - Receive 14-digit CENSIMP plant identifier
                  </li>
                </ol>
              </div>

              <Card className="bg-red-50 border-red-200">
                <CardContent className="pt-4">
                  <h4 className="font-semibold text-red-900 mb-2">CRITICAL DEADLINE</h4>
                  <p className="text-sm text-red-800">
                    Plant registration must be completed within <strong>30 days</strong> of grid connection.
                    Late registration results in penalties of <strong>€1,000 to €10,000</strong>.
                  </p>
                </CardContent>
              </Card>

              <div>
                <h3 className="font-semibold text-lg mb-2">Required Information</h3>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Producer fiscal code and legal details</li>
                  <li>Plant technical specifications (power, technology, location)</li>
                  <li>Grid connection date (exact date is critical for deadline)</li>
                  <li>DSO (Distribution System Operator) details</li>
                  <li>Connection point information</li>
                </ul>
              </div>

              <div>
                <h3 className="font-semibold text-lg mb-2">Authentication Requirements</h3>
                <p className="text-sm">
                  Terna GAUDÌ registration requires either:
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm mt-2">
                  <li>
                    <strong>Digital Certificate:</strong> Required for plants >10 MW
                  </li>
                  <li>
                    <strong>SPID Level 2:</strong> Accepted for smaller plants
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Register Producer Dialog */}
      <Dialog open={showProducerDialog} onOpenChange={setShowProducerDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Register Producer in Terna GAUDÌ</DialogTitle>
            <DialogDescription>Register the legal entity that owns the renewable energy plant.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="producer-name">Legal Name</Label>
              <Input id="producer-name" placeholder="Cooperativa Energia Rinnovabile" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="producer-fiscal">Fiscal Code / P.IVA</Label>
              <Input id="producer-fiscal" placeholder="12345678901" maxLength={11} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="producer-address">Legal Address</Label>
              <Input id="producer-address" placeholder="Via Roma 1, 00100 Roma" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowProducerDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => {
                toast({
                  title: 'Producer Registration',
                  description: 'Full registration form will be available in next update',
                });
                setShowProducerDialog(false);
              }}
            >
              Register Producer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Register Plant Dialog */}
      <Dialog open={showPlantDialog} onOpenChange={setShowPlantDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Register Plant in Terna GAUDÌ</DialogTitle>
            <DialogDescription>
              CRITICAL: Must be completed within 30 days of grid connection to avoid €1,000-10,000 penalty.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Card className="bg-red-50 border-red-200">
              <CardContent className="pt-4">
                <p className="text-sm text-red-900">
                  <strong>30-DAY DEADLINE:</strong> Late registration results in penalties of €1,000 to €10,000. Ensure
                  you have all required information before starting.
                </p>
              </CardContent>
            </Card>

            <div className="space-y-2">
              <Label htmlFor="plant-select">Select Plant</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select plant to register" />
                </SelectTrigger>
                <SelectContent>
                  {plants?.map((plant: any) => (
                    <SelectItem key={plant.id} value={plant.id.toString()}>
                      {plant.name} - {plant.power_kw} kW
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="grid-connection-date">Grid Connection Date *</Label>
              <Input id="grid-connection-date" type="date" />
              <p className="text-xs text-muted-foreground">
                The exact date the plant was connected to the grid. This determines your 30-day registration deadline.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="producer-select">Producer</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select producer" />
                </SelectTrigger>
                <SelectContent>
                  {producers.map((producer) => (
                    <SelectItem key={producer.producer_id} value={producer.producer_id}>
                      {producer.name} ({producer.producer_id})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPlantDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => {
                toast({
                  title: 'Plant Registration',
                  description: 'Full registration wizard will be available in next update',
                });
                setShowPlantDialog(false);
              }}
            >
              Continue to Registration
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
