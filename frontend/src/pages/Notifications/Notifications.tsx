/**
 * Notifications Page
 * User notifications and alerts center
 */

import React, { useState, useEffect } from 'react';
import { Bell, Check, X, AlertCircle, Info, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import apiClient from '@/services/api/apiClient';

interface Notification {
  id: number;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  read: boolean;
  created_at: string;
  link?: string;
}

export default function Notifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/notifications');
      setNotifications(response.data || []);
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (id: number) => {
    try {
      await apiClient.patch(`/notifications/${id}/read`);
      setNotifications(notifications.map((n) => (n.id === id ? { ...n, read: true } : n)));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await apiClient.post('/notifications/read-all');
      setNotifications(notifications.map((n) => ({ ...n, read: true })));
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />;
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      default:
        return <Info className="h-5 w-5 text-blue-600" />;
    }
  };

  const filteredNotifications = notifications.filter((n) => filter === 'all' || !n.read);

  const unreadCount = notifications.filter((n) => !n.read).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Notifications</h1>
          <p className="text-muted-foreground mt-1">All notifications and system alerts</p>
        </div>
        <div className="flex gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'unread')}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="all">All</option>
            <option value="unread">Unread ({unreadCount})</option>
          </select>
          {unreadCount > 0 && (
            <Button variant="outline" onClick={markAllAsRead}>
              Mark All as Read
            </Button>
          )}
        </div>
      </div>

      {/* Notifications List */}
      <div className="space-y-2">
        {filteredNotifications.map((notification) => (
          <div
            key={notification.id}
            className={`border rounded-lg p-4 flex items-start gap-4 ${
              !notification.read ? 'bg-primary/5 border-primary/20' : ''
            }`}
          >
            <div className="mt-1">{getIcon(notification.type)}</div>
            <div className="flex-1">
              <h3 className="font-semibold">{notification.title}</h3>
              <p className="text-sm text-muted-foreground mt-1">{notification.message}</p>
              <p className="text-xs text-muted-foreground mt-2">
                {new Date(notification.created_at).toLocaleString()}
              </p>
            </div>
            {!notification.read && (
              <Button variant="ghost" size="sm" onClick={() => markAsRead(notification.id)}>
                <Check className="h-4 w-4" />
              </Button>
            )}
          </div>
        ))}
      </div>

      {filteredNotifications.length === 0 && (
        <div className="text-center py-12">
          <Bell className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No notifications</p>
        </div>
      )}
    </div>
  );
}
