/**
 * CER Member Dashboard
 * Member-facing portal showing their benefits, energy usage, savings, and payments
 * BUSINESS VALUE: Increase member satisfaction, reduce churn, improve transparency
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import {
  TrendingUp,
  DollarSign,
  Zap,
  Calendar,
  FileText,
  Download,
  Info,
  Award,
  Leaf,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { memberService, type MemberDashboardData } from '@/services/api/member.service';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

export const MemberDashboard: React.FC = () => {
  const { cerId, memberId } = useParams<{ cerId: string; memberId: string }>();

  const { data, isLoading } = useQuery<MemberDashboardData>({
    queryKey: ['cer', 'member', 'dashboard', cerId, memberId],
    queryFn: async () => {
      if (!cerId || !memberId) {
        throw new Error('CER ID and Member ID are required');
      }
      return memberService.getMemberDashboard(parseInt(cerId), parseInt(memberId));
    },
    refetchInterval: 300000, // 5 minutes
    enabled: !!cerId && !!memberId,
  });

  if (isLoading || !data) {
    return <div className="p-8 text-center">Loading your dashboard...</div>;
  }

  const memberTypeColors = {
    consumer: 'bg-blue-100 text-blue-700',
    producer: 'bg-green-100 text-green-700',
    prosumer: 'bg-purple-100 text-purple-700',
  };

  const energyBreakdown = [
    { name: 'Self-Consumed', value: data.energy.self_consumed_mtd, color: '#3b82f6' },
    { name: 'Shared', value: data.energy.shared_mtd, color: '#10b981' },
    { name: 'Grid', value: data.energy.consumed_mtd - data.energy.self_consumed_mtd - data.energy.shared_mtd, color: '#f59e0b' },
  ];

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Welcome, {data.member.name}!</h1>
          <div className="flex items-center gap-3 mt-2">
            <Badge className={memberTypeColors[data.member.member_type]} variant="outline">
              {data.member.member_type.toUpperCase()}
            </Badge>
            <span className="text-sm text-muted-foreground">
              Member since {new Date(data.member.join_date).toLocaleDateString()}
            </span>
          </div>
        </div>
        <div>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Download Report
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard
          title="This Month's Savings"
          value={`€${data.financial.total_benefit_mtd.toFixed(2)}`}
          subtitle={`€${data.financial.savings_mtd.toFixed(2)} savings + €${data.financial.incentives_mtd.toFixed(2)} incentives`}
          icon={<DollarSign className="h-5 w-5" />}
          color="text-green-600"
        />
        <SummaryCard
          title="Energy Shared"
          value={`${data.energy.shared_mtd.toFixed(0)} kWh`}
          subtitle="This month"
          icon={<Zap className="h-5 w-5" />}
          color="text-blue-600"
        />
        <SummaryCard
          title="YTD Total Benefit"
          value={`€${data.financial.total_benefit_ytd.toFixed(2)}`}
          subtitle={`${new Date().getFullYear()} savings`}
          icon={<TrendingUp className="h-5 w-5" />}
          color="text-purple-600"
        />
        <SummaryCard
          title="CO₂ Avoided"
          value={`${data.environmental.co2_avoided_ytd.toFixed(0)} kg`}
          subtitle={`≈ ${data.environmental.trees_equivalent} trees`}
          icon={<Leaf className="h-5 w-5" />}
          color="text-green-600"
        />
      </div>

      {/* Main Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="energy">Energy</TabsTrigger>
          <TabsTrigger value="financial">Financial</TabsTrigger>
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
          <TabsTrigger value="community">Community</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Energy Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Energy Consumption Breakdown (MTD)</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={energyBreakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value.toFixed(0)} kWh`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {energyBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Total Consumed:</span>
                    <span className="font-semibold">{data.energy.consumed_mtd.toFixed(0)} kWh</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">From Community:</span>
                    <span className="font-semibold text-green-600">{data.energy.shared_mtd.toFixed(0)} kWh</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Monthly Trends */}
            <Card>
              <CardHeader>
                <CardTitle>Savings & Incentives Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.history}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="savings" fill="#3b82f6" name="Savings (€)" />
                    <Bar dataKey="incentives" fill="#10b981" name="Incentives (€)" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Pending Payments Alert */}
          {data.financial.pending_payments > 0 && (
            <Card className="border-orange-200 bg-orange-50">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <Info className="h-5 w-5 text-orange-600 mt-0.5" />
                  <div>
                    <p className="font-semibold text-orange-900">
                      Pending Payment: €{data.financial.pending_payments.toFixed(2)}
                    </p>
                    <p className="text-sm text-orange-700 mt-1">
                      Your payment will be processed within 30 days. Check the Invoices tab for details.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Energy Tab */}
        <TabsContent value="energy" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Energy Flow (Last 12 Months)</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={data.history}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  {data.member.member_type !== 'consumer' && (
                    <Area type="monotone" dataKey="produced" stackId="1" stroke="#10b981" fill="#10b981" name="Produced (kWh)" />
                  )}
                  <Area type="monotone" dataKey="consumed" stackId="2" stroke="#3b82f6" fill="#60a5fa" name="Consumed (kWh)" />
                  <Area type="monotone" dataKey="shared" stackId="2" stroke="#f59e0b" fill="#fbbf24" name="Shared (kWh)" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <EnergyMetricCard
              title="Month-to-Date"
              consumed={data.energy.consumed_mtd}
              produced={data.energy.produced_mtd}
              shared={data.energy.shared_mtd}
            />
            <EnergyMetricCard
              title="Year-to-Date"
              consumed={data.energy.consumed_ytd}
              produced={data.energy.produced_ytd}
              shared={data.energy.shared_ytd}
            />
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Self-Sufficiency Rate
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">
                  {((data.energy.self_consumed_mtd / data.energy.consumed_mtd) * 100).toFixed(1)}%
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  Energy you produced and consumed
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Financial Tab */}
        <TabsContent value="financial" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Total Lifetime Benefit</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  €{data.financial.total_benefit_ytd.toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">{new Date().getFullYear()} year-to-date</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Last Payment</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  €{data.financial.last_payment_amount.toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {data.financial.last_payment_date
                    ? new Date(data.financial.last_payment_date).toLocaleDateString()
                    : 'No payments yet'}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Pending Payment</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  €{data.financial.pending_payments.toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Processing within 30 days</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Payment History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                Payment history feature coming soon
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Invoices Tab */}
        <TabsContent value="invoices" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Your Invoices</CardTitle>
            </CardHeader>
            <CardContent>
              {data.invoices.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No invoices available yet
                </div>
              ) : (
                <div className="space-y-3">
                  {data.invoices.map((invoice) => (
                    <div
                      key={invoice.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="h-5 w-5 text-gray-400" />
                        <div>
                          <div className="font-medium">{invoice.invoice_number}</div>
                          <div className="text-sm text-muted-foreground">
                            {new Date(invoice.date).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <div className="font-semibold">€{invoice.amount.toFixed(2)}</div>
                          <Badge variant={invoice.status === 'paid' ? 'default' : 'outline'} className="text-xs">
                            {invoice.status}
                          </Badge>
                        </div>
                        <Button size="sm" variant="ghost">
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Community Tab */}
        <TabsContent value="community" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Community</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{data.community.cer_name}</div>
                <p className="text-sm text-muted-foreground mt-1">
                  {data.community.total_members} total members
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Total Capacity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{data.community.total_capacity_kw} kW</div>
                <p className="text-sm text-muted-foreground mt-1">Community generation</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Award className="h-4 w-4" />
                  Your Ranking
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">#{data.community.member_rank}</div>
                <p className="text-sm text-muted-foreground mt-1">By energy shared</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Community Announcements</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                No announcements at this time
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Helper Components
const SummaryCard: React.FC<{
  title: string;
  value: string;
  subtitle: string;
  icon: React.ReactNode;
  color?: string;
}> = ({ title, value, subtitle, icon, color = 'text-blue-600' }) => {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-muted-foreground">{title}</span>
          <div className={color}>{icon}</div>
        </div>
        <div className="text-2xl font-bold">{value}</div>
        <div className="text-xs text-muted-foreground mt-1">{subtitle}</div>
      </CardContent>
    </Card>
  );
};

const EnergyMetricCard: React.FC<{
  title: string;
  consumed: number;
  produced: number;
  shared: number;
}> = ({ title, consumed, produced, shared }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Consumed:</span>
          <span className="font-semibold">{consumed.toFixed(0)} kWh</span>
        </div>
        {produced > 0 && (
          <div className="flex justify-between text-sm text-green-600">
            <span>Produced:</span>
            <span className="font-semibold">{produced.toFixed(0)} kWh</span>
          </div>
        )}
        <div className="flex justify-between text-sm text-blue-600">
          <span>Shared:</span>
          <span className="font-semibold">{shared.toFixed(0)} kWh</span>
        </div>
      </CardContent>
    </Card>
  );
};

export default MemberDashboard;
