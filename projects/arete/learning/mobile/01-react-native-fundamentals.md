# Arete Mobile — React Native Fundamentals

Split out from the original single-file `mobile-learning.md` (Expo SDK 54 + React Native). See
also `02-navigation-and-state.md`, `03-api-layer.md`, `04-ui-patterns-from-arete-screens.md`,
`05-push-notifications-and-advanced-topics.md`, `06-the-home-trail-case-study.md`, and
`07-study-path.md`.

---

# Mobile Engineering — Beginner to Advanced
### Everything used in the Arete mobile app (Expo SDK 54 + React Native), and why

---

---

## Part 1 — Absolute Beginner

### What React Native actually is

React Native (RN) lets you write UI in JavaScript/TypeScript, but it does **not** render HTML in a webview. Your `<View>` becomes a real Android `ViewGroup` / iOS `UIView`. That's why RN apps feel native — they are native views, driven by JS.

**Expo** is a toolchain on top of RN: it gives you the build system (EAS), a standard library of native modules (`expo-haptics`, `expo-notifications`, `expo-router`), and removes the need to touch Xcode/Android Studio for most work.

### The three primitives you'll use 95% of the time

```tsx
import { View, Text, StyleSheet } from 'react-native';

export default function Hello() {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>ARETE</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { padding: 16, backgroundColor: '#12121A', borderRadius: 8 },
  title: { color: '#FFF', fontSize: 20, fontWeight: '800' },
});
```

Key differences from web:
- There is no `div`/`span`/`p`. `View` = container, `Text` = ALL text (text outside `<Text>` crashes), `Image`, `ScrollView`, `TextInput`, `TouchableOpacity` (a pressable).
- Styles are JS objects, not CSS. No cascading, no classes, no units (numbers are density-independent pixels).
- **Everything is flexbox by default**, and `flexDirection` defaults to `column` (web defaults to `row`).

### Flexbox mental model (used everywhere in Arete)

```tsx
// A row with an icon left, text filling the middle, button right:
<View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
  <Text>🔥</Text>
  <View style={{ flex: 1 }}>            {/* flex: 1 = "take remaining space" */}
    <Text>Spiritual</Text>
  </View>
  <TouchableOpacity>...</TouchableOpacity>
</View>
```

This exact pattern is the `shieldRow` in `streaks.tsx`. Learn `flexDirection`, `alignItems` (cross-axis), `justifyContent` (main axis), `flex: 1`, and `gap` — that's 90% of layout.

### State and effects — the two hooks that run everything

```tsx
const [count, setCount] = useState(0);        // component-local state

useEffect(() => {
  fetchData();                                 // runs after mount
  return () => cleanup();                      // runs on unmount
}, []);                                        // [] = run once
```

Rules that save hours of debugging:
- State updates are async — never read `count` right after `setCount(count + 1)`. Use the function form: `setCount(c => c + 1)` (see `setTick((t) => t + 1)` in the quest timer).
- The dependency array decides when an effect re-runs. `[]` = mount only. `[activeTab]` = whenever `activeTab` changes (this is how the HISTORY tab lazy-loads in `quests.tsx`).

---

