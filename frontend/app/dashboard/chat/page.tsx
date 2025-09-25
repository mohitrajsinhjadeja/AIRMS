'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { apiKeysApi } from '@/lib/api'
import { Send, Bot, User, AlertTriangle, Shield } from 'lucide-react'

// ✅ Use your UI wrapper for all Select components
import { Select, SelectContent, SelectTrigger, SelectValue, SelectItem } from '@/components/ui/select'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  risk_score?: number
  risk_flags?: string[]
}

interface ApiKey {
  id: string
  name: string
  key_preview: string
  is_active: boolean
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string>('')
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [selectedApiKey, setSelectedApiKey] = useState<string>('')
  const [error, setError] = useState<string>('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Fetch API keys on component mount
  useEffect(() => {
    fetchApiKeys()
  }, [])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const fetchApiKeys = async () => {
    try {
      const response = await apiKeysApi.list()
      const keys = response.data.filter((key: ApiKey) => key.is_active)
      setApiKeys(keys)
      if (keys.length > 0) {
        setSelectedApiKey(keys[0].key_preview)
      }
    } catch (error) {
      console.error('Failed to fetch API keys:', error)
      setError('Failed to load API keys. Please create an API key first.')
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    
    if (!selectedApiKey) {
      setError('Please select an API key first')
      return
    }

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setError('')

    try {
      // Call the chat API
      const response = await fetch('/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${selectedApiKey}`
        },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_id: conversationId || undefined
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()

      // Set conversation ID if this is the first message
      if (!conversationId) {
        setConversationId(data.conversation_id)
      }

      // Add assistant response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.message,
        timestamp: data.timestamp,
        risk_score: data.risk_score,
        risk_flags: data.risk_flags
      }

      setMessages(prev => [...prev, assistantMessage])

    } catch (error) {
      console.error('Chat error:', error)
      setError(`Failed to send message: ${error instanceof Error ? error.message : 'Unknown error'}`)
      
      // Add error message to chat
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
        timestamp: new Date().toISOString(),
        risk_score: 0,
        risk_flags: ['error']
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    setMessages([])
    setConversationId('')
    setError('')
  }

  const getRiskColor = (score: number) => {
    if (score >= 0.7) return 'destructive'
    if (score >= 0.4) return 'default'
    return 'secondary'
  }

  const getRiskLabel = (score: number) => {
    if (score >= 0.7) return 'High Risk'
    if (score >= 0.4) return 'Medium Risk'
    return 'Low Risk'
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">AIRMS Chatbot</h1>
        <p className="text-muted-foreground">
          Chat with the AI assistant and see real-time risk assessment
        </p>
      </div>

      {/* API Key Selection */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            API Configuration
          </CardTitle>
          <CardDescription>
            Select an API key to authenticate your chat requests
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">API Key</label>
              <Select value={selectedApiKey} onValueChange={setSelectedApiKey}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select an API key" />
                </SelectTrigger>
                <SelectContent>
                  {apiKeys.map((key) => (
                    <SelectItem key={key.id} value={key.key_preview}>
                      {key.name} ({key.key_preview})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button variant="outline" onClick={fetchApiKeys}>
              Refresh Keys
            </Button>
            <Button variant="outline" onClick={clearChat}>
              Clear Chat
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert className="mb-6" variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Chat Messages */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            Chat Messages
            {conversationId && (
              <Badge variant="outline" className="ml-auto">
                ID: {conversationId.slice(0, 8)}...
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 min-h-[400px] max-h-[600px] overflow-y-auto">
            {messages.length === 0 ? (
              <div className="text-center text-muted-foreground py-12">
                <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Start a conversation by typing a message below</p>
              </div>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`flex gap-3 max-w-[80%] ${
                      message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                    }`}
                  >
                    <div className="flex-shrink-0">
                      {message.role === 'user' ? (
                        <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                          <User className="h-4 w-4 text-primary-foreground" />
                        </div>
                      ) : (
                        <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                          <Bot className="h-4 w-4 text-secondary-foreground" />
                        </div>
                      )}
                    </div>
                    <div className="flex-1">
                      <div
                        className={`rounded-lg p-3 ${
                          message.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-secondary text-secondary-foreground'
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{message.content}</p>
                      </div>
                      <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                        <span>
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </span>
                        {message.risk_score !== undefined && (
                          <>
                            <Badge
                              variant={getRiskColor(message.risk_score)}
                              className="text-xs"
                            >
                              {getRiskLabel(message.risk_score)} ({(message.risk_score * 100).toFixed(0)}%)
                            </Badge>
                            {message.risk_flags && message.risk_flags.length > 0 && (
                              <div className="flex gap-1">
                                {message.risk_flags.map((flag, i) => (
                                  <Badge key={i} variant="outline" className="text-xs">
                                    {flag}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        </CardContent>
      </Card>

      {/* Message Input */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
              className="flex-1 min-h-[60px] resize-none"
              disabled={loading || !selectedApiKey}
            />
            <Button
              onClick={sendMessage}
              disabled={loading || !input.trim() || !selectedApiKey}
              size="lg"
              className="px-6"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            {selectedApiKey
              ? `Using API key: ${selectedApiKey}`
              : 'Please select an API key to start chatting'}
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
