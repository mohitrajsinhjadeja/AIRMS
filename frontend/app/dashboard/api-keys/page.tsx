'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { apiKeysApi } from '@/lib/api'
import { 
  KeyIcon, 
  PlusIcon, 
  TrashIcon, 
  ClipboardDocumentIcon,
  ClockIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

interface ApiKey {
  id: number
  key_id: string
  name: string
  description: string
  environment: string
  is_active: boolean
  usage_count: number
  usage_limit: number | null
  created_at: string
  last_used: string | null
  masked_key: string
}

export default function APIKeysPage() {
  const { user } = useAuth()
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [showNewKeyForm, setShowNewKeyForm] = useState(false)
  const [newKeyForm, setNewKeyForm] = useState({
    name: '',
    description: '',
    environment: 'production',
    usage_limit: null as number | null
  })
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    fetchApiKeys()
  }, [])

  const fetchApiKeys = async () => {
    try {
      setLoading(true)
      const response = await apiKeysApi.list()
      console.log('API Keys Response:', response.data)
      setApiKeys(response.data)
    } catch (error) {
      console.error('Failed to fetch API keys:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newKeyForm.name.trim()) return

    try {
      setCreating(true)
      const response = await apiKeysApi.create({
        key_name: newKeyForm.name,
        permissions: ['chat.completions'],
        usage_limit: newKeyForm.usage_limit || undefined
      })
      
      console.log('Created API Key:', response.data)
      await fetchApiKeys() // Refresh the list
      setShowNewKeyForm(false)
      setNewKeyForm({
        name: '',
        description: '',
        environment: 'production',
        usage_limit: null
      })
    } catch (error) {
      console.error('Failed to create API key:', error)
    } finally {
      setCreating(false)
    }
  }

  const handleDeleteKey = async (keyId: number) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return
    }

    try {
      await apiKeysApi.delete(keyId.toString())
      await fetchApiKeys() // Refresh the list
    } catch (error) {
      console.error('Failed to delete API key:', error)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    // You could add a toast notification here
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getUsagePercentage = (used: number, limit: number | null) => {
    if (!limit) return 0
    return Math.min((used / limit) * 100, 100)
  }

  const getEnvironmentColor = (env: string) => {
    switch (env) {
      case 'production': return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'development': return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'testing': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-white">API Keys</h1>
            <p className="text-gray-400 mt-1">Manage your API keys for accessing AIRMS services</p>
          </div>
          <div className="w-32 h-10 bg-white/20 rounded-lg animate-pulse"></div>
        </div>
        
        <div className="space-y-4">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-6 animate-pulse">
              <div className="space-y-3">
                <div className="h-4 bg-white/20 rounded w-1/4"></div>
                <div className="h-6 bg-white/30 rounded w-3/4"></div>
                <div className="h-3 bg-white/10 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">API Keys</h1>
          <p className="text-gray-400 mt-1">Manage your API keys for accessing AIRMS services</p>
        </div>
        <button
          onClick={() => setShowNewKeyForm(true)}
          className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <PlusIcon className="h-4 w-4" />
          <span>Create New Key</span>
        </button>
      </div>

      {/* New Key Form */}
      {showNewKeyForm && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Create New API Key</h3>
          <form onSubmit={handleCreateKey} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Key Name
              </label>
              <input
                type="text"
                value={newKeyForm.name}
                onChange={(e) => setNewKeyForm({ ...newKeyForm, name: e.target.value })}
                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter a name for your API key"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Description (Optional)
              </label>
              <input
                type="text"
                value={newKeyForm.description}
                onChange={(e) => setNewKeyForm({ ...newKeyForm, description: e.target.value })}
                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Describe what this key will be used for"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Usage Limit (Optional)
              </label>
              <input
                type="number"
                value={newKeyForm.usage_limit || ''}
                onChange={(e) => setNewKeyForm({ ...newKeyForm, usage_limit: e.target.value ? parseInt(e.target.value) : null })}
                className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Maximum number of requests per month"
              />
            </div>
            <div className="flex items-center space-x-3">
              <button
                type="submit"
                disabled={creating}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-4 py-2 rounded-lg transition-colors"
              >
                {creating ? 'Creating...' : 'Create Key'}
              </button>
              <button
                type="button"
                onClick={() => setShowNewKeyForm(false)}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* API Keys List */}
      <div className="space-y-4">
        {apiKeys.length === 0 ? (
          <div className="text-center py-12">
            <KeyIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No API Keys</h3>
            <p className="text-gray-400 mb-4">Create your first API key to start using AIRMS services</p>
            <button
              onClick={() => setShowNewKeyForm(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Create API Key
            </button>
          </div>
        ) : (
          apiKeys.map((apiKey) => (
            <div key={apiKey.id} className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <KeyIcon className="h-5 w-5 text-blue-400" />
                    <h3 className="text-lg font-semibold text-white">{apiKey.name}</h3>
                    <span className={`px-2 py-1 text-xs rounded-full border ${getEnvironmentColor(apiKey.environment)}`}>
                      {apiKey.environment}
                    </span>
                    {apiKey.is_active ? (
                      <span className="px-2 py-1 text-xs rounded-full bg-green-500/20 text-green-400 border border-green-500/30">
                        Active
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs rounded-full bg-red-500/20 text-red-400 border border-red-500/30">
                        Inactive
                      </span>
                    )}
                  </div>
                  
                  {apiKey.description && (
                    <p className="text-gray-400 text-sm mb-3">{apiKey.description}</p>
                  )}
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-400 mb-4">
                    <div className="flex items-center space-x-1">
                      <ClockIcon className="h-4 w-4" />
                      <span>Created {formatDate(apiKey.created_at)}</span>
                    </div>
                    {apiKey.last_used && (
                      <div className="flex items-center space-x-1">
                        <ArrowTrendingUpIcon className="h-4 w-4" />
                        <span>Last used {formatDate(apiKey.last_used)}</span>
                      </div>
                    )}
                  </div>

                  <div className="bg-gray-900/50 rounded-lg p-3 mb-4">
                    <div className="flex items-center justify-between">
                      <code className="text-green-400 font-mono text-sm">{apiKey.masked_key}</code>
                      <button
                        onClick={() => copyToClipboard(apiKey.key_id)}
                        className="text-gray-400 hover:text-white transition-colors"
                        title="Copy full key"
                      >
                        <ClipboardDocumentIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  {/* Usage Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="flex items-center space-x-2 mb-1">
                        <ChartBarIcon className="h-4 w-4 text-blue-400" />
                        <span className="text-sm text-gray-400">Usage</span>
                      </div>
                      <div className="text-lg font-semibold text-white">
                        {apiKey.usage_count.toLocaleString()}
                        {apiKey.usage_limit && (
                          <span className="text-sm text-gray-400 font-normal">
                            /{apiKey.usage_limit.toLocaleString()}
                          </span>
                        )}
                      </div>
                      {apiKey.usage_limit && (
                        <div className="mt-2">
                          <div className="bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${getUsagePercentage(apiKey.usage_count, apiKey.usage_limit)}%` }}
                            />
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            {getUsagePercentage(apiKey.usage_count, apiKey.usage_limit).toFixed(1)}% used
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="flex items-center space-x-2 mb-1">
                        <ShieldCheckIcon className="h-4 w-4 text-green-400" />
                        <span className="text-sm text-gray-400">Status</span>
                      </div>
                      <div className="text-lg font-semibold text-white">
                        {apiKey.is_active ? 'Active' : 'Inactive'}
                      </div>
                    </div>
                    
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="flex items-center space-x-2 mb-1">
                        <ExclamationTriangleIcon className="h-4 w-4 text-yellow-400" />
                        <span className="text-sm text-gray-400">Environment</span>
                      </div>
                      <div className="text-lg font-semibold text-white capitalize">
                        {apiKey.environment}
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="ml-4">
                  <button
                    onClick={() => handleDeleteKey(apiKey.id)}
                    className="text-red-400 hover:text-red-300 transition-colors p-2"
                    title="Delete API key"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
