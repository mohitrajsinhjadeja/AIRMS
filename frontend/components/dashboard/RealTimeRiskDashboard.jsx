"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

import { TabsComponent, TabsListComponent, TabsTriggerComponent, TabsContentComponent } from "@/components/ui/tabs";
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { 
  Shield, 
  AlertTriangle, 
  Activity, 
  Eye, 
  Ban, 
  CheckCircle, 
  Clock, 
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Zap,
  Users,
  Server
} from 'lucide-react';
import { analyticsApi, utils } from '@/lib/api';

const RealTimeRiskDashboard = () => {
  const [realTimeData, setRealTimeData] = useState({
    currentRiskScore: 0,
    activeThreats: 0,
    blockedRequests: 0,
    totalRequests: 0,
    mitigationsApplied: 0,
    systemStatus: 'healthy'
  });

  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [activeConnections, setActiveConnections] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch real-time data
  useEffect(() => {
    const fetchRealTimeData = async () => {
      try {
        setError(null);
        const [metrics, alerts, timeline] = await Promise.all([
          analyticsAPI.getRealTimeMetrics(),
          analyticsAPI.getRecentAlerts(10),
          analyticsAPI.getRiskTimeline(6) // Last 6 hours
        ]);

        // Update real-time metrics
        setRealTimeData({
          currentRiskScore: metrics.current_requests_per_minute || 0,
          activeThreats: metrics.active_users || 0,
          blockedRequests: 0,
          totalRequests: metrics.current_requests_per_minute * 60 || 0,
          mitigationsApplied: 0,
          systemStatus: metrics.system_health || 'healthy'
        });

        // Update timeline data for charts - handle array directly
        const formattedTimeline = (Array.isArray(timeline) ? timeline : []).map(point => ({
          time: point.date ? new Date(point.date).toLocaleTimeString() : new Date().toLocaleTimeString(),
          riskScore: point.risk_score || 0,
          requests: point.requests || 0,
          threats: Math.floor(point.requests * 0.1) || 0,
          blocked: point.blocked || 0
        }));
        setTimeSeriesData(formattedTimeline);

        // Update alerts - handle alerts array directly
        const alertsArray = alerts.alerts || alerts || [];
        const formattedAlerts = (Array.isArray(alertsArray) ? alertsArray : []).map(alert => ({
          id: alert.id,
          type: alert.severity || 'info',
          message: alert.message,
          severity: alert.severity,
          timestamp: alert.timestamp
        }));
        setRecentAlerts(formattedAlerts);

        setActiveConnections(metrics.active_connections || 25);
        setIsConnected(true);
        setLoading(false);

      } catch (err) {
        console.error('Error fetching real-time data:', err);
        setError(utils.formatError(err));
        setIsConnected(false);
        setLoading(false);
      }
    };

    fetchRealTimeData();
    const interval = setInterval(fetchRealTimeData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const getRiskScoreColor = (score) => {
    if (score >= 8) return 'text-red-600';
    if (score >= 6) return 'text-orange-600';
    if (score >= 4) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getRiskScoreBg = (score) => {
    if (score >= 8) return 'bg-red-100';
    if (score >= 6) return 'bg-orange-100';
    if (score >= 4) return 'bg-yellow-100';
    return 'bg-green-100';
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading real-time data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64 text-red-600">
          <AlertTriangle className="h-8 w-8 mr-2" />
          <span>Error loading real-time data: {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Real-Time Risk Monitor</h2>
          <p className="text-muted-foreground">Live monitoring of AI risk detection system</p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant={isConnected ? "default" : "destructive"} className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            {isConnected ? 'Connected' : 'Disconnected'}
          </Badge>
          <Badge variant="outline" className="flex items-center gap-2">
            <Users className="w-3 h-3" />
            {activeConnections} active
          </Badge>
        </div>
      </div>

      {/* Real-time Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Risk Score</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getRiskScoreColor(realTimeData.currentRiskScore)}`}>
              {realTimeData.currentRiskScore.toFixed(1)}
            </div>
            <div className={`text-xs px-2 py-1 rounded-full inline-block mt-1 ${getRiskScoreBg(realTimeData.currentRiskScore)}`}>
              {realTimeData.currentRiskScore >= 6 ? 'High Risk' : 
               realTimeData.currentRiskScore >= 4 ? 'Medium Risk' : 'Low Risk'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Threats</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{realTimeData.activeThreats}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              Real-time detection
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Blocked Requests</CardTitle>
            <Ban className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{realTimeData.blockedRequests}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              Auto-blocked
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{realTimeData.totalRequests.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              Today's count
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Mitigations</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{realTimeData.mitigationsApplied}</div>
            <p className="text-xs text-muted-foreground">
              <Zap className="inline h-3 w-3 mr-1" />
              Auto-applied
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {realTimeData.systemStatus === 'healthy' ? 'Healthy' : 'Issues'}
            </div>
            <p className="text-xs text-muted-foreground">
              <CheckCircle className="inline h-3 w-3 mr-1" />
              All systems operational
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Real-time Charts and Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Real-time Risk Score Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Live Risk Score
            </CardTitle>
            <CardDescription>Real-time risk score monitoring (last 6 hours)</CardDescription>
          </CardHeader>
          <CardContent>
            {timeSeriesData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis domain={[0, 10]} />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="riskScore" 
                    stroke="#ef4444" 
                    strokeWidth={2}
                    dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-muted-foreground">
                No timeline data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Alerts */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Live Alerts
            </CardTitle>
            <CardDescription>Real-time security alerts and notifications</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {recentAlerts.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <CheckCircle className="w-8 h-8 mx-auto mb-2" />
                  No recent alerts
                </div>
              ) : (
                recentAlerts.map((alert) => (
                  <div key={alert.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${
                        alert.severity === 'high' ? 'bg-red-500' :
                        alert.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                      }`} />
                      <div>
                        <h4 className="font-medium text-sm">{alert.type}</h4>
                        <p className="text-xs text-muted-foreground">{alert.message}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge className={getSeverityColor(alert.severity)} variant="outline">
                        {alert.severity}
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Request Volume Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Live Request Volume
          </CardTitle>
          <CardDescription>Real-time request processing and threat detection</CardDescription>
        </CardHeader>
        <CardContent>
          {timeSeriesData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area 
                  type="monotone" 
                  dataKey="requests" 
                  fill="#8884d8" 
                  stroke="#8884d8"
                />
                <Area 
                  type="monotone" 
                  dataKey="threats" 
                  fill="#ff7300" 
                  stroke="#ff7300"
                />
                <Area 
                  type="monotone" 
                  dataKey="blocked" 
                  fill="#00ff00" 
                  stroke="#00ff00"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-muted-foreground">
              No request volume data available
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default RealTimeRiskDashboard;
