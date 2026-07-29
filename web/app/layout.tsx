import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ask Your Tally",
  description: "Chat with your live TallyPrime books",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
