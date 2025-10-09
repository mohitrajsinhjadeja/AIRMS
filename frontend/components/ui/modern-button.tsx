import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'gradient'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  isLoading?: boolean
}

const ModernButton = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        className={cn(
          // Base styles
          'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed',
          
          // Size variants
          {
            'text-xs px-3 py-1.5 rounded-lg': size === 'sm',
            'text-sm px-4 py-2 rounded-xl': size === 'md',
            'text-base px-6 py-3 rounded-xl': size === 'lg',
            'text-lg px-8 py-4 rounded-2xl': size === 'xl',
          },
          
          // Variant styles
          {
            // Primary - Gradient
            'gradient-primary text-white shadow-lg hover:shadow-xl transform hover:scale-105 focus:ring-purple-500': 
              variant === 'primary',
            
            // Secondary - Glass
            'glass-card text-white hover:bg-white/20 focus:ring-white/50': 
              variant === 'secondary',
            
            // Outline - Border with glass
            'border border-white/30 text-white hover:bg-white/10 focus:ring-white/50': 
              variant === 'outline',
            
            // Ghost - Minimal
            'text-white hover:bg-white/10 focus:ring-white/50': 
              variant === 'ghost',
            
            // Destructive - Red gradient
            'gradient-destructive text-white shadow-lg hover:shadow-xl transform hover:scale-105 focus:ring-red-500': 
              variant === 'destructive',
            
            // Gradient - Animated gradient
            'gradient-secondary text-white shadow-lg hover:shadow-xl transform hover:scale-105 animate-gradient focus:ring-pink-500': 
              variant === 'gradient',
          },
          
          className
        )}
        disabled={disabled || isLoading}
        ref={ref}
        {...props}
      >
        {isLoading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )}
        {children}
      </button>
    )
  }
)

ModernButton.displayName = 'ModernButton'

export { ModernButton }
