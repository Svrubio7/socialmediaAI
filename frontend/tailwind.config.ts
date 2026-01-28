import type { Config } from 'tailwindcss'

export default {
  content: [
    './components/**/*.{js,vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './composables/**/*.{js,ts}',
    './plugins/**/*.{js,ts}',
    './utils/**/*.{js,ts}',
    './app.vue',
    './error.vue',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif'],
        mono: ['"Space Mono"', 'ui-monospace', 'SFMono-Regular', '"SF Mono"', 'Menlo', 'Monaco', 'Consolas', '"Liberation Mono"', '"Courier New"', 'monospace'],
      },
      colors: {
        // Color palette based on user preference - darker variants
        primary: {
          50: '#f4f7f4',
          100: '#e6ebe6',
          200: '#cdd8cd',
          300: '#a8bda8',
          400: '#7d9a7d',
          500: '#697565', // Base sage green
          600: '#556152',
          700: '#454f44',
          800: '#3a413a',
          900: '#313731',
          950: '#1a1d1a',
        },
        accent: {
          50: '#fcfaf6',
          100: '#f7f3ea',
          200: '#ECDFCC', // Cream accent
          300: '#e0cdb0',
          400: '#d4b78e',
          500: '#c9a06f',
          600: '#b8885a',
          700: '#9a6d4b',
          800: '#7d5941',
          900: '#664a38',
          950: '#36261c',
        },
        // Deep dark theme - even darker
        surface: {
          50: '#f5f5f5',
          100: '#e8e8e8',
          200: '#d4d4d4',
          300: '#b0b0b0',
          400: '#888888',
          500: '#697565',
          600: '#3C3D37',
          700: '#252622',
          800: '#1a1b18',
          900: '#121310',
          950: '#0a0a09', // Near black
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'fade-in-up': 'fadeInUp 0.6s ease-out',
        'fade-in-down': 'fadeInDown 0.5s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'slide-in-left': 'slideInLeft 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'typewriter': 'typewriter 2s steps(40) forwards',
        'blink': 'blink 1s step-end infinite',
        'text-reveal': 'textReveal 0.8s ease-out forwards',
        'word-reveal': 'wordReveal 0.5s ease-out forwards',
        'letter-bounce': 'letterBounce 0.3s ease-out forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeInDown: {
          '0%': { opacity: '0', transform: 'translateY(-16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { opacity: '0.5' },
          '100%': { opacity: '1' },
        },
        typewriter: {
          'from': { width: '0' },
          'to': { width: '100%' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
        textReveal: {
          '0%': { 
            opacity: '0',
            transform: 'translateY(20px)',
            filter: 'blur(10px)',
          },
          '100%': { 
            opacity: '1',
            transform: 'translateY(0)',
            filter: 'blur(0)',
          },
        },
        wordReveal: {
          '0%': { 
            opacity: '0',
            transform: 'translateY(100%)',
          },
          '100%': { 
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        letterBounce: {
          '0%': { 
            opacity: '0',
            transform: 'translateY(-20px) scale(0.8)',
          },
          '60%': { 
            transform: 'translateY(5px) scale(1.1)',
          },
          '100%': { 
            opacity: '1',
            transform: 'translateY(0) scale(1)',
          },
        },
      },
      transitionTimingFunction: {
        'out-expo': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'in-expo': 'cubic-bezier(0.7, 0, 0.84, 0)',
      },
      boxShadow: {
        'glow-sm': '0 0 15px -3px rgba(105, 117, 101, 0.3)',
        'glow-md': '0 0 25px -5px rgba(105, 117, 101, 0.4)',
        'glow-lg': '0 0 35px -5px rgba(105, 117, 101, 0.5)',
        'glow-accent': '0 0 25px -5px rgba(236, 223, 204, 0.3)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'shimmer': 'linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent)',
      },
    },
  },
  plugins: [],
} satisfies Config
