import { ModernCard, ModernCardContent } from './modern-card'
import { cn } from '@/lib/utils'

interface MetricCardProps {
  title: string
  value: string | number
  change?: {
    value: number
    type: 'increase' | 'decrease'
    period: string
  }
  icon: React.ReactNode
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'pink'
  className?: string
}

const colorClasses = {
  blue: {
    gradient: 'from-blue-500 to-cyan-500',
    bg: 'bg-blue-500/20',
    text: 'text-blue-300',
    icon: 'text-blue-400',
  },
  green: {
    gradient: 'from-green-500 to-emerald-500',
    bg: 'bg-green-500/20',
    text: 'text-green-300',
    icon: 'text-green-400',
  },
  yellow: {
    gradient: 'from-yellow-500 to-orange-500',
    bg: 'bg-yellow-500/20',
    text: 'text-yellow-300',
    icon: 'text-yellow-400',
  },
  red: {
    gradient: 'from-red-500 to-pink-500',
    bg: 'bg-red-500/20',
    text: 'text-red-300',
    icon: 'text-red-400',
  },
  purple: {
    gradient: 'from-purple-500 to-indigo-500',
    bg: 'bg-purple-500/20',
    text: 'text-purple-300',
    icon: 'text-purple-400',
  },
  pink: {
    gradient: 'from-pink-500 to-rose-500',
    bg: 'bg-pink-500/20',
    text: 'text-pink-300',
    icon: 'text-pink-400',
  },
}

export function MetricCard({ 
  title, 
  value, 
  change, 
  icon, 
  color = 'blue',
  className 
}: MetricCardProps) {
  const colorClass = colorClasses[color]

  return (
    <ModernCard className={cn('relative overflow-hidden', className)} hover glow>
      {/* Gradient overlay */}
      <div className={cn('absolute inset-0 bg-gradient-to-br opacity-10', colorClass.gradient)} />
      
      <ModernCardContent className="relative">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm text-white/70 mb-1">{title}</p>
            <p className="text-2xl font-bold text-white mb-2">{value}</p>
            
            {change && (
              <div className="flex items-center space-x-1">
                <div className={cn(
                  'flex items-center space-x-1 text-xs px-2 py-1 rounded-full',
                  change.type === 'increase' ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'
                )}>
                  <span>{change.type === 'increase' ? '↗' : '↘'}</span>
                  <span>{Math.abs(change.value)}%</span>
                </div>
                <span className="text-xs text-white/50">{change.period}</span>
              </div>
            )}
          </div>
          
          <div className={cn('p-3 rounded-xl', colorClass.bg)}>
            <div className={cn('h-6 w-6', colorClass.icon)}>
              {icon}
            </div>
          </div>
        </div>
      </ModernCardContent>
    </ModernCard>
  )
}

export default MetricCard
