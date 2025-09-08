import Foundation

@main
struct NanosecondOptionsConsoleMain {
    static func main() {
        print("🚀 Starting Nanosecond Options Console Demo")
        let _ = NanosecondOptionsTradingSystem.createDemoSystem()
        // Run the main run loop briefly so timers and async tasks can execute
        RunLoop.current.run(until: Date().addingTimeInterval(2.0))
        print("✅ Demo finished")
    }
}


