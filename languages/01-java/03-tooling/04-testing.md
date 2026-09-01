# Testing

**Source:** **[reference — this is a real gap, not just an unexercised one]**. Neither project shipped a test suite — which is exactly the kind of thing the original knowledgebase critique meant by "signals self-direction, not engineering ability." Automated testing is one of the clearest engineering-maturity signals there is, so this file covers it properly, and the honest next step is to actually write tests against the two Java projects (and the [[languages/01-java/02-jvm-and-concurrency/exercises/README|concurrency exercises]] already ship with a runnable harness as a first move in that direction).

## The testing pyramid

- **Unit tests** — one class/method in isolation, dependencies mocked. Fast (milliseconds), numerous, the base of the pyramid.
- **Integration tests** — several components together, real DB/broker (often via containers). Slower, fewer.
- **End-to-end tests** — the whole system through its public interface. Slowest, fewest.

Keep the base wide and the top narrow: most bugs are cheapest to catch as unit tests.

## JUnit 5 — the standard framework

```java
class SubscriptionServiceTest {

    @Test
    void rejectsBlankMerchantId() {
        var service = new SubscriptionService(new InMemoryStore(), stubCallbacks());
        var result = service.subscribe(blankMerchantRequest());
        assertEquals("100", result.get("responseCode"));
    }

    @ParameterizedTest
    @ValueSource(strings = {"", "  ", "\t"})
    void treatsAllBlankVariantsAsInvalid(String merchantId) {   // one test, many inputs
        assertTrue(new Validator().isBlank(merchantId));
    }

    @BeforeEach void setUp() { /* runs before every test */ }
}
```

Core pieces: `@Test` marks a test; `@BeforeEach`/`@AfterEach` (per test) and `@BeforeAll`/`@AfterAll` (once) manage fixtures; `@ParameterizedTest` runs the same logic over many inputs; `@DisplayName` gives readable names. Assertions live in `org.junit.jupiter.api.Assertions` (`assertEquals`, `assertTrue`, `assertThrows`, `assertAll`) — or use **AssertJ** for fluent, readable chains (`assertThat(result).containsEntry("responseCode", "100")`).

**Structure every test as Arrange–Act–Assert** (given/when/then): set up state, perform the one action under test, assert the outcome. One logical assertion per test; the test name states the behavior being verified.

## Mockito — isolating the unit

Constructor injection ([[languages/01-java/03-tooling/02-dependency-injection|Dependency Injection]]) is what makes this possible: you inject *test doubles* instead of real collaborators. A **mock** is a stand-in whose behavior you program and whose interactions you verify:

```java
@ExtendWith(MockitoExtension.class)
class CallbackServiceTest {
    @Mock Store store;                       // a fake Store
    @InjectMocks CallbackService service;    // real service, mocks injected into it

    @Test
    void resolvesCallbackUrlFromProvision() {
        when(store.getProvision("M1", "P1"))                     // stub: program the mock's response
            .thenReturn(new ProvisionRecord("https://hook.url"));

        String url = service.resolveCallbackUrl("M1", "P1", "fallback");

        assertEquals("https://hook.url", url);
        verify(store).getProvision("M1", "P1");                  // verify the interaction happened
    }
}
```

`when(...).thenReturn(...)` stubs a return; `verify(...)` asserts a call was made; `any()`/`eq()` are argument matchers; `ArgumentCaptor` captures what a mock was called with. The discipline: **mock the boundaries you don't own** (the DB, the HTTP client), test the real logic in between. Over-mocking (mocking the class under test's own internals) tests the mocks, not the code.

## Integration testing

For anything that must exercise a real database or broker, mocks lie — you need the real thing. **Testcontainers** spins up a throwaway Docker container (a real MySQL, a real RabbitMQ) per test run, so integration tests hit genuine infrastructure and clean up after themselves:

```java
@Testcontainers
class TransactionRepositoryIT {
    @Container static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8");
    // point the repository at mysql.getJdbcUrl(), run real inserts, assert on real rows
}
```

Spring Boot's `@SpringBootTest` boots the actual application context for full-slice tests; `@DataJpaTest`/`@WebMvcTest` boot only one slice (persistence, or the web layer with `MockMvc`) for faster focused tests. This is where the JDBC pipeline and the Spring endpoints ([[languages/01-java/04-persistence/01-jdbc-and-data-modeling|JDBC]], [[backend/frameworks/java/01-spring-boot|Spring Boot]]) *should* be tested — against a real containerized MySQL, not a mock.

## The wider landscape (roadmap.sh breadth)

| Tool | Niche |
|---|---|
| **JUnit 5** | the default unit/integration framework |
| **Mockito** | mocking/stubbing collaborators |
| **AssertJ** | fluent assertions (pairs with JUnit) |
| **TestNG** | JUnit alternative, richer suite/grouping config; common in older/enterprise suites |
| **Cucumber-JVM** | BDD — tests written as `Given/When/Then` plain-language scenarios, mapped to step code; for business-readable acceptance tests |
| **REST Assured** | fluent HTTP API testing (`given().when().get().then().statusCode(200)`) — ideal for the sandbox's endpoints |
| **JMeter** | load/performance testing — throughput and latency under concurrent load, not correctness |
| **JMH** | the JVM microbenchmark harness — the *only* correct way to benchmark Java, because it handles JIT warmup and dead-code elimination that naive `System.nanoTime()` benchmarks get wrong ([[languages/01-java/02-jvm-and-concurrency/01-jvm-internals\|JVM Internals]]) |

## Related
- [[languages/01-java/03-tooling/02-dependency-injection|Dependency Injection]] — what makes a class mockable in the first place
- [[languages/01-java/02-jvm-and-concurrency/exercises/README|Concurrency Exercises]] — a runnable test harness you implement against, the first real reps
- [[backend/frameworks/java/01-spring-boot|Spring Boot]] — `@SpringBootTest` slices for the web layer
