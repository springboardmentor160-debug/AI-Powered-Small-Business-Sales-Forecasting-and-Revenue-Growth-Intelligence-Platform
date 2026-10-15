import defaultTheme from "tailwindcss/defaultTheme";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: [
          '"Plus Jakarta Sans Variable"',
          '"Plus Jakarta Sans"',
          ...defaultTheme.fontFamily.sans,
        ],
      },
      boxShadow: {
        card: "0 1px 2px rgb(15 23 42 / 0.04), 0 1px 3px rgb(15 23 42 / 0.06)",
        pop: "0 12px 32px -12px rgb(15 23 42 / 0.28)",
      },
    },
  },
  plugins: [],
};
