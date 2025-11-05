/**
 * Member Detail Page - Full member management interface
 * Migrated from Sentrics with comprehensive functionality
 */

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Edit, Save, Trash2, Plus, Loader2 } from 'lucide-react';
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
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { toast } from 'sonner';
import { cerService, CERMember, CERMemberAsset } from '@/services/api/cer.service';
import { AddAssetDialog } from '@/components/cer/members/AddAssetDialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';

const memberFormSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  address: z.string().min(1, 'Address is required'),
  pod_id: z.string().min(1, 'POD ID is required'),
  member_type: z.enum(['consumer', 'producer', 'prosumer']),
  user_type: z.enum(['real', 'simulated']),
  load_profile_type: z.enum(['residential', 'commercial', 'industrial', 'custom']),
  contracted_power: z.number().min(0).optional(),
  smart_meter_id: z.string().optional(),
  meter_type: z.string().optional(),
  fiscal_code: z.string().optional(),
  vat_number: z.string().optional(),
  voltage_level: z.string().optional(),
  status: z.enum(['active', 'inactive', 'pending']),
});

type MemberFormData = z.infer<typeof memberFormSchema>;

export default function MemberDetail() {
  const { id: cerId, memberId } = useParams<{ id: string; memberId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);

  // Parse IDs safely, return null if invalid
  const cerIdNum = cerId && !isNaN(parseInt(cerId)) ? parseInt(cerId) : null;
  const memberIdNum = memberId && !isNaN(parseInt(memberId)) ? parseInt(memberId) : null;

  const { data: member, isLoading } = useQuery({
    queryKey: ['cer-member', cerIdNum, memberIdNum],
    queryFn: async () => {
      if (!cerIdNum || !memberIdNum) return null;
      return cerService.getMember(cerIdNum, memberIdNum);
    },
    enabled: !!cerIdNum && !!memberIdNum,
  });

  const { data: assets, isLoading: loadingAssets } = useQuery({
    queryKey: ['member-assets', cerIdNum, memberIdNum],
    queryFn: async () => {
      if (!cerIdNum || !memberIdNum) return [];
      return cerService.getMemberAssets(cerIdNum, memberIdNum);
    },
    enabled: !!cerIdNum && !!memberIdNum,
  });

  const form = useForm<MemberFormData>({
    resolver: zodResolver(memberFormSchema),
    defaultValues: {
      name: '',
      address: '',
      pod_id: '',
      member_type: 'consumer',
      user_type: 'real',
      load_profile_type: 'residential',
      contracted_power: 0,
      status: 'active',
    },
  });

  // Populate form when member data loads
  React.useEffect(() => {
    if (member && !isEditing) {
      form.reset({
        name: member.name,
        address: member.address,
        pod_id: member.pod_id,
        member_type: member.member_type as 'consumer' | 'producer' | 'prosumer',
        user_type: (member.user_type || 'real') as 'real' | 'simulated',
        load_profile_type: member.load_profile_type as
          | 'residential'
          | 'commercial'
          | 'industrial'
          | 'custom',
        contracted_power: member.contracted_power || 0,
        smart_meter_id: member.smart_meter_id || '',
        meter_type: member.meter_type || '',
        fiscal_code: member.fiscal_code || '',
        vat_number: member.vat_number || '',
        voltage_level: member.voltage_level || '',
        status: member.status as 'active' | 'inactive' | 'pending',
      });
    }
  }, [member, form, isEditing]);

  const { mutate: updateMember, isPending: isUpdating } = useMutation({
    mutationFn: async (data: MemberFormData) => {
      if (!cerIdNum || !memberIdNum) throw new Error('Invalid community or member ID');
      return cerService.updateMember(cerIdNum, memberIdNum, data);
    },
    onSuccess: () => {
      if (cerIdNum && memberIdNum) {
        queryClient.invalidateQueries({ queryKey: ['cer-member', cerIdNum, memberIdNum] });
        queryClient.invalidateQueries({ queryKey: ['cer-members', cerIdNum] });
        toast.success('Member updated successfully');
        setIsEditing(false);
      }
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to update member');
    },
  });

  const { mutate: deleteMember, isPending: isDeleting } = useMutation({
    mutationFn: async () => {
      if (!cerIdNum || !memberIdNum) throw new Error('Invalid community or member ID');
      return cerService.deleteMember(cerIdNum, memberIdNum);
    },
    onSuccess: () => {
      if (cerIdNum) {
        queryClient.invalidateQueries({ queryKey: ['cer-members', cerIdNum] });
        toast.success('Member deleted successfully');
        navigate(`/cer/${cerIdNum}`);
      }
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete member');
    },
  });

  const { mutate: deleteAsset } = useMutation({
    mutationFn: async (assetId: number) => {
      if (!cerIdNum || !memberIdNum) throw new Error('Invalid community or member ID');
      return cerService.deleteMemberAsset(cerIdNum, memberIdNum, assetId);
    },
    onSuccess: () => {
      if (cerIdNum && memberIdNum) {
        queryClient.invalidateQueries({ queryKey: ['member-assets', cerIdNum, memberIdNum] });
        queryClient.invalidateQueries({ queryKey: ['cer-members', cerIdNum] });
        toast.success('Asset deleted successfully');
      }
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to delete asset');
    },
  });

  function onSubmit(data: MemberFormData) {
    updateMember(data);
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!member) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">Member not found</p>
          <Button onClick={() => navigate(`/cer/${cerId}`)} className="mt-4">
            Back to Community
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
          <Button variant="ghost" onClick={() => cerIdNum && navigate(`/cer/${cerIdNum}`)}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{member.name}</h1>
            <p className="text-muted-foreground">{member.pod_id}</p>
            <div className="flex gap-2 mt-2">
              <Badge variant="outline" className="capitalize">
                {member.member_type}
              </Badge>
              <Badge variant={member.status === 'active' ? 'default' : 'secondary'}>
                {member.status}
              </Badge>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          {isEditing ? (
            <>
              <Button
                variant="outline"
                onClick={() => {
                  setIsEditing(false);
                  form.reset();
                }}
              >
                Cancel
              </Button>
              <Button onClick={form.handleSubmit(onSubmit)} disabled={isUpdating}>
                <Save className="mr-2 h-4 w-4" />
                {isUpdating ? 'Saving...' : 'Save'}
              </Button>
            </>
          ) : (
            <>
              <Button onClick={() => setIsEditing(true)}>
                <Edit className="mr-2 h-4 w-4" />
                Edit
              </Button>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive">
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Delete Member</AlertDialogTitle>
                    <AlertDialogDescription>
                      Are you sure you want to delete {member.name}? This action cannot be undone.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={() => deleteMember()}
                      className="bg-destructive text-destructive-foreground"
                    >
                      {isDeleting ? 'Deleting...' : 'Delete'}
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </>
          )}
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Energy Produced</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(member.energy_produced || 0).toFixed(2)} kWh</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Energy Consumed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(member.energy_consumed || 0).toFixed(2)} kWh</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Energy Shared</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(member.energy_shared || 0).toFixed(2)} kWh</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Assets</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{assets?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              Total capacity: {assets?.reduce((sum, a) => sum + a.capacity, 0).toFixed(1) || 0} kW
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="basic" className="space-y-4">
        <TabsList>
          <TabsTrigger value="basic">Basic Info</TabsTrigger>
          <TabsTrigger value="assets">Assets</TabsTrigger>
          <TabsTrigger value="technical">Technical</TabsTrigger>
          <TabsTrigger value="energy">Energy Stats</TabsTrigger>
        </TabsList>

        {/* Basic Info Tab */}
        <TabsContent value="basic" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Name</FormLabel>
                          <FormControl>
                            <Input {...field} disabled={!isEditing} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="pod_id"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>POD ID</FormLabel>
                          <FormControl>
                            <Input {...field} disabled={!isEditing} className="font-mono" />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <FormField
                    control={form.control}
                    name="address"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Address</FormLabel>
                        <FormControl>
                          <Input {...field} disabled={!isEditing} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="member_type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Member Type</FormLabel>
                          <Select
                            onValueChange={field.onChange}
                            value={field.value}
                            disabled={!isEditing}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="consumer">Consumer</SelectItem>
                              <SelectItem value="producer">Producer</SelectItem>
                              <SelectItem value="prosumer">Prosumer</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="user_type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>User Type</FormLabel>
                          <Select
                            onValueChange={field.onChange}
                            value={field.value}
                            disabled={!isEditing}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="real">Real</SelectItem>
                              <SelectItem value="simulated">Simulated</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="load_profile_type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Load Profile Type</FormLabel>
                          <Select
                            onValueChange={field.onChange}
                            value={field.value}
                            disabled={!isEditing}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="residential">Residential</SelectItem>
                              <SelectItem value="commercial">Commercial</SelectItem>
                              <SelectItem value="industrial">Industrial</SelectItem>
                              <SelectItem value="custom">Custom</SelectItem>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="contracted_power"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Contracted Power (kW)</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              {...field}
                              onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                              disabled={!isEditing}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="smart_meter_id"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Smart Meter ID</FormLabel>
                          <FormControl>
                            <Input {...field} disabled={!isEditing} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="meter_type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Meter Type</FormLabel>
                          <FormControl>
                            <Input {...field} disabled={!isEditing} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="fiscal_code"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Fiscal Code</FormLabel>
                          <FormControl>
                            <Input {...field} disabled={!isEditing} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="vat_number"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>VAT Number</FormLabel>
                          <FormControl>
                            <Input {...field} disabled={!isEditing} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <FormField
                    control={form.control}
                    name="status"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Status</FormLabel>
                        <Select
                          onValueChange={field.onChange}
                          value={field.value}
                          disabled={!isEditing}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="active">Active</SelectItem>
                            <SelectItem value="inactive">Inactive</SelectItem>
                            <SelectItem value="pending">Pending</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </form>
              </Form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Assets Tab */}
        <TabsContent value="assets" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Member Assets</CardTitle>
                {(member.member_type === 'producer' || member.member_type === 'prosumer') &&
                  cerIdNum && (
                    <AddAssetDialog member={member} cerId={cerIdNum}>
                      <Button>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Asset
                      </Button>
                    </AddAssetDialog>
                  )}
              </div>
            </CardHeader>
            <CardContent>
              {loadingAssets ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              ) : assets && assets.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Capacity</TableHead>
                      <TableHead>Installation Date</TableHead>
                      <TableHead>GSE ID</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {assets.map((asset: CERMemberAsset) => (
                      <TableRow key={asset.id}>
                        <TableCell className="font-medium">{asset.name}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{asset.asset_type}</Badge>
                        </TableCell>
                        <TableCell>{asset.capacity} kW</TableCell>
                        <TableCell>
                          {new Date(asset.installation_date).toLocaleDateString()}
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {asset.gse_registration_id || '-'}
                        </TableCell>
                        <TableCell>
                          <Badge variant={asset.status === 'active' ? 'default' : 'secondary'}>
                            {asset.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Delete Asset</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Are you sure you want to delete {asset.name}? This action cannot
                                  be undone.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => deleteAsset(asset.id)}
                                  className="bg-destructive text-destructive-foreground"
                                >
                                  Delete
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No assets yet</p>
                  {(member.member_type === 'producer' || member.member_type === 'prosumer') &&
                    cerIdNum && (
                      <AddAssetDialog member={member} cerId={cerIdNum}>
                        <Button className="mt-4" variant="outline">
                          Add First Asset
                        </Button>
                      </AddAssetDialog>
                    )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Technical Tab */}
        <TabsContent value="technical" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Technical Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm text-muted-foreground">Voltage Level:</span>
                  <p className="font-medium">{member.voltage_level || 'Not set'}</p>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Meter Type:</span>
                  <p className="font-medium">{member.meter_type || 'Not set'}</p>
                </div>
              </div>
              {member.technical_info && Object.keys(member.technical_info).length > 0 && (
                <div>
                  <span className="text-sm text-muted-foreground">Additional Technical Info:</span>
                  <pre className="mt-2 p-4 bg-muted rounded-md text-sm overflow-auto">
                    {JSON.stringify(member.technical_info, null, 2)}
                  </pre>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Energy Stats Tab */}
        <TabsContent value="energy" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Energy Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm text-muted-foreground">Total Energy Produced:</span>
                  <p className="text-2xl font-bold">
                    {(member.energy_produced || 0).toFixed(2)} kWh
                  </p>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Total Energy Consumed:</span>
                  <p className="text-2xl font-bold">
                    {(member.energy_consumed || 0).toFixed(2)} kWh
                  </p>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Total Energy Shared:</span>
                  <p className="text-2xl font-bold">{(member.energy_shared || 0).toFixed(2)} kWh</p>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">Contracted Power:</span>
                  <p className="text-2xl font-bold">
                    {member.contracted_power?.toFixed(1) || 0} kW
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
