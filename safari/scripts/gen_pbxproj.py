#!/usr/bin/env python3
"""Emit safari/NewsMinusSafari.xcodeproj/project.pbxproj (macOS + iOS Safari Web Extension).

Targets:
  NewsMinusHost / NewsMinusExtension          — macOS host app + .appex
  NewsMinusHostIOS / NewsMinusExtensioniOS    — iOS host app + .appex

iOS Release configs use Manual signing (App Store profiles) so archives are
headless; Debug stays Automatic for the simulator. Profile names / identity /
team are overridable via env (see scripts/release.env.example).
"""
from __future__ import annotations

import hashlib
import json
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
PROJ_DIR = os.path.join(ROOT, "NewsMinusSafari.xcodeproj")
OUT = os.path.join(PROJ_DIR, "project.pbxproj")
MANIFEST = os.path.normpath(os.path.join(ROOT, "..", "manifest.json"))


def nid(seed: str) -> str:
    """Deterministic 24-hex PBX IDs so regenerating the project does not rewrite every UUID."""
    return hashlib.sha256(f"NYTNA:{seed}".encode()).hexdigest()[:24].upper()


def load_marketing_version() -> str:
    try:
        with open(MANIFEST, encoding="utf-8") as f:
            data = json.load(f)
        v = data.get("version", "1.0.0")
        return str(v)
    except OSError:
        return "1.0.0"


MV = load_marketing_version()


def build_number(version: str) -> int:
    """Monotonic CFBundleVersion derived from the marketing version (1.3.1 -> 10301)."""
    parts = (version.split(".") + ["0", "0", "0"])[:3]
    nums = []
    for part in parts:
        digits = "".join(ch for ch in part if ch.isdigit())
        nums.append(int(digits or 0))
    return nums[0] * 10000 + nums[1] * 100 + nums[2]


BN = build_number(MV)

# iOS App Store signing (Release only; Debug stays Automatic for simulator/dev).
IOS_TEAM = os.environ.get("APPLE_TEAM_ID", "3A5647GGDY")
IOS_SIGN_IDENTITY = os.environ.get("IOS_SIGN_IDENTITY", "Apple Distribution")
IOS_HOST_PROFILE = os.environ.get("IOS_HOST_PROFILE", "NewsMinus iOS App Store")
IOS_EXT_PROFILE = os.environ.get("IOS_EXT_PROFILE", "NewsMinus iOS Extension App Store")
IOS_HOST_BUNDLE = os.environ.get("IOS_BUNDLE_ID", "com.nunus.NYTimesCleanerHost.ios")
IOS_EXT_BUNDLE = os.environ.get("IOS_EXT_BUNDLE_ID", f"{IOS_HOST_BUNDLE}.extension")

# —— IDs (stable across regenerations) ——
I = {k: nid(k) for k in [
    "P_ROOT", "G_MAIN", "G_SHARED", "G_HOST", "G_EXT", "G_IOS", "G_SCRIPTS", "G_PROD",
    "FR_SWIFT", "FR_HANDLER", "FR_INFO", "FR_HOST_INFO", "FR_HOST_ENT", "FR_EXT_ENT", "FR_SCRIPT",
    "FR_ASSETS", "FR_APPICNS", "FR_IOS_HOST_ENT", "FR_IOS_EXT_ENT", "FR_PRIVACY",
    "PR_HOST_APP", "PR_EXT_APPEX", "PR_HOST_IOS", "PR_EXT_IOS",
    "BF_APP", "BF_HANDLER", "BF_EMBED", "BF_APPICNS",
    "BF_APP_IOS", "BF_HANDLER_IOS", "BF_EMBED_IOS",
    "BF_ASSETS_IOS", "BF_PRIVACY_IOS", "BF_PRIVACY_EXT_MAC", "BF_PRIVACY_EXT_IOS",
    "PX", "TD", "CP", "PX_IOS", "TD_IOS", "CP_IOS",
    "FW_HOST", "FW_EXT", "FW_IOS_H", "FW_IOS_E",
    "SRC_HOST", "SRC_EXT", "SRC_HOST_IOS", "SRC_EXT_IOS",
    "SH_EXT", "SH_IOS",
    "RS_HOST", "RS_IOS", "RS_EXT_MAC", "RS_EXT_IOS",
    "DBG_PROJ", "REL_PROJ", "DBG_HOST", "REL_HOST", "DBG_EXT", "REL_EXT",
    "DBG_HIOS", "REL_HIOS", "DBG_EIOS", "REL_EIOS",
    "XC_LIST_PROJ", "XC_LIST_HOST", "XC_LIST_EXT", "XC_LIST_HIOS", "XC_LIST_EIOS",
    "T_HOST", "T_EXT", "T_HOST_IOS", "T_EXT_IOS",
]}
for k, v in I.items():
    globals()[k] = v

