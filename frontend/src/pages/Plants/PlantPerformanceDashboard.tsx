/**
 * Plant Performance Dashboard
 * Real-time monitoring, production analytics, and performance KPIs
 * BUSINESS VALUE: Detect issues early, optimize production, prevent €100K+ losses
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import {
  TrendingUp,
  TrendingDown,
  Zap,
  Sun,
  AlertTriangle,
  CheckCircle2,
  Activity,
  Calendar,
  DollarSign,
  Gauge,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { DateRangePicker, DateRange } from '@/components/ui/date-range-picker';
import { apiClient } from '@/services/api/apiClient';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface PlantPerformanceData {
  // Real-time metrics
  current_power: number; // kW
  today_production: number; // kWh
  today_revenue: number; // EUR
  status: 'operational' | 'degraded' | 'offline' | 'maintenance';

  // Performance KPIs
  performance_ratio: number; // %
  availability: number; // %
  capacity_factor: number; // %

  // Production data
  daily_production: Array<{
    date: string;
    production: number; // kWh
    forecast: number; // kWh
    irradiance: number; // W/m²
  }>;

  // Alerts and issues
  active_alerts: Array<{
    id: number;
    severity: 'critical' | 'high' | 'medium' | 'low';
    message: string;
    timestamp: string;
  }>;

  // Financial
  mtd_revenue: number; // Month-to-date
  ytd_revenue: number; // Year-to-date
  estimated_monthly: number;

  // Environmental
  co2_avoided: number; // tons
  trees_equivalent: number;
}

export const PlantPerformanceDashboard: React.FC = () => {
  const { plantId } = useParams<{ plantId: string }>();
  const [dateRange, setDateRange] = useState<DateRange>({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    to: new Date(),
  });
  const [refreshInterval, setRefreshInterval] = useState(300000); // 5 minutes

  // Fetch performance data
  const { data, isLoading, error } = useQuery<PlantPerformanceData>({
    queryKey: ['plant', 'performance', plantId, dateRange],
    queryFn: async () => {
      const response = await apiClient.get(`/plants/${plantId}/performance`, {
        params: {
          from: dateRange.from?.toISOString(),
          to: dateRange.to?.toISOString(),
        },
      });
      return response.data;
    },
    refetchInterval: refreshInterval, // Auto-refresh
  });

  if (isLoading) {
    return <div className="p-8 text-center">Loading performance data...</div>;
  }

  if (error || !data) {
    return <div className="p-8 text-center text-red-600">Failed to load performance data</div>;
  }

  const statusColors = {
    operational: 'bg-green-100 text-green-700',
    degraded: 'bg-yellow-100 text-yellow-700',
    offline: 'bg-red-100 text-red-700',
    maintenance: 'bg-blue-100 text-blue-700',
  };

  const alertSeverityColors = {
    critical: 'bg-red-100 text-red-700 border-red-300',
    high: 'bg-orange-100 text-orange-700 border-orange-300',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    low: 'bg-blue-100 text-blue-700 border-blue-300',
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header with Status and Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Plant Performance Dashboard</h1>
          <div className="flex items-center gap-3 mt-2">
            <Badge className={statusColors[data.status]} variant="outline">
              {data.status.toUpperCase()}
            </Badge>
            <span className="text-sm text-muted-foreground">
              Last updated: {new Date().toLocaleTimeString()}
            </span>
          </div>
        </div>
        <div className="flex gap-3">
          <DateRangePicker value={dateRange} onChange={setDateRange} />
          <select
            className="border rounded px-3 py-2 text-sm"
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
          >
            <option value={60000}>Refresh: 1 min</option>
            <option value={300000}>Refresh: 5 min</option>
            <option value={600000}>Refresh: 10 min</option>
            <option value={0}>Manual</option>
          </select>
        </div>
      </div>

      {/* Active Alerts */}
      {data.active_alerts.length > 0 && (
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-700">
              <AlertTriangle className="h-5 w-5" />
              Active Alerts ({data.active_alerts.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.active_alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-3 rounded border ${alertSeverityColors[alert.severity]}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-medium">{alert.message}</div>
                      <div className="text-xs mt-1">
                        {new Date(alert.timestamp).toLocaleString()}
                      </div>
                    </div>
                    <Badge variant="outline" className="uppercase text-xs">
                      {alert.severity}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Real-time Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Current Power"
          value={`${data.current_power.toFixed(1)} kW`}
          icon={<Zap className="h-5 w-5" />}
          trend={data.current_power > 0 ? 'up' : 'neutral'}
          color="text-blue-600"
        />
        <MetricCard
          title="Today's Production"
          value={`${data.today_production.toFixed(1)} kWh`}
          icon={<Sun className="h-5 w-5" />}
          subtitle={`€${data.today_revenue.toFixed(2)} revenue`}
          color="text-green-600"
        />
        <MetricCard
          title="Performance Ratio"
          value={`${data.performance_ratio.toFixed(1)}%`}
          icon={<Gauge className="h-5 w-5" />}
          trend={data.performance_ratio >= 75 ? 'up' : 'down'}
          subtitle={data.performance_ratio >= 75 ? 'Excellent' : 'Needs attention'}
          color={data.performance_ratio >= 75 ? 'text-green-600' : 'text-orange-600'}
        />
        <MetricCard
          title="Availability"
          value={`${data.availability.toFixed(1)}%`}
          icon={<Activity className="h-5 w-5" />}
          trend={data.availability >= 95 ? 'up' : 'down'}
          color={data.availability >= 95 ? 'text-green-600' : 'text-orange-600'}
        />
      </div>

      {/* Tabs for Different Views */}
      <Tabs defaultValue="production" className="space-y-4">
        <TabsList>
          <TabsTrigger value="production">Production</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="financial">Financial</TabsTrigger>
          <TabsTrigger value="environmental">Environmental</TabsTrigger>
        </TabsList>

        {/* Production Tab */}
        <TabsContent value="production" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Daily Production vs Forecast</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={data.daily_production}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis label={{ value: 'kWh', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="forecast"
                    stroke="#94a3b8"
                    fill="#e2e8f0"
                    name="Forecast"
                  />
                  <Area
                    type="monotone"
                    dataKey="production"
                    stroke="#3b82f6"
                    fill="#60a5fa"
                    name="Actual Production"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Production vs Solar Irradiance</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data.daily_production}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis yAxisId="left" label={{ value: 'kWh', angle: -90, position: 'insideLeft' }} />
                  <YAxis yAxisId="right" orientation="right" label={{ value: 'W/m²', angle: 90, position: 'insideRight' }} />
                  <Tooltip />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="production"
                    stroke="#3b82f6"
                    name="Production (kWh)"
                    strokeWidth={2}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="irradiance"
                    stroke="#f59e0b"
                    name="Irradiance (W/m²)"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <PerformanceKPI
              title="Performance Ratio"
              value={data.performance_ratio}
              unit="%"
              target={80}
              description="Actual vs theoretical production"
            />
            <PerformanceKPI
              title="Availability"
              value={data.availability}
              unit="%"
              target={95}
              description="Uptime percentage"
            />
            <PerformanceKPI
              title="Capacity Factor"
              value={data.capacity_factor}
              unit="%"
              target={20}
              description="Average power vs peak capacity"
            />
          </div>
        </TabsContent>

        {/* Financial Tab */}
        <TabsContent value="financial" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Month-to-Date Revenue
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">€{data.mtd_revenue.toLocaleString()}</div>
                <div className="text-sm text-muted-foreground mt-1">
                  Estimated monthly: €{data.estimated_monthly.toLocaleString()}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Year-to-Date Revenue
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">€{data.ytd_revenue.toLocaleString()}</div>
                <div className="text-sm text-muted-foreground mt-1">
                  {new Date().toLocaleDateString('en-US', { year: 'numeric' })}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Today's Revenue
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">€{data.today_revenue.toFixed(2)}</div>
                <div className="text-sm text-muted-foreground mt-1">
                  {data.today_production.toFixed(1)} kWh produced
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Environmental Tab */}
        <TabsContent value="environmental" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>CO₂ Emissions Avoided</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold text-green-600">
                  {data.co2_avoided.toFixed(1)} tons
                </div>
                <div className="text-sm text-muted-foreground mt-2">
                  Equivalent to {data.trees_equivalent.toLocaleString()} trees planted
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Environmental Impact</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm">Clean Energy Produced</span>
                    <span className="font-semibold">{data.today_production.toLocaleString()} kWh</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Fossil Fuel Offset</span>
                    <span className="font-semibold">{(data.today_production * 0.4).toFixed(0)} kg coal</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Homes Powered</span>
                    <span className="font-semibold">{Math.floor(data.today_production / 30)} homes/day</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Helper Components
const MetricCard: React.FC<{
  title: string;
  value: string;
  icon: React.ReactNode;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  color?: string;
}> = ({ title, value, icon, subtitle, trend, color = 'text-blue-600' }) => {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-muted-foreground">{title}</span>
          <div className={color}>{icon}</div>
        </div>
        <div className="flex items-baseline gap-2">
          <div className="text-2xl font-bold">{value}</div>
          {trend && trend !== 'neutral' && (
            <div className={trend === 'up' ? 'text-green-600' : 'text-red-600'}>
              {trend === 'up' ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
            </div>
          )}
        </div>
        {subtitle && <div className="text-xs text-muted-foreground mt-1">{subtitle}</div>}
      </CardContent>
    </Card>
  );
};

const PerformanceKPI: React.FC<{
  title: string;
  value: number;
  unit: string;
  target: number;
  description: string;
}> = ({ title, value, unit, target, description }) => {
  const percentage = (value / target) * 100;
  const status = value >= target ? 'good' : value >= target * 0.9 ? 'warning' : 'critical';

  const statusColors = {
    good: 'bg-green-500',
    warning: 'bg-yellow-500',
    critical: 'bg-red-500',
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold">{value.toFixed(1)}</span>
          <span className="text-lg text-muted-foreground">{unit}</span>
        </div>
        <div className="space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Target: {target}{unit}</span>
            <span className={status === 'good' ? 'text-green-600' : status === 'warning' ? 'text-yellow-600' : 'text-red-600'}>
              {percentage.toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${statusColors[status]}`}
              style={{ width: `${Math.min(100, percentage)}%` }}
            />
          </div>
        </div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
};

export default PlantPerformanceDashboard;
