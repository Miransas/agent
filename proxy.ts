import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// TODO: enable real server-side auth protection in 7D when JWT moves to HTTP-only cookie.
// For now, all routes pass through — client-side DashboardGuard handles redirects.
// (Next.js 16 renamed `middleware` → `proxy`; see node_modules/next/dist/docs/01-app/03-api-reference/03-file-conventions/proxy.md)
export function proxy(_request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: [
    // Match all request paths except for:
    // - api routes
    // - _next static files
    // - favicon, OG images, etc
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\.png).*)",
  ],
};
