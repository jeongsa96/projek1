import withMT from "@material-tailwind/html/utils/withMT";
 
/** @type {import('tailwindcss').Config} */
module.exports = withMT({
  safelist: [
        { pattern: /^icon-\[[a-z]{2,4}--[a-z0-9-]+\]$/ }, // Example pattern for dynamic icon classes
      ],
  content: [
    './templates/**/*.html'
  ],
  theme: {
    extend: {},
  },
  plugins: [],
});