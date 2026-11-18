/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        't-bg': '#080808',
        't-surface': '#0e0e0e',
        't-panel': '#141414',
        't-border': '#1c1c1c',
        't-line': '#2a2a2a',
        't-text': '#e5e5e5',
        't-white': '#ffffff',
        't-muted': '#737373',
        't-dim': '#404040',
        't-sub': '#a3a3a3',
        't-orange': '#ff5500',      // Signature FlipScout neon orange
        't-amber': '#ff5500',       // Terminal orange accent
        't-green': '#10b981',
        't-blue': '#00c3ff',        // Cyan-blue resale and clock accent
        't-cyan': '#00c3ff',
        't-red': '#ef4444',
      },
      fontFamily: {
        display: ['"Barlow Condensed"', 'Impact', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
