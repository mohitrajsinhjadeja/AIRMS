'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { LoadingSpinner } from '@/components/ui/loading'
import { ModernButton } from '@/components/ui/modern-button'
import { ModernCard, ModernCardContent } from '@/components/ui/modern-card'
import { 
  SparklesIcon,
  ShieldCheckIcon,
  BoltIcon,
  ChartBarIcon,
  ArrowRightIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  KeyIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

export default function HomePage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    // Redirect to login page by default if not authenticated
    if (!loading && !user) {
      router.push('/login')
    } else if (!loading && user) {
      router.push('/dashboard')
    }
  }, [user, loading, router])

  if (!mounted || loading) {
    return <LoadingSpinner />
  }

  if (user) {
    return null // Will redirect to dashboard
  }

  // This will only show briefly before redirect
  return <LoadingSpinner />

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center space-y-8">
            {/* Logo */}
            <div className="flex items-center justify-center space-x-4">
              <div className="w-16 h-16 gradient-primary rounded-3xl flex items-center justify-center animate-gradient">
                <SparklesIcon className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-5xl font-bold text-white">AIRMS</h1>
                <p className="text-white/70">AI Risk Management System</p>
              </div>
            </div>

            {/* Main Headline */}
            <div className="space-y-6 max-w-4xl mx-auto">
              <h2 className="text-6xl md:text-7xl font-bold text-white leading-tight">
                Secure AI
                <span className="block gradient-primary bg-clip-text text-transparent animate-gradient">
                  At Scale
                </span>
              </h2>
              <p className="text-xl text-white/80 max-w-2xl mx-auto leading-relaxed">
                Advanced risk detection and mitigation for AI applications. 
                Protect your users, data, and reputation with real-time monitoring.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/register">
                <ModernButton variant="gradient" size="xl" className="px-8">
                  <SparklesIcon className="w-5 h-5 mr-2" />
                  Start Free Trial
                  <ArrowRightIcon className="w-5 h-5 ml-2" />
                </ModernButton>
              </Link>
              <Link href="/login">
                <ModernButton variant="outline" size="xl" className="px-8">
                  Sign In
                </ModernButton>
              </Link>
            </div>

            {/* Social Proof */}
            <div className="pt-8">
              <p className="text-white/50 text-sm mb-4">Trusted by developers worldwide</p>
              <div className="flex items-center justify-center space-x-8 opacity-60">
                <div className="text-white/40 font-semibold">OpenAI</div>
                <div className="text-white/40 font-semibold">Anthropic</div>
                <div className="text-white/40 font-semibold">Groq</div>
                <div className="text-white/40 font-semibold">Cohere</div>
              </div>
            </div>
          </div>
        </div>

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-20 h-20 gradient-secondary rounded-2xl opacity-20 animate-float"></div>
        <div className="absolute bottom-20 right-10 w-16 h-16 gradient-tertiary rounded-xl opacity-20 animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/4 w-12 h-12 gradient-accent rounded-lg opacity-15 animate-float" style={{ animationDelay: '1s' }}></div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h3 className="text-4xl font-bold text-white mb-4">Powerful Features</h3>
            <p className="text-xl text-white/70 max-w-2xl mx-auto">
              Everything you need to secure your AI applications
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Real-time Monitoring */}
            <ModernCard className="relative group" hover glow>
              <div className="absolute inset-0 gradient-primary opacity-5 rounded-2xl"></div>
              <ModernCardContent className="relative p-8">
                <div className="w-12 h-12 gradient-primary rounded-xl flex items-center justify-center mb-6">
                  <ClockIcon className="h-6 w-6 text-white" />
                </div>
                <h4 className="text-xl font-bold text-white mb-4">Real-time Monitoring</h4>
                <p className="text-white/70 mb-6">
                  Monitor AI interactions in real-time with instant risk detection.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm text-white/60">
                    <CheckIcon className="h-4 w-4 text-green-400 mr-2" />
                    Live threat detection
                  </li>
                  <li className="flex items-center text-sm text-white/60">
                    <CheckIcon className="h-4 w-4 text-green-400 mr-2" />
                    Instant alerts
                  </li>
                </ul>
              </ModernCardContent>
            </ModernCard>

            {/* Risk Detection */}
            <ModernCard className="relative group" hover glow>
              <div className="absolute inset-0 gradient-secondary opacity-5 rounded-2xl"></div>
              <ModernCardContent className="relative p-8">
                <div className="w-12 h-12 gradient-secondary rounded-xl flex items-center justify-center mb-6">
                  <ExclamationTriangleIcon className="h-6 w-6 text-white" />
                </div>
                <h4 className="text-xl font-bold text-white mb-4">Risk Detection</h4>
                <p className="text-white/70 mb-6">
                  Detect PII, bias, and harmful content with AI-powered analysis.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm text-white/60">
                    <CheckIcon className="h-4 w-4 text-green-400 mr-2" />
                    PII detection
                  </li>
                  <li className="flex items-center text-sm text-white/60">
                    <CheckIcon className="h-4 w-4 text-green-400 mr-2" />
                    Bias analysis
                  </li>
                </ul>
              </ModernCardContent>
            </ModernCard>

            {/* API Management */}
            <ModernCard className="relative group" hover glow>
              <div className="absolute inset-0 gradient-tertiary opacity-5 rounded-2xl"></div>
              <ModernCardContent className="relative p-8">
                <div className="w-12 h-12 gradient-tertiary rounded-xl flex items-center justify-center mb-6">
                  <KeyIcon className="h-6 w-6 text-white" />
                </div>
                <h4 className="text-xl font-bold text-white mb-4">API Management</h4>
                <p className="text-white/70 mb-6">
                  Secure API access with advanced key management and tracking.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm text-white/60">
                    <CheckIcon className="h-4 w-4 text-green-400 mr-2" />
                    Secure API keys
                  </li>
                  <li className="flex items-center text-sm text-white/60">
                    <CheckIcon className="h-4 w-4 text-green-400 mr-2" />
                    Usage analytics
                  </li>
                </ul>
              </ModernCardContent>
            </ModernCard>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <ModernCard variant="gradient" className="relative overflow-hidden">
            <div className="absolute inset-0 gradient-primary opacity-20"></div>
            <ModernCardContent className="relative p-12">
              <h3 className="text-3xl font-bold text-white mb-4">
                Ready to Secure Your AI?
              </h3>
              <p className="text-xl text-white/80 mb-8">
                Join developers building safer AI applications with AIRMS
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/register">
                  <ModernButton variant="primary" size="xl" className="px-8">
                    <SparklesIcon className="w-5 h-5 mr-2" />
                    Get Started Free
                  </ModernButton>
                </Link>
              </div>
            </ModernCardContent>
          </ModernCard>
        </div>
      </section>
    </div>
  )
}