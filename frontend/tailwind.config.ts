import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./layouts/**/*.{ts,tsx}", "./hooks/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#141614",
        graphite: "#2f342f",
        mist: "#f5f7f2",
        paper: "#fffdf7",
        moss: "#49664d",
        sage: "#dfe9dc",
        copper: "#b86b3e",
        ocean: "#2f6575"
      },
      boxShadow: {
        panel: "0 18px 45px rgba(37, 48, 38, 0.12)"
      }
    }
  },
  plugins: [require("@tailwindcss/forms")]
};

export default config;

