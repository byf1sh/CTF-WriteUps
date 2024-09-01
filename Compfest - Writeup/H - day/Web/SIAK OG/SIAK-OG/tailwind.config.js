/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./views/*.ejs'],
  theme: {
    extend: {},
    colors: {
      primary: '#4256A0',
      secondary: '#5D71BC',
      yellow: '#fbbf24',
      black: '#000000',
      white: '#ffffff',
      lightgray: '#D5D5D5',
      lightergray: '#ECECEC',
      gray: '#888888',
      shadow: '#1f2937',
      nav: '#444444',
      hover: '#777777',
      lightred: '#FFE4E4',
    }
  },
  plugins: [
  {
  tailwindcss: {},
  autoprefixer: {},
  },
  ],
  };
