import { extendTheme } from "@chakra-ui/react";

const theme = extendTheme({
  colors: {
    primary: {
      500: "#5B2A86",
    },
    secondary: {
      500: "#F4B400",
    },
    success: {
      500: "#4CAF50",
    },
    accent: {
      500: "#6A1B9A",
    },
    background: {
      100: "#FAFAFC",
    },
    text: {
      900: "#333333",
      700: "#555555",
    },
  },
  styles: {
    global: {
      body: {
        bg: "#FAFAFC",
        color: "#333333",
      },
    },
  },
  fonts: {
    heading: `'Poppins', sans-serif`,
    body: `'Poppins', sans-serif`,
  },
});

export default theme;