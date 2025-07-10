import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const backendUrl = "http://backend:8000";
    const apiResponse = await fetch(`${backendUrl}/api/leads/batch-score`, {
      method: 'POST',
      body: formData,
    });

    const responseData = await apiResponse.json();

    if (!apiResponse.ok) {
      return NextResponse.json({ detail: responseData.detail || 'Error from backend' }, { status: apiResponse.status });
    }

    return NextResponse.json(responseData, { status: apiResponse.status });

  } catch (error) {
    console.error('Batch score API route error:', error);
    return NextResponse.json(
      { detail: 'Internal Server Error in Next.js API route' },
      { status: 500 }
    );
  }
}