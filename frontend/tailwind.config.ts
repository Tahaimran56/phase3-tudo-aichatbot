import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
      },
      // Mobile-first breakpoints (Tailwind default is mobile-first)
      screens: {
        'xs': '320px',  // Minimum mobile
        'sm': '640px',  // Small devices
        'md': '768px',  // Tablets
        'lg': '1024px', // Desktops
        'xl': '1280px', // Large desktops
        '2xl': '1536px', // Extra large
      },
      // Minimum touch target size
      minHeight: {
        'touch': '44px',
      },
      minWidth: {
        'touch': '44px',
      },
    },
  },
  plugins: [],
};

export default config;
