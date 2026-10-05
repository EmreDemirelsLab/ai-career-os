import { NextRequest, NextResponse } from "next/server";

type Context = { params: Promise<{ path?: string[] }> };
async function proxy(request: NextRequest, context: Context) {
  if (
    request.method !== "GET" &&
    request.headers.get("origin") !== request.nextUrl.origin
  )
    return NextResponse.json({ detail: "Origin denied" }, { status: 403 });
  const token = request.cookies.get("career_session")?.value;
  if (!token)
    return NextResponse.json({ detail: "Oturum açmalısın." }, { status: 401 });
  const { path = [] } = await context.params;
  if (path.some((x) => !/^[a-zA-Z0-9_-]+$/.test(x)))
    return NextResponse.json({ detail: "Invalid route" }, { status: 400 });
  const headers: Record<string, string> = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  if (request.headers.get("x-confirm-delete"))
    headers["X-Confirm-Delete"] = request.headers.get("x-confirm-delete")!;
  const body = request.method === "GET" ? undefined : await request.text();
  if (body && body.length > 100000)
    return NextResponse.json({ detail: "İstek çok büyük." }, { status: 413 });
  try {
    const response = await fetch(
      `${process.env.API_INTERNAL_URL || "http://127.0.0.1:8000"}/workspace${path.length ? "/" + path.join("/") : ""}`,
      {
        method: request.method,
        headers,
        body: body || undefined,
        cache: "no-store",
        signal: AbortSignal.timeout(10000),
      },
    );
    return new NextResponse(
      response.status === 204 ? null : await response.text(),
      {
        status: response.status,
        headers: {
          "Content-Type": "application/json",
          "Cache-Control": "no-store",
        },
      },
    );
  } catch {
    return NextResponse.json(
      { detail: "API şu anda erişilemiyor." },
      { status: 503 },
    );
  }
}
export const GET = proxy;
export const POST = proxy;
export const DELETE = proxy;
