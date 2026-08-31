# Flutter

**Dart + its own rendering engine.** The language is [[languages/10-dart/README|its own course]]; this is the framework.

## The one thing that defines it

**Flutter doesn't use platform widgets. It draws every pixel itself** with its own engine (Impeller, which replaced Skia).

That single decision explains everything:

- ✅ **Pixel-identical on both platforms** — because nothing is a platform widget
- ✅ **Total design control** — you're painting, not configuring
- ✅ **New Flutter versions change your UI everywhere at once** — no waiting for OS adoption
- ❌ **You don't inherit platform behaviour** — text selection, accessibility affordances and scroll physics are reimplementations, and they're good but not identical
- ❌ **Larger binaries** — the engine ships with your app
- ❌ **New OS features need a plugin**

## Everything is a widget

```dart
class FeedScreen extends StatelessWidget {
  const FeedScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Feed')),
      body: Consumer<FeedViewModel>(
        builder: (context, vm, _) => switch (vm.state) {
          Loading()      => const Center(child: CircularProgressIndicator()),
          Error(:final m) => ErrorView(message: m, onRetry: vm.retry),
          Success(:final items) => ListView.builder(          // ← lazy
            itemCount: items.length,
            itemBuilder: (_, i) => ItemRow(key: ValueKey(items[i].id), item: items[i]),
          ),
        },
      ),
    );
  }
}
```

**Layout, padding, alignment and styling are all widgets**, which produces deep nesting. That's the framework's most-criticised trait. **Extract widgets into named classes early** — it's the main thing that keeps a Flutter codebase readable.

**`const` constructors matter.** A `const` widget is skipped during rebuilds. **Turn on the `prefer_const_constructors` lint** — it's a real, free performance win.

## State management — the perennial question

Flutter deliberately ships no opinion, so the ecosystem produced many:

| | |
|---|---|
| **`setState`** | Built in. Fine for genuinely local state |
| **Provider** | The long-standing default. Simple, widely known |
| **Riverpod** | Provider's successor — compile-safe, testable, no `BuildContext` needed. **The common recommendation now** |
| **Bloc** | Event → state, very explicit. Popular in larger teams |
| **signals / GetX** | Others you'll encounter. **GetX is widely criticised** for doing too much |

**Pick one and use it consistently.** Mixing three is the single most common cause of an unmaintainable Flutter codebase.

## The tooling, which is genuinely excellent

- **Hot reload** — sub-second, preserves state. **The best iteration loop in mobile**, and the main reason people love Flutter
- **DevTools** — widget inspector, timeline, memory
- **`flutter doctor`** diagnoses environment problems
- **One codebase → iOS, Android, web, desktop.** Mobile is the mature target; treat web and desktop as viable but less proven

```bash
flutter run
flutter build appbundle --release
flutter test
```

## Platform integration

**Plugins** wrap native APIs (`camera`, `geolocator`, `shared_preferences`). Most common needs are covered on pub.dev.

**Check plugin health before depending on it** — pub.dev shows maintenance status, and an abandoned plugin is a real risk. **For anything unusual you'll write platform channels yourself**, which means writing Swift and Kotlin anyway.

**Platform adaptation:** `Theme.of(context).platform`, and Cupertino widgets for iOS-style UI. **Most Flutter apps use Material everywhere** and accept looking slightly non-native on iOS — usually fine for a branded app, occasionally not.

## What to watch

- **Deep widget nesting** — extract components
- **`setState` on a large subtree** rebuilds all of it
- **`ListView` vs `ListView.builder`** — the non-builder version constructs every child. **Always use `.builder` for real lists**
- **Missing `const`**
- **Plugin abandonment**
- **Binary size** — Flutter apps start larger. Use `--split-debug-info` and check the size report
- **Accessibility needs deliberate work** — the `Semantics` widget. **You don't get it free the way you do with platform widgets.** Test with TalkBack and VoiceOver

## Related
- [[languages/10-dart/README|Dart]] — the language
- [[mobile/14-native-vs-cross-platform|native vs cross-platform]] — when to choose this
- [[mobile/README|the mobile course]]