s = f"""// !$*UTF8*$!
{{
\tarchiveVersion = 1;
\tclasses = {{
\t}};
\tobjectVersion = 56;
\tobjects = {{

/* Begin PBXBuildFile section */
\t\t{BF_APP} /* NewsMinusHostApp.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {FR_SWIFT} /* NewsMinusHostApp.swift */; }};
\t\t{BF_HANDLER} /* SafariWebExtensionHandler.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {FR_HANDLER} /* SafariWebExtensionHandler.swift */; }};
\t\t{BF_EMBED} /* NewsMinusExtension.appex in Embed Foundation Extensions */ = {{isa = PBXBuildFile; fileRef = {PR_EXT_APPEX} /* NewsMinusExtension.appex */; settings = {{ATTRIBUTES = (RemoveHeadersOnCopy, ); }}; }};
\t\t{BF_APPICNS} /* AppIcon.icns in Resources */ = {{isa = PBXBuildFile; fileRef = {FR_APPICNS} /* AppIcon.icns */; }};
\t\t{BF_APP_IOS} /* NewsMinusHostApp.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {FR_SWIFT} /* NewsMinusHostApp.swift */; }};
\t\t{BF_HANDLER_IOS} /* SafariWebExtensionHandler.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {FR_HANDLER} /* SafariWebExtensionHandler.swift */; }};
\t\t{BF_EMBED_IOS} /* NewsMinusExtensioniOS.appex in Embed Foundation Extensions */ = {{isa = PBXBuildFile; fileRef = {PR_EXT_IOS} /* NewsMinusExtensioniOS.appex */; settings = {{ATTRIBUTES = (RemoveHeadersOnCopy, ); }}; }};
\t\t{BF_ASSETS_IOS} /* Assets.xcassets in Resources */ = {{isa = PBXBuildFile; fileRef = {FR_ASSETS} /* Assets.xcassets */; }};
\t\t{BF_PRIVACY_IOS} /* PrivacyInfo.xcprivacy in Resources */ = {{isa = PBXBuildFile; fileRef = {FR_PRIVACY} /* PrivacyInfo.xcprivacy */; }};
\t\t{BF_PRIVACY_EXT_MAC} /* PrivacyInfo.xcprivacy in Resources */ = {{isa = PBXBuildFile; fileRef = {FR_PRIVACY} /* PrivacyInfo.xcprivacy */; }};
\t\t{BF_PRIVACY_EXT_IOS} /* PrivacyInfo.xcprivacy in Resources */ = {{isa = PBXBuildFile; fileRef = {FR_PRIVACY} /* PrivacyInfo.xcprivacy */; }};
/* End PBXBuildFile section */

/* Begin PBXContainerItemProxy section */
\t\t{PX} /* PBXContainerItemProxy */ = {{
\t\t\tisa = PBXContainerItemProxy;
\t\t\tcontainerPortal = {P_ROOT} /* Project object */;
\t\t\tproxyType = 1;
\t\t\tremoteGlobalIDString = {T_EXT};
\t\t\tremoteInfo = NewsMinusExtension;
\t\t}};
\t\t{PX_IOS} /* PBXContainerItemProxy */ = {{
\t\t\tisa = PBXContainerItemProxy;
\t\t\tcontainerPortal = {P_ROOT} /* Project object */;
\t\t\tproxyType = 1;
\t\t\tremoteGlobalIDString = {T_EXT_IOS};
\t\t\tremoteInfo = NewsMinusExtensioniOS;
\t\t}};
/* End PBXContainerItemProxy section */

/* Begin PBXCopyFilesBuildPhase section */
\t\t{CP} /* Embed Foundation Extensions */ = {{
\t\t\tisa = PBXCopyFilesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tdstPath = "";
\t\t\tdstSubfolderSpec = 13;
\t\t\tfiles = (
\t\t\t\t{BF_EMBED} /* NewsMinusExtension.appex in Embed Foundation Extensions */,
\t\t\t);
\t\t\tname = "Embed Foundation Extensions";
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
\t\t{CP_IOS} /* Embed Foundation Extensions */ = {{
\t\t\tisa = PBXCopyFilesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tdstPath = "";
\t\t\tdstSubfolderSpec = 13;
\t\t\tfiles = (
\t\t\t\t{BF_EMBED_IOS} /* NewsMinusExtensioniOS.appex in Embed Foundation Extensions */,
\t\t\t);
\t\t\tname = "Embed Foundation Extensions";
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXCopyFilesBuildPhase section */

/* Begin PBXFileReference section */
\t\t{FR_SWIFT} /* NewsMinusHostApp.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = NewsMinusHostApp.swift; sourceTree = "<group>"; }};
\t\t{FR_HANDLER} /* SafariWebExtensionHandler.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = SafariWebExtensionHandler.swift; sourceTree = "<group>"; }};
\t\t{FR_INFO} /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
\t\t{FR_HOST_INFO} /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
\t\t{FR_HOST_ENT} /* NewsMinusHost.entitlements */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.entitlements; path = NewsMinusHost.entitlements; sourceTree = "<group>"; }};
\t\t{FR_ASSETS} /* Assets.xcassets */ = {{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; }};
\t\t{FR_APPICNS} /* AppIcon.icns */ = {{isa = PBXFileReference; lastKnownFileType = image.icns; path = AppIcon.icns; sourceTree = "<group>"; }};
\t\t{FR_EXT_ENT} /* NewsMinusExtension.entitlements */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.entitlements; path = NewsMinusExtension.entitlements; sourceTree = "<group>"; }};
\t\t{FR_SCRIPT} /* copy-web-extension-resources.sh */ = {{isa = PBXFileReference; lastKnownFileType = text.script.sh; path = "copy-web-extension-resources.sh"; sourceTree = "<group>"; }};
\t\t{FR_IOS_HOST_ENT} /* NewsMinusHostIOS.entitlements */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.entitlements; path = NewsMinusHostIOS.entitlements; sourceTree = "<group>"; }};
\t\t{FR_IOS_EXT_ENT} /* NewsMinusExtensionIOS.entitlements */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.entitlements; path = NewsMinusExtensionIOS.entitlements; sourceTree = "<group>"; }};
\t\t{FR_PRIVACY} /* PrivacyInfo.xcprivacy */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = PrivacyInfo.xcprivacy; sourceTree = "<group>"; }};
\t\t{PR_HOST_APP} /* NewsMinusHost.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = NewsMinusHost.app; sourceTree = BUILT_PRODUCTS_DIR; }};
\t\t{PR_EXT_APPEX} /* NewsMinusExtension.appex */ = {{isa = PBXFileReference; explicitFileType = "wrapper.app-extension"; includeInIndex = 0; path = NewsMinusExtension.appex; sourceTree = BUILT_PRODUCTS_DIR; }};
\t\t{PR_HOST_IOS} /* NewsMinusHostIOS.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = NewsMinusHostIOS.app; sourceTree = BUILT_PRODUCTS_DIR; }};
\t\t{PR_EXT_IOS} /* NewsMinusExtensioniOS.appex */ = {{isa = PBXFileReference; explicitFileType = "wrapper.app-extension"; includeInIndex = 0; path = NewsMinusExtensioniOS.appex; sourceTree = BUILT_PRODUCTS_DIR; }};
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
\t\t{FW_HOST} /* Frameworks */ = {{isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = ( ); runOnlyForDeploymentPostprocessing = 0; }};
\t\t{FW_EXT} /* Frameworks */ = {{isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = ( ); runOnlyForDeploymentPostprocessing = 0; }};
\t\t{FW_IOS_H} /* Frameworks */ = {{isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = ( ); runOnlyForDeploymentPostprocessing = 0; }};
\t\t{FW_IOS_E} /* Frameworks */ = {{isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = ( ); runOnlyForDeploymentPostprocessing = 0; }};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
\t\t{G_MAIN} = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{G_SHARED} /* Shared */,
\t\t\t\t{G_HOST} /* Host */,
\t\t\t\t{G_EXT} /* Extension */,
\t\t\t\t{G_IOS} /* iOS */,
\t\t\t\t{G_SCRIPTS} /* scripts */,
\t\t\t\t{G_PROD} /* Products */,
\t\t\t);
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{G_SHARED} /* Shared */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{FR_SWIFT} /* NewsMinusHostApp.swift */,
\t\t\t);
\t\t\tpath = Shared;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{G_HOST} /* Host */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{FR_ASSETS} /* Assets.xcassets */,
\t\t\t\t{FR_APPICNS} /* AppIcon.icns */,
\t\t\t\t{FR_HOST_INFO} /* Info.plist */,
\t\t\t\t{FR_HOST_ENT} /* NewsMinusHost.entitlements */,
\t\t\t);
\t\t\tpath = Host;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{G_EXT} /* Extension */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{FR_HANDLER} /* SafariWebExtensionHandler.swift */,
\t\t\t\t{FR_INFO} /* Info.plist */,
\t\t\t\t{FR_EXT_ENT} /* NewsMinusExtension.entitlements */,
\t\t\t);
\t\t\tpath = Extension;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{G_IOS} /* iOS */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{FR_IOS_HOST_ENT} /* NewsMinusHostIOS.entitlements */,
\t\t\t\t{FR_IOS_EXT_ENT} /* NewsMinusExtensionIOS.entitlements */,
\t\t\t\t{FR_PRIVACY} /* PrivacyInfo.xcprivacy */,
\t\t\t);
\t\t\tpath = iOS;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{G_SCRIPTS} /* scripts */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{FR_SCRIPT} /* copy-web-extension-resources.sh */,
\t\t\t);
\t\t\tpath = scripts;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{G_PROD} /* Products */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{PR_HOST_APP} /* NewsMinusHost.app */,
\t\t\t\t{PR_EXT_APPEX} /* NewsMinusExtension.appex */,
\t\t\t\t{PR_HOST_IOS} /* NewsMinusHostIOS.app */,
\t\t\t\t{PR_EXT_IOS} /* NewsMinusExtensioniOS.appex */,
\t\t\t);
\t\t\tname = Products;
\t\t\tsourceTree = "<group>";
\t\t}};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
\t\t{T_HOST} /* NewsMinusHost */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {XC_LIST_HOST} /* Build configuration list for PBXNativeTarget "NewsMinusHost" */;
\t\t\tbuildPhases = (
\t\t\t\t{SRC_HOST} /* Sources */,
\t\t\t\t{FW_HOST} /* Frameworks */,
\t\t\t\t{RS_HOST} /* Resources */,
\t\t\t\t{CP} /* Embed Foundation Extensions */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t\t{TD} /* PBXTargetDependency */,
\t\t\t);
\t\t\tname = NewsMinusHost;
\t\t\tproductName = NewsMinusHost;
\t\t\tproductReference = {PR_HOST_APP} /* NewsMinusHost.app */;
\t\t\tproductType = "com.apple.product-type.application";
\t\t}};
\t\t{T_EXT} /* NewsMinusExtension */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {XC_LIST_EXT} /* Build configuration list for PBXNativeTarget "NewsMinusExtension" */;
\t\t\tbuildPhases = (
\t\t\t\t{SH_EXT} /* Copy web extension resources */,
\t\t\t\t{SRC_EXT} /* Sources */,
\t\t\t\t{FW_EXT} /* Frameworks */,
\t\t\t\t{RS_EXT_MAC} /* Resources */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = NewsMinusExtension;
\t\t\tproductName = NewsMinusExtension;
\t\t\tproductReference = {PR_EXT_APPEX} /* NewsMinusExtension.appex */;
\t\t\tproductType = "com.apple.product-type.app-extension";
\t\t}};
\t\t{T_HOST_IOS} /* NewsMinusHostIOS */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {XC_LIST_HIOS} /* Build configuration list for PBXNativeTarget "NewsMinusHostIOS" */;
\t\t\tbuildPhases = (
\t\t\t\t{SRC_HOST_IOS} /* Sources */,
\t\t\t\t{FW_IOS_H} /* Frameworks */,
\t\t\t\t{RS_IOS} /* Resources */,
\t\t\t\t{CP_IOS} /* Embed Foundation Extensions */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t\t{TD_IOS} /* PBXTargetDependency */,
\t\t\t);
\t\t\tname = NewsMinusHostIOS;
\t\t\tproductName = NewsMinusHostIOS;
\t\t\tproductReference = {PR_HOST_IOS} /* NewsMinusHostIOS.app */;
\t\t\tproductType = "com.apple.product-type.application";
\t\t}};
\t\t{T_EXT_IOS} /* NewsMinusExtensioniOS */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {XC_LIST_EIOS} /* Build configuration list for PBXNativeTarget "NewsMinusExtensioniOS" */;
\t\t\tbuildPhases = (
\t\t\t\t{SH_IOS} /* Copy web extension resources */,
\t\t\t\t{SRC_EXT_IOS} /* Sources */,
\t\t\t\t{FW_IOS_E} /* Frameworks */,
\t\t\t\t{RS_EXT_IOS} /* Resources */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = NewsMinusExtensioniOS;
\t\t\tproductName = NewsMinusExtensioniOS;
\t\t\tproductReference = {PR_EXT_IOS} /* NewsMinusExtensioniOS.appex */;
\t\t\tproductType = "com.apple.product-type.app-extension";
\t\t}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
\t\t{P_ROOT} /* Project object */ = {{
\t\t\tisa = PBXProject;
\t\t\tattributes = {{
\t\t\t\tBuildIndependentTargetsInParallel = 1;
\t\t\t\tLastSwiftUpdateCheck = 1500;
\t\t\t\tLastUpgradeCheck = 1500;
\t\t\t\tTargetAttributes = {{
\t\t\t\t\t{T_HOST} = {{CreatedOnToolsVersion = 15.0; }};
\t\t\t\t\t{T_EXT} = {{CreatedOnToolsVersion = 15.0; }};
\t\t\t\t\t{T_HOST_IOS} = {{CreatedOnToolsVersion = 15.0; }};
\t\t\t\t\t{T_EXT_IOS} = {{CreatedOnToolsVersion = 15.0; }};
\t\t\t\t}};
\t\t\t}};
\t\t\tbuildConfigurationList = {XC_LIST_PROJ} /* Build configuration list for PBXProject "NewsMinusSafari" */;
\t\t\tcompatibilityVersion = "Xcode 14.0";
\t\t\tdevelopmentRegion = en;
\t\t\thasScannedForEncodings = 0;
\t\t\tknownRegions = (
\t\t\t\ten,
\t\t\t\tBase,
\t\t\t);
\t\t\tmainGroup = {G_MAIN};
\t\t\tproductRefGroup = {G_PROD} /* Products */;
\t\t\tprojectDirPath = "";
\t\t\tprojectRoot = "";
\t\t\ttargets = (
\t\t\t\t{T_HOST} /* NewsMinusHost */,
\t\t\t\t{T_EXT} /* NewsMinusExtension */,
\t\t\t\t{T_HOST_IOS} /* NewsMinusHostIOS */,
\t\t\t\t{T_EXT_IOS} /* NewsMinusExtensioniOS */,
\t\t\t);
\t\t}};
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
\t\t{RS_HOST} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{BF_APPICNS} /* AppIcon.icns in Resources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
\t\t{RS_IOS} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{BF_ASSETS_IOS} /* Assets.xcassets in Resources */,
\t\t\t\t{BF_PRIVACY_IOS} /* PrivacyInfo.xcprivacy in Resources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
\t\t{RS_EXT_MAC} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{BF_PRIVACY_EXT_MAC} /* PrivacyInfo.xcprivacy in Resources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
\t\t{RS_EXT_IOS} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{BF_PRIVACY_EXT_IOS} /* PrivacyInfo.xcprivacy in Resources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXResourcesBuildPhase section */

/* Begin PBXShellScriptBuildPhase section */
\t\t{SH_EXT} /* Copy web extension resources */ = {{
\t\t\tisa = PBXShellScriptBuildPhase;
\t\t\talwaysOutOfDate = 1;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\tname = "Copy web extension resources";
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t\tshellPath = /bin/sh;
\t\t\tshellScript = "cd \\"$PROJECT_DIR\\" && /bin/sh ./scripts/copy-web-extension-resources.sh\\n";
\t\t}};
\t\t{SH_IOS} /* Copy web extension resources */ = {{
\t\t\tisa = PBXShellScriptBuildPhase;
\t\t\talwaysOutOfDate = 1;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\tname = "Copy web extension resources";
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t\tshellPath = /bin/sh;
\t\t\tshellScript = "cd \\"$PROJECT_DIR\\" && /bin/sh ./scripts/copy-web-extension-resources.sh\\n";
\t\t}};
/* End PBXShellScriptBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
\t\t{SRC_HOST} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{BF_APP} /* NewsMinusHostApp.swift in Sources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
\t\t{SRC_EXT} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{BF_HANDLER} /* SafariWebExtensionHandler.swift in Sources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
\t\t{SRC_HOST_IOS} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{BF_APP_IOS} /* NewsMinusHostApp.swift in Sources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
\t\t{SRC_EXT_IOS} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{BF_HANDLER_IOS} /* SafariWebExtensionHandler.swift in Sources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXSourcesBuildPhase section */

/* Begin PBXTargetDependency section */
\t\t{TD} /* PBXTargetDependency */ = {{
\t\t\tisa = PBXTargetDependency;
\t\t\ttarget = {T_EXT} /* NewsMinusExtension */;
\t\t\ttargetProxy = {PX} /* PBXContainerItemProxy */;
\t\t}};
\t\t{TD_IOS} /* PBXTargetDependency */ = {{
\t\t\tisa = PBXTargetDependency;
\t\t\ttarget = {T_EXT_IOS} /* NewsMinusExtensioniOS */;
\t\t\ttargetProxy = {PX_IOS} /* PBXContainerItemProxy */;
\t\t}};
/* End PBXTargetDependency section */

/* Begin XCBuildConfiguration section */
\t\t{DBG_PROJ} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;
\t\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;
\t\t\t\tCOPY_PHASE_STRIP = NO;
\t\t\t\tDEBUG_INFORMATION_FORMAT = dwarf;
\t\t\t\tENABLE_TESTABILITY = YES;
\t\t\t\tGCC_DYNAMIC_NO_PIC = NO;
\t\t\t\tGCC_OPTIMIZATION_LEVEL = 0;
\t\t\t\tONLY_ACTIVE_ARCH = YES;
\t\t\t\tSWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG;
\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = "-Onone";
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{REL_PROJ} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;
\t\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;
\t\t\t\tCOPY_PHASE_STRIP = NO;
\t\t\t\tDEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
\t\t\t\tENABLE_NS_ASSERTIONS = NO;
\t\t\t\tSWIFT_COMPILATION_MODE = wholemodule;
\t\t\t}};
\t\t\tname = Release;
\t\t}};
\t\t{DBG_HOST} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tCODE_SIGN_ENTITLEMENTS = Host/NewsMinusHost.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCOMBINE_HIDPI_IMAGES = YES;
\t\t\t\tCURRENT_PROJECT_VERSION = {BN};
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\tINFOPLIST_FILE = Host/Info.plist;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = NewsMinus;
\t\t\t\tINFOPLIST_KEY_CFBundleIconFile = AppIcon;
\t\t\t\tINFOPLIST_KEY_LSApplicationCategoryType = "public.app-category.news";
\t\t\t\tINFOPLIST_KEY_NSHumanReadableCopyright = "";
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/../Frameworks",
\t\t\t\t);
\t\t\t\tMACOSX_DEPLOYMENT_TARGET = 14.0;
\t\t\t\tMARKETING_VERSION = 3.0.7;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.nunus.NYTimesCleanerHost;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSDKROOT = macosx;
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{REL_HOST} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tCODE_SIGN_ENTITLEMENTS = Host/NewsMinusHost.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCOMBINE_HIDPI_IMAGES = YES;
\t\t\t\tCURRENT_PROJECT_VERSION = {BN};
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\tINFOPLIST_FILE = Host/Info.plist;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = NewsMinus;
\t\t\t\tINFOPLIST_KEY_CFBundleIconFile = AppIcon;
\t\t\t\tINFOPLIST_KEY_LSApplicationCategoryType = "public.app-category.news";
\t\t\t\tINFOPLIST_KEY_NSHumanReadableCopyright = "";
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/../Frameworks",
\t\t\t\t);
\t\t\t\tMACOSX_DEPLOYMENT_TARGET = 14.0;
\t\t\t\tMARKETING_VERSION = 3.0.7;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.nunus.NYTimesCleanerHost;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSDKROOT = macosx;
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t}};
\t\t\tname = Release;
\t\t}};
\t\t{DBG_EXT} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tCODE_SIGN_ENTITLEMENTS = Extension/NewsMinusExtension.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = {BN};
\t\t\t\tENABLE_USER_SCRIPT_SANDBOXING = NO;
\t\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\t\tINFOPLIST_FILE = Extension/Info.plist;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = NewsMinus;
\t\t\t\tINFOPLIST_KEY_NSHumanReadableCopyright = "";
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/../Frameworks",
\t\t\t\t\t"@executable_path/../../../../Frameworks",
\t\t\t\t);
\t\t\t\tMACOSX_DEPLOYMENT_TARGET = 14.0;
\t\t\t\tMARKETING_VERSION = 3.0.7;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.nunus.NYTimesCleanerHost.Extension;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSDKROOT = macosx;
\t\t\t\tSKIP_INSTALL = YES;
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{REL_EXT} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tCODE_SIGN_ENTITLEMENTS = Extension/NewsMinusExtension.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = {BN};
\t\t\t\tENABLE_USER_SCRIPT_SANDBOXING = NO;
\t\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\t\tINFOPLIST_FILE = Extension/Info.plist;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = NewsMinus;
\t\t\t\tINFOPLIST_KEY_NSHumanReadableCopyright = "";
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/../Frameworks",
\t\t\t\t\t"@executable_path/../../../../Frameworks",
\t\t\t\t);
\t\t\t\tMACOSX_DEPLOYMENT_TARGET = 14.0;
\t\t\t\tMARKETING_VERSION = 3.0.7;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.nunus.NYTimesCleanerHost.Extension;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSDKROOT = macosx;
\t\t\t\tSKIP_INSTALL = YES;
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t}};
\t\t\tname = Release;
\t\t}};
\t\t{DBG_HIOS} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tCODE_SIGN_ENTITLEMENTS = iOS/NewsMinusHostIOS.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = {BN};
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = NewsMinus;
\t\t\t\tINFOPLIST_KEY_ITSAppUsesNonExemptEncryption = NO;
\t\t\t\tINFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES;
\t\t\t\tINFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;
\t\t\t\tINFOPLIST_KEY_UILaunchScreen_Generation = YES;
\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPad = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 3.0.7;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = {IOS_HOST_BUNDLE};
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSDKROOT = iphoneos;
\t\t\t\tSUPPORTED_PLATFORMS = "iphoneos iphonesimulator";
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{REL_HIOS} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tCODE_SIGN_ENTITLEMENTS = iOS/NewsMinusHostIOS.entitlements;
\t\t\t\tCODE_SIGN_IDENTITY = "{IOS_SIGN_IDENTITY}";
\t\t\t\t"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "{IOS_SIGN_IDENTITY}";
\t\t\t\tCODE_SIGN_STYLE = Manual;
\t\t\t\tCURRENT_PROJECT_VERSION = {BN};
\t\t\t\tDEVELOPMENT_TEAM = {IOS_TEAM};
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = NewsMinus;
\t\t\t\tINFOPLIST_KEY_ITSAppUsesNonExemptEncryption = NO;
\t\t\t\tINFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES;
\t\t\t\tINFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;
\t\t\t\tINFOPLIST_KEY_UILaunchScreen_Generation = YES;
\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPad = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 3.0.7;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = {IOS_HOST_BUNDLE};
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tPROVISIONING_PROFILE_SPECIFIER = "{IOS_HOST_PROFILE}";
\t\t\t\tSDKROOT = iphoneos;
\t\t\t\tSUPPORTED_PLATFORMS = "iphoneos iphonesimulator";
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t\t}};
\t\t\tname = Release;
\t\t}};
\t\t{DBG_EIOS} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tCODE_SIGN_ENTITLEMENTS = iOS/NewsMinusExtensionIOS.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = {BN};
\t\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\t\tINFOPLIST_FILE = Extension/Info.plist;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = NewsMinus;
\t\t\t\tINFOPLIST_KEY_NSHumanReadableCopyright = "";
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t\t"@executable_path/../../Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 3.0.7;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = {IOS_EXT_BUNDLE};
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSDKROOT = iphoneos;
\t\t\t\tSKIP_INSTALL = YES;
\t\t\t\tSUPPORTED_PLATFORMS = "iphoneos iphonesimulator";
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{REL_EIOS} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
\t\t\t\tCODE_SIGN_ENTITLEMENTS = iOS/NewsMinusExtensionIOS.entitlements;
\t\t\t\tCODE_SIGN_IDENTITY = "{IOS_SIGN_IDENTITY}";
\t\t\t\t"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "{IOS_SIGN_IDENTITY}";
\t\t\t\tCODE_SIGN_STYLE = Manual;
\t\t\t\tCURRENT_PROJECT_VERSION = {BN};
\t\t\t\tDEVELOPMENT_TEAM = {IOS_TEAM};
\t\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\t\tINFOPLIST_FILE = Extension/Info.plist;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = NewsMinus;
\t\t\t\tINFOPLIST_KEY_NSHumanReadableCopyright = "";
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t\t"@executable_path/../../Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 3.0.7;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = {IOS_EXT_BUNDLE};
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tPROVISIONING_PROFILE_SPECIFIER = "{IOS_EXT_PROFILE}";
\t\t\t\tSDKROOT = iphoneos;
\t\t\t\tSKIP_INSTALL = YES;
\t\t\t\tSUPPORTED_PLATFORMS = "iphoneos iphonesimulator";
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t\t}};
\t\t\tname = Release;
\t\t}};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
\t\t{XC_LIST_HOST} /* Build configuration list for PBXNativeTarget "NewsMinusHost" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{DBG_HOST} /* Debug */,
\t\t\t\t{REL_HOST} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
\t\t{XC_LIST_EXT} /* Build configuration list for PBXNativeTarget "NewsMinusExtension" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{DBG_EXT} /* Debug */,
\t\t\t\t{REL_EXT} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
\t\t{XC_LIST_HIOS} /* Build configuration list for PBXNativeTarget "NewsMinusHostIOS" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{DBG_HIOS} /* Debug */,
\t\t\t\t{REL_HIOS} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
\t\t{XC_LIST_EIOS} /* Build configuration list for PBXNativeTarget "NewsMinusExtensioniOS" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{DBG_EIOS} /* Debug */,
\t\t\t\t{REL_EIOS} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
\t\t{XC_LIST_PROJ} /* Build configuration list for PBXProject "NewsMinusSafari" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{DBG_PROJ} /* Debug */,
\t\t\t\t{REL_PROJ} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
/* End XCConfigurationList section */
\t}};
\trootObject = {P_ROOT} /* Project object */;
}}
"""

os.makedirs(PROJ_DIR, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(s)
print("Wrote", OUT, "MARKETING_VERSION=", MV, "CURRENT_PROJECT_VERSION=", BN)
