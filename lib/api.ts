import { getToken, clearToken } from "./auth";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_COURIERX_API_URL || "http://localhost:8080";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface ErrorBody {
  error?: string;
  message?: string;
}

async function apiFetch<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  // TODO: move to HTTP-only cookie before production
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  let body: ErrorBody & Record<string, unknown> = {};
  try {
    body = (await res.json()) as ErrorBody & Record<string, unknown>;
  } catch {
    body = {};
  }

  if (!res.ok) {
    if (res.status === 401) {
      // TODO: move to HTTP-only cookie before production
      clearToken();
    }
    throw new ApiError(
      res.status,
      body.error || "unknown_error",
      body.message || res.statusText
    );
  }

  return body as T;
}

export interface AuthResponse {
  user_id: string;
  workspace_id: string;
  email: string;
  token: string;
}

export interface MeResponse {
  user_id: string;
  workspace_id: string;
  email: string;
  name: string | null;
}

export interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  created_at: string;
  last_used_at: string | null;
  revoked_at: string | null;
}

export interface CreateApiKeyResponse {
  id: string;
  name: string;
  /** Full plaintext key — shown once on creation. */
  key: string;
  key_prefix: string;
  created_at: string;
}

export const api = {
  auth: {
    register: (data: { email: string; password: string; name?: string }) =>
      apiFetch<AuthResponse>("/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    login: (data: { email: string; password: string }) =>
      apiFetch<AuthResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    me: () => apiFetch<MeResponse>("/auth/me"),
  },
  apiKeys: {
    list: () => apiFetch<{ keys: ApiKey[] }>("/v1/api-keys"),
    create: (name: string) =>
      apiFetch<CreateApiKeyResponse>("/v1/api-keys", {
        method: "POST",
        body: JSON.stringify({ name }),
      }),
    revoke: (id: string) =>
      apiFetch<void>(`/v1/api-keys/${id}`, {
        method: "DELETE",
      }),
  },
};
