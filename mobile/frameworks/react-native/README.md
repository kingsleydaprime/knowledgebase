# React Native

**TypeScript driving real native components.** If you know [[frontend/frameworks/react/README|React]], you know most of this already.

## The one thing that defines it

**A `<View>` is a real `UIView`. A `<Text>` is a real `UILabel`.** React Native isn't drawing a UI that looks native — **it's operating the actual native UI toolkit from JavaScript.**

Which means you inherit platform behaviour free: scroll physics, text selection, accessibility, keyboard handling, and the platform's own look.

## Use Expo

**This is the single most useful piece of advice here.** Expo used to mean "limited"; it now means "the sane way to build React Native." Managed builds, over-the-air updates, a large library of native modules, and config plugins for the ones it doesn't include — **and you can still drop to native code when needed.**

```bash
npx create-expo-app@latest my-app
npx expo start
eas build --platform all          # cloud builds, no Mac needed for iOS
```

**`eas build` means you can build for iOS without owning a Mac**, which is a genuine advantage over every other route to the App Store.

## The shape

```tsx
export default function FeedScreen() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['feed'],
    queryFn: fetchFeed,
  });

  if (isLoading) return <ActivityIndicator />;
  if (error) return <ErrorView onRetry={refetch} />;

  return (
    <FlashList
      data={data}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => <ItemRow item={item} />}
      estimatedItemSize={80}
    />
  );
}
```

**The stack that's become standard:**

| | |
|---|---|
| **Expo Router** | File-based navigation, like Next.js |
| **TanStack Query** | Server state — **the biggest win you can adopt** → [[frontend/04-state-and-data/README\|server state]] |
| **Zustand / Jotai** | Client state. Redux if you need its ecosystem |
| **Reanimated** | Animations **on the UI thread**, so they stay smooth |
| **FlashList** | A faster `FlatList`. Use it for long lists |
| **NativeWind** | Tailwind for RN, if you like Tailwind |
| **MMKV** | Fast key-value storage |

## The New Architecture — why old criticism is stale

React Native's historical weakness was **the bridge**: JS and native communicated by passing serialised JSON asynchronously, which was the performance ceiling and the source of the "RN is laggy" reputation.

**The New Architecture (JSI, Fabric, TurboModules) removes the bridge** — JS holds direct references to native objects and can call them synchronously. It's the default now.

**So performance criticism written before ~2024 is describing a system that no longer exists.** Judge it on the current architecture.

## Over-the-air updates — a real advantage

**`expo-updates` ships JS-only changes directly to users, bypassing store review.** Fix a bug in minutes rather than days.

**The limits, which matter:** it only works for JS/asset changes — **native changes still require a store release** — and both stores allow it for bug fixes and improvements but **not for changing what your app fundamentally does.** Abusing it risks removal.

Still, **it's the closest thing mobile has to a normal deploy** → [[mobile/13-release-and-distribution|release]].

## What to watch

- **Long lists.** Use `FlashList`; a plain `ScrollView` over hundreds of items will jank
- **Animations on the JS thread.** Use **Reanimated** so they run on the UI thread and survive JS being busy
- **Large images** — resize server-side; use `expo-image`
- **Dependency upgrades.** RN upgrades have a reputation, though Expo's managed workflow has substantially improved this
- **`console.log` in release builds** is a real performance cost
- **Platform differences still exist.** `Platform.select`, and **test both** — "write once, test twice" is the honest slogan
- **You still need native knowledge** for anything unusual. Budget for it

## Related
- [[frontend/frameworks/react/README|React]] — the model
- [[web3/frameworks/javascript/README|TypeScript patterns]] — the same discipline elsewhere
- [[mobile/14-native-vs-cross-platform|native vs cross-platform]] — when to choose this
- [[mobile/README|the mobile course]]
