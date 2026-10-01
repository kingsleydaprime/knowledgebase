// eslint.config.js — verified with ESLint 9.39, eslint-plugin-import 2.32
import { readdirSync } from "node:fs";
import importPlugin from "eslint-plugin-import";
import tseslint from "typescript-eslint";

// One zone per (feature, other feature) pair: a feature may import another
// feature's index.ts, and nothing else from it.
const features = readdirSync("./src/features");
const featureZones = features.flatMap((feature) =>
  features
    .filter((other) => other !== feature)
    .map((other) => ({
      target: `./src/features/${feature}`,
      from: `./src/features/${other}`,
      except: ["./index.ts"],
      message: `Import ${other} through features/${other}/index.ts, not its internals.`,
    })),
);

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
          ...featureZones,
          { target: "./src/shared", from: "./src/features", message: "shared/ must not depend on a feature." },
        ],
      },
    ],
  },
});
