'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <Card>
          <CardHeader>
            <CardTitle>Frontend Test Page</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p>✅ Next.js 15 is working</p>
              <p>✅ Tailwind CSS is working</p>
              <p>✅ Components are rendering</p>
              <Button>✅ Button component works</Button>
              
              <div className="mt-8">
                <h3 className="text-lg font-semibold mb-4">Navigation Links</h3>
                <div className="space-x-4">
                  <a href="/login" className="text-blue-600 hover:underline">
                    Login Page
                  </a>
                  <a href="/register" className="text-blue-600 hover:underline">
                    Register Page
                  </a>
                  <a href="/dashboard" className="text-blue-600 hover:underline">
                    Dashboard (requires auth)
                  </a>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
