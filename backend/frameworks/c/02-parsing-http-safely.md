# Parsing HTTP Safely

**[Advanced]** — Every byte of an HTTP request is attacker-controlled, and C gives you no bounds checking. This is where the CVEs come from.

## The threat model

An HTTP parser is the most exposed code you will ever write. Before authentication, before routing, before any of your logic runs, you are parsing bytes chosen by anyone on the internet.

In [[languages/04-c/README|C]] that means:

- **No bounds checking** — an unchecked index is a buffer overflow
- **No length on a string** — `char *` carries no size ([[languages/04-c/06-arrays-strings-and-decay|array decay]])
- **Integer overflow is [[languages/04-c/10-undefined-behaviour|undefined]]** — and a `Content-Length` you multiply is attacker-controlled
- **A stack buffer overflow can overwrite the return address**, which is arbitrary code execution → [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|Exploits]]

Every one of these has a CVE history in real servers.

## What a request looks like

```
GET /path?query=1 HTTP/1.1\r\n
Host: example.com\r\n
Content-Length: 42\r\n
\r\n
<body>
```

Simple to describe, and the specification has enough ambiguity that **disagreement between two parsers is itself a vulnerability** — see request smuggling below.

## The rules

### 1. Bound everything, before you parse it

```c
#define MAX_REQUEST_LINE  8192
#define MAX_HEADER_COUNT  100
#define MAX_HEADER_SIZE   8192
#define MAX_BODY_SIZE     (10 * 1024 * 1024)
#define MAX_URI_LENGTH    2048
```

An unbounded read is a denial of service: a client sending headers forever fills your heap. Enforce limits **as you read**, not after.

```c
if (c->in_len + n > MAX_HEADER_SIZE) { respond_431(c); return; }
```

### 2. Never `strcpy`, `strcat`, `sprintf`, or `gets`

```c
char path[256];
strcpy(path, request_path);        // ☠ buffer overflow, no error, no warning
```

```c
if (path_len >= sizeof buf) { respond_414(c); return; }
memcpy(buf, request_path, path_len);
buf[path_len] = '\0';
```

Or `snprintf`, which always terminates. **Never `strncpy`** — it doesn't NUL-terminate on truncation, which converts a bounded copy into an unbounded read. → [[languages/04-c/06-arrays-strings-and-decay|Arrays, Strings and Decay]]

### 3. Work with pointer + length, not NUL-terminated strings

```c
typedef struct { const char *p; size_t len; } str_t;
```

The request buffer is **not** NUL-terminated — it's whatever bytes arrived. Treating it as a C string means `strlen` walks off the end of your buffer. Carry the length explicitly, everywhere. This is what `std::string_view`, Go's slices and Rust's `&str` give you for free.

Use `memchr`, not `strchr`; `memcmp`, not `strcmp`.

### 4. Parse `Content-Length` defensively

```c
errno = 0;
char *end;
unsigned long long len = strtoull(value, &end, 10);
if (end == value || *end != '\0' || errno == ERANGE || len > MAX_BODY_SIZE) {
    respond_400(c);
    return;
}
```

Checks that matter: **digits were consumed**, **nothing trailing** (`"42abc"` must not parse as 42), **no overflow**, and **within your limit**.

`atoi` cannot report any of these — it returns 0 for `"banana"`. → [[languages/04-c/09-the-standard-library|The Standard Library]]

Reject a negative `Content-Length`, a duplicated `Content-Length` header, and any `Content-Length` alongside `Transfer-Encoding: chunked`. All three are smuggling vectors.

### 5. Watch every arithmetic operation on attacker input

```c
size_t total = header_len + body_len;             // may WRAP
char *buf = malloc(total);                         // tiny allocation
memcpy(buf, data, header_len + body_len);          // heap overflow
```

```c
if (body_len > SIZE_MAX - header_len) { respond_400(c); return; }
size_t total = header_len + body_len;
```

The integer-overflow-into-heap-overflow pattern is one of the most productive CVE shapes in existence. `calloc` checks its own multiplication; addition you must check yourself. → [[languages/04-c/04-types-and-integers|Types and Integers]]

### 6. Validate the path before it touches a filesystem

```c
if (strstr(path, "..")) { respond_400(c); return; }
```

**That check is insufficient**, which is the point. `..%2f`, `..%252f` (double-encoded), `..\\`, overlong UTF-8, and a NUL byte in the middle all bypass a naive substring test.

The correct approach: URL-decode **once**, reject any remaining `..` or NUL, resolve with `realpath()`, and verify the result is still under your document root:

