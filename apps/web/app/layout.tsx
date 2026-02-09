import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "QADMS",
  description: "QA Design Management System",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-page font-sans text-ink min-h-screen">{children}</body>
    </html>
  );
}
