import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Lenny Growth Assistant",
  description: "Enterprise RAG & Content Engine grounded in Lenny's Podcast transcripts",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full antialiased overflow-hidden">
        {children}
      </body>
    </html>
  );
}
