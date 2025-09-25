"use client";

import React from 'react';

import { TabsComponent, TabsListComponent, TabsTriggerComponent, TabsContentComponent } from "@/components/ui/tabs";

import RiskMonitorSettingsPage from '@/components/dashboard/RiskMonitorSettingsPage';
import RealTimeRiskDashboard from '@/components/dashboard/RealTimeRiskDashboard';
import { Activity, Settings } from 'lucide-react';

export default function RiskMonitorPage() {
  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Risk Monitor</h1>
        <p className="text-muted-foreground">
          Monitor and configure your AI risk detection system in real-time
        </p>
      </div>
      
      <TabsComponent defaultValue="dashboard" className="space-y-6">
        <TabsListComponent className="grid w-full grid-cols-2">
          <TabsTriggerComponent value="dashboard" className="flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Live Dashboard
          </TabsTriggerComponent>
          <TabsTriggerComponent value="settings" className="flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Settings
          </TabsTriggerComponent>
        </TabsListComponent>

        <TabsContentComponent value="dashboard">
          <RealTimeRiskDashboard />
        </TabsContentComponent>

        <TabsContentComponent value="settings">
          <RiskMonitorSettingsPage />
        </TabsContentComponent>
      </TabsComponent>
    </div>
  );
}
