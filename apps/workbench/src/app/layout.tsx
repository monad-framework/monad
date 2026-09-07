import type { Metadata } from "next";

import "./globals.css";
import "./workbench-v0.css";

export const metadata: Metadata = {
  title: "Monad Workbench",
  description:
    "Local-first read-only engineering workbench for governed Monad projections.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
