# Figma Token Exports

Store raw token exports from Figma/Tokens Studio in this directory.

## Accepted Top-Level Groups

- `color.*`
- `spacing.*`
- `typography.*`
- `radius.*`
- `shadow.*`

Additional groups are allowed but treated as non-blocking warnings during import.

## Supported Input Shapes

- Tokens Studio style grouped tokens (`color`, `spacing`, `typography`, `radius`, `shadow`)
- FigmaDMS `theme-config.json` shape (`colors[]` plus `uiTokens`)

## Naming Guidance

- Use lower-case, dot-safe paths.
- Prefer semantic names over raw intent (`color.text.primary`, not `color.blue.500`).
- Keep aliases explicit in the export source when possible.
