# Core APIs

**Source:** the date/time↔JDBC bridging and the quoted-CSV regex/parsing are real project code; the rest (NIO, networking, modules, annotations, cryptography beyond SHA-256) is **[reference]** — roadmap.sh Java nodes the projects didn't exercise, covered here as an orientation map rather than deep dives, with pointers to where the applied versions live.

## Date and Time (`java.time`)

The Java 8 `java.time` API replaced the broken, mutable, not-thread-safe legacy `Date`/`Calendar`. The core types are **immutable** and each models one concept precisely:

| Type | Represents |
|---|---|
| `LocalDate` | a date, no time, no zone (`2026-07-30`) |
| `LocalTime` | a time of day, no date |
| `LocalDateTime` | date + time, **no** zone |
| `ZonedDateTime` | date + time + zone — the one to use for absolute instants across zones |
| `Instant` | a point on the UTC timeline (epoch-based) |
| `Duration` / `Period` | an amount of time / calendar amount |

```java
LocalDate start = LocalDate.parse("2026-07-30");        // ISO-8601 by default
if (!end.isAfter(start)) throw new IllegalArgumentException("end must be after start");
```

**The JDBC bridge** is real project friction: `java.time` postdates JDBC's `java.sql.Timestamp` by two decades, so you convert at the boundary:

```java
stmt.setTimestamp(5, Timestamp.valueOf(localDateTime));               // write
LocalDateTime dt = resultSet.getTimestamp("col").toLocalDateTime();  // read
```

`Timestamp.valueOf` treats the value as local (no zone) — fine only when app and DB share a timezone; otherwise go through `Instant`/`ZonedDateTime`.

At the beginner level the everyday surface is `now()`, the accessors, comparison, and formatting — the pieces the alarm-clock project leans on:

```java
LocalDate.now();                    // today
LocalTime now = LocalTime.now();    // current time of day
now.getHour(); now.getMinute(); now.getSecond();      // component accessors
LocalTime alarm = LocalTime.parse("08:00");
now.isBefore(alarm);                // true — also isAfter(); the basis for a "wait until" loop

// Formatting — turn a temporal into a string (and parse back)
String pretty = now.format(DateTimeFormatter.ofPattern("HH:mm:ss"));   // "07:26:41"
```

Because the types are immutable, "modifying" returns a new value: `now.plusHours(1)`, `today.plusDays(7)` — the original is untouched.

## Regular expressions

`Pattern` compiles a regex; `Matcher` runs it. Compile once and reuse for anything hot — compilation isn't free:

```java
private static final Pattern DUP_ID =
        Pattern.compile("Duplicate entry '(.+?)' for key 'PRIMARY'");   // compiled once

Matcher m = DUP_ID.matcher(sqlErrorMessage);
if (m.find()) String id = m.group(1);   // extract the colliding key from a MySQL error
```

That's real code from the pipeline's PK-collision handler. `String.split`, `matches`, and `replaceAll` all take regexes — which is exactly the trap in the CSV parser ([[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing]]): `split(",")` breaks on commas inside quoted fields, so a quote-aware parser is needed instead.

## IO and NIO

Two generations of file/stream APIs:

- **Classic IO** (`java.io`) — stream-based: `InputStream`/`OutputStream` (bytes), `Reader`/`Writer` (chars), wrapped in `BufferedReader`/`BufferedWriter` for efficiency. The pipeline streams a 1.5GB CSV line-by-line through a `BufferedReader` — flat memory regardless of file size (see [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing]]).
- **NIO.2** (`java.nio.file`) — the modern path/file API: `Path`, `Files.readAllLines`, `Files.lines` (a lazy `Stream<String>`), `Files.newBufferedReader`, `Files.deleteIfExists`. Prefer it for new code.

```java
try (BufferedReader r = Files.newBufferedReader(Path.of(filePath))) {
    r.lines().forEach(this::process);   // streaming — never loads the whole file
}
```

Always wrap resources in try-with-resources ([[languages/01-java/01-language/06-exceptions|Exceptions]]).

At the beginner level, the classic pair is `FileWriter` to write and `BufferedReader` + `FileReader` to read line-by-line. File access can fail, so the calls are checked (`IOException`) and belong in try-with-resources:

