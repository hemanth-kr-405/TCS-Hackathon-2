/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Poppins', 'sans-serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          blue: '#A7C7E7',
          'blue-soft': '#DCECF8',
          mint: '#B8E0D2',
          'mint-soft': '#E4F5EF',
          bg: '#F5F5F5',
          surface: '#FFFFFF',
          heading: '#18324A',
          text: '#18324A',
          muted: '#64748B',
          border: '#E2E8F0',
          negative: '#EF4444',
          'negative-soft': '#FEF2F2',
          warning: '#F59E0B',
          'warning-soft': '#FFFBEB',
          success: '#10B981',
          'success-soft': '#ECFDF5',
        }
      }
    },
  },
  plugins: [],
}
