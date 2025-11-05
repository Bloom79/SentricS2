/**
 * CER Detail Page - Comprehensive Community Management
 * Migrated from Sentrics with full functionality
 */

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeft,
  Edit,
  Users,
  FileText,
  ClipboardCheck,
  Activity,
  Settings,
  Factory,
  Link2,
  Unlink,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
import { cerService, CERMember } from '@/services/api/cer.service';
import { AddMemberDialog } from '@/components/cer/members/AddMemberDialog';
import { AddAssetDialog } from '@/components/cer/members/AddAssetDialog';
import { ParticipationRequestsTab } from '@/components/cer/ParticipationRequestsTab';
import { DocumentsTab } from '@/components/cer/DocumentsTab';
import { ComplianceTab } from '@/components/cer/ComplianceTab';
import { Loader2, Plus, Clock } from 'lucide-react';
import apiClient from '@/services/api/apiClient';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

export default function CERDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Parse ID safely, return null if invalid
  const cerId = id && !isNaN(parseInt(id)) ? parseInt(id) : null;

  const { data: cer, isLoading: loadingCER } = useQuery({
    queryKey: ['cer', cerId],
    queryFn: async () => {
      if (!cerId) return null;
      return cerService.getCER(cerId);
    },
    enabled: !!cerId,
  });

  const { data: members, isLoading: loadingMembers } = useQuery({
    queryKey: ['cer-members', cerId],
    queryFn: async () => {
      if (!cerId) return [];
      const membersList = await cerService.getMembers(cerId);
      // Load assets for each member
      const membersWithAssets = await Promise.all(
        membersList.map(async (member) => {
          try {
            const assets = await cerService.getMemberAssets(cerId, member.id);
            return { ...member, assets };
          } catch {
            return { ...member, assets: [] };
          }
        })
      );
      return membersWithAssets;
    },
    enabled: !!cerId,
  });

  const { data: stats } = useQuery({
    queryKey: ['cer-stats', cerId],
    queryFn: async () => {
      if (!cerId) return null;
      return cerService.getCERStats(cerId);
    },
    enabled: !!cerId,
  });

  const { data: cerPlants, isLoading: loadingPlants } = useQuery({
    queryKey: ['cer-plants', cerId],
    queryFn: async () => {
      if (!cerId) return [];
      return cerService.getCERPlants(cerId);
    },
    enabled: !!cerId,
  });

  const { data: allPlants } = useQuery({
    queryKey: ['all-plants'],
    queryFn: async () => {
      const response = await apiClient.get('/plants');
      return response.data;
    },
  });

  // Member statistics
  const memberStats = React.useMemo(() => {
    if (!members) return { producers: 0, consumers: 0, prosumers: 0 };
    return {
      producers: members.filter((m) => m.member_type === 'producer').length,
      consumers: members.filter((m) => m.member_type === 'consumer').length,
      prosumers: members.filter((m) => m.member_type === 'prosumer').length,
    };
  }, [members]);

  if (loadingCER) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!cer) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">CER not found</p>
          <Button onClick={() => navigate('/cer')} className="mt-4">
            Back to CER
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/cer')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{cer.name}</h1>
            <p className="text-muted-foreground">
              {cer.description || 'Renewable Energy Community'}
            </p>
            <div className="flex gap-2 mt-2">
              <Badge variant={cer.status === 'active' ? 'default' : 'secondary'}>
                {cer.status}
              </Badge>
              <Badge variant="outline" className="capitalize">
                {cer.legal_type}
              </Badge>
            </div>
          </div>
        </div>
        {cerId && (
          <Button onClick={() => navigate(`/cer/${cerId}/edit`)}>
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </Button>
        )}
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{members?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              {memberStats.producers} producers, {memberStats.consumers} consumers,{' '}
              {memberStats.prosumers} prosumers
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Capacity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{cer.total_capacity.toFixed(1)} kW</div>
            <p className="text-xs text-muted-foreground">
              {stats?.total_capacity?.toFixed(1) || cer.total_capacity.toFixed(1)} kW installed
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Energy Shared</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.total_energy_shared?.toFixed(0) || 0} kWh
            </div>
            <p className="text-xs text-muted-foreground">Total shared energy</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">GSE Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{cer.gse_compliance_status || 'pending'}</div>
            <p className="text-xs text-muted-foreground">Compliance status</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="members" className="space-y-4">
        <TabsList>
          <TabsTrigger value="members">
            <Users className="w-4 h-4 mr-2" />
            Members
          </TabsTrigger>
          <TabsTrigger value="requests">
            <Clock className="w-4 h-4 mr-2" />
            Requests
          </TabsTrigger>
          <TabsTrigger value="overview">
            <FileText className="w-4 h-4 mr-2" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="documents">
            <FileText className="w-4 h-4 mr-2" />
            Documents
          </TabsTrigger>
          <TabsTrigger value="compliance">
            <ClipboardCheck className="w-4 h-4 mr-2" />
            Compliance
          </TabsTrigger>
          <TabsTrigger value="plants">
            <Factory className="w-4 h-4 mr-2" />
            Plants
          </TabsTrigger>
        </TabsList>

        {/* Members Tab */}
        <TabsContent value="members" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Community Members</CardTitle>
                {cerId && (
                  <AddMemberDialog communityId={cerId}>
                    <Button>
                      <Users className="w-4 h-4 mr-2" />
                      Add Member
                    </Button>
                  </AddMemberDialog>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {loadingMembers ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              ) : members && members.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>POD ID</TableHead>
                      <TableHead>Load Profile</TableHead>
                      <TableHead>Contracted Power</TableHead>
                      <TableHead>Assets</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Energy Shared</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {members.map((member: CERMember) => (
                      <TableRow key={member.id}>
                        <TableCell className="font-medium">{member.name}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="capitalize">
                            {member.member_type}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-mono text-sm">{member.pod_id}</TableCell>
                        <TableCell className="capitalize">{member.load_profile_type}</TableCell>
                        <TableCell>{member.contracted_power?.toFixed(1) || 0} kW</TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {member.assets && member.assets.length > 0 ? (
                              member.assets.map((asset) => (
                                <Badge key={asset.id} variant="outline" className="text-xs">
                                  {asset.asset_type} ({asset.capacity}kW)
                                </Badge>
                              ))
                            ) : (
                              <span className="text-xs text-muted-foreground">No assets</span>
                            )}
                            {(member.member_type === 'producer' ||
                              member.member_type === 'prosumer') &&
                              cerId && (
                                <AddAssetDialog member={member} cerId={cerId}>
                                  <Button size="sm" variant="ghost" className="h-6 px-2">
                                    <Plus className="h-3 w-3" />
                                  </Button>
                                </AddAssetDialog>
                              )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={member.status === 'active' ? 'default' : 'secondary'}>
                            {member.status}
                          </Badge>
                        </TableCell>
                        <TableCell>{(member.energy_shared || 0).toFixed(2)} kWh</TableCell>
                        <TableCell>
                          {cerId && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => navigate(`/cer/${cerId}/members/${member.id}`)}
                            >
                              View
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No members yet</p>
                  {cerId && (
                    <AddMemberDialog communityId={cerId}>
                      <Button className="mt-4" variant="outline">
                        Add First Member
                      </Button>
                    </AddMemberDialog>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Community Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <Badge variant={cer.status === 'active' ? 'default' : 'secondary'}>
                    {cer.status}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Legal Type:</span>
                  <span className="font-medium capitalize">{cer.legal_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Region:</span>
                  <span className="font-medium">{cer.region}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Address:</span>
                  <span className="font-medium text-right">{cer.address}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Primary Substation:</span>
                  <span className="font-medium">{cer.primary_substation_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Capacity:</span>
                  <span className="font-medium">{cer.total_capacity} kW</span>
                </div>
                {cer.pnrr_funding_applied && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">PNRR Funding:</span>
                    <Badge variant="outline">Applied</Badge>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Energy Statistics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {stats ? (
                  <>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Total Energy Produced:</span>
                      <span className="font-medium">
                        {stats.total_energy_produced?.toFixed(2) || 0} kWh
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Total Energy Consumed:</span>
                      <span className="font-medium">
                        {stats.total_energy_consumed?.toFixed(2) || 0} kWh
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Total Energy Shared:</span>
                      <span className="font-medium">
                        {stats.total_energy_shared?.toFixed(2) || 0} kWh
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Total Capacity:</span>
                      <span className="font-medium">
                        {stats.total_capacity?.toFixed(2) || 0} kW
                      </span>
                    </div>
                  </>
                ) : (
                  <p className="text-muted-foreground">No statistics available</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Participation Requests Tab */}
        <TabsContent value="requests" className="space-y-4">
          {cerId ? (
            <ParticipationRequestsTab cerId={cerId} />
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground">Invalid community ID</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Documents Tab */}
        <TabsContent value="documents" className="space-y-4">
          {cerId ? (
            <DocumentsTab cerId={cerId} />
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground">Invalid community ID</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance" className="space-y-4">
          {cerId ? (
            <ComplianceTab cerId={cerId} />
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground">Invalid community ID</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Plants Tab */}
        <TabsContent value="plants" className="space-y-4">
          {cerId ? (
            <PlantsTab
              cerId={cerId}
              cerPlants={cerPlants || []}
              allPlants={allPlants || []}
              loadingPlants={loadingPlants || false}
            />
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground">Invalid community ID</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Plants Tab Component
function PlantsTab({
  cerId,
  cerPlants,
  allPlants,
  loadingPlants,
}: {
  cerId: number;
  cerPlants: any[];
  allPlants: any[];
  loadingPlants: boolean;
}) {
  const queryClient = useQueryClient();
  const [showLinkDialog, setShowLinkDialog] = useState(false);
  const [selectedPlantId, setSelectedPlantId] = useState<number | null>(null);

  const { mutate: linkPlant, isPending: isLinking } = useMutation({
    mutationFn: async (plantId: number) => {
      return cerService.linkPlant(cerId, plantId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cer-plants', cerId] });
      queryClient.invalidateQueries({ queryKey: ['cer-stats', cerId] });
      queryClient.invalidateQueries({ queryKey: ['cer', cerId] });
      toast.success('Plant linked successfully');
      setShowLinkDialog(false);
      setSelectedPlantId(null);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to link plant');
    },
  });

  const { mutate: unlinkPlant, isPending: isUnlinking } = useMutation({
    mutationFn: async (plantId: number) => {
      return cerService.unlinkPlant(cerId, plantId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cer-plants', cerId] });
      queryClient.invalidateQueries({ queryKey: ['cer-stats', cerId] });
      queryClient.invalidateQueries({ queryKey: ['cer', cerId] });
      toast.success('Plant unlinked successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to unlink plant');
    },
  });

  // Get plants not yet linked to this CER
  const availablePlants = allPlants.filter(
    (plant) => !cerPlants.some((cp) => cp.id === plant.id) && !plant.cer_id
  );

  if (loadingPlants) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Linked Plants</CardTitle>
            <Button onClick={() => setShowLinkDialog(true)}>
              <Link2 className="mr-2 h-4 w-4" />
              Link Plant
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {cerPlants.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Code</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Capacity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {cerPlants.map((plant: any) => (
                  <TableRow key={plant.id}>
                    <TableCell className="font-medium">{plant.name}</TableCell>
                    <TableCell className="font-mono text-sm">{plant.code}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {plant.type}
                      </Badge>
                    </TableCell>
                    <TableCell>{plant.power_kw.toFixed(1)} kW</TableCell>
                    <TableCell>
                      <Badge variant={plant.status === 'in_operation' ? 'default' : 'secondary'}>
                        {plant.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => unlinkPlant(plant.id)}
                        disabled={isUnlinking}
                      >
                        <Unlink className="h-4 w-4 mr-1" />
                        Unlink
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Factory className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No plants linked yet</p>
              <Button className="mt-4" variant="outline" onClick={() => setShowLinkDialog(true)}>
                <Link2 className="mr-2 h-4 w-4" />
                Link First Plant
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Link Plant Dialog */}
      {showLinkDialog && (
        <Card>
          <CardHeader>
            <CardTitle>Link Plant to Community</CardTitle>
          </CardHeader>
          <CardContent>
            {availablePlants.length > 0 ? (
              <div className="space-y-2">
                <Select
                  value={selectedPlantId?.toString()}
                  onValueChange={(value) => setSelectedPlantId(parseInt(value))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a plant to link" />
                  </SelectTrigger>
                  <SelectContent>
                    {availablePlants.map((plant) => (
                      <SelectItem key={plant.id} value={plant.id.toString()}>
                        {plant.name} ({plant.code}) - {plant.power_kw} kW
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <div className="flex gap-2">
                  <Button
                    onClick={() => {
                      if (selectedPlantId) linkPlant(selectedPlantId);
                    }}
                    disabled={!selectedPlantId || isLinking}
                  >
                    {isLinking ? 'Linking...' : 'Link Plant'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowLinkDialog(false);
                      setSelectedPlantId(null);
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground">
                No available plants to link. All plants are already linked to communities.
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
