import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "AI Career OS · Foundation", description: "Evidence-led AI engineering career platform" };
export default function Layout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
