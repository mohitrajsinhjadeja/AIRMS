'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { notificationApi } from '@/lib/api'
import { 
  BellIcon,
  MagnifyingGlassIcon,
  UserIcon,
  SparklesIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  category?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  read: boolean;
  time_ago: string;
  action_url?: string;
}

export default function TopBar() {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [unreadCount, setUnreadCount] = useState(0)

  // Fetch notifications on component mount
  useEffect(() => {
    fetchNotifications()
    // Refresh notifications every 30 seconds
    const interval = setInterval(fetchNotifications, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchNotifications = async () => {
    try {
      const response = await notificationApi.getNotifications({ 
        limit: 10, 
        unread_only: false 
      })
      const notifications = response.data || []
      setNotifications(notifications)
      
      // Count unread notifications
      const unread = notifications.filter((n: Notification) => !n.read).length
      setUnreadCount(unread)
    } catch (error: any) {
      console.error('Failed to fetch notifications:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data
      })
      
      // Handle unauthorized errors
      if (error.response?.status === 401) {
        // Log out the user if token is invalid/expired
        const auth = useAuth()
        auth.logout()
      }
      
      // Fallback to empty array if API fails
      setNotifications([])
      setUnreadCount(0)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await notificationApi.markAsRead(notificationId)
      // Update local state
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await notificationApi.markAllAsRead()
      // Update local state
      setNotifications(prev => prev.map(n => ({ ...n, read: true })))
      setUnreadCount(0)
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error)
    }
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'warning':
        return 'bg-yellow-400'
      case 'error':
        return 'bg-red-400'
      case 'success':
        return 'bg-green-400'
      default:
        return 'bg-blue-400'
    }
  }

  return (
    <div className="lg:pl-64">
      <div className="sticky top-0 z-30 bg-gray-900 border-b border-gray-700">
        <div className="flex h-16 items-center justify-between px-6">
          {/* Search */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search..."
                className="w-full bg-gray-800 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
              />
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-4">
            {/* Active Calls Indicator */}
            <div className="hidden md:flex items-center space-x-2 text-sm text-gray-300">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Active calls: 0</span>
            </div>

            {/* Notifications */}
            <div className="relative group">
              <button className="relative p-2 text-white/70 hover:text-white transition-colors duration-200">
                <BellIcon className="h-5 w-5" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </button>

              {/* Notifications Dropdown */}
              <div className="absolute right-0 mt-2 w-80 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 transform translate-y-1 group-hover:translate-y-0">
                <div className="glass-card rounded-xl border border-white/10 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-white">Notifications</h3>
                    {unreadCount > 0 && (
                      <button 
                        onClick={handleMarkAllAsRead}
                        className="text-xs text-purple-300 hover:text-purple-200 transition-colors duration-200"
                      >
                        Mark all read
                      </button>
                    )}
                  </div>
                  
                  <div className="space-y-3 max-h-80 overflow-y-auto">
                    {loading ? (
                      <div className="flex items-center justify-center py-4">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                      </div>
                    ) : notifications.length > 0 ? (
                      notifications.map((notification) => (
                        <div 
                          key={notification.id} 
                          className={`flex items-start space-x-3 p-2 hover:bg-white/5 rounded-lg transition-colors duration-200 cursor-pointer ${
                            !notification.read ? 'bg-white/5' : ''
                          }`}
                          onClick={() => !notification.read && handleMarkAsRead(notification.id)}
                        >
                          <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${getNotificationIcon(notification.type)}`} />
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm ${notification.read ? 'text-white/70' : 'text-white font-medium'}`}>
                              {notification.message}
                            </p>
                            <p className="text-xs text-white/50">{notification.time_ago}</p>
                          </div>
                          {!notification.read && (
                            <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full"></div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-4 text-white/50 text-sm">
                        No notifications yet
                      </div>
                    )}
                  </div>
                  
                  <button className="w-full mt-3 text-xs text-purple-300 hover:text-purple-200 transition-colors duration-200">
                    View all notifications
                  </button>
                </div>
              </div>
            </div>

            {/* User Menu */}
            <div className="relative group">
              <button className="flex items-center space-x-3 p-2 hover:bg-white/10 rounded-xl transition-all duration-200">
                <div className="w-8 h-8 gradient-primary rounded-full flex items-center justify-center animate-gradient">
                  <UserIcon className="h-4 w-4 text-white" />
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium text-white">{user?.email?.split('@')[0] || 'User'}</p>
                  <p className="text-xs text-white/50">Developer</p>
                </div>
              </button>

              {/* User Dropdown */}
              <div className="absolute right-0 mt-2 w-56 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 transform translate-y-1 group-hover:translate-y-0">
                <div className="glass-card rounded-xl border border-white/10 p-2">
                  <div className="px-3 py-2 border-b border-white/10 mb-2">
                    <p className="text-sm font-medium text-white">{user?.email}</p>
                    <p className="text-xs text-white/50">Free Plan</p>
                  </div>
                  <a href="/dashboard/settings" className="flex items-center space-x-2 px-3 py-2 text-sm text-white/70 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-200">
                    <UserIcon className="h-4 w-4" />
                    <span>Profile Settings</span>
                  </a>
                  <a href="/dashboard/billing" className="flex items-center space-x-2 px-3 py-2 text-sm text-white/70 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-200">
                    <SparklesIcon className="h-4 w-4" />
                    <span>Upgrade Plan</span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
