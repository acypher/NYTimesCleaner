#!/usr/bin/env bash
# Archive and export the iOS Safari host app (NewsMinusHostIOS) for App
# Store Connect. Prints the exported .ipa path on the last line (mirrors
# build-safari-mac.sh).
#
# Signing is fully headless: the iOS Release configs use Manual signing with an
# "Apple Distribution" identity + explicit App Store provisioning profiles. The
# identity lives in a dedicated keychain (created here, self-passworded) so we
# never prompt the login keychain. The .p12 is shared with Nunus (same Apple
# team): if scripts/keys/ios-signing/dist.p12 is missing we reuse
# ../nunus/NunusCursor/scripts/keys/ios-signing/dist.p12. Missing provisioning
# profiles are created via ./scripts/ensure-ios-signing.sh (ASC API). If no
# .p12 can be found at all, we fall back to Automatic signing via
# -allowProvisioningUpdates (needs a registered device on the account).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=lib/load-release-env.sh
source "$SCRIPT_DIR/lib/load-release-env.sh"

SAFARI_DIR="$ROOT/safari"
PROJECT="$SAFARI_DIR/NewsMinusSafari.xcodeproj"
SCHEME="NewsMinusHostIOS"
BUILD_DIR="$SAFARI_DIR/build"
ARCHIVE_PATH="$BUILD_DIR/NewsMinusHostIOS.xcarchive"
EXPORT_DIR="$BUILD_DIR/export-ios"
EXPORT_PLIST="$BUILD_DIR/ExportOptions-ios.plist"

# --- signing configuration (overridable via env / release.env) ---
IOS_SIGN_IDENTITY="${IOS_SIGN_IDENTITY:-Apple Distribution}"
IOS_HOST_PROFILE="${IOS_HOST_PROFILE:-NewsMinus iOS App Store}"
IOS_EXT_PROFILE="${IOS_EXT_PROFILE:-NewsMinus iOS Extension App Store}"
IOS_HOST_BUNDLE="${IOS_BUNDLE_ID:-com.nunus.NYTimesCleanerHost.ios}"
IOS_EXT_BUNDLE="${IOS_EXT_BUNDLE_ID:-${IOS_HOST_BUNDLE}.extension}"
IOS_SIGN_P12="${IOS_SIGN_P12:-$ROOT/scripts/keys/ios-signing/dist.p12}"
NUNUS_P12="$ROOT/../nunus/NunusCursor/scripts/keys/ios-signing/dist.p12"
IOS_SIGN_KEYCHAIN="${IOS_SIGN_KEYCHAIN:-$BUILD_DIR/newsminus-ios-signing.keychain-db}"
IOS_SIGN_KEYCHAIN_PW="${IOS_SIGN_KEYCHAIN_PW:-newsminus-temp-signing}"

# Reuse the Nunus distribution .p12 (same Apple team) when no local copy exists.
if [[ ! -f "$IOS_SIGN_P12" && -f "$NUNUS_P12" ]]; then
  echo "note: using shared Nunus signing identity: $NUNUS_P12"
  IOS_SIGN_P12="$NUNUS_P12"
fi
if [[ -z "${IOS_SIGN_P12_PW:-}" && -f "${IOS_SIGN_P12}.password" ]]; then
  IOS_SIGN_P12_PW="$(tr -d '\n' <"${IOS_SIGN_P12}.password")"
fi
IOS_SIGN_P12_PW="${IOS_SIGN_P12_PW:-nunus}"

if [[ -z "${APPLE_TEAM_ID:-}" ]]; then
  echo "error: APPLE_TEAM_ID is required (set in scripts/release.env or shared Nunus release.env)" >&2
  exit 1
fi

# Keep the generated project (version, signing settings) in sync.
python3 "$SAFARI_DIR/scripts/gen_pbxproj.py"

# iOS app icons are required for App Store upload; generate if missing.
if [[ ! -f "$SAFARI_DIR/Host/Assets.xcassets/AppIcon.appiconset/ios-marketing-1024.png" ]]; then
  echo "iOS app icons missing; regenerating asset catalog..."
  sh "$SAFARI_DIR/scripts/generate-mac-app-icons.sh"
fi

mkdir -p "$BUILD_DIR"

# Ensure the distribution identity is present in a dedicated, self-passworded
# keychain and available to codesign without any GUI prompt. Returns 0 if manual
# signing is ready, 1 if the .p12 asset is missing (caller falls back to auto).
setup_signing_keychain() {
  [[ -f "$IOS_SIGN_P12" ]] || return 1
  local login="$HOME/Library/Keychains/login.keychain-db"
  if [[ ! -f "$IOS_SIGN_KEYCHAIN" ]]; then
    security create-keychain -p "$IOS_SIGN_KEYCHAIN_PW" "$IOS_SIGN_KEYCHAIN"
  fi
  security set-keychain-settings "$IOS_SIGN_KEYCHAIN"          # no auto-lock timeout
  security unlock-keychain -p "$IOS_SIGN_KEYCHAIN_PW" "$IOS_SIGN_KEYCHAIN"
  if ! security find-identity -v -p codesigning "$IOS_SIGN_KEYCHAIN" | grep -q "$IOS_SIGN_IDENTITY"; then
    security import "$IOS_SIGN_P12" -k "$IOS_SIGN_KEYCHAIN" -P "$IOS_SIGN_P12_PW" \
      -T /usr/bin/codesign -T /usr/bin/xcodebuild -T /usr/bin/productbuild
    security set-key-partition-list -S apple-tool:,apple:,codesign: \
      -s -k "$IOS_SIGN_KEYCHAIN_PW" "$IOS_SIGN_KEYCHAIN" >/dev/null
  fi
  # keep the signing keychain in the search list (login stays for the WWDR intermediate)
  if ! security list-keychains -d user | grep -q "$(basename "$IOS_SIGN_KEYCHAIN")"; then
    security list-keychains -d user -s "$IOS_SIGN_KEYCHAIN" "$login"
  fi
  return 0
}

