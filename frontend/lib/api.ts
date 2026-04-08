import type {
  AdviceRequest,
  AdviceResponse,
  AnswerPayload,
  NextResponse,
  ResultResponse,
  StartResponse,
} from "./types";
import { ApiError } from "./types";

const DEFAULT_BASE = "http://127.0.0.1:8000";

function getBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (url && url.length > 0) return url.replace(/\/$/, "");
  // NEXT_PUBLIC_* is inlined at build time on Vercel — set it in Project → Settings → Environment Variables
  if (process.env.NODE_ENV === "production") {
    throw new ApiError(
      "Missing NEXT_PUBLIC_API_BASE_URL. Add it in Vercel (Environment Variables), then redeploy.",
      0
    );
  }
  return DEFAULT_BASE;
}

async function parseErrorBody(res: Response): Promise<string | undefined> {
  try {
    const data = (await res.json()) as { detail?: unknown };
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail
        .map((e) => (typeof e === "object" && e && "msg" in e ? String((e as { msg: string }).msg) : String(e)))
        .join("; ");
    }
  } catch {
    /* ignore */
  }
  return undefined;
}

async function requestJson<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const url = `${getBaseUrl()}${path}`;
  let res: Response;
  try {
    res = await fetch(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Network error";
    throw new ApiError(`Cannot reach API at ${getBaseUrl()}. ${msg}`, 0);
  }

  if (!res.ok) {
    const detail = await parseErrorBody(res);
    throw new ApiError(
      detail ?? (res.statusText || "Request failed"),
      res.status,
      detail
    );
  }

  return res.json() as Promise<T>;
}

export async function startAssessment(): Promise<StartResponse> {
  return requestJson<StartResponse>("/start", { method: "POST" });
}

export async function submitAnswer(
  session_id: string,
  answer: AnswerPayload
): Promise<NextResponse> {
  return requestJson<NextResponse>("/next", {
    method: "POST",
    body: JSON.stringify({ session_id, answer }),
  });
}

export async function fetchCareerAdvice(
  payload: AdviceRequest
): Promise<AdviceResponse> {
  return requestJson<AdviceResponse>("/advice", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchAssessmentResult(
  session_id: string
): Promise<ResultResponse> {
  return requestJson<ResultResponse>(`/result/${encodeURIComponent(session_id)}`, {
    method: "GET",
  });
}
