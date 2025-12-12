# Blender Asset Exporter

Custom tool for exporting Blender assets to Unity

## Prerequisites

1. Make sure `blender` and `node` are installed and available in your terminal.

   ```bash
   blender --version
   node --version
   npm --version
   ```

2. Install yarn package manager if you don't have it already:

   ```bash
   npm install -g yarn
   ```

3. Install dependencies

   ```bash
    yarn install
    ```

## Building the Extension

```bash
yarn build
```

## Development

To quickly test changes, you can watch the source files and rebuild on changes:

```bash
yarn watch
```

Make sure to re-install the extension in Blender after building.
