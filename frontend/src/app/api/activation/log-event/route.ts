import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const backendUrl = "http://backend:8000";
    const apiResponse = await fetch(`${backendUrl}/api/activation/log-event`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!apiResponse.ok) {
      const errorText = await apiResponse.text();
      throw new Error(`Error from backend: ${apiResponse.status} ${errorText}`);
    }

    const responseData = await apiResponse.json();

    return NextResponse.json(responseData, { status: apiResponse.status });

  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json(
      { message: 'Internal Server Error in Next.js API route' },
      { status: 500 }
    );
  }
}