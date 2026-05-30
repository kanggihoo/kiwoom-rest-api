import { fetchBackendJson, toNextResponse } from "@/lib/upstream/client";

type HealthResponse = {
  status: string;
  service: string;
};

export const dynamic = "force-dynamic";

export async function GET() {
  const result = await fetchBackendJson<HealthResponse>("/health");
  return toNextResponse(result);
}
