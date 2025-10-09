'use client'

import { useState, useEffect } from 'react'
import { analyticsApi } from '@/lib/api'
import { ModernCard, ModernCardContent, ModernCardHeader, ModernCardTitle, ModernCardDescription } from '@/components/ui/modern-card'
import { MetricCard } from '@/components/ui/metric-card'
import { formatNumber, formatRiskScore, getRiskLevel } from '@/lib/utils'
import { 
  ChartBarIcon, 
  ShieldExclamationIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  SparklesIcon,
  FireIcon,
  BoltIcon,
  ShieldCheckIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'

interface DashboardStats {
  total_requests: number
  high_risk_requests: number
  blocked_requests: number
  avg_risk_score: number
  total_users: number
  active_users: number
}

interface TimelineEntry {
  date: string
  requests: number
  risk_score: number
  blocked: number
}

interface RealTimeStats {
  current_requests_per_minute: number
  active_users: number
  avg_response_time: number
  system_health: string
  last_updated: string
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [timeline, setTimeline] = useState<TimelineEntry[]>([])
  const [realTimeStats, setRealTimeStats] = useState<RealTimeStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsResponse, timelineResponse, realTimeResponse] = await Promise.all([
          analyticsApi.statistics(30),
          analyticsApi.getRiskTimeline(30),
          analyticsApi.getRealTimeMetrics()
        ]);
        
        setStats(statsResponse.data);
        setTimeline(timelineResponse.data);
        setRealTimeStats(realTimeResponse.data);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        {/* Loading Header */}
        <div className="text-center space-y-4">
          <div className="w-16 h-16 mx-auto bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl animate-pulse"></div>
          <div className="space-y-2">
            <div className="h-8 bg-white/20 rounded-lg w-64 mx-auto animate-pulse"></div>
            <div className="h-4 bg-white/10 rounded w-48 mx-auto animate-pulse"></div>
          </div>
        </div>
        
        {/* Loading Metrics */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <ModernCard key={i} className="animate-pulse">
              <ModernCardContent>
                <div className="space-y-3">
                  <div className="h-4 bg-white/20 rounded w-2/3"></div>
                  <div className="h-8 bg-white/30 rounded w-1/2"></div>
                  <div className="h-3 bg-white/10 rounded w-3/4"></div>
                </div>
              </ModernCardContent>
            </ModernCard>
          ))}
        </div>
      </div>
    )
  }

  // Calculate derived metrics from real data
  const highRiskPercentage = stats ? ((stats.high_risk_requests / stats.total_requests) * 100) : 0
  const riskLevel = stats ? getRiskLevel(stats.avg_risk_score) : { level: 'Unknown', color: 'text-gray-500' }

  return (
    <div className="space-y-8">
      {/* Hero Header */}
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold text-gray-300">AIRMS Dashboard</h1>
        <h2 className="text-4xl font-bold text-white">Risk Management Overview</h2>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-blue-900/50 border border-blue-700 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-300 text-sm font-medium">Total Requests</p>
              <p className="text-3xl font-bold text-white">{formatNumber(stats?.total_requests || 0)}</p>
              <div className="flex items-center mt-2">
                <ArrowTrendingUpIcon className="h-4 w-4 text-green-400 mr-1" />
                <span className="text-green-400 text-sm">Live data</span>
              </div>
            </div>
            <ChartBarIcon className="h-12 w-12 text-blue-400" />
          </div>
        </div>
        
        <div className="bg-yellow-900/50 border border-yellow-700 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-300 text-sm font-medium">Avg Risk Score</p>
              <p className="text-3xl font-bold text-white">{formatRiskScore(stats?.avg_risk_score || 0)}</p>
              <div className="flex items-center mt-2">
                <span className={`text-sm ${riskLevel.color}`}>{riskLevel.level} Risk</span>
              </div>
            </div>
            <ShieldExclamationIcon className="h-12 w-12 text-yellow-400" />
          </div>
        </div>
        
        <div className="bg-red-900/50 border border-red-700 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-300 text-sm font-medium">High Risk Requests</p>
              <p className="text-3xl font-bold text-white">{formatNumber(stats?.high_risk_requests || 0)}</p>
              <div className="flex items-center mt-2">
                <span className="text-red-400 text-sm">{highRiskPercentage.toFixed(1)}% of total</span>
              </div>
            </div>
            <ExclamationTriangleIcon className="h-12 w-12 text-red-400" />
          </div>
        </div>
        
        <div className="bg-purple-900/50 border border-purple-700 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-300 text-sm font-medium">Blocked Requests</p>
              <p className="text-3xl font-bold text-white">{formatNumber(stats?.blocked_requests || 0)}</p>
              <div className="flex items-center mt-2">
                <ShieldCheckIcon className="h-4 w-4 text-green-400 mr-1" />
                <span className="text-green-400 text-sm">Protected</span>
              </div>
            </div>
            <ShieldCheckIcon className="h-12 w-12 text-purple-400" />
          </div>
        </div>
      </div>

      {/* Real-time Activity */}
      {realTimeStats && (
        <ModernCard variant="gradient" className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20"></div>
          <ModernCardHeader className="relative">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                <BoltIcon className="h-5 w-5 text-white" />
              </div>
              <div>
                <ModernCardTitle>Real-time System Status</ModernCardTitle>
                <ModernCardDescription>Live monitoring • Updated: {new Date(realTimeStats.last_updated).toLocaleTimeString()}</ModernCardDescription>
              </div>
            </div>
          </ModernCardHeader>
          <ModernCardContent className="relative">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center p-4 bg-white/10 rounded-xl backdrop-blur-sm">
                <div className="text-2xl font-bold text-white mb-1">{realTimeStats.current_requests_per_minute}</div>
                <div className="text-sm text-white/70">Requests/min</div>
                <div className="flex items-center justify-center mt-2">
                  <BoltIcon className="h-4 w-4 text-blue-400 mr-1" />
                  <span className="text-xs text-blue-400">Live</span>
                </div>
              </div>
              <div className="text-center p-4 bg-white/10 rounded-xl backdrop-blur-sm">
                <div className="text-2xl font-bold text-white mb-1">{realTimeStats.active_users}</div>
                <div className="text-sm text-white/70">Active Users</div>
                <div className="flex items-center justify-center mt-2">
                  <ArrowTrendingUpIcon className="h-4 w-4 text-green-400 mr-1" />
                  <span className="text-xs text-green-400">Online</span>
                </div>
              </div>
              <div className="text-center p-4 bg-white/10 rounded-xl backdrop-blur-sm">
                <div className="text-2xl font-bold text-white mb-1">{realTimeStats.avg_response_time.toFixed(0)}ms</div>
                <div className="text-sm text-white/70">Response Time</div>
                <div className="flex items-center justify-center mt-2">
                  <ClockIcon className="h-4 w-4 text-yellow-400 mr-1" />
                  <span className="text-xs text-yellow-400">Avg</span>
                </div>
              </div>
              <div className="text-center p-4 bg-white/10 rounded-xl backdrop-blur-sm">
                <div className="text-2xl font-bold text-white mb-1 capitalize">{realTimeStats.system_health}</div>
                <div className="text-sm text-white/70">System Status</div>
                <div className="flex items-center justify-center mt-2">
                  <CheckCircleIcon className="h-4 w-4 text-green-400 mr-1" />
                  <span className="text-xs text-green-400">Operational</span>
                </div>
              </div>
            </div>
          </ModernCardContent>
        </ModernCard>
      )}

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Timeline */}
        <ModernCard className="relative overflow-hidden" hover glow>
          <ModernCardHeader>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <ChartBarIcon className="h-4 w-4 text-blue-400" />
              </div>
              <div>
                <ModernCardTitle>Risk Score Timeline</ModernCardTitle>
                <ModernCardDescription>Trend analysis • Last 30 days</ModernCardDescription>
              </div>
            </div>
          </ModernCardHeader>
          <ModernCardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timeline}>
                  <defs>
                    <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.7)' }}
                    axisLine={{ stroke: 'rgba(255,255,255,0.2)' }}
                    tickLine={{ stroke: 'rgba(255,255,255,0.2)' }}
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis 
                    tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.7)' }}
                    axisLine={{ stroke: 'rgba(255,255,255,0.2)' }}
                    tickLine={{ stroke: 'rgba(255,255,255,0.2)' }}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'rgba(15, 15, 35, 0.95)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '12px',
                      color: 'white',
                      backdropFilter: 'blur(20px)'
                    }}
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value: any) => [value.toFixed(2), 'Risk Score']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="risk_score" 
                    stroke="#8b5cf6" 
                    strokeWidth={3}
                    dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, fill: '#a855f7' }}
                    fill="url(#riskGradient)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </ModernCardContent>
        </ModernCard>

        {/* Requests Timeline */}
        <ModernCard className="relative overflow-hidden" hover glow>
          <ModernCardHeader>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center">
                <ChartBarIcon className="h-4 w-4 text-green-400" />
              </div>
              <div>
                <ModernCardTitle>Request Volume</ModernCardTitle>
                <ModernCardDescription>Daily request trends</ModernCardDescription>
              </div>
            </div>
          </ModernCardHeader>
          <ModernCardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={timeline}>
                  <defs>
                    <linearGradient id="requestGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#059669" stopOpacity={0.6}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.7)' }}
                    axisLine={{ stroke: 'rgba(255,255,255,0.2)' }}
                    tickLine={{ stroke: 'rgba(255,255,255,0.2)' }}
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis 
                    tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.7)' }}
                    axisLine={{ stroke: 'rgba(255,255,255,0.2)' }}
                    tickLine={{ stroke: 'rgba(255,255,255,0.2)' }}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'rgba(15, 15, 35, 0.95)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '12px',
                      color: 'white',
                      backdropFilter: 'blur(20px)'
                    }}
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value: any) => [value.toLocaleString(), 'Requests']}
                  />
                  <Bar 
                    dataKey="requests" 
                    fill="url(#requestGradient)"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ModernCardContent>
        </ModernCard>
      </div>

      {/* System Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ModernCard className="relative overflow-hidden" hover glow>
          <ModernCardHeader>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <SparklesIcon className="h-4 w-4 text-blue-400" />
              </div>
              <div>
                <ModernCardTitle>User Activity</ModernCardTitle>
                <ModernCardDescription>Current system usage</ModernCardDescription>
              </div>
            </div>
          </ModernCardHeader>
          <ModernCardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <span className="text-white/70">Total Users</span>
                <span className="text-white font-semibold">{formatNumber(stats?.total_users || 0)}</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <span className="text-white/70">Active Users</span>
                <span className="text-green-400 font-semibold">{formatNumber(stats?.active_users || 0)}</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <span className="text-white/70">Activity Rate</span>
                <span className="text-blue-400 font-semibold">
                  {stats ? ((stats.active_users / stats.total_users) * 100).toFixed(1) : 0}%
                </span>
              </div>
            </div>
          </ModernCardContent>
        </ModernCard>

        <ModernCard className="relative overflow-hidden" hover glow>
          <ModernCardHeader>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <ShieldCheckIcon className="h-4 w-4 text-purple-400" />
              </div>
              <div>
                <ModernCardTitle>Security Metrics</ModernCardTitle>
                <ModernCardDescription>Risk management overview</ModernCardDescription>
              </div>
            </div>
          </ModernCardHeader>
          <ModernCardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <span className="text-white/70">Risk Detection Rate</span>
                <span className="text-yellow-400 font-semibold">
                  {stats ? ((stats.high_risk_requests / stats.total_requests) * 100).toFixed(1) : 0}%
                </span>
              </div>
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <span className="text-white/70">Block Rate</span>
                <span className="text-red-400 font-semibold">
                  {stats ? ((stats.blocked_requests / stats.total_requests) * 100).toFixed(1) : 0}%
                </span>
              </div>
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <span className="text-white/70">System Health</span>
                <span className="text-green-400 font-semibold capitalize">
                  {realTimeStats?.system_health || 'Unknown'}
                </span>
              </div>
            </div>
          </ModernCardContent>
        </ModernCard>
      </div>
    </div>
  )
}
