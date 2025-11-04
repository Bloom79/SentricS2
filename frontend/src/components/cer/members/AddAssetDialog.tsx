import { ReactNode } from "react";
import { useForm } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { cerService, CERMember } from "@/services/api/cer.service";

const formSchema = z.object({
  name: z.string().min(1, "Name is required"),
  asset_type: z.enum(["SOLAR", "WIND", "STORAGE", "BIOMASS", "HYDRO"]),
  capacity: z.number().min(0.1, "Capacity must be at least 0.1 kW").max(100, "Capacity cannot exceed 100 kW"),
  installation_date: z.string().min(1, "Installation date is required"),
  gse_registration_id: z.string().optional(),
  status: z.enum(["active", "maintenance", "inactive", "decommissioned"]).default("active"),
  asset_metadata: z.object({
    panel_type: z.string().optional(),
    inverter_model: z.string().optional(),
    orientation: z.string().optional(),
    tilt_angle: z.number().optional(),
  }).optional(),
});

type FormData = z.infer<typeof formSchema>;

interface AddAssetDialogProps {
  member: CERMember;
  cerId: number;
  children: ReactNode;
}

export function AddAssetDialog({ member, cerId, children }: AddAssetDialogProps) {
  const queryClient = useQueryClient();
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      asset_type: "SOLAR",
      capacity: 0,
      installation_date: new Date().toISOString().split("T")[0],
      gse_registration_id: "",
      status: "active",
      asset_metadata: {
        panel_type: "",
        inverter_model: "",
        orientation: "south",
        tilt_angle: 30,
      },
    },
  });

  const assetType = form.watch("asset_type");
  const showSolarFields = assetType === "SOLAR";

  const { mutate: addAsset, isPending } = useMutation({
    mutationFn: async (data: FormData) => {
      return cerService.createMemberAsset(cerId, member.id, {
        ...data,
        installation_date: data.installation_date,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cer-members", cerId] });
      queryClient.invalidateQueries({ queryKey: ["member-assets", cerId, member.id] });
      toast.success("Asset added successfully");
      form.reset();
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to add asset");
    },
  });

  function onSubmit(data: FormData) {
    addAsset(data);
  }

  return (
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Asset</DialogTitle>
          <DialogDescription>
            Add a new energy asset for {member.name} ({member.pod_id}). Fill in the required information below.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Asset Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter asset name" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="asset_type"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Asset Type</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select asset type" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="SOLAR">Solar PV</SelectItem>
                      <SelectItem value="WIND">Wind Turbine</SelectItem>
                      <SelectItem value="STORAGE">Energy Storage</SelectItem>
                      <SelectItem value="BIOMASS">Biomass Plant</SelectItem>
                      <SelectItem value="HYDRO">Hydroelectric</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="capacity"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Capacity (kW)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.1"
                        placeholder="Enter capacity"
                        {...field}
                        onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                      />
                    </FormControl>
                    <FormDescription>Maximum: 100 kW per asset</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="installation_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Installation Date</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="gse_registration_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>GSE Registration ID (Optional)</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter GSE registration ID" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="status"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Status</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select status" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="maintenance">Maintenance</SelectItem>
                      <SelectItem value="inactive">Inactive</SelectItem>
                      <SelectItem value="decommissioned">Decommissioned</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {showSolarFields && (
              <div className="space-y-4 border-t pt-4">
                <h3 className="text-lg font-medium">Solar Panel Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="asset_metadata.panel_type"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Panel Type</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select panel type" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="monocrystalline">Monocrystalline</SelectItem>
                            <SelectItem value="polycrystalline">Polycrystalline</SelectItem>
                            <SelectItem value="thin_film">Thin Film</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="asset_metadata.orientation"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Orientation</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select orientation" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="north">North</SelectItem>
                            <SelectItem value="south">South</SelectItem>
                            <SelectItem value="east">East</SelectItem>
                            <SelectItem value="west">West</SelectItem>
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
                    name="asset_metadata.tilt_angle"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Tilt Angle (degrees)</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="Enter tilt angle"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="asset_metadata.inverter_model"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Inverter Model</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter inverter model" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>
            )}

            <DialogFooter>
              <Button type="submit" disabled={isPending}>
                {isPending ? "Adding..." : "Add Asset"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}

