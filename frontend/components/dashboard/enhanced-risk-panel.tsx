"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button, ButtonProps } from '@/components/ui/button'
import { Input, InputProps } from '@/components/ui/input'
import { Textarea, TextareaProps } from '@/components/ui/textarea'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { TabsComponent, TabsListComponent, TabsTriggerComponent, TabsContentComponent } from "@/components/ui/tabs";

import { 
  Shield, 
  AlertTriangle, 
  Brain, 
  Zap, 
  Clock, 
  CheckCircle, 
  XCircle,
  Activity,
  BarChart3,
  FileText,
  Settings
} from 'lucide-react';

interface RiskAssessmentResult {
  assessment_id: string
  content: string
  overall_risk_score: number
  severity_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'MINIMAL'
  risk_types_detected: string[]
  hallucination_detected: boolean
  adversarial_detected: boolean
  compliance_implications: string[]
  mitigation_strategies: string[]
  escalation_required: boolean
  timestamp: string
  processing_time_ms: number
}

interface DetectionStatus {
  enhanced_detection_enabled: boolean
  components: {
    hallucination_detector: boolean
    adversarial_detector: boolean
    risk_matrix_engine: boolean
  }
  version: string
  last_updated: string
}

type BadgeVariant = 'default' | 'secondary' | 'destructive' | 'outline';

