# Coroutines and Flow

**[Advanced]** — Kotlin's concurrency model, and the single most important thing to learn in the language.

## The idea

**A coroutine is a computation that can suspend without blocking a thread.**

```kotlin
suspend fun loadProfile(id: String): Profile {
    val user = api.user(id)          // suspends. The THREAD is released.
    val posts = api.posts(id)
    return Profile(user, posts)
}
```

**Sequential-looking code that doesn't block.** No callbacks, no `CompletableFuture` chains. `suspend` marks a function that may suspend, and it can only be called from another suspending function or a coroutine.

**Thousands of coroutines can run on a handful of threads**, because a suspended coroutine isn't holding one.

## Structured concurrency — the guarantee

**Every coroutine has a scope, and children cannot outlive the parent.**

```kotlin
class FeedViewModel : ViewModel() {
    fun load() {
        viewModelScope.launch {          // cancelled when the ViewModel clears
            val items = repo.fetch()
            _state.value = Success(items)
        }
    }
}
```

**`viewModelScope` cancels everything when the screen goes away.** That's the guarantee that makes this different from raw threads: **no leaked work, no callbacks firing into a dead screen** → [[mobile/03-the-app-lifecycle|the lifecycle]].

**The scopes you'll use:** `viewModelScope`, `lifecycleScope`, `coroutineScope { }` (inside a suspend function), and `GlobalScope` — **which you should essentially never use**, because it has no lifecycle and leaks by design.

## Parallel work

```kotlin
// Sequential — waits for user before starting posts
val user = api.user(id)
val posts = api.posts(id)

// Parallel
coroutineScope {
    val user = async { api.user(id) }
    val posts = async { api.posts(id) }
    Profile(user.await(), posts.await())
}
```

**`launch` fires and forgets; `async` returns a `Deferred` you `await`.** Writing sequential `await`s where the work is independent is the most common performance mistake.

## Dispatchers

```kotlin
withContext(Dispatchers.IO)      { database.query() }   // blocking I/O
withContext(Dispatchers.Default) { heavyComputation() } // CPU work
withContext(Dispatchers.Main)    { updateUi() }         // Android UI thread
```

**A suspending function should be safe to call from any dispatcher** — it should switch internally rather than requiring the caller to know. That's the "main-safety" convention, and Retrofit and Room both follow it, so you rarely need `withContext(Dispatchers.IO)` around them.

## Cancellation is cooperative

```kotlin
suspend fun process(items: List<Item>) {
    for (item in items) {
        ensureActive()            // throws CancellationException if cancelled
        heavyWork(item)
    }
}
```

**Nothing forcibly stops a coroutine.** Suspending functions in the standard library check for cancellation, so an `await`-heavy loop is fine — **but a long CPU-bound loop with no suspension points ignores cancellation completely.**

**Never catch `CancellationException` and swallow it:**

```kotlin
try { work() }
catch (e: CancellationException) { throw e }    // ← rethrow, ALWAYS
catch (e: Exception) { handle(e) }
```

**A generic `catch (e: Exception)` swallows cancellation** and breaks structured concurrency. This is a real and common bug.

## Flow

**A cold asynchronous stream** — the coroutine equivalent of a sequence.

```kotlin
fun observeUsers(): Flow<List<User>> = flow {
    while (true) {
        emit(api.users())
        delay(30_000)
    }
}

viewModelScope.launch {
    repo.observeUsers()
        .map { it.filter(User::isActive) }
        .catch { emit(emptyList()) }
        .collect { _state.value = it }
}
```

**Cold** means nothing runs until you `collect`, and each collector gets its own execution.

**`StateFlow` and `SharedFlow` are hot** — they exist independently of collectors:

```kotlin
private val _state = MutableStateFlow<UiState>(Loading)
val state: StateFlow<UiState> = _state.asStateFlow()      // always has a current value
```

**`StateFlow` for state** (always has a value, conflates, deduplicates equal values). **`SharedFlow` for events** (no initial value, doesn't deduplicate) → [[mobile/05-state-and-architecture|architecture]].

**The Android idiom:**

```kotlin
val uiState: StateFlow<UiState> = repo.observeItems()
    .map { UiState.Success(it) }
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), UiState.Loading)
```

**The 5-second grace period keeps the upstream alive through a configuration change** instead of restarting the query on every rotation.

**And in Compose: `collectAsStateWithLifecycle()`, not `collectAsState()`** — the latter keeps collecting while backgrounded, wasting work and battery. **This is one of the most common Android mistakes.**

## Exceptions

**`launch` propagates exceptions up and cancels the scope; `async` holds them until you `await`.**

```kotlin
supervisorScope {
    launch { mayFail() }     // failure does NOT cancel siblings
    launch { alsoRuns() }
}
```

**`coroutineScope` cancels all children if one fails; `supervisorScope` doesn't.** Use supervisor when children are independent.

## Key insight

**Coroutines make asynchronous code look sequential, and structured concurrency makes it impossible to leak** — a scope that dies takes its work with it. The two things that bite are **swallowing `CancellationException` in a generic catch**, and **CPU-bound loops with no suspension points that ignore cancellation entirely.** Get those right and the model mostly disappears.

## Related
- [[languages/09-kotlin/04-functions-and-idioms|functions]] — `inline` and suspending lambdas
- [[languages/08-swift/10-concurrency-and-actors|Swift concurrency]] — the same problem, similar shape
- [[mobile/frameworks/android/README|Android]] — where this is used daily
- [[languages/01-java/README|Java concurrency]] — what this replaces
