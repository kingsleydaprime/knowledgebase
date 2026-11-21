---
id: 610c9bd1-c5d6-4fb6-9359-5a2af81eac08
---

# Coroutines and Flow

## The idea
<!-- bite: 5415b643-5eab-4713-a85a-8f7c4b7adebb -->

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
<!-- bite: 7df0b81c-da6f-4665-9d6f-fc44ff5b0606 -->

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
<!-- bite: 15799b89-407a-43f5-bd09-dabbf0f6fbb6 -->

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
<!-- bite: 2d0d2e55-36bb-4010-b266-d6d85cf41d4e -->

```kotlin
withContext(Dispatchers.IO)      { database.query() }   // blocking I/O
withContext(Dispatchers.Default) { heavyComputation() } // CPU work
withContext(Dispatchers.Main)    { updateUi() }         // Android UI thread
```

**A suspending function should be safe to call from any dispatcher** — it should switch internally rather than requiring the caller to know. That's the "main-safety" convention, and Retrofit and Room both follow it, so you rarely need `withContext(Dispatchers.IO)` around them.

## Cancellation is cooperative
<!-- bite: ed13d0f3-2897-46e1-8758-da4aa8a14306 -->

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
<!-- bite: edb7431f-e1a2-47f7-9961-4b53d8727c3c -->

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
<!-- bite: 9b8f9aa6-177f-40b9-a657-61d74471dcbd -->

**`launch` propagates exceptions up and cancels the scope; `async` holds them until you `await`.**

```kotlin
supervisorScope {
    launch { mayFail() }     // failure does NOT cancel siblings
    launch { alsoRuns() }
}
```

**`coroutineScope` cancels all children if one fails; `supervisorScope` doesn't.** Use supervisor when children are independent.

## Key insight
<!-- bite: 65ffbffe-1e01-428d-a865-f19b8eee28b3 -->

**Coroutines make asynchronous code look sequential, and structured concurrency makes it impossible to leak** — a scope that dies takes its work with it. The two things that bite are **swallowing `CancellationException` in a generic catch**, and **CPU-bound loops with no suspension points that ignore cancellation entirely.** Get those right and the model mostly disappears.

## Related
<!-- bite: 24c0685a-fde1-44f2-a7c5-c8ed5fc15cbc -->
- [[languages/09-kotlin/04-functions-and-idioms|functions]] — `inline` and suspending lambdas
- [[languages/08-swift/10-concurrency-and-actors|Swift concurrency]] — the same problem, similar shape
- [[mobile/frameworks/android/index|Android]] — where this is used daily
- [[languages/01-java/index|Java concurrency]] — what this replaces

## About this lesson
<!-- bite: c0b53b8a-bbd9-4cbc-98d0-a0c155ddb644 -->

**Level:** Advanced. **Covers:** Kotlin's concurrency model, and the single most important thing to learn in the language.
