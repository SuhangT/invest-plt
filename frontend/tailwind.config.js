/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0a0e1a',
          surface: '#141824',
          border: '#1f2937',
          text: '#e5e7eb',
          muted: '#9ca3af',
        },
        trade: {
          green: '#22c55e',
          red: '#ef4444',
          'green-light': '#e0ffff',
          'red-light': '#ffe4e1',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
