/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        dark: {
          bg: "#060d18",
          bg2: "#081020",
          surface: "#0b1426",
          surface2: "#111d33",
          surface3: "#182640",
          border: "#1c2d4a",
          borderLight: "#264060",
          text: "#f1f5f9",
          textSecondary: "#cbd5e1",
          muted: "#64748b",
          accent: "#d4a574",
          accentHover: "#e8c4a0",
        },
        light: {
          bg: "#FFFFFF",
          bg2: "#FAFBFD",
          surface: "#FFFFFF",
          surface2: "#F0F4F8",
          border: "#D8E0EC",
          borderLight: "#C4CFDE",
          text: "#0c1829",
          textSecondary: "#1e3050",
          muted: "#546580",
          accent: "#b87a4e",
          accentHover: "#9a6540",
        },
      },
      fontFamily: {
        sans: [
          "DM Sans",
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        heading: [
          "DM Serif Display",
          "Georgia",
          "serif",
        ],
      },
      boxShadow: {
        "neon-purple": "0 0 30px -5px rgba(6, 182, 212, 0.45)",
        "neon-multi": "0 0 35px -5px rgba(56, 189, 248, 0.35), 0 0 35px -5px rgba(6, 182, 212, 0.35)",
        "glass-dark": "0 8px 32px 0 rgba(0, 0, 0, 0.8)",
        "glass-light": "0 8px 30px rgba(0, 0, 0, 0.08)",
      },
      animation: {
        "float-orb": "floatOrb 6s ease-in-out infinite",
        "pulse-glow": "pulseGlow 4s ease-in-out infinite",
        "gradient-x": "gradientX 8s ease infinite",
        "spin-slow": "spin 20s linear infinite",
      },
      keyframes: {
        floatOrb: {
          "0%, 100%": { transform: "translateY(0px) scale(1)" },
          "50%": { transform: "translateY(-10px) scale(1.04)" },
        },
        pulseGlow: {
          "0%, 100%": { opacity: "0.55", filter: "blur(20px)" },
          "50%": { opacity: "0.9", filter: "blur(30px)" },
        },
        gradientX: {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
      },
    },
  },
  plugins: [],
};
