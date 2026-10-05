import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "AI Career OS · Kişisel Çalışma Alanı",
  description: "Kanıta dayalı AI mühendisliği, öğrenme ve teknik İngilizce",
};
export default function Layout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}
