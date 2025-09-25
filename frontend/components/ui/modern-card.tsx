import { forwardRef } from 'react'
import { cn } from '@/lib/utils'

export interface ModernCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'glass' | 'solid' | 'gradient' | 'bordered'
  hover?: boolean
  glow?: boolean
}

const ModernCard = forwardRef<HTMLDivElement, ModernCardProps>(
  ({ className, variant = 'glass', hover = true, glow = false, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'rounded-2xl transition-all duration-300',
          
          // Variant styles
          {
            // Glass morphism
            'glass-card': variant === 'glass',
            
            // Solid card
            'bg-white/95 backdrop-blur-sm border border-white/20 shadow-lg': variant === 'solid',
            
            // Gradient background
            'gradient-primary border border-white/20 shadow-lg': variant === 'gradient',
            
            // Bordered
            'bg-transparent border-2 border-white/30': variant === 'bordered',
          },
          
          // Hover effects
          {
            'hover:shadow-xl hover:scale-105 cursor-pointer': hover,
            'hover:shadow-2xl hover:shadow-purple-500/25': hover && glow,
          },
          
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)

ModernCard.displayName = 'ModernCard'

const ModernCardHeader = forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('flex flex-col space-y-1.5 p-6 pb-4', className)}
      {...props}
    />
  )
)

ModernCardHeader.displayName = 'ModernCardHeader'

const ModernCardTitle = forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      className={cn('text-lg font-semibold leading-none tracking-tight text-white', className)}
      {...props}
    />
  )
)

ModernCardTitle.displayName = 'ModernCardTitle'

const ModernCardDescription = forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p
      ref={ref}
      className={cn('text-sm text-white/70', className)}
      {...props}
    />
  )
)

ModernCardDescription.displayName = 'ModernCardDescription'

const ModernCardContent = forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div 
      ref={ref} 
      className={cn('p-6 pt-0', className)} 
      {...props} 
    />
  )
)

ModernCardContent.displayName = 'ModernCardContent'

const ModernCardFooter = forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('flex items-center p-6 pt-0', className)}
      {...props}
    />
  )
)

ModernCardFooter.displayName = 'ModernCardFooter'

export {
  ModernCard,
  ModernCardHeader,
  ModernCardTitle,
  ModernCardDescription,
  ModernCardContent,
  ModernCardFooter,
}
