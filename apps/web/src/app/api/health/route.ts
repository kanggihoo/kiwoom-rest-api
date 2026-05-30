import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

type BackendHealth = {
  status: string;
  service: string;
};

const fastApiBaseUrl = process.env.FASTAPI_BASE_URL ?? "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${fastApiBaseUrl}/health`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        {
          status: "error",
          service: "upbit-dashboard-web",
          backendStatus: response.status,
        },
        { status: 502 },
      );
    }

    const backend = (await response.json()) as BackendHealth;

    return NextResponse.json({
      status: "ok",
      service: "upbit-dashboard-web",
      backend,
    });
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        service: "upbit-dashboard-web",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 502 },
    );
  }
}
