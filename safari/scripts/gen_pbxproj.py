#!/usr/bin/env python3
"""Emit safari/NYTimesCleanerSafari.xcodeproj/project.pbxproj (macOS host + Safari Web Extension only)."""
from __future__ import annotations

import hashlib
import json
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
PROJ_DIR = os.path.join(ROOT, "NYTimesCleanerSafari.xcodeproj")
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

# —— IDs (stable for one generation; re-run script to regenerate) ——
I = {k: nid(k) for k in [
    "P_ROOT", "G_MAIN", "G_SHARED", "G_HOST", "G_EXT", "G_SCRIPTS", "G_PROD",
    "FR_SWIFT", "FR_HANDLER", "FR_INFO", "FR_HOST_ENT", "FR_EXT_ENT", "FR_SCRIPT",
    "FR_ASSETS", "FR_APPICNS",
    "PR_HOST_APP", "PR_EXT_APPEX",
    "BF_APP", "BF_HANDLER", "BF_EMBED", "BF_APPICNS",
    "PX", "TD", "CP",
    "FW_HOST", "FW_EXT",
    "SRC_HOST", "SRC_EXT",
    "SH_EXT",
    "RS_HOST",
    "DBG_PROJ", "REL_PROJ", "DBG_HOST", "REL_HOST", "DBG_EXT", "REL_EXT",
    "XC_LIST_PROJ", "XC_LIST_HOST", "XC_LIST_EXT",
    "T_HOST", "T_EXT",
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
\t\t{BF_APP} /* NYTimesCleanerHostApp.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {FR_SWIFT} /* NYTimesCleanerHostApp.swift */; }};
\t\t{BF_HANDLER} /* SafariWebExtensionHandler.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {FR_HANDLER} /* SafariWebExtensionHandler.swift */; }};
\t\t{BF_EMBED} /* NYTimesCleanerExtension.appex in Embed Foundation Extensions */ = {{isa = PBXBuildFile; fileRef = {PR_EXT_APPEX} /* NYTimesCleanerExtension.appex */; settings = {{ATTRIBUTES = (RemoveHeadersOnCopy, ); }}; }};
\t\t{BF_APPICNS} /* AppIcon.icns in Resources */ = {{isa = PBXBuildFile; fileRef = {FR_APPICNS} /* AppIcon.icns */; }};
/* End PBXBuildFile section */

/* Begin PBXContainerItemProxy section */
\t\t{PX} /* PBXContainerItemProxy */ = {{
\t\t\tisa = PBXContainerItemProxy;
\t\t\tcontainerPortal = {P_ROOT} /* Project object */;
\t\t\tproxyType = 1;
\t\t\tremoteGlobalIDString = {T_EXT};
\t\t\tremoteInfo = NYTimesCleanerExtension;
\t\t}};
/* End PBXContainerItemProxy section */

