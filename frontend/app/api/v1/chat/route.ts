import { NextRequest, NextResponse } from 'next/server';

// Handle GET requests to verify route is working
export async function GET() {
  return NextResponse.json({ status: 'Chat API route is active' });
}

// Forward chat requests to backend
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

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://airms-backend-1013218741719.us-central1.run.app' ||'http://localhost:8000';
    console.log('🔄 Forwarding chat request to:', `${API_URL}/api/v1/chat`);
    
    const response = await fetch(`${API_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': auth,
      },
      body: JSON.stringify(body),
      credentials: 'include',
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend Error:', {
        status: response.status,
        statusText: response.statusText,
        body: errorText
      });
      
      return NextResponse.json(
        { 
          error: `Backend returned ${response.status}: ${response.statusText}`,
          details: errorText
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Chat response:', data);
    return NextResponse.json(data);

  } catch (error: any) {
    console.error('Chat API Error:', {
      message: error.message,
      stack: error.stack,
      cause: error.cause
    });
    
    return NextResponse.json(
      { 
        error: 'Chat API Error',
        message: error.message || 'Internal Server Error',
        type: error.name
      },
      { status: 500 }
    );
  }
}