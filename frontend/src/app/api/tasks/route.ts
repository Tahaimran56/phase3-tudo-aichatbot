/**
 * API proxy route for tasks endpoints
 * Proxies /api/tasks requests to the backend API
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';

async function proxyRequest(request: NextRequest, method: string, path: string = '') {
  const url = `${BACKEND_URL}/tasks${path}`;

  try {
    const headers: HeadersInit = {};

    // Copy relevant headers
    request.headers.forEach((value, key) => {
      if (
        key.toLowerCase() !== 'host' &&
        key.toLowerCase() !== 'connection' &&
        key.toLowerCase() !== 'content-length'
      ) {
        headers[key] = value;
      }
    });

    const options: RequestInit = {
      method,
      headers,
      credentials: 'include',
    };

    // Add body for POST, PUT, PATCH requests
    if (method !== 'GET' && method !== 'DELETE') {
      const body = await request.text();
      if (body) {
        options.body = body;
      }
    }

    const response = await fetch(url, options);
    const data = await response.text();

    // Create response with backend data
    const nextResponse = new NextResponse(data, {
      status: response.status,
      statusText: response.statusText,
    });

    // Copy response headers (including Set-Cookie)
    response.headers.forEach((value, key) => {
      nextResponse.headers.set(key, value);
    });

    return nextResponse;
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { detail: 'Failed to connect to backend API' },
      { status: 502 }
    );
  }
}

export async function GET(request: NextRequest) {
  return proxyRequest(request, 'GET');
}

export async function POST(request: NextRequest) {
  return proxyRequest(request, 'POST');
}