export function EnhancedRiskPanel() {
  const [content, setContent] = useState('')
  const [domain, setDomain] = useState('')
  const [userPopulation, setUserPopulation] = useState('')
  const [isAssessing, setIsAssessing] = useState(false)
  const [result, setResult] = useState<RiskAssessmentResult | null>(null)
  const [status, setStatus] = useState<DetectionStatus | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDetectionStatus()
  }, [])

  const fetchDetectionStatus = async () => {
    try {
      const response = await fetch('/api/v1/enhanced-risk/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      if (response.ok) {
        const statusData = await response.json()
        setStatus(statusData)
      }
    } catch (err) {
      console.error('Failed to fetch detection status:', err)
    }
  }

  const assessContent = async () => {
    if (!content.trim()) {
      setError('Please enter content to assess')
      return
    }

    setIsAssessing(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/v1/enhanced-risk/assess', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          content,
          domain: domain || undefined,
          user_population: userPopulation || undefined,
          save_to_history: true
        })
      })

      if (response.ok) {
        const assessmentResult = await response.json()
        setResult(assessmentResult)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Assessment failed')
      }
    } catch (err) {
      setError('Network error occurred')
      console.error('Assessment error:', err)
    } finally {
      setIsAssessing(false)
    }
  }

  const runTestSuite = async () => {
    setIsAssessing(true)
    setError(null)

    try {
      const response = await fetch('/api/v1/enhanced-risk/test', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      if (response.ok) {
        const testResults = await response.json()
        console.log('Test results:', testResults)
        // You could show test results in a modal or separate component
        alert(`Test Suite Results:\n${testResults.passed_tests}/${testResults.total_tests} tests passed\nSuccess Rate: ${testResults.success_rate.toFixed(1)}%`)
      } else {
        setError('Test suite failed')
      }
    } catch (err) {
      setError('Failed to run test suite')
    } finally {
      setIsAssessing(false)
    }
  }

  const getSeverityColor = (severity: RiskAssessmentResult['severity_level']): string => {
    switch (severity) {
      case 'CRITICAL': return 'bg-red-500'
      case 'HIGH': return 'bg-orange-500'
      case 'MEDIUM': return 'bg-yellow-500'
      case 'LOW': return 'bg-blue-500'
      case 'MINIMAL': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return <XCircle className="h-4 w-4" />
      case 'HIGH': return <AlertTriangle className="h-4 w-4" />
      case 'MEDIUM': return <Activity className="h-4 w-4" />
      case 'LOW': return <CheckCircle className="h-4 w-4" />
      case 'MINIMAL': return <CheckCircle className="h-4 w-4" />
      default: return <Activity className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Detection Status Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Enhanced Risk Detection System
          </CardTitle>
          <CardDescription>
            Advanced AI safety with hallucination detection, adversarial protection, and compliance monitoring
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Badge className="" variant={status?.enhanced_detection_enabled ? "default" : "secondary"}>
                {status?.enhanced_detection_enabled ? "ACTIVE" : "INACTIVE"}
              </Badge>
              {status && (
                <div className="text-sm text-muted-foreground">
                  Version {status.version} • Updated {new Date(status.last_updated).toLocaleString()}
                </div>
              )}
            </div>
            <Button onClick={runTestSuite} variant="outline" size="sm" disabled={isAssessing}>
              <Settings className="h-4 w-4 mr-2" />
              Run Test Suite
            </Button>
          </div>

          {status && (
            <div className="mt-4 grid grid-cols-3 gap-4">
              <div className="flex items-center gap-2">
                <Brain className="h-4 w-4" />
                <span className="text-sm">Hallucination Detection</span>
                <Badge variant={status.components.hallucination_detector ? "default" : "secondary"} className="ml-auto">
                  {status.components.hallucination_detector ? "ON" : "OFF"}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4" />
                <span className="text-sm">Adversarial Protection</span>
                <Badge variant={status.components.adversarial_detector ? "default" : "secondary"} className="ml-auto">
                  {status.components.adversarial_detector ? "ON" : "OFF"}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                <span className="text-sm">Risk Matrix Engine</span>
                <Badge variant={status.components.risk_matrix_engine ? "default" : "secondary"} className="ml-auto">
                  {status.components.risk_matrix_engine ? "ON" : "OFF"}
                </Badge>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Assessment Interface */}
      <TabsComponent defaultValue="assess" className="w-full">
        <TabsListComponent className="grid w-full grid-cols-2">
          <TabsTriggerComponent value="assess">Risk Assessment</TabsTriggerComponent>
          <TabsTriggerComponent value="results">Results & Analysis</TabsTriggerComponent>
        </TabsListComponent>

        <TabsContentComponent value="assess" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Content Risk Assessment</CardTitle>
              <CardDescription>
                Analyze content for hallucinations, adversarial attacks, and compliance risks
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Content to Analyze</label>
                <Textarea
                  placeholder="Enter the content you want to assess for risks..."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="mt-1"
                  rows={4}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Domain (Optional)</label>
                  <Input
                    placeholder="e.g., healthcare, finance, legal"
                    value={domain}
                    onChange={(e) => setDomain(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">User Population (Optional)</label>
                  <Input
                    placeholder="e.g., elderly, children, general"
                    value={userPopulation}
                    onChange={(e) => setUserPopulation(e.target.value)}
                    className="mt-1"
                  />
                </div>
              </div>

              <Button 
                onClick={assessContent} 
                disabled={isAssessing || !content.trim()}
                className="w-full"
              >
                {isAssessing ? (
                  <>
                    <Zap className="h-4 w-4 mr-2 animate-spin" />
                    Analyzing Content...
                  </>
                ) : (
                  <>
                    <Shield className="h-4 w-4 mr-2" />
                    Assess Risk
                  </>
                )}
              </Button>

              {error && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle>Assessment Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContentComponent>

        <TabsContentComponent value="results" className="space-y-4">
          {result ? (
            <>
              {/* Overall Risk Score */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    {getSeverityIcon(result.severity_level)}
                    Risk Assessment Results
                  </CardTitle>
                  <CardDescription>
                    Assessment ID: {result.assessment_id} • 
                    Processed in {result.processing_time_ms.toFixed(0)}ms
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Overall Risk Score</span>
                        <Badge variant="default" className={`${getSeverityColor(result.severity_level)}`}>
                          {result.severity_level}
                        </Badge>
                      </div>
                      <Progress value={result.overall_risk_score * 100} className="h-2" />
                      <div className="text-sm text-muted-foreground mt-1">
                        {(result.overall_risk_score * 100).toFixed(1)}% risk level
                      </div>
                    </div>

                    {result.risk_types_detected.length > 0 && (
                      <div>
                        <span className="text-sm font-medium">Detected Risk Types</span>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {result.risk_types_detected.map((type, index) => (
                            <Badge key={index} variant="outline" className="text-sm">
                              {type.replace('_', ' ')}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-4">
                      <div className="flex items-center gap-2">
                        <Brain className="h-4 w-4" />
                        <span className="text-sm">Hallucination Detected</span>
                        <Badge 
                          variant={result.hallucination_detected ? "destructive" : "default"}
                          className="ml-auto"
                        >
                          {result.hallucination_detected ? "YES" : "NO"}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <Shield className="h-4 w-4" />
                        <span className="text-sm">Adversarial Attack</span>
                        <Badge 
                          variant={result.adversarial_detected ? "destructive" : "default"}
                          className="ml-auto"
                        >
                          {result.adversarial_detected ? "YES" : "NO"}
                        </Badge>
                      </div>
                    </div>

                    {result.escalation_required && (
                      <Alert variant="destructive">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertTitle>Escalation Required</AlertTitle>
                        <AlertDescription>
                          This assessment requires immediate attention due to high risk level.
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Compliance & Mitigation */}
              {(result.compliance_implications.length > 0 || result.mitigation_strategies.length > 0) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {result.compliance_implications.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <FileText className="h-4 w-4" />
                          Compliance Implications
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {result.compliance_implications.map((implication, index) => (
                            <Badge key={index} variant="outline" className="block w-fit">
                              {implication}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {result.mitigation_strategies.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <CheckCircle className="h-4 w-4" />
                          Mitigation Strategies
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {result.mitigation_strategies.slice(0, 3).map((strategy, index) => (
                            <div key={index} className="text-sm p-2 bg-muted rounded">
                              {strategy}
                            </div>
                          ))}
                          {result.mitigation_strategies.length > 3 && (
                            <div className="text-sm text-muted-foreground">
                              +{result.mitigation_strategies.length - 3} more strategies
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="py-8">
                <div className="text-center text-muted-foreground">
                  <Activity className="h-8 w-8 mx-auto mb-2" />
                  <p>No assessment results yet</p>
                  <p className="text-sm">Run a risk assessment to see detailed results here</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContentComponent>
      </TabsComponent>
    </div>
  )
}
