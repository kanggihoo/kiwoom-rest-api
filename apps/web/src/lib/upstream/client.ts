import type { ErrorEnvelope, RestErrorCode } from "@/lib/contracts/errors";

import { NextResponse } from "next/server";

import { isErrorEnvelope } from "@/lib/contracts/decoders";

type UpstreamRequestInit = Omit<RequestInit, "signal"> & {
  timeoutMs?: number;
};

type ErrorEnvelopeLike = ErrorEnvelope;

const DEFAULT_TIMEOUT_MS = 5_000;
const DEFAULT_UPSTREAM_BASE_URL = "http://localhost:8000";

export type UpstreamResult<TData> =
  | {
      ok: true;
      status: number;
      data: TData;
    }
  | {
      ok: false;
      status: number;
      envelope: ErrorEnvelopeLike;
    };

function normalizePath(path: string): string {
  return path.startsWith("/") ? path : `/${path}`;
}

function getBackendBaseUrl(): string {
  return (process.env.FASTAPI_BASE_URL ?? DEFAULT_UPSTREAM_BASE_URL).replace(/\/$/, "");
}

function makeErrorEnvelope(
  code: RestErrorCode,
  message: string,
  details: Record<string, unknown> | null = null,
): ErrorEnvelope {
  return {
    type: "error",
    timestamp: new Date().toISOString(),
    data: {
      code,
      message,
      details,
    },
  };
}

function makeBackendErrorResponse(
  status: number,
  code: RestErrorCode,
  message: string,
  details?: Record<string, unknown> | null,
): UpstreamResult<never> {
  const envelope = makeErrorEnvelope(code, message, details ?? null);

  return {
    ok: false,
    status,
    envelope,
  };
}

function parseJsonOrFallback(rawText: string): { ok: true; value: unknown } | { ok: false } {
  if (!rawText.trim()) {
    return { ok: false };
  }

  try {
    return { ok: true, value: JSON.parse(rawText) };
  } catch {
    return { ok: false };
  }
}

function fallbackCodeFromStatus(status: number): RestErrorCode {
  switch (status) {
    case 400:
      return "BAD_REQUEST";
    case 404:
      return "NOT_FOUND";
    case 418:
      return "TEMPORARILY_BLOCKED";
    case 422:
      return "VALIDATION_ERROR";
    case 429:
      return "RATE_LIMITED";
    case 504:
      return "UPBIT_TIMEOUT";
    case 500:
    case 502:
    case 503:
      return "UPBIT_ERROR";
    default:
      return "INTERNAL_ERROR";
  }
}

export async function fetchBackendJson<TData>(
  path: string,
  init: UpstreamRequestInit = {},
): Promise<UpstreamResult<TData>> {
  const timeoutMs = init.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const normalizedPath = normalizePath(path);
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${getBackendBaseUrl()}${normalizedPath}`, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init.headers ?? {}),
      },
      signal: controller.signal,
    });

    const rawBody = await response.text();
    const parsedBody = parseJsonOrFallback(rawBody);

    if (!response.ok) {
      if (parsedBody.ok && isErrorEnvelope(parsedBody.value)) {
        const envelope = parsedBody.value;
        return {
          ok: false,
          status: response.status,
          envelope,
        };
      }

      return makeBackendErrorResponse(
        response.status,
        fallbackCodeFromStatus(response.status),
        `Upstream responded with HTTP ${response.status}`,
        rawBody ? { rawBody } : null,
      );
    }

    if (!parsedBody.ok) {
      return makeBackendErrorResponse(
        502,
        "UPBIT_ERROR",
        "Invalid JSON response from upstream.",
        { path: normalizedPath, rawBody },
      );
    }

    return {
      ok: true,
      status: response.status,
      data: parsedBody.value as TData,
    };
  } catch (error) {
    const isTimeout = error instanceof DOMException && error.name === "AbortError";
    if (isTimeout) {
      return makeBackendErrorResponse(
        504,
        "UPBIT_TIMEOUT",
        `Upstream request timed out after ${timeoutMs}ms.`,
        { path: normalizedPath },
      );
    }

    return makeBackendErrorResponse(
      502,
      "UPBIT_ERROR",
      "Failed to call upstream.",
      { path: normalizedPath, error: String(error) },
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export function toNextResponse<TData>(result: UpstreamResult<TData>) {
  if (result.ok) {
    return NextResponse.json(result.data, { status: result.status });
  }

  return NextResponse.json(result.envelope, { status: result.status });
}
