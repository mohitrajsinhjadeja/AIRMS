"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Shield, 
  Lock, 
  Key, 
  AlertTriangle,
  Clock,
  Globe,
  Smartphone,
  Save
} from 'lucide-react';
import { Badge } from "@/components/ui/badge";

const SecuritySettings = () => {
  const [settings, setSettings] = useState({
    twoFactor: {
      enabled: false,
      method: 'app',
      backupCodes: []
    },
    sessions: {
      maxSessions: 5,
      sessionTimeout: 24,
      requireReauth: true
    },
    ipWhitelist: {
      enabled: false,
      addresses: []
    },
    apiSecurity: {
      rateLimiting: true,
      requestLogging: true,
      ipRestrictions: false
    }
  });
  const [loading, setLoading] = useState(false);
  const [activeSessions, setActiveSessions] = useState([]);
  const [newIpAddress, setNewIpAddress] = useState('');

  useEffect(() => {
    loadSecuritySettings();
    loadActiveSessions();
  }, []);

  const loadSecuritySettings = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      const mockSettings = {
        twoFactor: {
          enabled: true,
          method: 'app',
          backupCodes: ['123456', '789012', '345678']
        },
        sessions: {
          maxSessions: 5,
          sessionTimeout: 24,
          requireReauth: true
        },
        ipWhitelist: {
          enabled: false,
          addresses: ['192.168.1.100', '10.0.0.50']
        },
        apiSecurity: {
          rateLimiting: true,
          requestLogging: true,
          ipRestrictions: false
        }
      };
      setSettings(mockSettings);
    } catch (error) {
      console.error('Failed to load security settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadActiveSessions = async () => {
    try {
      // TODO: Replace with actual API call
      const mockSessions = [
        {
          id: '1',
          device: 'Chrome on Windows',
          location: 'New York, US',
          ip: '192.168.1.100',
          lastActive: '2024-01-20T14:30:00Z',
          current: true
        },
        {
          id: '2',
          device: 'Safari on iPhone',
          location: 'New York, US',
          ip: '192.168.1.101',
          lastActive: '2024-01-20T10:15:00Z',
          current: false
        }
      ];
      setActiveSessions(mockSessions);
    } catch (error) {
      console.error('Failed to load active sessions:', error);
    }
  };

  const updateTwoFactor = (field, value) => {
    setSettings(prev => ({
      ...prev,
      twoFactor: {
        ...prev.twoFactor,
        [field]: value
      }
    }));
  };

  const updateSessions = (field, value) => {
    setSettings(prev => ({
      ...prev,
      sessions: {
        ...prev.sessions,
        [field]: value
      }
    }));
  };

  const updateIpWhitelist = (field, value) => {
    setSettings(prev => ({
      ...prev,
      ipWhitelist: {
        ...prev.ipWhitelist,
        [field]: value
      }
    }));
  };

  const updateApiSecurity = (field, value) => {
    setSettings(prev => ({
      ...prev,
      apiSecurity: {
        ...prev.apiSecurity,
        [field]: value
      }
    }));
  };

  const addIpAddress = () => {
    if (newIpAddress.trim()) {
      updateIpWhitelist('addresses', [...settings.ipWhitelist.addresses, newIpAddress.trim()]);
      setNewIpAddress('');
    }
  };

  const removeIpAddress = (index) => {
    const newAddresses = settings.ipWhitelist.addresses.filter((_, i) => i !== index);
    updateIpWhitelist('addresses', newAddresses);
  };

  const revokeSession = async (sessionId) => {
    try {
      // TODO: Replace with actual API call
      setActiveSessions(prev => prev.filter(session => session.id !== sessionId));
      console.log('Session revoked successfully');
    } catch (error) {
      console.error('Failed to revoke session:', error);
    }
  };

  const saveSettings = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      console.log('Saving security settings:', settings);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('Security settings saved successfully');
    } catch (error) {
      console.error('Failed to save security settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold">Security Settings</h3>
        <p className="text-sm text-muted-foreground">
          Manage your account security and access controls
        </p>
      </div>

      {/* Two-Factor Authentication */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Two-Factor Authentication
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label>Enable Two-Factor Authentication</Label>
              <p className="text-sm text-muted-foreground">Add an extra layer of security to your account</p>
            </div>
            <Switch
              checked={settings.twoFactor.enabled}
              onCheckedChange={(checked) => updateTwoFactor('enabled', checked)}
            />
          </div>
          
          {settings.twoFactor.enabled && (
            <div className="space-y-4 pt-4 border-t">
              <div>
                <Label>Authentication Method</Label>
                <Select value={settings.twoFactor.method} onValueChange={(value) => updateTwoFactor('method', value)}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="app">Authenticator App</SelectItem>
                    <SelectItem value="sms">SMS</SelectItem>
                    <SelectItem value="email">Email</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label>Backup Codes</Label>
                <p className="text-sm text-muted-foreground mb-2">
                  Save these backup codes in a safe place. You can use them to access your account if you lose your device.
                </p>
                <div className="grid grid-cols-3 gap-2">
                  {settings.twoFactor.backupCodes.map((code, index) => (
                    <code key={index} className="text-sm bg-gray-100 p-2 rounded">
                      {code}
                    </code>
                  ))}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Session Management */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="w-5 h-5" />
            Session Management
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Maximum Concurrent Sessions</Label>
              <Input
                type="number"
                value={settings.sessions.maxSessions}
                onChange={(e) => updateSessions('maxSessions', parseInt(e.target.value))}
                min="1"
                max="20"
              />
            </div>
            <div>
              <Label>Session Timeout (hours)</Label>
              <Input
                type="number"
                value={settings.sessions.sessionTimeout}
                onChange={(e) => updateSessions('sessionTimeout', parseInt(e.target.value))}
                min="1"
                max="72"
              />
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <Label>Require Re-authentication for Sensitive Actions</Label>
              <p className="text-sm text-muted-foreground">Prompt for password before performing sensitive operations</p>
            </div>
            <Switch
              checked={settings.sessions.requireReauth}
              onCheckedChange={(checked) => updateSessions('requireReauth', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* IP Whitelist */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lock className="w-5 h-5" />
            IP Whitelist
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label>Enable IP Whitelist</Label>
              <p className="text-sm text-muted-foreground">Allow access only from specific IP addresses</p>
            </div>
            <Switch
              checked={settings.ipWhitelist.enabled}
              onCheckedChange={(checked) => updateIpWhitelist('enabled', checked)}
            />
          </div>
          
          {settings.ipWhitelist.enabled && (
            <div className="space-y-4 pt-4 border-t">
              <div className="flex gap-2">
                <Input
                  placeholder="Enter IP address"
                  value={newIpAddress}
                  onChange={(e) => setNewIpAddress(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addIpAddress()}
                />
                <Button onClick={addIpAddress}>Add</Button>
              </div>
              
              <div className="space-y-2">
                {settings.ipWhitelist.addresses.map((ip, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span>{ip}</span>
                    <Button variant="ghost" size="sm" onClick={() => removeIpAddress(index)}>
                      Remove
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* API Security */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="w-5 h-5" />
            API Security
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label>Rate Limiting</Label>
              <p className="text-sm text-muted-foreground">Prevent abuse by limiting API requests</p>
            </div>
            <Switch
              checked={settings.apiSecurity.rateLimiting}
              onCheckedChange={(checked) => updateApiSecurity('rateLimiting', checked)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <Label>Request Logging</Label>
              <p className="text-sm text-muted-foreground">Log all API requests for monitoring</p>
            </div>
            <Switch
              checked={settings.apiSecurity.requestLogging}
              onCheckedChange={(checked) => updateApiSecurity('requestLogging', checked)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <Label>IP Restrictions</Label>
              <p className="text-sm text-muted-foreground">Restrict API access by IP address</p>
            </div>
            <Switch
              checked={settings.apiSecurity.ipRestrictions}
              onCheckedChange={(checked) => updateApiSecurity('ipRestrictions', checked)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Active Sessions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Smartphone className="w-5 h-5" />
            Active Sessions
          </CardTitle>
        </CardHeader>
        <CardContent>
          {activeSessions.length > 0 ? (
            <div className="space-y-3">
              {activeSessions.map((session) => (
                <div key={session.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex-1">
                    <div className="font-medium">{session.device}</div>
                    <div className="text-sm text-muted-foreground">
                      {session.location} • {session.ip}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Last active: {formatDate(session.lastActive)}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {session.current && (
                      <Badge variant="secondary">Current Session</Badge>
                    )}
                    {!session.current && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => revokeSession(session.id)}
                      >
                        Revoke
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-center py-4">No active sessions found</p>
          )}
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={saveSettings} disabled={loading}>
          <Save className="w-4 h-4 mr-2" />
          {loading ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>
    </div>
  );
};

export default SecuritySettings;
