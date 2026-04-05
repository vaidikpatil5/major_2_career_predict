import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { AssessmentProvider } from "@/context/AssessmentContext";
import "./globals.css";

const geistSans = Geist({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Career Navigator",
  description:
    "Discover career paths aligned with your personality and strengths.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.className} min-h-screen antialiased text-slate-900`}
      >
        <AssessmentProvider>{children}</AssessmentProvider>
      </body>
    </html>
  );
}
