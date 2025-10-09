import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: 'glass' | 'solid' | 'outline'
  icon?: React.ReactNode
  error?: string
}

const ModernInput = forwardRef<HTMLInputElement, InputProps>(
  ({ className, variant = 'glass', icon, error, type, ...props }, ref) => {
    return (
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50">
            {icon}
          </div>
        )}
        <input
          type={type}
          className={cn(
            'w-full text-white placeholder-white/50 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500',
            
            // Variant styles
            {
              // Glass
              'glass-card px-4 py-3 rounded-xl border border-white/20': variant === 'glass',
              
              // Solid
              'bg-white/10 backdrop-blur-sm px-4 py-3 rounded-xl border border-white/20': variant === 'solid',
              
              // Outline
              'bg-transparent px-4 py-3 rounded-xl border-2 border-white/30': variant === 'outline',
            },
            
            // Icon padding
            {
              'pl-10': icon,
            },
            
            // Error state
            {
              'border-red-400 focus:ring-red-500': error,
            },
            
            className
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-red-300">{error}</p>
        )}
      </div>
    )
  }
)

ModernInput.displayName = 'ModernInput'

export { ModernInput }
