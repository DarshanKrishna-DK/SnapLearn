/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        pixel: ['"Press Start 2P"', 'cursive'],
        body: ['"Space Grotesk"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        maroon: {
          50: '#fdf2f4',
          100: '#fce7ea',
          200: '#f9d0d9',
          300: '#e8a0b0',
          400: '#c75a72',
          500: '#7a2040',
          600: '#5c1830',
          700: '#3d0f1d',
          800: '#2a0a14',
          900: '#1a050c',
          950: '#120307',
        },
        cream: {
          50: '#fffef9',
          100: '#faf6ee',
          200: '#f0e8d8',
          300: '#e4d4bc',
          400: '#d4c4a4',
          500: '#c4b08c',
        },
        gold: { 400: '#c9a24a', 500: '#b8862f' },
      },
      minHeight: {
        screen: '100dvh',
      },
      boxShadow: {
        professional: '0 4px 20px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1)',
        'maroon-glow': '0 0 20px rgba(139, 21, 56, 0.3), 0 0 40px rgba(139, 21, 56, 0.1)',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0) rotateX(0deg)' },
          '50%': { transform: 'translateY(-6px) rotateX(2deg)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(201, 162, 74, 0.2)' },
          '50%': { boxShadow: '0 0 24px 2px rgba(201, 162, 74, 0.35)' },
        },
        meshPulse: {
          '0%, 100%': { opacity: '0.02' },
          '50%': { opacity: '0.05' },
        },
        professionalFadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        float: 'float 5s ease-in-out infinite',
        'pulse-glow': 'pulseGlow 3.5s ease-in-out infinite',
        'mesh-pulse': 'meshPulse 3s ease-in-out infinite',
        'professional-fade-in': 'professionalFadeIn 0.6s ease-out',
      },
      backgroundImage: {
        'mesh-gradient': 'linear-gradient(135deg, rgba(139, 21, 56, 0.1), rgba(245, 241, 232, 0.05))',
        'professional-gradient':
          'linear-gradient(110deg, rgba(139, 21, 56, 0.02) 0%, rgba(245, 241, 232, 0.01) 40%, rgba(0,0,0,0.1) 100%)',
      },
    },
  },
  plugins: [],
};
