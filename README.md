# Blender Asset Exporter

Custom tool for exporting Blender assets to Unity

## Build from Source

1. Make sure `blender` is installed and accessible from the command line.
   You can verify this by running:

   ```bash
   blender --version
   ```

2. Run the build command with Blender.

   ```bash
   blender --command extension build --source-dir=source
   ```

## Development

To quickly test changes, you can watch the source files and rebuild on changes:

```bash
yarn install
yarn watch
```

Make sure to re-install the extension in Blender after building.
