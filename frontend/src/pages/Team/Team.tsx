/**
 * Team Page
 * Team management and collaboration
 */

import { useState, useEffect } from 'react';
import { Users, UserPlus, Mail, Phone, Shield, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import apiClient from '@/services/api/apiClient';

interface TeamMember {
  id: number;
  name: string;
  email: string;
  role: string;
  phone?: string;
  avatar_url?: string;
  status: string;
  last_active?: string;
}

export default function Team() {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTeam();
  }, []);

  const loadTeam = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/users');
      setMembers(response.data || []);
    } catch (error) {
      console.error('Error loading team:', error);
    } finally {
      setLoading(false);
    }
  };

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
          <h1 className="text-3xl font-bold">Team</h1>
          <p className="text-muted-foreground mt-1">Manage team members, roles, and permissions</p>
        </div>
        <Button>
          <UserPlus className="mr-2 h-4 w-4" />
          Invite Member
        </Button>
      </div>

      {/* Team Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {members.map((member) => (
          <div key={member.id} className="border rounded-lg p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                  {member.avatar_url ? (
                    <img
                      src={member.avatar_url}
                      alt={member.name}
                      className="h-12 w-12 rounded-full"
                    />
                  ) : (
                    <span className="text-lg font-medium">
                      {member.name.charAt(0).toUpperCase()}
                    </span>
                  )}
                </div>
                <div>
                  <h3 className="font-semibold">{member.name}</h3>
                  <p className="text-sm text-muted-foreground">{member.email}</p>
                </div>
              </div>
              {member.status === 'ACTIVE' && <CheckCircle className="h-5 w-5 text-green-600" />}
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Role:</span>
                <span className="font-medium">{member.role}</span>
              </div>
              {member.phone && (
                <div className="flex items-center gap-2">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">{member.phone}</span>
                </div>
              )}
              {member.last_active && (
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">Last active:</span>
                  <span className="font-medium">
                    {new Date(member.last_active).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>

            <div className="flex gap-2 mt-4">
              <Button variant="outline" size="sm" className="flex-1">
                <Mail className="mr-2 h-4 w-4" />
                Contact
              </Button>
              <Button variant="outline" size="sm">
                View
              </Button>
            </div>
          </div>
        ))}
      </div>

      {members.length === 0 && (
        <div className="text-center py-12">
          <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No team members found</p>
        </div>
      )}
    </div>
  );
}
