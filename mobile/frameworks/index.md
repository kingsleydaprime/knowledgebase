# Mobile Frameworks

**"How this stack does it."** Sections [[mobile/01-what-makes-mobile-different|01]]–[[mobile/14-native-vs-cross-platform|14]] hold true whichever you pick; this folder is the per-stack implementation layer, copying the [[backend/frameworks/index|backend/frameworks]] convention.

**Read [[mobile/14-native-vs-cross-platform|note 14]] first** — it's the decision these folders implement.

| Stack | Language | Best for |
|---|---|---|
| [[mobile/frameworks/ios/index\|ios/]] | [[languages/08-swift/index\|Swift]] | Platform-idiomatic iOS, deep OS integration |
| [[mobile/frameworks/android/index\|android/]] | [[languages/09-kotlin/index\|Kotlin]] | Platform-idiomatic Android, the larger global market |
| [[mobile/frameworks/flutter/index\|flutter/]] | [[languages/10-dart/index\|Dart]] | Design-led apps, one codebase, consistent UI |
| [[mobile/frameworks/react-native/index\|react-native/]] | TypeScript | Teams that already know [[frontend/frameworks/react/index\|React]] |

**Kotlin Multiplatform** doesn't get its own folder because it isn't a UI framework — it's shared Kotlin logic under native SwiftUI and Compose UIs. It's covered in [[mobile/14-native-vs-cross-platform|note 14]] and [[languages/09-kotlin/index|the Kotlin course]].

## Related
- [[mobile/index|the mobile course]] · [[mobile/projects|projects]]
- [[backend/frameworks/index|backend/frameworks]] — the convention this copies
- [[languages/index|languages]] — the languages themselves
