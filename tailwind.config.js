/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",  // root directory
    "./**/templates/**/*.html"  // inside apps

  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

