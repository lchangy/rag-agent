/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#f9fafb",
        ink: "#172033",
        muted: "#5e6b7f",
        line: "#d9e1ea",
        primary: "#3b82f6",
        success: "#166534",
        successBg: "#ecfdf3",
        danger: "#b42318",
        dangerBg: "#fef3f2",
      },
      boxShadow: {
        shell: "0 24px 60px -34px rgba(15, 23, 42, 0.28)",
      },
      fontFamily: {
        display: ['"Iowan Old Style"', '"Palatino Linotype"', '"Book Antiqua"', "serif"],
        body: ['"Avenir Next"', '"Segoe UI"', "sans-serif"],
      },
    },
  },
  plugins: [],
};
