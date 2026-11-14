# Mobile

## What mobile development is

**Mobile development is building apps for phones and tablets: the apps you install from the App Store or Google Play.**

There are two main platforms: **iOS** (iPhones and iPads, made by Apple) and **Android** (phones from Samsung, Tecno, Google and many others). You can build an app separately for each, using each platform's own language, or build one app that runs on both, using tools like Flutter or React Native.

Building for phones is different from building websites, because you're not in control. The phone can pause your app the moment the user switches away, close it completely to free memory, refuse to let it run in the background, and deny it the camera or location. Apple and Google also review every app and can refuse to publish it. Most of this course is about writing apps that cope with all of that.

## What you'll be able to do

By the end you will be able to:
- explain what makes phones different from web and desktop, and the differences between iOS and Android;
- write an app that survives being paused or closed by the phone without losing the user's work;
- build screens with modern tools (SwiftUI, Jetpack Compose, Flutter or React Native) and move between them;
- make an app that keeps working without internet, and syncs when the connection comes back;
- ask for permissions politely, keep the battery healthy, and keep data safe on the device;
- release an app to the stores and roll out updates safely;
- choose between building for each platform separately or for both at once.

## Where to start

**Before you start:** basic programming ([[programming-fundamentals/index|Programming Fundamentals]]). Some [[frontend/index|frontend]] helps, because modern mobile screens are built the same way.

The notes work whichever platform you choose. Start with 01–03: they're the limits phones put on you, and everything after is about working within them. **Read 14 right after 02** if you still need to choose between building for each platform separately or for both at once.

1. [[mobile/01-what-makes-mobile-different|What Makes Mobile Different]]: the six limits of building for phones, what changes compared with the web, and what's actually nicer.
2. [[mobile/02-the-two-platforms|The Two Platforms]]: iOS and Android compared on what affects your work, how much they share, and where to start.
3. [[mobile/03-the-app-lifecycle|The App Lifecycle]]: the note that shapes the most code. The phone decides when your app runs, pauses and dies, and how to make sure the user loses nothing.
4. [[mobile/04-declarative-ui|Declarative UI]]: building screens by describing what they should look like for the current data. SwiftUI, Compose and React all work this way.
5. [[mobile/05-state-and-architecture|State and Architecture]]: how to organise an app's code and data, the way both platforms now recommend.
6. [[mobile/06-navigation|Navigation]]: moving between screens, the back button, and opening the right screen from a link.
7. [[mobile/07-data-and-offline-first|Data and Offline-First]]: the most important design decision: keep the data on the phone first, so the app works without internet, then sync it.
8. [[mobile/08-networking-on-mobile|Networking on Mobile]]: why phone networks are slow and costly for the battery, and designing for apps that stay in use for years.
9. [[mobile/09-permissions-and-privacy|Permissions and Privacy]]: asking for the camera, location and so on in a way users accept, and the privacy rules the stores enforce.
10. [[mobile/10-background-work-and-push|Background Work and Push]]: what your app can do when it's not on screen (much less than you'd think), and push notifications.
11. [[mobile/11-performance-and-battery|Performance and Battery]]: starting quickly, scrolling smoothly, and where the battery actually goes.
12. [[mobile/12-security-on-device|Security on the Device]]: the app runs on hardware the user, or an attacker, controls. Nothing in your app is secret, so the server must check everything.
13. [[mobile/13-release-and-distribution|Release and Distribution]]: getting through store review, releasing to a few users first, and two switches to build in before you need them.
14. [[mobile/14-native-vs-cross-platform|Native vs Cross-Platform]]: choosing between separate apps for each platform and one app for both, based on your team and your app.

## Frameworks: building for a specific platform

- [[mobile/frameworks/ios/index|iOS]]: Swift and SwiftUI.
- [[mobile/frameworks/android/index|Android]]: Kotlin and Jetpack Compose.
- [[mobile/frameworks/flutter/index|Flutter]]: Dart, one app for both platforms, drawn by Flutter itself.
- [[mobile/frameworks/react-native/index|React Native]]: TypeScript, one app for both platforms, using real native components. Start with Expo.

The languages have their own courses: [[languages/08-swift/index|Swift]], [[languages/09-kotlin/index|Kotlin]] and [[languages/10-dart/index|Dart]]. For React Native's TypeScript, see [[frontend/frameworks/react/index|React]].

## Practice

- [[mobile/projects|Projects]]: hands-on tasks, each with a clear "done when". Start with "survive process death", an afternoon that teaches the core idea. The one that matters most is publishing a small app to a store, because that process can't be practised any other way.
- [[mobile/interview/index|Mobile interview prep]]: the questions about the app lifecycle are the ones that separate people who've shipped apps from people who've followed tutorials.

## Key ideas to remember

1. **The phone can close your app at any moment.** Save what matters so the user never loses work. → [[mobile/03-the-app-lifecycle|03]]
2. **Keep the data on the phone first,** and treat the internet as something that comes and goes. → [[mobile/07-data-and-offline-first|07]]
3. **Nothing inside your app is secret.** Anyone can take it apart; the server must check everything. → [[mobile/12-security-on-device|12]]
4. **Build a way to switch features off remotely before you need it.** Once an app is released, users update slowly. → [[mobile/13-release-and-distribution|13]]

## Related

- [[frontend/index|Frontend]]: the closest discipline; note 04 is largely shared with it.
- [[backend/index|Backend]]: the server your app talks to.
- [[desktop/index|Desktop]]: the same "one app or several?" question, for computers.
- [[os/index|Operating Systems]]: what "the phone closes your app" means underneath.

---

## About this course

- **Size:** 14 notes, plus guides for four frameworks and interview prep. Written in August 2026, when the vault had courses for web, desktop and games but nothing for phones.
- **Where it came from:** reference sources. Nothing here has yet been published to a store by its author; the [[mobile/projects|projects]] exist to change that.
