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
  ExclamationTriangleIcon,
  ArrowPathIcon,
  EyeIcon
} from '@heroicons/react/24/outline'

interface ApiKey {
  id: string  // Backend returns string IDs
  name: string
  key_preview: string  // Backend uses key_preview instead of masked_key
  full_key?: string    // Full key for copying
  created_at: string
  is_active: boolean
  permissions: string[]
  // Optional fields that may not be present in mock data
  description?: string
  environment?: string
  usage_count?: number
  usage_limit?: number | null
  last_used?: string | null
  key?: string  // Alternative full key field (for creation responses)
}

export default function APIKeysPage() {
  const { user } = useAuth()
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [showNewKeyForm, setShowNewKeyForm] = useState(false)
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<ApiKey | null>(null)
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
      // Handle the nested data structure: response.data.data.keys
      const keys = response.data?.data?.keys || response.data?.keys || response.data || []
      setApiKeys(keys)
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
        permissions: ['read', 'write'],
        usage_limit: newKeyForm.usage_limit || undefined
      })
      
      console.log('Created API Key:', response.data)
      
      // Store the newly created key (which has the full key) separately
      const createdKey = response.data.key
      setNewlyCreatedKey(createdKey)
      
      // Refresh the list to get updated keys
      await fetchApiKeys()
      setShowNewKeyForm(false)
      setNewKeyForm({
        name: '',
        description: '',
        environment: 'production',
        usage_limit: null
      })
      
      // Clear the newly created key highlight after 30 seconds
      setTimeout(() => setNewlyCreatedKey(null), 30000)
    } catch (error) {
      console.error('Failed to create API key:', error)
    } finally {
      setCreating(false)
    }
  }

  const handleDeleteKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return
    }

    try {
      await apiKeysApi.delete(keyId)
      await fetchApiKeys() // Refresh the list
    } catch (error) {
      console.error('Failed to delete API key:', error)
    }
  }

  const handleRegenerateKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to regenerate this API key? The old key will no longer work.')) {
      return
    }

    try {
      const response = await apiKeysApi.regenerate(keyId)
      console.log('Regenerated API Key:', response.data)
      
      // Store the regenerated key (which has the full key) separately
      const regeneratedKey = response.data.key
      setNewlyCreatedKey(regeneratedKey)
      
      // Refresh the list to get updated keys
      await fetchApiKeys()
      
      // Clear the newly created key highlight after 30 seconds
      setTimeout(() => setNewlyCreatedKey(null), 30000)
    } catch (error) {
      console.error('Failed to regenerate API key:', error)
    }
  }

  const [copiedKey, setCopiedKey] = useState<string | null>(null)

  const handleRevealAndCopy = async (keyId: string) => {
    try {
      console.log('🔍 [API Keys] Revealing key:', keyId)
      const response = await apiKeysApi.reveal(keyId)
      console.log('✅ [API Keys] Reveal response:', response.data)
      
      const fullKey = response.data.data?.full_key || response.data.full_key
      if (!fullKey) {
        throw new Error('No full key in response')
      }
      
      await copyToClipboard(fullKey, keyId)
      console.log('✅ [API Keys] Key copied successfully')
    } catch (error) {
      console.error('❌ [API Keys] Failed to reveal API key:', error)
      alert('Failed to reveal the full API key. Please try again or regenerate the key.')
    }
  }

  const copyToClipboard = async (text: string, keyId?: string) => {
    try {
      await navigator.clipboard.writeText(text);
      console.log('✅ [Clipboard] Text copied:', text.substring(0, 20) + '...')
      
      // Set copied state using keyId if provided, otherwise use the text
      setCopiedKey(keyId || text);
      setTimeout(() => setCopiedKey(null), 2000);
    } catch (err) {
      console.error('❌ [Clipboard] Failed to copy:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      
      // Show feedback even for fallback
      setCopiedKey(keyId || text);
      setTimeout(() => setCopiedKey(null), 2000);
    }
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

      {/* Newly Created Key Banner */}
      {newlyCreatedKey && (
        <div className="bg-gradient-to-r from-green-600/20 to-blue-600/20 border-2 border-green-500/30 rounded-xl p-6 mb-6 relative">
          <button
            onClick={() => setNewlyCreatedKey(null)}
            className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
            title="Dismiss"
          >
            ✕
          </button>
          
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center">
              <KeyIcon className="h-5 w-5 text-green-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">✅ New API Key Created Successfully!</h3>
              <p className="text-green-300 text-sm">Save this key now - it won't be shown again in full</p>
            </div>
          </div>
          
          <div className="bg-gray-900/70 rounded-lg p-4 mb-4">
            <div className="text-xs text-gray-400 mb-2">Full API Key (copy now!)</div>
            <div className="flex items-center justify-between">
              <code className="text-green-400 font-mono text-sm break-all mr-4">{newlyCreatedKey.full_key}</code>
              <button
                onClick={() => copyToClipboard(newlyCreatedKey.full_key!, newlyCreatedKey.id)}
                className={`flex-shrink-0 p-2 rounded-lg transition-colors ${
                  copiedKey === newlyCreatedKey.id
                    ? 'bg-green-600/30 text-green-400' 
                    : 'bg-green-600/20 text-green-400 hover:bg-green-600/30'
                }`}
                title="Copy full API key"
              >
                <ClipboardDocumentIcon className="h-4 w-4" />
              </button>
            </div>
            {copiedKey === newlyCreatedKey.id && (
              <div className="text-xs text-green-400 mt-2 flex items-center">
                <span className="mr-1">✓</span>
                Full API key copied to clipboard!
              </div>
            )}
          </div>
          
          <div className="text-xs text-gray-400">
            <strong>Key Details:</strong> {newlyCreatedKey.name} • Permissions: {newlyCreatedKey.permissions?.join(', ')} • Created: {formatDate(newlyCreatedKey.created_at)}
          </div>
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
                    {apiKey.environment && (
                      <span className={`px-2 py-1 text-xs rounded-full border ${getEnvironmentColor(apiKey.environment)}`}>
                        {apiKey.environment}
                      </span>
                    )}
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
                      <span>Created {apiKey.created_at ? formatDate(apiKey.created_at) : 'Unknown'}</span>
                    </div>
                    {apiKey.last_used && (
                      <div className="flex items-center space-x-1">
                        <ArrowTrendingUpIcon className="h-4 w-4" />
                        <span>Last used {formatDate(apiKey.last_used)}</span>
                      </div>
                    )}
                  </div>

                  <div className="bg-gray-900/50 rounded-lg p-3 mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex-1">
                        <div className="text-xs text-gray-400 mb-1">API Key Preview</div>
                        <code className="text-green-400 font-mono text-sm">{apiKey.key_preview}</code>
                      </div>
                      {apiKey.full_key || apiKey.key ? (
                        <button
                          onClick={() => copyToClipboard(apiKey.full_key || apiKey.key!, apiKey.id)}
                          className={`ml-3 p-2 rounded-lg transition-colors ${
                            copiedKey === apiKey.id
                              ? 'bg-green-600/20 text-green-400' 
                              : 'bg-gray-600/20 text-gray-400 hover:text-white hover:bg-gray-600/30'
                          }`}
                          title={copiedKey === apiKey.id ? "Copied!" : "Copy full API key"}
                        >
                          <ClipboardDocumentIcon className="h-4 w-4" />
                        </button>
                      ) : (
                        <button
                          onClick={() => handleRevealAndCopy(apiKey.id)}
                          className={`ml-3 p-2 rounded-lg transition-colors ${
                            copiedKey === apiKey.id
                              ? 'bg-green-600/20 text-green-400' 
                              : 'bg-blue-600/20 text-blue-400 hover:text-blue-300 hover:bg-blue-600/30'
                          }`}
                          title={copiedKey === apiKey.id ? "Copied!" : "Reveal and copy full API key"}
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                    
                    {copiedKey === apiKey.id ? (
                      <div className="text-xs text-green-400 flex items-center">
                        <span className="mr-1">✓</span>
                        Full API key copied to clipboard!
                      </div>
                    ) : apiKey.full_key || apiKey.key ? (
                      <div className="text-xs text-gray-500">
                        Click the copy button to copy the full API key
                      </div>
                    ) : (
                      <div className="text-xs text-blue-500 flex items-center">
                        <span className="mr-1">👁️</span>
                        Click the eye button to reveal and copy the full API key
                      </div>
                    )}
                  </div>

                  {/* Usage Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="flex items-center space-x-2 mb-1">
                        <ChartBarIcon className="h-4 w-4 text-blue-400" />
                        <span className="text-sm text-gray-400">Usage</span>
                      </div>
                      <div className="text-lg font-semibold text-white">
                        {(apiKey.usage_count || 0).toLocaleString()}
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
                              style={{ width: `${getUsagePercentage(apiKey.usage_count || 0, apiKey.usage_limit)}%` }}
                            />
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            {getUsagePercentage(apiKey.usage_count || 0, apiKey.usage_limit).toFixed(1)}% used
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
                        <span className="text-sm text-gray-400">Permissions</span>
                      </div>
                      <div className="text-lg font-semibold text-white">
                        {apiKey.permissions?.join(', ') || 'Standard'}
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="ml-4 flex items-center space-x-2">
                  <button
                    onClick={() => handleRegenerateKey(apiKey.id)}
                    className="text-blue-400 hover:text-blue-300 transition-colors p-2"
                    title="Regenerate API key"
                  >
                    <ArrowPathIcon className="h-5 w-5" />
                  </button>
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
