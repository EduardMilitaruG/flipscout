import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Archive Scout — Control Panel",
  description: "Dashboard for the Archive Scout deal-hunting bot",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} antialiased`}>
        {children}
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: "#0d0d14",
              color: "#fff",
              border: "1px solid rgba(255,255,255,0.07)",
              borderRadius: "12px",
              fontSize: "13px",
            },
            success: {
              iconTheme: { primary: "#9333ea", secondary: "#fff" },
            },
          }}
        />
      </body>
    </html>
  );
}
