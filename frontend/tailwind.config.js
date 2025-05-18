/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Main colors based on aespa Whiplash MV style
        'neon-blue': '#00f0ff',
        'neon-pink': '#ff00e5',
        'deep-space': '#10101a',
        'pure-black': '#000000',
        'neon-green': '#39ff14',
        'neon-purple': '#bc13fe',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
        display: ['var(--font-orbitron)', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'cyber-gradient': 'linear-gradient(to right, var(--tw-gradient-stops))',
      },
      animation: {
        'glow-pulse': 'glow-pulse 2s infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { 
            textShadow: '0 0 8px rgba(0, 240, 255, 0.7), 0 0 12px rgba(0, 240, 255, 0.5)' 
          },
          '50%': { 
            textShadow: '0 0 16px rgba(255, 0, 229, 0.7), 0 0 20px rgba(255, 0, 229, 0.5)' 
          },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      backdropFilter: {
        'glass': 'blur(16px) saturate(180%)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}; 