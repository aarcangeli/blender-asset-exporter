# Blender Asset Exporter

Custom tool for exporting Blender assets to Unity

## How to build

1. Make sure `blender` is in your `PATH`

   ```bash
   blender --version
   ```

2. Install Node.js and yarn

   ```bash
   npm install -g yarn
   ```

3. Install dependencies

   ```bash
    yarn install
    ```

4. Build the extension

    ```bash
    yarn build
    ```

## Development

To quickly test changes, you can watch the source files and rebuild on changes:

```bash
yarn watch
```

Make sure to re-install the extension in Blender after building.