/* Begin PBXCopyFilesBuildPhase section */
\t\t{CP} /* Embed Foundation Extensions */ = {{
\t\t\tisa = PBXCopyFilesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tdstPath = "";
\t\t\tdstSubfolderSpec = 13;
\t\t\tfiles = (
\t\t\t\t{BF_EMBED} /* NYTimesCleanerExtension.appex in Embed Foundation Extensions */,
\t\t\t);
\t\t\tname = "Embed Foundation Extensions";
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXCopyFilesBuildPhase section */

/* Begin PBXFileReference section */
\t\t{FR_SWIFT} /* NYTimesCleanerHostApp.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = NYTimesCleanerHostApp.swift; sourceTree = "<group>"; }};
\t\t{FR_HANDLER} /* SafariWebExtensionHandler.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = SafariWebExtensionHandler.swift; sourceTree = "<group>"; }};
\t\t{FR_INFO} /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
\t\t{FR_HOST_ENT} /* NYTimesCleanerHost.entitlements */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.entitlements; path = NYTimesCleanerHost.entitlements; sourceTree = "<group>"; }};
\t\t{FR_ASSETS} /* Assets.xcassets */ = {{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; }};
\t\t{FR_APPICNS} /* AppIcon.icns */ = {{isa = PBXFileReference; lastKnownFileType = image.icns; path = AppIcon.icns; sourceTree = "<group>"; }};
\t\t{FR_EXT_ENT} /* NYTimesCleanerExtension.entitlements */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.entitlements; path = NYTimesCleanerExtension.entitlements; sourceTree = "<group>"; }};
\t\t{FR_SCRIPT} /* copy-web-extension-resources.sh */ = {{isa = PBXFileReference; lastKnownFileType = text.script.sh; path = "copy-web-extension-resources.sh"; sourceTree = "<group>"; }};
\t\t{PR_HOST_APP} /* NYTimesCleanerHost.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = NYTimesCleanerHost.app; sourceTree = BUILT_PRODUCTS_DIR; }};
\t\t{PR_EXT_APPEX} /* NYTimesCleanerExtension.appex */ = {{isa = PBXFileReference; explicitFileType = "wrapper.app-extension"; includeInIndex = 0; path = NYTimesCleanerExtension.appex; sourceTree = BUILT_PRODUCTS_DIR; }};
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
\t\t{FW_HOST} /* Frameworks */ = {{isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = ( ); runOnlyForDeploymentPostprocessing = 0; }};
\t\t{FW_EXT} /* Frameworks */ = {{isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = ( ); runOnlyForDeploymentPostprocessing = 0; }};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
\t\t{G_MAIN} = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{G_SHARED} /* Shared */,
\t\t\t\t{G_HOST} /* Host */,
\t\t\t\t{G_EXT} /* Extension */,
\t\t\t\t{G_SCRIPTS} /* scripts */,
\t\t\t\t{G_PROD} /* Products */,
\t\t\t);
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{G_SHARED} /* Shared */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{FR_SWIFT} /* NYTimesCleanerHostApp.swift */,
\t\t\t);
\t\t\tpath = Shared;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{G_HOST} /* Host */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{FR_ASSETS} /* Assets.xcassets */,
\t\t\t\t{FR_APPICNS} /* AppIcon.icns */,
\t\t\t\t{FR_HOST_ENT} /* NYTimesCleanerHost.entitlements */,
\t\t\t);
\t\t\tpath = Host;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{G_EXT} /* Extension */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{FR_HANDLER} /* SafariWebExtensionHandler.swift */,
\t\t\t\t{FR_INFO} /* Info.plist */,
\t\t\t\t{FR_EXT_ENT} /* NYTimesCleanerExtension.entitlements */,
\t\t\t);
\t\t\tpath = Extension;
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
\t\t\t\t{PR_HOST_APP} /* NYTimesCleanerHost.app */,
\t\t\t\t{PR_EXT_APPEX} /* NYTimesCleanerExtension.appex */,
\t\t\t);
\t\t\tname = Products;
\t\t\tsourceTree = "<group>";
\t\t}};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
\t\t{T_HOST} /* NYTimesCleanerHost */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {XC_LIST_HOST} /* Build configuration list for PBXNativeTarget "NYTimesCleanerHost" */;
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
\t\t\tname = NYTimesCleanerHost;
\t\t\tproductName = NYTimesCleanerHost;
\t\t\tproductReference = {PR_HOST_APP} /* NYTimesCleanerHost.app */;
\t\t\tproductType = "com.apple.product-type.application";
\t\t}};
\t\t{T_EXT} /* NYTimesCleanerExtension */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {XC_LIST_EXT} /* Build configuration list for PBXNativeTarget "NYTimesCleanerExtension" */;
\t\t\tbuildPhases = (
\t\t\t\t{SH_EXT} /* Copy web extension resources */,
\t\t\t\t{SRC_EXT} /* Sources */,
\t\t\t\t{FW_EXT} /* Frameworks */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = NYTimesCleanerExtension;
\t\t\tproductName = NYTimesCleanerExtension;
\t\t\tproductReference = {PR_EXT_APPEX} /* NYTimesCleanerExtension.appex */;
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
\t\t\t\t}};
\t\t\t}};
\t\t\tbuildConfigurationList = {XC_LIST_PROJ} /* Build configuration list for PBXProject "NYTimesCleanerSafari" */;
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
\t\t\t\t{T_HOST} /* NYTimesCleanerHost */,
\t\t\t\t{T_EXT} /* NYTimesCleanerExtension */,
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
/* End PBXShellScriptBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
\t\t{SRC_HOST} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{BF_APP} /* NYTimesCleanerHostApp.swift in Sources */,
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
/* End PBXSourcesBuildPhase section */

/* Begin PBXTargetDependency section */
\t\t{TD} /* PBXTargetDependency */ = {{
\t\t\tisa = PBXTargetDependency;
\t\t\ttarget = {T_EXT} /* NYTimesCleanerExtension */;
\t\t\ttargetProxy = {PX} /* PBXContainerItemProxy */;
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
\t\t\t\tCODE_SIGN_ENTITLEMENTS = Host/NYTimesCleanerHost.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCOMBINE_HIDPI_IMAGES = YES;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = NewsMinus;
\t\t\t\tINFOPLIST_KEY_NSHumanReadableCopyright = "";
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/../Frameworks",
\t\t\t\t);
\t\t\t\tMACOSX_DEPLOYMENT_TARGET = 14.0;
\t\t\t\tMARKETING_VERSION = {MV};
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
\t\t\t\tCODE_SIGN_ENTITLEMENTS = Host/NYTimesCleanerHost.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCOMBINE_HIDPI_IMAGES = YES;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = NewsMinus;
\t\t\t\tINFOPLIST_KEY_NSHumanReadableCopyright = "";
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/../Frameworks",
\t\t\t\t);
\t\t\t\tMACOSX_DEPLOYMENT_TARGET = 14.0;
\t\t\t\tMARKETING_VERSION = {MV};
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
\t\t\t\tCODE_SIGN_ENTITLEMENTS = Extension/NYTimesCleanerExtension.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
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
\t\t\t\tMARKETING_VERSION = {MV};
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
\t\t\t\tCODE_SIGN_ENTITLEMENTS = Extension/NYTimesCleanerExtension.entitlements;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
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
\t\t\t\tMARKETING_VERSION = {MV};
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.nunus.NYTimesCleanerHost.Extension;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSDKROOT = macosx;
\t\t\t\tSKIP_INSTALL = YES;
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t}};
\t\t\tname = Release;
\t\t}};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
\t\t{XC_LIST_HOST} /* Build configuration list for PBXNativeTarget "NYTimesCleanerHost" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{DBG_HOST} /* Debug */,
\t\t\t\t{REL_HOST} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
\t\t{XC_LIST_EXT} /* Build configuration list for PBXNativeTarget "NYTimesCleanerExtension" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{DBG_EXT} /* Debug */,
\t\t\t\t{REL_EXT} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
\t\t{XC_LIST_PROJ} /* Build configuration list for PBXProject "NYTimesCleanerSafari" */ = {{
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
print("Wrote", OUT, "MARKETING_VERSION=", MV)
