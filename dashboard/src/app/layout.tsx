import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI MultiColony Ecosystem - Dashboard",
  description: "Autonomous Agent Operating System Dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#050510] text-white antialiased">{children}</body>
    </html>
  );
}