```java
// Write — FileWriter creates/overwrites (new FileWriter(path, true) appends instead)
try (FileWriter writer = new FileWriter("output.txt")) {
    writer.write("Hello\n");
    writer.write("World\n");
}

// Read — BufferedReader.readLine() returns null at end-of-file, the natural loop sentinel
try (BufferedReader reader = new BufferedReader(new FileReader("words.txt"))) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
}
```

Reading a word list from a file this way — then picking one at random — is exactly how the beginner **hangman** project loads its answers instead of hard-coding them.

## Networking

`java.net` for sockets (`Socket`, `ServerSocket`) and the modern `java.net.http.HttpClient` (Java 11+) for HTTP:

```java
HttpClient client = HttpClient.newHttpClient();
HttpResponse<String> resp = client.send(
        HttpRequest.newBuilder(URI.create(url)).GET().build(),
        HttpResponse.BodyHandlers.ofString());
```

In a Spring app you'd typically use `RestTemplate`/`WebClient` instead ([[languages/01-java/05-web-and-api/03-api-design-and-documentation|API Design]]) — the payment sandbox fires callbacks with `RestTemplate`. Raw sockets matter mostly for low-level/latency-sensitive work, which is where the JVM-internals and concurrency material earns its keep.

## Annotations

Metadata attached to code, readable at compile time or runtime. You *consume* them everywhere (`@Override`, `@FunctionalInterface`, Spring's `@Service`, JPA's `@Entity`); occasionally you *define* one:

```java
@Retention(RetentionPolicy.RUNTIME)   // available via reflection at runtime
@Target(ElementType.METHOD)
public @interface RateLimited { int perSecond() default 10; }
```

`@Retention` controls whether the annotation survives to runtime (`RUNTIME`) or is discarded (`SOURCE`/`CLASS`); `@Target` restricts where it can be applied. Frameworks read runtime-retained annotations via **reflection** to wire behavior — how Spring finds `@Service` beans and springdoc builds the OpenAPI spec ([[languages/01-java/05-web-and-api/03-api-design-and-documentation|API Design]]). Reflection also underlies Lombok's compile-time processing and mocking libraries ([[languages/01-java/03-tooling/04-testing|Testing]]).

## Modules (JPMS)

The Java Platform Module System (Java 9+) adds a layer above packages: a `module-info.java` declares what a module `exports` and what it `requires`, giving strong encapsulation across jar boundaries:

```java
module com.itc.pipeline {
    requires java.sql;
    exports com.itc.pipeline.api;   // only this package is visible to other modules
}
```

Most application code (including both projects) runs fine on the unnamed classpath without modules; JPMS matters most for large libraries and for building slim custom runtimes with `jlink`. **[reference — not used in either project]**

## Cryptography

`java.security` / `javax.crypto`: `MessageDigest` (hashing), `Cipher` (encryption), `SecureRandom` (CSPRNG), `KeyGenerator`. The pipeline uses two of these for real:

```java
MessageDigest md = MessageDigest.getInstance("SHA-256");
String hash = HexFormat.of().formatHex(md.digest(input.getBytes(StandardCharsets.UTF_8)));   // idempotency key
SecureRandom random = new SecureRandom();   // unpredictable IDs — never plain Random for anything security-adjacent
```

SHA-256 as an idempotency fingerprint is in [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation]]; `SecureRandom` for ID generation is there too. For actual encryption, prefer vetted higher-level libraries over hand-assembling `Cipher` — the deeper cryptography material lives in [[cybersecurity/05-cryptography/README|cybersecurity/cryptography]].

## Playing audio (`javax.sound.sampled`)

The built-in sound API plays uncompressed audio (WAV/AIFF — **not** MP3, which needs an external library or a conversion to WAV). Three types cooperate: `AudioSystem` (the factory), `AudioInputStream` (the decoded stream), and `Clip` (an in-memory player you can `start`/`stop`/`close` and seek). Every step throws a checked exception, so the whole thing is a try-with-resources with several `catch` arms:

```java
try (AudioInputStream audio = AudioSystem.getAudioInputStream(new File("song.wav"))) {
    Clip clip = AudioSystem.getClip();
    clip.open(audio);
    clip.start();                                    // non-blocking — returns immediately
    clip.setMicrosecondPosition(0);                  // seek to start (a "reset")
    // ... keep the program alive while it plays (below), then clip.stop() / clip.close()
} catch (UnsupportedAudioFileException e) {           // wrong/compressed format
    System.out.println("Audio format not supported");
} catch (LineUnavailableException e) {                // the audio line is busy
    System.out.println("Audio line unavailable");
} catch (IOException e) {                             // catch-all safety net, listed last
    System.out.println("Error reading audio file");
}
```

The catch order matters: **most-specific first, the broad `IOException` last** ([[languages/01-java/01-language/06-exceptions|Exceptions]]). One beginner gotcha: `clip.start()` returns immediately, so a program that starts a clip and then ends will cut the sound off — you must keep the main thread alive (a blocking `scanner.nextLine()`, a `Thread.sleep`, or a loop on `clip.isRunning()`). This is the whole **audio player** project: a menu loop reading `p`/`s`/`r`/`q` and calling `clip.start()` / `clip.stop()` / `setMicrosecondPosition(0)` / `clip.close()`. For a simple system beep with no file at all: `Toolkit.getDefaultToolkit().beep();`.

## Scheduling: `java.util.Timer` and `TimerTask`

`Timer` runs a `TimerTask` on a background thread — once after a delay, or repeatedly at a fixed rate. `TimerTask` is abstract with one method to fill in, `run()`, which is the textbook use for an **anonymous class** ([[languages/01-java/01-language/05-functional-programming|Functional Programming]]):

```java
Timer timer = new Timer();
int[] count = { 10 };                                // boxed in an array so the inner class can mutate it
timer.scheduleAtFixedRate(new TimerTask() {
    @Override public void run() {
        System.out.println(count[0]);
        if (count[0]-- <= 0) {
            System.out.println("Happy New Year!");
            timer.cancel();                          // stop the timer, or it repeats forever
        }
    }
}, 0, 1000);                                          // initial delay 0ms, then every 1000ms
```

That's the **countdown timer** project. `schedule(task, delay)` fires once; `scheduleAtFixedRate(task, delay, period)` repeats — and `timer.cancel()` is mandatory or the JVM keeps ticking. (For richer scheduling in real apps, use `ScheduledExecutorService` from [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]] or Spring's `@Scheduled` from [[languages/01-java/05-web-and-api/01-spring-boot|Spring Boot]].)

## Capstone project: the alarm clock

The final beginner project ties several of these APIs together — `LocalTime`, threading, and audio. An `AlarmClock` **implements `Runnable`** so it can run on its own thread; its `run()` polls `LocalTime.now()` once a second until the alarm time, then plays a WAV `Clip`:

```java
class AlarmClock implements Runnable {
    private final LocalTime alarmTime;
    private final String filePath;
    AlarmClock(LocalTime alarmTime, String filePath) {
        this.alarmTime = alarmTime;
        this.filePath = filePath;
    }
    @Override public void run() {
        while (LocalTime.now().isBefore(alarmTime)) {
            LocalTime now = LocalTime.now();
            System.out.printf("\r%02d:%02d:%02d", now.getHour(), now.getMinute(), now.getSecond());
            try { Thread.sleep(1000); }                       // wait a second, then re-check
            catch (InterruptedException e) { System.out.println("Interrupted"); }
        }
        System.out.println("\nAlarm!");
        playSound(filePath);                                  // the Clip code from the audio section
    }
    private void playSound(String path) { /* AudioSystem/Clip try-with-resources */ }
}

// In main:
Thread alarmThread = new Thread(new AlarmClock(LocalTime.parse("08:00"), "alarm.wav"));
alarmThread.start();                                          // runs run() off the main thread
```

Two details worth lifting out: `printf("\r...")` uses a **carriage return** to redraw the clock in place instead of scrolling, and running the alarm on a separate `Thread` keeps the main thread free to read a "press enter to stop" line — the same `start()`-not-`run()` rule from [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Concurrency]].

## Related
- [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — streaming IO and the CSV/regex parsing in anger
- [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation & Idempotency]] — `MessageDigest` and `SecureRandom` applied
- [[cybersecurity/05-cryptography/README|Cryptography (cybersecurity)]] — the crypto primitives in depth
