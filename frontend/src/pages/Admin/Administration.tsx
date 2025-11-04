/**
 * Administration Page
 * System administration and configuration
 */

import React from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  Settings,
  Shield,
  Database,
  Key,
  Globe,
  Activity,
  HardDrive,
  Mail,
  FileText,
  ChevronRight,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface AdminCard {
  title: string;
  description: string;
  icon: React.ElementType;
  link: string;
  color: string;
  available: boolean;
}

export default function Administration() {
  const { user } = useAuth();

  const adminCards: AdminCard[] = [
    {
      title: 'User Management',
      description: 'Manage users, roles, and permissions',
      icon: Users,
      link: '/admin/users',
      color: 'blue',
      available: true,
    },
    {
      title: 'System Configuration',
      description: 'General settings and system parameters',
      icon: Settings,
      link: '/admin/settings',
      color: 'purple',
      available: false,
    },
    {
      title: 'Security',
      description: 'Security policies and audit logs',
      icon: Shield,
      link: '/admin/security',
      color: 'green',
      available: false,
    },
    {
      title: 'Database',
      description: 'Backup, maintenance, and optimization',
      icon: Database,
      link: '/admin/database',
      color: 'orange',
      available: false,
    },
    {
      title: 'API Keys',
      description: 'Manage API keys and external integrations',
      icon: Key,
      link: '/admin/api-keys',
      color: 'red',
      available: false,
    },
    {
      title: 'Multi-Tenant',
      description: 'Manage tenants and dedicated configurations',
      icon: Globe,
      link: '/admin/tenants',
      color: 'indigo',
      available: false,
    },
    {
      title: 'Monitoring',
      description: 'System performance and usage metrics',
      icon: Activity,
      link: '/admin/monitoring',
      color: 'yellow',
      available: false,
    },
    {
      title: 'Storage',
      description: 'Storage space and archived documents',
      icon: HardDrive,
      link: '/admin/storage',
      color: 'gray',
      available: false,
    },
    {
      title: 'Email',
      description: 'Email notification configuration and templates',
      icon: Mail,
      link: '/admin/email',
      color: 'pink',
      available: false,
    },
    {
      title: 'System Logs',
      description: 'View and analyze system logs',
      icon: FileText,
      link: '/admin/logs',
      color: 'cyan',
      available: false,
    },
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, string> = {
      blue: 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400',
      purple: 'bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-400',
      green: 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-400',
      orange: 'bg-orange-100 dark:bg-orange-900 text-orange-600 dark:text-orange-400',
      red: 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-400',
      indigo: 'bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-400',
      yellow: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-600 dark:text-yellow-400',
      gray: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400',
      pink: 'bg-pink-100 dark:bg-pink-900 text-pink-600 dark:text-pink-400',
      cyan: 'bg-cyan-100 dark:bg-cyan-900 text-cyan-600 dark:text-cyan-400',
    };
    return colors[color] || colors.gray;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Administration</h1>
        <p className="text-muted-foreground mt-1">
          System administration and configuration
        </p>
      </div>

      {/* Admin Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {adminCards.map((card) => {
          const Icon = card.icon;
          return (
            <Link
              key={card.link}
              to={card.available ? card.link : '#'}
              className={`border rounded-lg p-6 hover:shadow-md transition-all ${
                card.available
                  ? 'cursor-pointer hover:border-primary'
                  : 'opacity-60 cursor-not-allowed'
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-lg ${getColorClasses(card.color)}`}>
                  <Icon className="h-6 w-6" />
                </div>
                {card.available && (
                  <ChevronRight className="h-5 w-5 text-muted-foreground" />
                )}
                {!card.available && (
                  <span className="text-xs bg-muted px-2 py-1 rounded">
                    Coming Soon
                  </span>
                )}
              </div>
              <h3 className="font-semibold text-lg mb-2">{card.title}</h3>
              <p className="text-sm text-muted-foreground">{card.description}</p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}


