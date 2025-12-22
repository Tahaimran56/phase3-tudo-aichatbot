/**
 * API proxy route for individual task operations
 * Proxies /api/tasks/:id requests to the backend API
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';

async function proxyRequest(
  request: NextRequest,
  taskId: string,
  method: string
) {
  const url = `${BACKEND_URL}/tasks/${taskId}`;

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

    // Add body for PUT, PATCH requests
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

    // Copy response headers
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

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  return proxyRequest(request, params.id, 'GET');
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  return proxyRequest(request, params.id, 'PUT');
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  return proxyRequest(request, params.id, 'PATCH');
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  return proxyRequest(request, params.id, 'DELETE');
}
