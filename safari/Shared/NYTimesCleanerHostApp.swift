import SwiftUI

@main
struct NYTimesCleanerHostApp: App {
    var body: some Scene {
        WindowGroup {
            Text(
                "NewsMinus runs in Safari. Turn it on under Safari -> Settings -> Extensions and allow supported news sites."
            )
            .padding(24)
            .multilineTextAlignment(.center)
            #if os(macOS)
                .frame(minWidth: 360, minHeight: 160)
            #endif
        }
    }
}
