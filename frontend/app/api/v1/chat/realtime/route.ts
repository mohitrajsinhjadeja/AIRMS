import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    // Validate request
    if (req.headers.get('content-type') !== 'application/json') {
      return NextResponse.json(
        { error: 'Content-Type must be application/json' },
        { status: 400 }
      );
    }

    const auth = req.headers.get('authorization');
    if (!auth || !auth.startsWith('Bearer ')) {
      return NextResponse.json(
        { error: 'Missing or invalid Authorization header' },
        { status: 401 }
      );
    }

    const body = await req.json();
    if (!body.message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Use localhost for development, production API for deployed
    const API_URL = process.env.NODE_ENV === 'production' 
      ? 'https://airms-backend-1013218741719.us-central1.run.app'
      : 'http://localhost:8000';
    
    const endpoint = `${API_URL}/api/v1/chat/realtime`;
    console.log('🚀 Forwarding realtime chat request to:', endpoint);
    
    // Forward request to the new real-time endpoint
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': auth,
      },
      body: JSON.stringify({
        message: body.message,
        conversation_id: body.conversation_id,
        context: {
          ...body.context,
          frontend_source: 'nextjs_dashboard',
          user_agent: req.headers.get('user-agent'),
          timestamp: new Date().toISOString()
        }
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend Real-time API Error:', {
        status: response.status,
        statusText: response.statusText,
        body: errorText,
        endpoint
      });
      
      return NextResponse.json(
        { 
          error: `Backend returned ${response.status}: ${response.statusText}`,
          details: errorText,
          endpoint
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('✅ Real-time chat response received:', {
      risk_score: data.risk_score,
      risk_flags: data.risk_flags,
      conversation_id: data.conversation_id?.slice(0, 8) + '...',
      message_length: data.message?.length
    });

    // Validate the response format
    if (typeof data.risk_score !== 'number' || !Array.isArray(data.risk_flags)) {
      console.warn('⚠️  Backend response format unexpected:', data);
      
      // Try to normalize the response
      const normalizedData = {
        message: data.message || 'Response received but format was unexpected',
        risk_score: typeof data.risk_score === 'number' ? data.risk_score : 0,
        risk_flags: Array.isArray(data.risk_flags) ? data.risk_flags : ['Unknown'],
        conversation_id: data.conversation_id || 'unknown',
        timestamp: data.timestamp || new Date().toISOString()
      };
      
      return NextResponse.json(normalizedData);
    }

    return NextResponse.json(data);

  } catch (error: any) {
    console.error('Real-time Chat API Error:', {
      message: error.message,
      stack: error.stack,
      cause: error.cause
    });
    
    return NextResponse.json(
      { 
        error: 'Real-time Chat API Error',
        message: error.message || 'Internal Server Error',
        type: error.name,
        // Fallback response format for frontend compatibility
        risk_score: 0,
        risk_flags: ['API Error'],
        conversation_id: 'error-' + Date.now(),
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}