"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { 
  Key, 
  Plus, 
  Trash2, 
  Eye, 
  EyeOff, 
  Copy,
  Calendar,
  Activity
} from 'lucide-react';

const APIKeySettings = () => {
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showNewKeyForm, setShowNewKeyForm] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [visibleKeys, setVisibleKeys] = useState(new Set());

  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      const mockKeys = [
        {
          id: '1',
          name: 'Production API Key',
          key: 'sk-1234567890abcdef1234567890abcdef',
          created_at: '2024-01-15T10:30:00Z',
          last_used: '2024-01-20T14:22:00Z',
          usage_count: 1250,
          is_active: true
        },
        {
          id: '2',
          name: 'Development Key',
          key: 'sk-abcdef1234567890abcdef1234567890',
          created_at: '2024-01-10T09:15:00Z',
          last_used: '2024-01-19T16:45:00Z',
          usage_count: 89,
          is_active: true
        }
      ];
      setApiKeys(mockKeys);
    } catch (error) {
      console.error('Failed to load API keys:', error);
      // Toast notification would go here if useToast was available
    } finally {
      setLoading(false);
    }
  };

  const createApiKey = async () => {
    if (!newKeyName.trim()) {
      // Toast notification would go here if useToast was available
      return;
    }

    try {
      setLoading(true);
      // TODO: Replace with actual API call
      const newKey = {
        id: Date.now().toString(),
        name: newKeyName,
        key: `sk-${Math.random().toString(36).substr(2, 32)}`,
        created_at: new Date().toISOString(),
        last_used: null,
        usage_count: 0,
        is_active: true
      };

      setApiKeys(prev => [...prev, newKey]);
      setNewKeyName('');
      setShowNewKeyForm(false);
      
      // Toast notification would go here if useToast was available
    } catch (error) {
      console.error('Failed to create API key:', error);
      // Toast notification would go here if useToast was available
    } finally {
      setLoading(false);
    }
  };

  const deleteApiKey = async (keyId) => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      setApiKeys(prev => prev.filter(key => key.id !== keyId));
      
      // Toast notification would go here if useToast was available
    } catch (error) {
      console.error('Failed to delete API key:', error);
      // Toast notification would go here if useToast was available
    } finally {
      setLoading(false);
    }
  };

  const toggleKeyVisibility = (keyId) => {
    setVisibleKeys(prev => {
      const newSet = new Set(prev);
      if (newSet.has(keyId)) {
        newSet.delete(keyId);
      } else {
        newSet.add(keyId);
      }
      return newSet;
    });
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // Toast notification would go here if useToast was available
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  const maskApiKey = (key) => {
    return `${key.substring(0, 8)}${'*'.repeat(24)}${key.substring(-4)}`;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold">API Keys</h3>
          <p className="text-sm text-muted-foreground">
            Manage your API keys for accessing the Risk Agent API
          </p>
        </div>
        <Button onClick={() => setShowNewKeyForm(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create New Key
        </Button>
      </div>

      {showNewKeyForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create New API Key</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="keyName">Key Name</Label>
              <Input
                id="keyName"
                placeholder="e.g., Production API Key"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={createApiKey} disabled={loading}>
                Create Key
              </Button>
              <Button 
                variant="outline" 
                onClick={() => {
                  setShowNewKeyForm(false);
                  setNewKeyName('');
                }}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="space-y-4">
        {apiKeys.map((apiKey) => (
          <Card key={apiKey.id}>
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Key className="w-4 h-4" />
                    <h4 className="font-medium">{apiKey.name}</h4>
                    <Badge variant={apiKey.is_active ? "default" : "secondary"}>
                      {apiKey.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <code className="text-sm bg-gray-100 px-2 py-1 rounded">
                        {visibleKeys.has(apiKey.id) ? apiKey.key : maskApiKey(apiKey.key)}
                      </code>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => toggleKeyVisibility(apiKey.id)}
                      >
                        {visibleKeys.has(apiKey.id) ? (
                          <EyeOff className="w-4 h-4" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => copyToClipboard(apiKey.key)}
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        Created: {formatDate(apiKey.created_at)}
                      </div>
                      <div className="flex items-center gap-1">
                        <Activity className="w-3 h-3" />
                        Last used: {formatDate(apiKey.last_used)}
                      </div>
                      <div>
                        Usage: {apiKey.usage_count.toLocaleString()} requests
                      </div>
                    </div>
                  </div>
                </div>
                
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={() => deleteApiKey(apiKey.id)}
                  disabled={loading}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {apiKeys.length === 0 && !loading && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <Key className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No API Keys</h3>
              <p className="text-muted-foreground mb-4">
                Create your first API key to start using the Risk Agent API
              </p>
              <Button onClick={() => setShowNewKeyForm(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create API Key
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default APIKeySettings;