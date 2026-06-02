import type { CandlesListResponse } from "@/lib/contracts/rest";
import { fetchBackendJson, toNextResponse } from "@/lib/upstream/client";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const path = `/api/candles${url.search}`;
  const result = await fetchBackendJson<CandlesListResponse>(path);
  return toNextResponse(result);
}
