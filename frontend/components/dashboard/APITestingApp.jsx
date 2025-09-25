
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

import { TabsComponent, TabsListComponent, TabsTriggerComponent, TabsContentComponent } from "@/components/ui/tabs";

import { 
  Play, 
  Copy, 
  Download, 
  Clock, 
  CheckCircle, 
  XCircle,
  Activity,
  Code,
  History
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const APITestingApp = () => {
  const [request, setRequest] = useState({
    method: 'POST',
    endpoint: '/api/v1/chat/completions',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
    },
    body: JSON.stringify({
      model: "gpt-3.5-turbo",
      messages: [
        {
          role: "user",
          content: "Hello, can you help me with something?"
        }
      ],
      max_tokens: 150,
      temperature: 0.7
    }, null, 2)
  });

  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [selectedPreset, setSelectedPreset] = useState('');
  const { toast } = useToast();

  const presets = {
    'chat-completion': {
      name: 'Chat Completion',
      method: 'POST',
      endpoint: '/api/v1/chat/completions',
      body: {
        model: "gpt-3.5-turbo",
        messages: [
          { role: "user", content: "Hello, can you help me with something?" }
        ],
        max_tokens: 150,
        temperature: 0.7
      }
    },
    'risk-analysis': {
      name: 'Risk Analysis',
      method: 'POST',
      endpoint: '/api/v1/analyze/risk',
      body: {
        text: "This is a sample text to analyze for potential risks",
        analysis_type: "comprehensive"
      }
    },
    'content-sanitization': {
      name: 'Content Sanitization',
      method: 'POST',
      endpoint: '/api/v1/sanitize',
      body: {
        text: "This text contains some PII like email@example.com and phone 123-456-7890",
        sanitization_level: "strict"
      }
    },
    'dashboard-stats': {
      name: 'Dashboard Statistics',
      method: 'GET',
      endpoint: '/api/v1/analytics/statistics?days=7',
      body: null
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    const savedHistory = localStorage.getItem('api_test_history');
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
  };

  const saveToHistory = (requestData, responseData) => {
    const historyItem = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      request: requestData,
      response: responseData,
      status: responseData.status,
      duration: responseData.duration
    };

    const newHistory = [historyItem, ...history.slice(0, 49)]; // Keep last 50
    setHistory(newHistory);
    localStorage.setItem('api_test_history', JSON.stringify(newHistory));
  };

  const sendRequest = async () => {
    setLoading(true);
    const startTime = Date.now();

    try {
      const response = await fetch(request.endpoint, {
        method: request.method,
        headers: request.headers,
        body: request.body
      });

      const data = await response.json();
      const duration = Date.now() - startTime;

      const result = {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        data: data,
        duration: duration
      };

      setResponse(result);
      saveToHistory(request, result);
      toast({
        title: "Request completed",
        description: `${response.status} ${response.statusText} in ${duration}ms`,
      });
    } catch (error) {
      const duration = Date.now() - startTime;
      setResponse({
        status: 'error',
        error: error.message,
        duration: duration
      });
      toast({
        title: "Request failed",
        description: error.message,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied to clipboard",
      description: "Content copied successfully"
    });
  };

  const downloadResponse = () => {
    const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `api-response-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const applyPreset = (presetKey) => {
    const preset = presets[presetKey];
    setRequest({
      method: preset.method,
      endpoint: preset.endpoint,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
      },
      body: preset.body ? JSON.stringify(preset.body, null, 2) : null
    });
    setSelectedPreset(presetKey);
  };

  const handleMethodChange = (method) => {
    setRequest({ ...request, method });
  };

  const handleEndpointChange = (endpoint) => {
    setRequest({ ...request, endpoint });
  };

  const handleHeadersChange = (headers) => {
    setRequest({ ...request, headers });
  };

  const handleBodyChange = (body) => {
    setRequest({ ...request, body });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">API Testing Playground</h1>
          <Badge variant="secondary" className="flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Live Testing
          </Badge>
        </div>

        <Tabs defaultValue="builder" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="builder">Request Builder</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
            <TabsTrigger value="presets">Presets</TabsTrigger>
          </TabsList>

          <TabsContent value="builder" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code className="w-5 h-5" />
                  Request Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="method">HTTP Method</Label>
                    <Select value={request.method} onValueChange={handleMethodChange}>
                      <SelectTrigger id="method">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="GET">GET</SelectItem>
                        <SelectItem value="POST">POST</SelectItem>
                        <SelectItem value="PUT">PUT</SelectItem>
                        <SelectItem value="DELETE">DELETE</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="endpoint">Endpoint</Label>
                    <Input
                      id="endpoint"
                      value={request.endpoint}
                      onChange={(e) => handleEndpointChange(e.target.value)}
                      placeholder="/api/v1/endpoint"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="headers">Headers</Label>
                  <Textarea
                    id="headers"
                    value={JSON.stringify(request.headers, null, 2)}
                    onChange={(e) => handleHeadersChange(JSON.parse(e.target.value))}
                    placeholder="Enter headers as JSON"
                    className="font-mono text-sm"
                  />
                </div>

                <div>
                  <Label htmlFor="body">Request Body</Label>
                  <Textarea
                    id="body"
                    value={request.body}
                    onChange={(e) => handleBodyChange(e.target.value)}
                    placeholder="Enter request body as JSON"
                    className="font-mono text-sm min-h-[200px]"
                  />
                </div>

                <div className="flex justify-end">
                  <Button 
                    onClick={sendRequest} 
                    disabled={loading}
                    className="flex items-center gap-2"
                  >
                    {loading ? (
                      <>
                        <Clock className="w-4 h-4 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        Send Request
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {response && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5" />
                    Response
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      {response.status === 'error' ? (
                        <XCircle className="w-5 h-5 text-red-500" />
                      ) : (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      )}
                      <span className="font-mono">
                        {response.status === 'error' ? response.error : `${response.status} ${response.statusText}`}
                      </span>
                      <Badge variant="secondary" className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {response.duration}ms
                      </Badge>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(JSON.stringify(response, null, 2))}
                        className="flex items-center gap-1"
                      >
                        <Copy className="w-4 h-4" />
                        Copy
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={downloadResponse}
                        className="flex items-center gap-1"
                      >
                        <Download className="w-4 h-4" />
                        Download
                      </Button>
                    </div>
                  </div>

                  <div>
                    <Label>Response Data</Label>
                    <div className="border rounded-md p-4 bg-gray-50 overflow-auto max-h-96">
                      <pre className="text-sm font-mono">
                        {JSON.stringify(response.data || response.error, null, 2)}
                      </pre>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="history" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <History className="w-5 h-5" />
                  Recent Requests
                </CardTitle>
              </CardHeader>
              <CardContent>
                {history.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No history yet</p>
                ) : (
                  <div className="space-y-3">
                    {history.map((item) => (
                      <div key={item.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-mono text-sm">{item.request.method}</span>
                              <span className="font-mono text-sm text-gray-600">{item.request.endpoint}</span>
                              {item.status === 200 ? (
                                <CheckCircle className="w-4 h-4 text-green-500" />
                              ) : (
                                <XCircle className="w-4 h-4 text-red-500" />
                              )}
                            </div>
                            <p className="text-xs text-gray-500">
                              {new Date(item.timestamp).toLocaleString()}
                            </p>
                          </div>
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {item.duration}ms
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="presets" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  API Presets
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(presets).map(([key, preset]) => (
                  <Card key={key} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-lg">{preset.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">Method:</span>
                          <Badge variant="secondary">{preset.method}</Badge>
                        </div>
                        <div>
                          <span className="text-sm font-medium">Endpoint:</span>
                          <p className="text-sm font-mono truncate">{preset.endpoint}</p>
                        </div>
                        <Button
                          onClick={() => applyPreset(key)}
                          variant={selectedPreset === key ? "default" : "outline"}
                          className="w-full"
                        >
                          Apply Preset
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default APITestingApp;
