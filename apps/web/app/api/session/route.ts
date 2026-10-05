import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  if (
    request.headers.get("origin") !==
    (process.env.WORKSPACE_ORIGIN || "http://localhost:3000")
  )
    return NextResponse.json({ detail: "Origin denied" }, { status: 403 });
  const body = await request.json().catch(() => null);
  const token = body?.token;
  if (typeof token !== "string" || token.length < 32 || token.length > 512)
    return NextResponse.json(
      { detail: "Geçerli erişim anahtarı gerekli." },
      { status: 400 },
    );
  try {
    const response = await fetch(
      `${process.env.API_INTERNAL_URL || "http://127.0.0.1:8000"}/workspace-session`,
      {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
        signal: AbortSignal.timeout(5000),
      },
    );
    if (!response.ok)
      return NextResponse.json(
        {
          detail:
            response.status === 503
              ? "Çalışma alanı anahtarı sunucuda yapılandırılmamış."
              : "Anahtar doğrulanamadı.",
        },
        { status: response.status },
      );
    const result = NextResponse.json({ ok: true });
    const session = await response.json();
    result.cookies.set("career_session", session.session_token, {
      httpOnly: true,
      sameSite: "strict",
      secure: (
        process.env.WORKSPACE_ORIGIN || "http://localhost:3000"
      ).startsWith("https://"),
      path: "/",
      maxAge: 8 * 60 * 60,
    });
    return result;
  } catch {
    return NextResponse.json(
      { detail: "API bağlantısı kurulamadı." },
      { status: 503 },
    );
  }
}
export async function DELETE(request: NextRequest) {
  if (
    request.headers.get("origin") !==
    (process.env.WORKSPACE_ORIGIN || "http://localhost:3000")
  )
    return NextResponse.json({ detail: "Origin denied" }, { status: 403 });
  const token = request.cookies.get("career_session")?.value;
  if (token) {
    try {
      const response = await fetch(
        `${process.env.API_INTERNAL_URL || "http://127.0.0.1:8000"}/workspace-session`,
        {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
          signal: AbortSignal.timeout(5000),
        },
      );
      if (!response.ok)
        return NextResponse.json(
          { detail: "Oturum sunucuda kapatılamadı." },
          { status: 503 },
        );
    } catch {
      return NextResponse.json(
        { detail: "Oturum sunucuda kapatılamadı." },
        { status: 503 },
      );
    }
  }
  const result = NextResponse.json({ ok: true });
  result.cookies.delete("career_session");
  return result;
}
