import { SparklesIcon } from '@heroicons/react/24/outline'

export function LoadingSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-4">
        {/* Animated Logo */}
        <div className="w-16 h-16 mx-auto gradient-primary rounded-2xl flex items-center justify-center animate-gradient">
          <SparklesIcon className="h-8 w-8 text-white animate-pulse" />
        </div>
        
        {/* Loading Text */}
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-white">Loading AIRMS</h3>
          <p className="text-white/70 text-sm">AI Risk Management System</p>
        </div>
        
        {/* Animated Dots */}
        <div className="flex items-center justify-center space-x-1">
          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  )
}

export function PageLoading() {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="text-center space-y-3">
        {/* Mini Animated Logo */}
        <div className="w-8 h-8 mx-auto gradient-primary rounded-xl flex items-center justify-center animate-gradient">
          <SparklesIcon className="h-4 w-4 text-white animate-pulse" />
        </div>
        
        {/* Loading Dots */}
        <div className="flex items-center justify-center space-x-1">
          <div className="w-1 h-1 bg-purple-400 rounded-full animate-bounce"></div>
          <div className="w-1 h-1 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-1 h-1 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  )
}

// Default export for backward compatibility
export default LoadingSpinner
