# Android

**Kotlin + Jetpack Compose.** The language is [[languages/09-kotlin/README|its own course]]; this is the platform.

## The toolchain

**Android Studio**, on any OS — which is why Android is the accessible starting point if you don't own a Mac.

```bash
./gradlew assembleDebug
./gradlew testDebugUnitTest
adb devices
adb shell am kill com.example.app        # simulate process death — DO THIS
```

**Gradle** is the build system, and it is the most-complained-about part of Android development. **Use version catalogs** (`libs.versions.toml`) to keep dependencies manageable.

## Jetpack — what "learning Android" actually means now

| Library | For |
|---|---|
| **Compose** | UI |
| **ViewModel** | State surviving configuration changes |
| **Room** | SQLite with compile-time-checked queries |
| **Navigation** | The back stack, type-safe routes |
| **WorkManager** | Deferrable background work |
| **DataStore** | Preferences (replaces SharedPreferences) |
| **Hilt** | Dependency injection |
| **Paging** | Large lists, incrementally loaded |

## Compose

```kotlin
@Composable
fun FeedScreen(vm: FeedViewModel = hiltViewModel()) {
    val state by vm.uiState.collectAsStateWithLifecycle()

    when (val s = state) {
        Loading      -> CircularProgressIndicator()
        is Error     -> ErrorView(s.message, onRetry = vm::retry)
        is Success   -> LazyColumn {
            items(s.items, key = { it.id }) { ItemRow(it) }   // ← stable key
        }
    }
}
```

**`collectAsStateWithLifecycle()`, not `collectAsState()`.** The latter keeps collecting while the app is backgrounded, wasting work and battery. This is a very common mistake.

**The ViewModel:**

```kotlin
@HiltViewModel
class FeedViewModel @Inject constructor(
    private val repo: FeedRepository,
    savedState: SavedStateHandle,        // ← survives PROCESS DEATH, unlike the ViewModel
) : ViewModel() {
    val uiState: StateFlow<UiState> = repo.observeItems()
        .map { UiState.Success(it) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), UiState.Loading)
}
```

**`ViewModel` survives rotation; `SavedStateHandle` survives process death.** Different problems, and you need both → [[mobile/03-the-app-lifecycle|the lifecycle]].

## Coroutines and Flow

- **`viewModelScope`** cancels automatically when the ViewModel clears
- **`Flow`** for streams; **`StateFlow`** for state that always has a current value
- **`SharingStarted.WhileSubscribed(5_000)`** — the 5-second grace period keeps the flow alive through a rotation instead of restarting the query
- **One-shot events** (navigation, snackbars) belong in a `Channel`, not in state → [[mobile/05-state-and-architecture|architecture]]

## The Android-specific taxes

**Manufacturer battery killers.** Xiaomi, Huawei, Oppo, Vivo, OnePlus and Samsung kill background work in undocumented ways. [dontkillmyapp.com](https://dontkillmyapp.com) catalogues it. **Never depend on background execution for correctness** → [[mobile/10-background-work-and-push|background work]].

**Fragmentation.** Test on a low-end device and an old OS version, not just your phone.

**Configuration changes recreate the Activity** — rotation, dark mode, language, split-screen. Multiple times a day, in normal use.

**Exported components.** `android:exported="false"` unless you genuinely mean otherwise → [[mobile/12-security-on-device|security]].

**Background restrictions tighten every release.** Each Android version adds limits, and `targetSdk` bumps are mandatory for Play. **Read the behaviour-changes page for every version you target** — this is where "it worked before the update" bugs come from.

## Release specifics

- **App Bundles**, not APKs — the store ships only what each device needs → [[mobile/11-performance-and-battery|app size]]
- **Play App Signing.** Turn it on. **Losing your signing key without it means you can never update the app again**
- **Staged rollout with the ability to halt** → [[mobile/13-release-and-distribution|release]]
- **Android Vitals** — crash-free rate and **ANRs**, both of which affect ranking
- **R8** for minification and shrinking

## Related
- [[languages/09-kotlin/README|Kotlin]] — the language
- [[mobile/README|the mobile course]] · [[mobile/frameworks/README|frameworks]]
- [[languages/01-java/README|Java]] — the JVM foundations still apply
