# Safari (Xcode)

The Chrome/Firefox web extension files live at the **repo root** (`manifest.json`, `background.js`, `sites/`, `icons/`). The Safari **NewsMinusExtension** `.appex` must ship the same files under **`Contents/Resources`**. The Run Script phase invokes [`scripts/copy-web-extension-resources.sh`](scripts/copy-web-extension-resources.sh) on each build.

## Open and build

1. Open **`safari/NewsMinusSafari.xcodeproj`** in Xcode (macOS **14+** for the extension Swift API used in `SafariWebExtensionHandler`).
2. Select the **NewsMinusHost** scheme, then **Product → Build**.
3. Run **NewsMinusHost.app** once if needed, then enable the extension: **Safari → Settings → Extensions** → turn on **NewsMinus** and allow access for **nytimes.com** (and subdomains if Safari prompts).

If the Xcode project file is missing or you changed target structure, regenerate it:

```sh
python3 safari/scripts/gen_pbxproj.py
```

## Run Script phase (already wired in generated project)

On the **NewsMinusExtension** target, **Build Phases** includes **Copy web extension resources** running before **Copy Bundle Resources**, with **Enable User Script Sandboxing** set to **No** so `cp`/`rsync` into the `.appex` is allowed.

If you move the `.xcodeproj` outside this repo, set the web root explicitly in that phase:

```sh
export NYTNA_WEBROOT="/absolute/path/to/NewsMinus"
/bin/sh "${NYTNA_WEBROOT}/safari/scripts/copy-web-extension-resources.sh"
```

## Icons (`images/STOP.png`)

From the repo root, with **`images/STOP.png`** present:

```sh
sh scripts/regenerate-icons.sh
```

This writes **`icons/icon{16,32,48,96,128}.png`** for the web extension manifest and fills **`safari/Host/Assets.xcassets/AppIcon.appiconset/`** plus **`safari/Host/AppIcon.icns`** for the Mac host. To regenerate only the Mac host assets:

```sh
sh safari/scripts/generate-mac-app-icons.sh
```

## Troubleshooting

The same issues are covered in the sibling **NunusCursor** project under `NunusCursor/safari/README.md`: **User Script Sandboxing**, **`unsealed contents` / codesign** (web assets must live only under `Contents/Resources/` — this copy script does that), and **App Store `manifest.json` description** length (Apple often caps at **112 characters**; keep the root `description` short).
