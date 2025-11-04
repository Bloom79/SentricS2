/**
 * Integrations Page
 * External integrations management
 */

import React, { useState } from 'react';
import {
  Link2,
  Shield,
  Activity,
  FileText,
  RefreshCw,
  Settings,
  CheckCircle,
  XCircle,
  AlertCircle,
  Clock,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Integration {
  id: string;
  name: string;
  status: 'Connected' | 'Disconnected' | 'Error' | 'Maintenance';
  lastSync: string;
  connectionType: string;
  queuedMessages: number;
  errors: number;
}

export default function Integrations() {
  const [integrations] = useState<Integration[]>([
    {
      id: 'gse',
      name: 'GSE',
      status: 'Connected',
      lastSync: '2024-03-15 14:30:22',
      connectionType: 'RPA',
      queuedMessages: 0,
      errors: 0,
    },
    {
      id: 'terna',
      name: 'Terna',
      status: 'Connected',
      lastSync: '2024-03-15 13:45:18',
      connectionType: 'API',
      queuedMessages: 2,
      errors: 0,
    },
    {
      id: 'dogane',
      name: 'Customs',
      status: 'Error',
      lastSync: '2024-03-15 10:15:33',
      connectionType: 'EDI',
      queuedMessages: 5,
      errors: 3,
    },
    {
      id: 'e-distribuzione',
      name: 'E-Distribuzione',
      status: 'Maintenance',
      lastSync: '2024-03-14 22:30:00',
      connectionType: 'PEC',
      queuedMessages: 12,
      errors: 0,
    },
  ]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Connected':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'Disconnected':
        return <XCircle className="h-5 w-5 text-gray-600" />;
      case 'Error':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      case 'Maintenance':
        return <Clock className="h-5 w-5 text-yellow-600" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Connected':
        return 'text-green-600';
      case 'Disconnected':
        return 'text-gray-600';
      case 'Error':
        return 'text-red-600';
      case 'Maintenance':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Integrations</h1>
          <p className="text-muted-foreground mt-1">
            Monitor and manage external system connections
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Sync All
          </Button>
        </div>
      </div>

      {/* Integration Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {integrations.map((integration) => (
          <div
            key={integration.id}
            className="border rounded-lg p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-primary/10 rounded-lg">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{integration.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    {integration.connectionType} Connection
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {getStatusIcon(integration.status)}
                <span className={`text-sm font-medium ${getStatusColor(integration.status)}`}>
                  {integration.status}
                </span>
              </div>
            </div>

            <div className="space-y-2 text-sm mb-4">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Last Sync:</span>
                <span className="font-medium">
                  {new Date(integration.lastSync).toLocaleString()}
                </span>
              </div>
              {integration.queuedMessages > 0 && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Queued:</span>
                  <span className="font-medium text-blue-600">
                    {integration.queuedMessages} messages
                  </span>
                </div>
              )}
              {integration.errors > 0 && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Errors:</span>
                  <span className="font-medium text-red-600">
                    {integration.errors}
                  </span>
                </div>
              )}
            </div>

            <div className="flex gap-2">
              <Button variant="outline" className="flex-1">
                <RefreshCw className="mr-2 h-4 w-4" />
                Test
              </Button>
              <Button className="flex-1">
                <Settings className="mr-2 h-4 w-4" />
                Configure
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


