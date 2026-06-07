// TODO: move JWT storage from localStorage to HTTP-only cookies before production.
// Current localStorage approach is vulnerable to XSS; cookies with HttpOnly + SameSite=Lax + Secure
// are required for production. Plan: add refresh token endpoint to API, switch this file to read
// from cookies, add fetch interceptor for auto-refresh on 401.

const TOKEN_KEY = "courierx_token";

export function getToken(): string | null {
  // TODO: move to HTTP-only cookie before production
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  // TODO: move to HTTP-only cookie before production
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  // TODO: move to HTTP-only cookie before production
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  // TODO: move to HTTP-only cookie before production
  return getToken() !== null;
}
