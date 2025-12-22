/**
 * API proxy route for authentication endpoints
 * Proxies all /api/auth/* requests to the backend API
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_API_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { all: string[] } }
) {
  return proxyRequest(request, params.all, 'GET');
}

export async function POST(
  request: NextRequest,
  { params }: { params: { all: string[] } }
) {
  return proxyRequest(request, params.all, 'POST');
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { all: string[] } }
) {
  return proxyRequest(request, params.all, 'PUT');
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { all: string[] } }
) {
  return proxyRequest(request, params.all, 'PATCH');
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { all: string[] } }
) {
  return proxyRequest(request, params.all, 'DELETE');
}

async function proxyRequest(
  request: NextRequest,
  pathSegments: string[],
  method: string
) {
  const path = pathSegments.join('/');
  const url = `${BACKEND_URL}/auth/${path}`;

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
