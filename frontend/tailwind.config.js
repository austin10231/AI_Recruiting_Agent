/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1f2b2a",
        fog: "#eef1eb",
        moss: "#5f7d64",
        clay: "#bf8d62",
        paper: "#f6f3ea"
      },
      boxShadow: {
        card: "0 20px 45px rgba(31, 43, 42, 0.12)",
        soft: "0 10px 30px rgba(31, 43, 42, 0.08)"
      },
      fontFamily: {
        title: ["Fraunces", "Georgia", "serif"],
        body: ["Space Grotesk", "system-ui", "sans-serif"]
      },
      keyframes: {
        reveal: {
          "0%": { opacity: "0", transform: "translateY(14px)" },
          "100%": { opacity: "1", transform: "translateY(0)" }
        }
      },
      animation: {
        reveal: "reveal 500ms ease forwards"
      }
    }
  },
  plugins: []
};
