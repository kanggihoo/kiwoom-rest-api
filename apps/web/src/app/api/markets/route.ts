import type { MarketsListResponse } from "@/lib/contracts/rest";
import { fetchBackendJson, toNextResponse } from "@/lib/upstream/client";

export const dynamic = "force-dynamic";

export async function GET() {
  const result = await fetchBackendJson<MarketsListResponse>("/api/markets");
  return toNextResponse(result);
}
