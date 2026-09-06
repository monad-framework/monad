import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Monad Workbench",
  description:
    "Internal cognitive workbench for planning and developing Monad.",
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
