"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { 
  User, 
  Mail, 
  Globe, 
  Bell, 
  Save,
  Settings
} from 'lucide-react';

const GeneralSettings = () => {
  const [settings, setSettings] = useState({
    profile: {
      name: '',
      email: '',
      company: '',
      timezone: 'UTC',
      language: 'en'
    },
    notifications: {
      emailAlerts: true,
      riskThresholdAlerts: true,
      weeklyReports: false,
      systemUpdates: true
    },
    preferences: {
      theme: 'light',
      dateFormat: 'MM/DD/YYYY',
      defaultDashboard: 'overview'
    }
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      const mockSettings = {
        profile: {
          name: 'John Doe',
          email: 'john.doe@example.com',
          company: 'Acme Corp',
          timezone: 'America/New_York',
          language: 'en'
        },
        notifications: {
          emailAlerts: true,
          riskThresholdAlerts: true,
          weeklyReports: false,
          systemUpdates: true
        },
        preferences: {
          theme: 'light',
          dateFormat: 'MM/DD/YYYY',
          defaultDashboard: 'overview'
        }
      };
      setSettings(mockSettings);
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = (field, value) => {
    setSettings(prev => ({
      ...prev,
      profile: {
        ...prev.profile,
        [field]: value
      }
    }));
  };

  const updateNotifications = (field, value) => {
    setSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [field]: value
      }
    }));
  };

  const updatePreferences = (field, value) => {
    setSettings(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [field]: value
      }
    }));
  };

  const saveSettings = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      console.log('Saving settings:', settings);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('Settings saved successfully');
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold">General Settings</h3>
        <p className="text-sm text-muted-foreground">
          Manage your account preferences and notification settings
        </p>
      </div>

      {/* Profile Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-5 h-5" />
            Profile Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                value={settings.profile.name}
                onChange={(e) => updateProfile('name', e.target.value)}
                placeholder="Enter your full name"
              />
            </div>
            <div>
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={settings.profile.email}
                onChange={(e) => updateProfile('email', e.target.value)}
                placeholder="Enter your email"
              />
            </div>
            <div>
              <Label htmlFor="company">Company</Label>
              <Input
                id="company"
                value={settings.profile.company}
                onChange={(e) => updateProfile('company', e.target.value)}
                placeholder="Enter your company name"
              />
            </div>
            <div>
              <Label htmlFor="timezone">Timezone</Label>
              <Select value={settings.profile.timezone} onValueChange={(value) => updateProfile('timezone', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select timezone" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="UTC">UTC</SelectItem>
                  <SelectItem value="America/New_York">Eastern Time</SelectItem>
                  <SelectItem value="America/Chicago">Central Time</SelectItem>
                  <SelectItem value="America/Denver">Mountain Time</SelectItem>
                  <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                  <SelectItem value="Europe/London">London</SelectItem>
                  <SelectItem value="Europe/Paris">Paris</SelectItem>
                  <SelectItem value="Asia/Tokyo">Tokyo</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Notification Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="emailAlerts">Email Alerts</Label>
                <p className="text-sm text-muted-foreground">Receive email notifications for important events</p>
              </div>
              <Switch
                id="emailAlerts"
                checked={settings.notifications.emailAlerts}
                onCheckedChange={(checked) => updateNotifications('emailAlerts', checked)}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="riskThresholdAlerts">Risk Threshold Alerts</Label>
                <p className="text-sm text-muted-foreground">Get notified when risk scores exceed thresholds</p>
              </div>
              <Switch
                id="riskThresholdAlerts"
                checked={settings.notifications.riskThresholdAlerts}
                onCheckedChange={(checked) => updateNotifications('riskThresholdAlerts', checked)}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="weeklyReports">Weekly Reports</Label>
                <p className="text-sm text-muted-foreground">Receive weekly summary reports</p>
              </div>
              <Switch
                id="weeklyReports"
                checked={settings.notifications.weeklyReports}
                onCheckedChange={(checked) => updateNotifications('weeklyReports', checked)}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="systemUpdates">System Updates</Label>
                <p className="text-sm text-muted-foreground">Get notified about system updates and maintenance</p>
              </div>
              <Switch
                id="systemUpdates"
                checked={settings.notifications.systemUpdates}
                onCheckedChange={(checked) => updateNotifications('systemUpdates', checked)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Application Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="theme">Theme</Label>
              <Select value={settings.preferences.theme} onValueChange={(value) => updatePreferences('theme', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select theme" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">Light</SelectItem>
                  <SelectItem value="dark">Dark</SelectItem>
                  <SelectItem value="system">System</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="dateFormat">Date Format</Label>
              <Select value={settings.preferences.dateFormat} onValueChange={(value) => updatePreferences('dateFormat', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select date format" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                  <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                  <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="defaultDashboard">Default Dashboard</Label>
              <Select value={settings.preferences.defaultDashboard} onValueChange={(value) => updatePreferences('defaultDashboard', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select default dashboard" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="overview">Overview</SelectItem>
                  <SelectItem value="analytics">Analytics</SelectItem>
                  <SelectItem value="logs">Risk Logs</SelectItem>
                  <SelectItem value="monitor">Real-time Monitor</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button 
          onClick={saveSettings}
          disabled={loading}
          className="px-6"
        >
          <Save className="w-4 h-4 mr-2" />
          {loading ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>
    </div>
  );
};

export default GeneralSettings;