/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "./preview.html"
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: "#2a14b4",
        "primary-container": "#4338ca",
        "on-primary": "#ffffff",
        "on-primary-container": "#c1beff",
        "primary-fixed": "#e3dfff",
        "primary-fixed-dim": "#c3c0ff",
        "on-primary-fixed": "#100069",
        "on-primary-fixed-variant": "#372abf",
        "inverse-primary": "#c3c0ff",

        secondary: "#006c4a",
        "secondary-container": "#82f5c1",
        "on-secondary": "#ffffff",
        "on-secondary-container": "#00714e",
        "secondary-fixed": "#85f8c4",
        "secondary-fixed-dim": "#68dba9",
        "on-secondary-fixed": "#002114",
        "on-secondary-fixed-variant": "#005137",

        tertiary: "#5c2f00",
        "tertiary-container": "#7d4200",
        "on-tertiary": "#ffffff",
        "on-tertiary-container": "#ffb477",
        "tertiary-fixed": "#ffdcc3",
        "tertiary-fixed-dim": "#ffb77d",
        "on-tertiary-fixed": "#2f1500",
        "on-tertiary-fixed-variant": "#6e3900",

        error: "#ba1a1a",
        "error-container": "#ffdad6",
        "on-error": "#ffffff",
        "on-error-container": "#93000a",

        surface: "#f8f9ff",
        background: "#f8f9ff",
        "on-surface": "#0d1c2e",
        "on-background": "#0d1c2e",
        "on-surface-variant": "#464554",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#eff4ff",
        "surface-container": "#e6eeff",
        "surface-container-high": "#dce9ff",
        "surface-container-highest": "#d5e3fc",
        "surface-bright": "#f8f9ff",
        "surface-dim": "#ccdbf3",
        "surface-variant": "#d5e3fc",
        "surface-tint": "#5148d7",
        "inverse-surface": "#233144",
        "inverse-on-surface": "#eaf1ff",
        outline: "#777586",
        "outline-variant": "#c7c4d7"
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        md: "0.5rem",
        lg: "0.5rem",
        xl: "0.75rem",
        "2xl": "1rem",
        full: "9999px"
      },
      spacing: {
        "space-xs": "0.25rem",
        "space-sm": "0.5rem",
        "space-md": "1rem",
        "space-lg": "1.5rem",
        "space-xl": "2.5rem",
        gutter: "1.5rem",
        "gutter-mobile": "1rem",
        margin: "2rem",
        "margin-mobile": "1rem"
      },
      fontFamily: {
        "display-lg": ["'Plus Jakarta Sans'", "sans-serif"],
        "headline-xl": ["'Plus Jakarta Sans'", "sans-serif"],
        "headline-lg": ["'Plus Jakarta Sans'", "sans-serif"],
        "headline-md": ["'Plus Jakarta Sans'", "sans-serif"],
        "title-sm": ["'Plus Jakarta Sans'", "sans-serif"],
        "body-lg": ["'Inter'", "sans-serif"],
        "body-md": ["'Inter'", "sans-serif"],
        "body-sm": ["'Inter'", "sans-serif"],
        "label-md": ["'Inter'", "sans-serif"],
        "label-sm": ["'Inter'", "sans-serif"],
        "code-sm": ["'Inter'", "monospace"]
      }
    }
  },
  plugins: []
};
