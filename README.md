# Blender Asset Exporter

Custom tool for exporting Blender assets to Unity and Unreal Engine.

The project is not ready for production use.

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

To quickly test changes, add the "source" directory as custom extension repository in Blender preferences.

Then enable the extension as normal.

To reload the extension after making changes, use the "Reload Scripts" button.

## Rules

- Always use relative imports within the source directory. ([doc](https://docs.blender.org/manual/en/latest/advanced/extensions/addons.html#relative-imports))
