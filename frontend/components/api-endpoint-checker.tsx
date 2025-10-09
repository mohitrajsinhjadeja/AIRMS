"use client";

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export function ApiEndpointChecker() {
  const [results, setResults] = useState<{[key: string]: {status: string, data?: any, error?: string}}>({});
  const [isVisible, setIsVisible] = useState(false);
  const [isChecking, setIsChecking] = useState(false);

  const endpoints = [
    '/api/v1/analytics/statistics?days=7',
    '/api/v1/analytics/timeline?days=7',
    '/api/v1/analytics/real-time-stats',
    '/api/v1/analytics/dashboard?days=7',
    '/api/v1/analytics/system/health',
    '/api/v1/auth/me'
  ];

  const checkEndpoints = async () => {
    setIsChecking(true);
    const newResults: {[key: string]: {status: string, data?: any, error?: string}} = {};
    
    for (const endpoint of endpoints) {
      try {
        const response = await api.get(endpoint);
        newResults[endpoint] = {
          status: 'success',
          data: response.data
        };
      } catch (error: any) {
        newResults[endpoint] = {
          status: 'error',
          error: error.response ? `${error.response.status}: ${error.response.statusText}` : error.message
        };
      }
    }
    
    setResults(newResults);
    setIsChecking(false);
  };

  useEffect(() => {
    // Add keyboard shortcut to show API checker (Ctrl+Shift+A)
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'A') {
        e.preventDefault();
        setIsVisible(prev => !prev);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (!isVisible) return null;

  return (
    <div 
      style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        zIndex: 9999,
        background: 'rgba(0,0,0,0.9)',
        color: 'white',
        padding: '20px',
        borderRadius: '10px',
        maxWidth: '800px',
        maxHeight: '80vh',
        overflow: 'auto',
        fontSize: '12px',
        fontFamily: 'monospace',
        boxShadow: '0 0 20px rgba(0,0,0,0.5)'
      }}
    >
      <h2 style={{ marginTop: 0 }}>API Endpoint Checker</h2>
      <p>Base URL: {api.defaults.baseURL}</p>
      
      <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
        <button 
          onClick={checkEndpoints}
          disabled={isChecking}
          style={{
            background: '#4a5568',
            color: 'white',
            border: 'none',
            padding: '8px 15px',
            borderRadius: '5px',
            cursor: isChecking ? 'not-allowed' : 'pointer'
          }}
        >
          {isChecking ? 'Checking...' : 'Check Endpoints'}
        </button>
        
        <button 
          onClick={() => setIsVisible(false)}
          style={{
            background: '#2d3748',
            color: 'white',
            border: 'none',
            padding: '8px 15px',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Close
        </button>
      </div>
      
      <div>
        {Object.entries(results).map(([endpoint, result]) => (
          <div 
            key={endpoint} 
            style={{ 
              marginBottom: '15px',
              padding: '10px',
              borderRadius: '5px',
              background: result.status === 'success' ? 'rgba(72, 187, 120, 0.2)' : 'rgba(245, 101, 101, 0.2)'
            }}
          >
            <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{endpoint}</div>
            <div style={{ 
              color: result.status === 'success' ? '#48bb78' : '#f56565',
              marginBottom: '5px'
            }}>
              Status: {result.status}
            </div>
            
            {result.error && (
              <div style={{ color: '#f56565' }}>Error: {result.error}</div>
            )}
            
            {result.data && (
              <details>
                <summary style={{ cursor: 'pointer', marginTop: '5px' }}>View Response Data</summary>
                <pre style={{ 
                  background: 'rgba(0,0,0,0.3)', 
                  padding: '10px', 
                  borderRadius: '5px',
                  overflowX: 'auto',
                  marginTop: '5px'
                }}>
                  {JSON.stringify(result.data, null, 2)}
                </pre>
              </details>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}