# Ensure the App Store provisioning profiles exist locally; create via ASC API
# if missing (idempotent, best-effort).
ensure_profiles() {
  local host_file ext_file
  host_file="$ROOT/scripts/keys/ios-signing/${IOS_HOST_PROFILE// /-}.mobileprovision"
  ext_file="$ROOT/scripts/keys/ios-signing/${IOS_EXT_PROFILE// /-}.mobileprovision"
  if [[ -f "$host_file" && -f "$ext_file" ]]; then
    mkdir -p "$HOME/Library/MobileDevice/Provisioning Profiles"
    cp "$host_file" "$ext_file" "$HOME/Library/MobileDevice/Provisioning Profiles/"
    return 0
  fi
  echo "Provisioning profiles missing; creating via App Store Connect API..."
  if ! "$SCRIPT_DIR/ensure-ios-signing.sh"; then
    echo "WARNING: could not provision profiles automatically; manual signing may fail." >&2
    return 1
  fi
}

SIGN_MODE="manual"
if setup_signing_keychain; then
  ensure_profiles || true
else
  echo "note: signing .p12 not found ($IOS_SIGN_P12); falling back to Automatic signing." >&2
  SIGN_MODE="auto"
fi

if [[ "$SIGN_MODE" == "manual" ]]; then
  cat >"$EXPORT_PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>method</key>
	<string>app-store-connect</string>
	<key>destination</key>
	<string>export</string>
	<key>teamID</key>
	<string>${APPLE_TEAM_ID}</string>
	<key>uploadSymbols</key>
	<true/>
	<key>signingStyle</key>
	<string>manual</string>
	<key>signingCertificate</key>
	<string>${IOS_SIGN_IDENTITY}</string>
	<key>provisioningProfiles</key>
	<dict>
		<key>${IOS_HOST_BUNDLE}</key>
		<string>${IOS_HOST_PROFILE}</string>
		<key>${IOS_EXT_BUNDLE}</key>
		<string>${IOS_EXT_PROFILE}</string>
	</dict>
</dict>
</plist>
EOF

  echo "Archiving $SCHEME (Release, manual signing) for iOS..."
  xcodebuild \
    -project "$PROJECT" \
    -scheme "$SCHEME" \
    -configuration Release \
    -sdk iphoneos \
    -destination "generic/platform=iOS" \
    -archivePath "$ARCHIVE_PATH" \
    archive \
    OTHER_CODE_SIGN_FLAGS="--keychain $IOS_SIGN_KEYCHAIN"

  echo "Exporting App Store package (manual)..."
  rm -rf "$EXPORT_DIR"
  xcodebuild \
    -exportArchive \
    -archivePath "$ARCHIVE_PATH" \
    -exportPath "$EXPORT_DIR" \
    -exportOptionsPlist "$EXPORT_PLIST"
else
  cat >"$EXPORT_PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>method</key>
	<string>app-store-connect</string>
	<key>destination</key>
	<string>export</string>
	<key>teamID</key>
	<string>${APPLE_TEAM_ID}</string>
	<key>uploadSymbols</key>
	<true/>
</dict>
</plist>
EOF

  echo "Archiving $SCHEME (Release, automatic signing) for iOS..."
  xcodebuild \
    -project "$PROJECT" \
    -scheme "$SCHEME" \
    -configuration Release \
    -sdk iphoneos \
    -destination "generic/platform=iOS" \
    -archivePath "$ARCHIVE_PATH" \
    archive \
    DEVELOPMENT_TEAM="$APPLE_TEAM_ID" \
    CODE_SIGN_STYLE=Automatic \
    -allowProvisioningUpdates

  echo "Exporting App Store package (automatic)..."
  rm -rf "$EXPORT_DIR"
  xcodebuild \
    -exportArchive \
    -archivePath "$ARCHIVE_PATH" \
    -exportPath "$EXPORT_DIR" \
    -exportOptionsPlist "$EXPORT_PLIST" \
    -allowProvisioningUpdates
fi

ipa="$(find "$EXPORT_DIR" -maxdepth 1 -name '*.ipa' | head -1)"
if [[ -z "$ipa" ]]; then
  echo "error: no .ipa found under $EXPORT_DIR" >&2
  exit 1
fi

echo "Exported: $ipa"
echo "$ipa"
