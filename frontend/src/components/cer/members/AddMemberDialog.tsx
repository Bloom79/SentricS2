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
import { Checkbox } from "@/components/ui/checkbox";
import { format } from "date-fns";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { cn } from "@/lib/utils";
import React from "react";
import { cerService } from "@/services/api/cer.service";

const baseFormSchema = z.object({
  name: z.string().min(1, "Name is required"),
  address: z.string().min(1, "Address is required"),
  pod_id: z.string().min(1, "POD ID is required"),
  load_profile_type: z.enum(["residential", "commercial", "industrial", "custom"]),
  contracted_power: z.number().min(0, "Contracted power must be positive").optional(),
  user_type: z.enum(["real", "simulated"]).default("real"),
  consumption_class: z.string().optional(),
  smart_meter_id: z.string().optional(),
  meter_type: z.string().optional(),
  fiscal_code: z.string().optional(),
  vat_number: z.string().optional(),
});

const productionFormSchema = z.object({
  plant_type: z.enum(["PHOTOVOLTAIC", "WIND", "HYDRO", "BIOMASS"]).optional(),
  plant_capacity: z.number().min(0, "Capacity must be positive").optional(),
  commissioning_date: z.date().optional(),
  is_incentivized: z.boolean().optional(),
  capital_contribution: z.number().min(0).max(100, "Contribution must be between 0 and 100").optional(),
  has_storage: z.boolean().optional(),
  storage_capacity: z.number().min(0, "Storage capacity must be positive").optional(),
});

const formSchema = z.discriminatedUnion("member_type", [
  z.object({
    member_type: z.literal("consumer"),
    ...baseFormSchema.shape,
  }),
  z.object({
    member_type: z.literal("producer"),
    ...baseFormSchema.shape,
    ...productionFormSchema.shape,
  }),
  z.object({
    member_type: z.literal("prosumer"),
    ...baseFormSchema.shape,
    ...productionFormSchema.shape,
  }),
]);

type FormData = z.infer<typeof formSchema>;

interface AddMemberDialogProps {
  children: ReactNode;
  communityId: number;
}

export function AddMemberDialog({ children, communityId }: AddMemberDialogProps) {
  const queryClient = useQueryClient();
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      member_type: "consumer",
      name: "",
      address: "",
      pod_id: "",
      load_profile_type: "residential",
      user_type: "real",
      contracted_power: 0,
    },
  });

  const memberType = form.watch("member_type");
  const hasStorage = form.watch("has_storage");
  const showProductionFields = memberType === "producer" || memberType === "prosumer";

  // When member type changes, set production field defaults if needed
  React.useEffect(() => {
    if (showProductionFields) {
      form.setValue("plant_type", "PHOTOVOLTAIC", { shouldValidate: true });
      form.setValue("plant_capacity", 0, { shouldValidate: true });
      form.setValue("commissioning_date", new Date(), { shouldValidate: true });
      form.setValue("is_incentivized", false, { shouldValidate: true });
      form.setValue("capital_contribution", 0, { shouldValidate: true });
      form.setValue("has_storage", false, { shouldValidate: true });
      form.setValue("storage_capacity", 0, { shouldValidate: true });
    }
  }, [showProductionFields, form]);

  const { mutate: addMember, isPending } = useMutation({
    mutationFn: async (data: FormData) => {
      return cerService.addMember(communityId, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cer-members", communityId] });
      queryClient.invalidateQueries({ queryKey: ["cer", communityId] });
      queryClient.invalidateQueries({ queryKey: ["cer-stats", communityId] });
      toast.success("Member added successfully");
      form.reset();
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to add member");
    },
  });

  function onSubmit(data: FormData) {
    addMember(data);
  }

  return (
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Member</DialogTitle>
          <DialogDescription>
            Add a new member to your energy community. Fill in the required information below.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="member_type"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Member Type</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select member type" />
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

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter member name" {...field} />
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
                      <Input placeholder="Enter POD ID" {...field} />
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
                    <Input placeholder="Enter address" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="load_profile_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Load Profile Type</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select load profile" />
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
                        placeholder="0"
                        {...field}
                        onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {showProductionFields && (
              <div className="space-y-4 border-t pt-4">
                <h3 className="text-lg font-medium">Production Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="plant_type"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Plant Type</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select plant type" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="PHOTOVOLTAIC">Photovoltaic</SelectItem>
                            <SelectItem value="WIND">Wind</SelectItem>
                            <SelectItem value="HYDRO">Hydro</SelectItem>
                            <SelectItem value="BIOMASS">Biomass</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="plant_capacity"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Plant Capacity (kW)</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="Enter capacity"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <FormField
                  control={form.control}
                  name="commissioning_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Commissioning Date</FormLabel>
                      <FormControl>
                        <Input
                          type="date"
                          {...field}
                          value={field.value ? format(field.value, "yyyy-MM-dd") : ""}
                          onChange={(e) => {
                            const date = e.target.value ? new Date(e.target.value) : undefined;
                            field.onChange(date);
                          }}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="is_incentivized"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                          <FormLabel>Incentivized Plant</FormLabel>
                          <FormDescription>
                            Check if the plant is eligible for incentives
                          </FormDescription>
                        </div>
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="capital_contribution"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Capital Contribution (%)</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="0"
                            {...field}
                            onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                          />
                        </FormControl>
                        <FormDescription>
                          Enter the percentage of capital contribution (0-100)
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <div className="space-y-4">
                  <FormField
                    control={form.control}
                    name="has_storage"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                          />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                          <FormLabel>Has Storage</FormLabel>
                          <FormDescription>
                            Check if the plant has energy storage capabilities
                          </FormDescription>
                        </div>
                      </FormItem>
                    )}
                  />

                  {hasStorage && (
                    <FormField
                      control={form.control}
                      name="storage_capacity"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Storage Capacity (kWh)</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              placeholder="Enter storage capacity"
                              {...field}
                              onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  )}
                </div>
              </div>
            )}

            <DialogFooter>
              <Button type="submit" disabled={isPending}>
                {isPending ? "Adding..." : "Add Member"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}