```c
char resolved[PATH_MAX];
if (!realpath(candidate, resolved)) { respond_404(c); return; }
if (strncmp(resolved, docroot, docroot_len) != 0) { respond_403(c); return; }
```

Decoding twice is itself a vulnerability — it's how `%252e` becomes `.`. → [[cybersecurity/04-web-security/README|Web Security]]

### 7. Reject, don't normalise

When input is ambiguous, **return 400**. Servers that try to be helpful — accepting bare `LF` instead of `CRLF`, tolerating whitespace before a header colon, accepting duplicate headers — create the disagreement that makes request smuggling possible.

```
Content-Length: 10
Transfer-Encoding: chunked
```

If your front-end proxy honours one and your backend honours the other, an attacker can hide a second request inside the first — poisoning the connection for the *next* user. **Reject requests containing both.**

## Use a real parser

The honest recommendation: **do not write the parser you ship.**

| Parser | Character |
|---|---|
| **llhttp** | Node.js's parser. Battle-tested against the entire internet, MIT |
| **picohttpparser** | tiny, extremely fast, header-only |
| **http-parser** | llhttp's predecessor; deprecated, still everywhere |

```c
llhttp_settings_t settings;
llhttp_settings_init(&settings);
settings.on_url = on_url;
settings.on_header_field = on_header_field;
settings.on_message_complete = on_complete;

llhttp_t parser;
llhttp_init(&parser, HTTP_REQUEST, &settings);

enum llhttp_errno err = llhttp_execute(&parser, data, len);
if (err != HPE_OK) { respond_400(c); return; }
```

These are **incremental** — feed them whatever bytes arrived, they call your callbacks when a complete element is parsed, and they hold state across calls. That's exactly what an [[backend/frameworks/c/01-the-accept-loop-and-event-loops|event loop]] needs.

Note the callback data is **not NUL-terminated** and points into your buffer, which may be reused on the next read. Copy anything you keep.

Write your own to learn — see the [[BUILD-PLAN|build-your-own-shit]] HTTP server guide. Ship llhttp.

## Fuzz it

If you do write a parser, fuzzing is not optional:

```c
// fuzz_target.c
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    parser_t p;
    parser_init(&p);
    parser_execute(&p, (const char *)data, size);   // ASan/UBSan catch what it triggers
    return 0;
}
```

```bash
clang -fsanitize=fuzzer,address,undefined fuzz_target.c parser.c -o fuzzer
./fuzzer corpus/ -max_total_time=300
```

**Fuzzing plus sanitizers finds the bugs that testing doesn't.** It's how OpenSSL, curl and SQLite stay alive, and OSS-Fuzz runs it continuously against hundreds of projects. A parser that hasn't been fuzzed has bugs — the only question is who finds them. → [[languages/04-c/13-debugging-and-tooling|Debugging and Tooling]]

## Hardening the process

Defence in depth, for when the parser is wrong anyway:

```bash
gcc -D_FORTIFY_SOURCE=2 -O2 \
    -fstack-protector-strong \      # canary detects stack smashing
    -fPIE -pie \                    # ASLR for the executable
    -Wl,-z,relro,-z,now \           # read-only GOT — blocks GOT overwrite
    -fsanitize=address              # dev/CI only
```

And at runtime: drop privileges after binding port 80 (`setuid` to a non-root user), `chroot` or a mount namespace, and `seccomp` to restrict syscalls. nginx and Kore both do privilege separation by design.

**Never run a C web server as root** beyond the `bind()` call.

## The summary

> Every byte is hostile. Bound everything. Carry lengths, never assume NUL. Check every arithmetic operation. Reject ambiguity rather than normalising it. Use llhttp. Fuzz what you write. Compile with hardening. Drop privileges.

That list is the price of writing HTTP in C, and it's the reason the [[backend/frameworks/c/README|honest recommendation]] for a new service is a memory-safe language — where most of this is handled by the type system rather than by discipline.

---

## Related
- [[backend/frameworks/c/01-the-accept-loop-and-event-loops|The Accept Loop and Event Loops]] — where bytes arrive
- [[backend/frameworks/c/03-the-c-frameworks|The C Frameworks]] — libraries that solved this already
- [[languages/04-c/06-arrays-strings-and-decay|C: Arrays, Strings and Decay]] · [[languages/04-c/10-undefined-behaviour|Undefined Behaviour]]
- [[cybersecurity/04-web-security/README|Web Security]] · [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|Exploits]]
- [[backend/frameworks/c/README|C backends]]
