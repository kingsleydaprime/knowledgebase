// eslint.config.js — verified with ESLint 9.39, eslint-plugin-import 2.32
import { readdirSync } from "node:fs";
import importPlugin from "eslint-plugin-import";
import tseslint from "typescript-eslint";

const features = readdirSync("./src/features");

export default tseslint.config({
  files: ["src/**/*.{ts,tsx}"],
  languageOptions: { parser: tseslint.parser },
  plugins: { import: importPlugin },
  settings: { "import/resolver": { typescript: true } },
  rules: {
    "import/no-restricted-paths": [
      "error",
      {
        zones: [
          // 1. Features never import each other. Compose them in app/ instead.
          ...features.map((feature) => ({
            target: `./src/features/${feature}`,
            from: "./src/features",
            except: [`./${feature}`],
          })),
          // 2. One direction only: shared → features → app.
          { target: "./src/features", from: "./src/app" },
          { target: "./src/shared", from: ["./src/features", "./src/app"] },
        ],
      },
    ],
  },
});
