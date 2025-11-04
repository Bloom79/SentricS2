/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
    './src/**/*.{html,js,ts,jsx,tsx}',
  ],
  safelist: [
    {
      pattern: /(grid-cols|sm:grid-cols|md:grid-cols|lg:grid-cols|xl:grid-cols)-(1|2|3|4)/,
    },
    {
      pattern: /(gap|sm:gap|md:gap|lg:gap)-(3|4|6)/,
    },
    {
      pattern: /(p|px|py|sm:p|sm:px|lg:p|lg:px)-(4|6|8)/,
    },
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        // Status colors
        status: {
          success: 'hsl(var(--status-success))',
          'success-bg': 'hsl(var(--status-success-bg))',
          info: 'hsl(var(--status-info))',
          'info-bg': 'hsl(var(--status-info-bg))',
          warning: 'hsl(var(--status-warning))',
          'warning-bg': 'hsl(var(--status-warning-bg))',
          error: 'hsl(var(--status-error))',
          'error-bg': 'hsl(var(--status-error-bg))',
        },
        // Category colors
        category: {
          purple: 'hsl(var(--category-purple))',
          'purple-bg': 'hsl(var(--category-purple-bg))',
          blue: 'hsl(var(--category-blue))',
          'blue-bg': 'hsl(var(--category-blue-bg))',
          teal: 'hsl(var(--category-teal))',
          'teal-bg': 'hsl(var(--category-teal-bg))',
          pink: 'hsl(var(--category-pink))',
          'pink-bg': 'hsl(var(--category-pink-bg))',
          orange: 'hsl(var(--category-orange))',
          'orange-bg': 'hsl(var(--category-orange-bg))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [],
};

