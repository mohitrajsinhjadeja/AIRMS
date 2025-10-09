import { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';

import { TabsComponent, TabsListComponent, TabsTriggerComponent, TabsContentComponent } from "@/components/ui/tabs";

import { 
  Shield, 
  Bell, 
  Mail, 
  Webhook, 
  Settings, 
  AlertTriangle,
  CheckCircle,
  Activity,
  Save,
  TestTube
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const RiskMonitorSettingsPage = () => {
  const [settings, setSettings] = useState({
    // Risk Detection Settings
    riskThresholds: {
      low: 3.0,
      medium: 6.0,
      high: 8.0,
      critical: 9.5
    },
    
    // Alert Settings
    alertSettings: {
      emailEnabled: true,
      webhookEnabled: false,
      realTimeAlerts: true,
      dailyDigest: true,
      weeklyReport: false
    },
    
    // Notification Channels
    notificationChannels: {
      email: 'user@example.com',
      webhookUrl: '',
      slackWebhook: '',
      discordWebhook: ''
    },
    
    // Monitoring Rules
    monitoringRules: [
      {
        id: 1,
        name: 'High Risk Content',
        condition: 'risk_score >= 8.0',
        action: 'block_and_alert',
        enabled: true
      },
      {
        id: 2,
        name: 'PII Detection',
        condition: 'contains_pii == true',
        action: 'sanitize_and_log',
        enabled: true
      },
      {
        id: 3,
        name: 'Bias Detection',
        condition: 'bias_score >= 7.0',
        action: 'flag_and_review',
        enabled: false
      }
    ],
    
    // Auto-mitigation
    autoMitigation: {
      enabled: true,
      sanitizePII: true,
      blockHighRisk: true,
      quarantineSuspicious: false
    }
  });

  const [loading, setLoading] = useState(false);
  const [testingNotification, setTestingNotification] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      const response = await fetch('/api/v1/settings/risk-monitor', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSettings(prev => ({ ...prev, ...data }));
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
      toast({
        title: "Error",
        description: "Failed to load risk monitor settings",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      const response = await fetch('/api/v1/settings/risk-monitor', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Risk monitor settings saved successfully"
        });
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast({
        title: "Error",
        description: "Failed to save risk monitor settings",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const testNotification = async (type) => {
    try {
      setTestingNotification(true);
      // TODO: Replace with actual API call
      const response = await fetch(`/api/v1/test-notification/${type}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        toast({
          title: "Test Sent",
          description: `Test ${type} notification sent successfully`
        });
      } else {
        throw new Error(`Failed to send test ${type}`);
      }
    } catch (error) {
      console.error(`Failed to test ${type}:`, error);
      toast({
        title: "Error",
        description: `Failed to send test ${type} notification`,
        variant: "destructive"
      });
    } finally {
      setTestingNotification(false);
    }
  };

  const updateRiskThreshold = (level, value) => {
    setSettings(prev => ({
      ...prev,
      riskThresholds: {
        ...prev.riskThresholds,
        [level]: parseFloat(value)
      }
    }));
  };

  const updateAlertSetting = (key, value) => {
    setSettings(prev => ({
      ...prev,
      alertSettings: {
        ...prev.alertSettings,
        [key]: value
      }
    }));
  };

  const updateNotificationChannel = (channel, value) => {
    setSettings(prev => ({
      ...prev,
      notificationChannels: {
        ...prev.notificationChannels,
        [channel]: value
      }
    }));
  };

  const updateAutoMitigation = (key, value) => {
    setSettings(prev => ({
      ...prev,
      autoMitigation: {
        ...prev.autoMitigation,
        [key]: value
      }
    }));
  };

  const toggleMonitoringRule = (ruleId) => {
    setSettings(prev => ({
      ...prev,
      monitoringRules: prev.monitoringRules.map(rule =>
        rule.id === ruleId ? { ...rule, enabled: !rule.enabled } : rule
      )
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Risk Monitor Settings</h2>
          <p className="text-gray-600">Configure risk detection thresholds and alert preferences</p>
        </div>
        <Badge variant="secondary" className="flex items-center gap-2">
          <Activity className="w-4 h-4" />
          Live Monitoring
        </Badge>
      </div>

      <Tabs defaultValue="thresholds" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="thresholds">Risk Thresholds</TabsTrigger>
          <TabsTrigger value="alerts">Alert Settings</TabsTrigger>
          <TabsTrigger value="rules">Monitoring Rules</TabsTrigger>
          <TabsTrigger value="mitigation">Auto-Mitigation</TabsTrigger>
        </TabsList>

        <TabsContent value="thresholds" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Risk Score Thresholds
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(settings.riskThresholds).map(([level, value]) => (
                  <div key={level} className="space-y-2">
                    <Label htmlFor={`threshold-${level}`} className="capitalize">
                      {level} Risk
                    </Label>
                    <Input
                      id={`threshold-${level}`}
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      value={value}
                      onChange={(e) => updateRiskThreshold(level, e.target.value)}
                    />
                    <p className="text-xs text-gray-500">
                      Score ≥ {value}
                    </p>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium mb-2">Risk Level Preview</h4>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-sm">Low: 0 - {settings.riskThresholds.low}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <span className="text-sm">Medium: {settings.riskThresholds.low} - {settings.riskThresholds.medium}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                    <span className="text-sm">High: {settings.riskThresholds.medium} - {settings.riskThresholds.high}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <span className="text-sm">Critical: {settings.riskThresholds.high}+</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="w-5 h-5" />
                Alert Preferences
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-medium">Alert Types</h4>
                  {Object.entries(settings.alertSettings).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <Label htmlFor={`alert-${key}`} className="capitalize">
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </Label>
                      <Switch
                        id={`alert-${key}`}
                        checked={value}
                        onCheckedChange={(checked) => updateAlertSetting(key, checked)}
                      />
                    </div>
                  ))}
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-medium">Notification Channels</h4>
                  <div className="space-y-3">
                    <div>
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        placeholder="user@example.com"
                        value={settings.notificationChannels.email}
                        onChange={(e) => updateNotificationChannel('email', e.target.value)}
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="webhook">Webhook URL</Label>
                      <Input
                        id="webhook"
                        placeholder="https://your-webhook-url.com"
                        value={settings.notificationChannels.webhookUrl}
                        onChange={(e) => updateNotificationChannel('webhookUrl', e.target.value)}
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="slack">Slack Webhook</Label>
                      <Input
                        id="slack"
                        placeholder="https://hooks.slack.com/services/..."
                        value={settings.notificationChannels.slackWebhook}
                        onChange={(e) => updateNotificationChannel('slackWebhook', e.target.value)}
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="discord">Discord Webhook</Label>
                      <Input
                        id="discord"
                        placeholder="https://discord.com/api/webhooks/..."
                        value={settings.notificationChannels.discordWebhook}
                        onChange={(e) => updateNotificationChannel('discordWebhook', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex gap-2 pt-4">
                <Button 
                  onClick={() => testNotification('email')}
                  disabled={testingNotification}
                  size="sm"
                >
                  <Mail className="w-4 h-4 mr-2" />
                  Test Email
                </Button>
                <Button 
                  onClick={() => testNotification('webhook')}
                  disabled={testingNotification}
                  size="sm"
                >
                  <Webhook className="w-4 h-4 mr-2" />
                  Test Webhook
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rules" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Monitoring Rules
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {settings.monitoringRules.map((rule) => (
                  <div key={rule.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-medium">{rule.name}</h4>
                          <Badge variant={rule.enabled ? "default" : "secondary"}>
                            {rule.enabled ? 'Enabled' : 'Disabled'}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          Condition: <code>{rule.condition}</code>
                        </p>
                        <p className="text-sm text-gray-600">
                          Action: <code>{rule.action}</code>
                        </p>
                      </div>
                      <Switch
                        checked={rule.enabled}
                        onCheckedChange={() => toggleMonitoringRule(rule.id)}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="mitigation" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Auto-Mitigation Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="font-medium">Auto-Mitigation Enabled</Label>
                    <p className="text-sm text-muted-foreground">Automatically handle detected risks</p>
                  </div>
                  <Switch
                    checked={settings.autoMitigation.enabled}
                    onCheckedChange={(checked) => updateAutoMitigation('enabled', checked)}
                  />
                </div>
                
                <div className="pt-4 space-y-4">
                  <h4 className="font-medium">Automatic Actions</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="sanitize-pii">Sanitize PII Data</Label>
                      <Switch
                        id="sanitize-pii"
                        checked={settings.autoMitigation.sanitizePII}
                        onCheckedChange={(checked) => updateAutoMitigation('sanitizePII', checked)}
                      />
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <Label htmlFor="block-high-risk">Block High-Risk Content</Label>
                      <Switch
                        id="block-high-risk"
                        checked={settings.autoMitigation.blockHighRisk}
                        onCheckedChange={(checked) => updateAutoMitigation('blockHighRisk', checked)}
                      />
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <Label htmlFor="quarantine-suspicious">Quarantine Suspicious Content</Label>
                      <Switch
                        id="quarantine-suspicious"
                        checked={settings.autoMitigation.quarantineSuspicious}
                        onCheckedChange={(checked) => updateAutoMitigation('quarantineSuspicious', checked)}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="flex justify-end">
        <Button 
          onClick={saveSettings}
          disabled={loading}
          className="px-6"
        >
          <Save className="w-4 h-4 mr-2" />
          {loading ? 'Saving...' : 'Save All Settings'}
        </Button>
      </div>
    </div>
  );
};

export default RiskMonitorSettingsPage;
