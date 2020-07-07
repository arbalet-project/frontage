module.exports = {
  root: true,
  env: {
    node: true
  },
  parserOptions: {
    project: "./tsconfig.json",
    parser: "@typescript-eslint/parser",
    ecmaVersion: 2019,
    sourceType: "module"
  },
  plugins: ["@typescript-eslint"],
  extends: [
    "airbnb-base",
    "plugin:import/errors",
    "plugin:import/warnings",
    "plugin:import/typescript",
    "plugin:@typescript-eslint/eslint-recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking",
    "plugin:security/recommended",
  ],
  rules: {
    "@typescript-eslint/member-delimiter-style": ["error", { "multiline": { "delimiter": "comma", "requireLast": true }, "singleline": { "delimiter": "comma", "requireLast": false } }],
    "import/extensions": ["error", "never"]
  }
};
