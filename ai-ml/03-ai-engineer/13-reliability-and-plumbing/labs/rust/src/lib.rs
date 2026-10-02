//! Retry, timeout, circuit breaker, fallback and token bucket around an async model call.
//! The same behaviour, and the same numbers, as the TypeScript lab.
use std::future::Future;
use std::pin::Pin;
use std::sync::Mutex;
use std::time::{Duration, SystemTime};
use tokio::time::{Instant, sleep};

/// Every way a call can fail. A `match` on it must cover every variant, so adding one
/// forces a decision about whether it's retryable.
#[derive(Debug, Clone, PartialEq)]
pub enum CallError {
    Status {
        status: u16,
        retry_after: Option<Duration>,
    },
    Timeout,    // our own deadline for one attempt
    Connection, // no response at all
    CircuitOpen,
    AllFailed(Vec<CallError>),
}

impl CallError {
    pub fn status(status: u16) -> Self {
        CallError::Status {
            status,
            retry_after: None,
        }
    }

    pub fn is_retryable(&self) -> bool {
        match self {
            CallError::Status { status, .. } => matches!(status, 408 | 429 | 500..),
            CallError::Timeout | CallError::Connection => true,
            CallError::CircuitOpen | CallError::AllFailed(_) => false,
        }
    }

    fn describe(&self) -> String {
        match self {
            CallError::Status { status, .. } => format!("HTTP {status}"),
            CallError::CircuitOpen => "CircuitOpenError".into(),
            other => format!("{other:?}"),
        }
    }
}

/// Seconds or an HTTP date, as a wait.
pub fn parse_retry_after(header: &str, now: SystemTime) -> Option<Duration> {
    let header = header.trim();
    if let Ok(seconds) = header.parse::<f64>() {
        return Some(Duration::from_secs_f64(seconds.max(0.0)));
    }
    let date = httpdate::parse_http_date(header).ok()?;
    Some(date.duration_since(now).unwrap_or(Duration::ZERO))
}

/// Full jitter: a random wait between 0 and min(cap, base × 2^(attempt − 1)), in whole milliseconds.
pub fn backoff(attempt: u32, base: Duration, cap: Duration, random: fn() -> f64) -> Duration {
    let ceiling = cap.min(base * 2u32.pow(attempt - 1)).as_millis() as f64;
    Duration::from_millis((random() * ceiling).round() as u64)
}

pub struct RetryOptions {
    pub max_attempts: u32,
    pub base: Duration,
    pub cap: Duration,
    pub deadline: Option<Duration>, // the whole operation, from the first try
    pub random: fn() -> f64,        // rand::random::<f64> in real code
}

impl RetryOptions {
    pub fn new(random: fn() -> f64) -> Self {
        RetryOptions {
            max_attempts: 3,
            base: Duration::from_millis(500),
            cap: Duration::from_secs(10),
            deadline: None,
            random,
        }
    }
}

pub async fn with_retry<T>(
    mut call: impl AsyncFnMut(u32) -> Result<T, CallError>,
    o: &RetryOptions,
    mut on_retry: impl FnMut(u32, Duration, &CallError),
) -> Result<T, CallError> {
    let started = Instant::now();
    let mut attempt = 1;
    loop {
        let error = match call(attempt).await {
            Ok(value) => return Ok(value),
            Err(error) if !error.is_retryable() || attempt >= o.max_attempts => return Err(error),
            Err(error) => error,
        };
        let wait = match &error {
            CallError::Status {
                retry_after: Some(wait),
                ..
            } => *wait, // the server knows best
            _ => backoff(attempt, o.base, o.cap, o.random),
        };
        if o.deadline
            .is_some_and(|deadline| started.elapsed() + wait > deadline)
        {
            return Err(error);
        }
        on_retry(attempt, wait, &error);
        sleep(wait).await;
        attempt += 1;
    }
}

/// When time runs out, the future is dropped. Dropping a future cancels it at its next `.await`,
/// so the request really stops; there is no separate cancel signal to pass along.
pub async fn with_timeout<T>(
    limit: Duration,
    call: impl Future<Output = Result<T, CallError>>,
) -> Result<T, CallError> {
    tokio::time::timeout(limit, call)
        .await
        .unwrap_or(Err(CallError::Timeout))
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum State {
    Closed,
    Open,
    HalfOpen,
}

struct BreakerInner {
    state: State,
    failures: u32,
    opened_at: Instant,
    trial_running: bool,
}

pub struct Breaker {
    threshold: u32,
    cool_down: Duration,
    inner: Mutex<BreakerInner>, // never held across an .await
}

impl Breaker {
    pub fn new(threshold: u32, cool_down: Duration) -> Self {
        let inner = BreakerInner {
            state: State::Closed,
            failures: 0,
            opened_at: Instant::now(),
            trial_running: false,
        };
        Breaker {
            threshold,
            cool_down,
            inner: Mutex::new(inner),
        }
    }

    pub fn current(&self) -> State {
        Self::refresh(&mut self.inner.lock().unwrap(), self.cool_down)
    }

    fn refresh(inner: &mut BreakerInner, cool_down: Duration) -> State {
        if inner.state == State::Open && inner.opened_at.elapsed() >= cool_down {
            inner.state = State::HalfOpen;
        }
        inner.state
    }

    /// A future does nothing until it's awaited, so when the circuit is open, `call` is never polled
    /// and no request is sent.
    pub async fn call<T>(
        &self,
        call: impl Future<Output = Result<T, CallError>>,
    ) -> Result<T, CallError> {
        let before = {
            let mut inner = self.inner.lock().unwrap();
            let state = Self::refresh(&mut inner, self.cool_down);
            if state == State::Open || (state == State::HalfOpen && inner.trial_running) {
                return Err(CallError::CircuitOpen);
            }
            inner.trial_running |= state == State::HalfOpen;
            state
        };
        let result = call.await;
        let mut inner = self.inner.lock().unwrap();
        if before == State::HalfOpen {
            inner.trial_running = false;
        }
        match &result {
            Ok(_) => (inner.state, inner.failures) = (State::Closed, 0),
            Err(error) if error.is_retryable() => {
                inner.failures += 1; // a 400 is our bug, not the provider's outage
                if before == State::HalfOpen || inner.failures >= self.threshold {
                    (inner.state, inner.opened_at) = (State::Open, Instant::now());
                }
            }
            Err(_) => {}
        }
        result
    }
}

pub type Pending<'a, T> = Pin<Box<dyn Future<Output = Result<T, CallError>> + 'a>>;

/// Tries each option in turn. Options are lazy futures, so the ones after a success never run.
pub async fn first_that_works<'a, T>(
    options: Vec<(&'a str, Pending<'a, T>)>,
    mut on_failure: impl FnMut(&str, &CallError),
) -> Result<(&'a str, T), CallError> {
    let mut errors = Vec::new();
    for (name, run) in options {
        match run.await {
            Ok(value) => return Ok((name, value)),
            Err(
                error @ CallError::Status {
                    status: 400 | 422, ..
                },
            ) => return Err(error), // every option would reject it
            Err(error) => {
                on_failure(name, &error);
                errors.push(error);
            }
        }
    }
    Err(CallError::AllFailed(errors))
}

/// The `governor` crate is the production version of this.
pub struct TokenBucket {
    capacity: f64,
    per_second: f64,
    state: Mutex<(f64, Instant)>, // tokens, last refill
}

impl TokenBucket {
    pub fn new(capacity: f64, per_second: f64) -> Self {
        TokenBucket {
            capacity,
            per_second,
            state: Mutex::new((capacity, Instant::now())),
        }
    }

    pub fn try_take(&self, cost: f64) -> Result<Duration, String> {
        if cost > self.capacity {
            return Err(format!(
                "a cost of {cost} can never fit a bucket of {}",
                self.capacity
            ));
        }
        let mut state = self.state.lock().unwrap();
        let (tokens, last) = *state;
        let tokens = self
            .capacity
            .min(tokens + last.elapsed().as_secs_f64() * self.per_second);
        if tokens >= cost {
            *state = (tokens - cost, Instant::now());
            return Ok(Duration::ZERO);
        }
        *state = (tokens, Instant::now());
        Ok(Duration::from_millis(
            ((cost - tokens) / self.per_second * 1000.0).ceil() as u64,
        ))
    }

    pub async fn take(&self, cost: f64) -> Result<(), String> {
        loop {
            match self.try_take(cost)? {
                Duration::ZERO => return Ok(()),
                wait => sleep(wait).await,
            }
        }
    }
}

pub struct Layers<'a> {
    pub timeout: Duration,
    pub retry: RetryOptions,
    pub breaker: &'a Breaker,
    pub fallback: Option<fn(&str) -> String>,
    pub log: &'a dyn Fn(String),
}

/// fallback( retry( breaker( timeout( call ) ) ) ), as in the main lesson. With one fallback, a
/// `match` on the primary's result says it more plainly than a list of boxed futures.
pub async fn resilient<'a>(
    name: &'a str,
    call: impl AsyncFn(&str) -> Result<String, CallError>,
    l: &Layers<'_>,
    input: &str,
) -> Result<(&'a str, String), CallError> {
    let primary = with_retry(
        async |_| l.breaker.call(with_timeout(l.timeout, call(input))).await,
        &l.retry,
        |attempt, wait, error| {
            (l.log)(format!(
                "{name}: attempt {attempt} failed ({}), retrying in {} ms",
                error.describe(),
                wait.as_millis()
            ))
        },
    )
    .await;
    match (primary, l.fallback) {
        (Ok(value), _) => Ok((name, value)),
        (
            Err(
                error @ CallError::Status {
                    status: 400 | 422, ..
                },
            ),
            _,
        ) => Err(error),
        (Err(error), fallback) => {
            (l.log)(format!("{name}: gave up ({})", error.describe()));
            fallback
                .map(|f| ("fallback", f(input)))
                .ok_or(CallError::AllFailed(vec![error]))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;
    use std::sync::atomic::{AtomicBool, Ordering};

    const MS: fn(u64) -> Duration = Duration::from_millis;

    fn half() -> f64 {
        0.5
    }
    fn top() -> f64 {
        0.999999
    }

    /// Fails with each status in turn, then answers.
    struct Flaky {
        statuses: Vec<u16>,
        reply: &'static str,
        calls: RefCell<Vec<u16>>,
    }

    impl Flaky {
        fn new(reply: &'static str, statuses: &[u16]) -> Self {
            Flaky {
                statuses: statuses.to_vec(),
                reply,
                calls: RefCell::new(vec![]),
            }
        }
        async fn run(&self) -> Result<String, CallError> {
            let mut calls = self.calls.borrow_mut();
            match self.statuses.get(calls.len()) {
                Some(&status) => {
                    calls.push(status);
                    Err(CallError::status(status))
                }
                None => {
                    calls.push(200);
                    Ok(self.reply.to_string())
                }
            }
        }
        fn count(&self) -> usize {
            self.calls.borrow().len()
        }
    }

    #[test]
    fn only_failures_a_second_try_could_fix_are_retryable() {
        assert!(
            [408, 429, 500, 502, 503, 529]
                .iter()
                .all(|&s| CallError::status(s).is_retryable())
        );
        assert!(
            ![400, 401, 403, 404, 422]
                .iter()
                .any(|&s| CallError::status(s).is_retryable())
        );
        assert!(CallError::Timeout.is_retryable() && CallError::Connection.is_retryable());
        assert!(!CallError::CircuitOpen.is_retryable());
    }

    #[test]
    fn retry_after_comes_as_seconds_or_a_date() {
        let now = httpdate::parse_http_date("Fri, 02 Oct 2026 12:00:00 GMT").unwrap();
        assert_eq!(parse_retry_after("7", now), Some(MS(7000)));
        assert_eq!(
            parse_retry_after("Fri, 02 Oct 2026 12:00:30 GMT", now),
            Some(MS(30_000))
        );
        assert_eq!(parse_retry_after("soon", now), None);
    }

    #[test]
    fn backoff_ceilings_double_up_to_a_cap() {
        let got: Vec<u128> = (1..=6)
            .map(|n| backoff(n, MS(500), MS(10_000), top).as_millis())
            .collect();
        assert_eq!(got, [500, 1000, 2000, 4000, 8000, 10000]);
    }

    // start_paused: tokio's clock is frozen, and jumps to the next timer whenever every task is
    // waiting. Real `sleep` and `timeout`, and a 30-second cool-down takes no time.
    #[tokio::test(start_paused = true)]
    async fn a_transient_failure_is_retried_until_it_succeeds() {
        let (start, model, slept) = (
            Instant::now(),
            Flaky::new("billing", &[503, 429]),
            RefCell::new(vec![]),
        );
        let reply = with_retry(
            async |_| model.run().await,
            &RetryOptions::new(half),
            |_, wait, _| slept.borrow_mut().push(wait),
        )
        .await;
        assert_eq!(reply, Ok("billing".into()));
        assert_eq!(*model.calls.borrow(), [503, 429, 200]);
        assert_eq!(
            (slept.into_inner(), start.elapsed()),
            (vec![MS(250), MS(500)], MS(750))
        );
    }

    #[tokio::test(start_paused = true)]
    async fn a_400_fails_at_once() {
        let model = Flaky::new("", &[400]);
        let result = with_retry(
            async |_| model.run().await,
            &RetryOptions::new(half),
            |_, _, _| {},
        )
        .await;
        assert_eq!((result, model.count()), (Err(CallError::status(400)), 1));
    }

    #[tokio::test(start_paused = true)]
    async fn retry_after_beats_our_guess_and_attempts_run_out() {
        let (start, calls) = (Instant::now(), RefCell::new(0));
        let limited = async |_| -> Result<(), CallError> {
            *calls.borrow_mut() += 1;
            Err(CallError::Status {
                status: 429,
                retry_after: Some(MS(7000)),
            })
        };
        assert!(
            with_retry(limited, &RetryOptions::new(half), |_, _, _| {})
                .await
                .is_err()
        );
        assert_eq!((calls.into_inner(), start.elapsed()), (3, MS(14_000)));
    }

    #[tokio::test(start_paused = true)]
    async fn the_deadline_stops_a_wait_that_would_overrun_it() {
        let (start, model) = (Instant::now(), Flaky::new("", &[503, 503, 503, 503]));
        let retry = RetryOptions {
            max_attempts: 10,
            base: MS(1000),
            deadline: Some(MS(5000)),
            ..RetryOptions::new(top)
        };
        assert!(
            with_retry(async |_| model.run().await, &retry, |_, _, _| {})
                .await
                .is_err()
        );
        assert_eq!((model.count(), start.elapsed()), (3, MS(3000))); // slept 1 s + 2 s; 4 s more would pass 5 s
    }

    #[tokio::test(start_paused = true)]
    async fn a_timeout_drops_a_call_that_would_hang() {
        static DROPPED: AtomicBool = AtomicBool::new(false);
        struct Guard;
        impl Drop for Guard {
            fn drop(&mut self) {
                DROPPED.store(true, Ordering::SeqCst);
            }
        }
        let hangs = async {
            let _guard = Guard;
            std::future::pending::<Result<String, CallError>>().await
        };
        assert_eq!(with_timeout(MS(20), hangs).await, Err(CallError::Timeout));
        assert!(DROPPED.load(Ordering::SeqCst)); // the call was dropped: cancelled, not left running
    }

    #[tokio::test(start_paused = true)]
    async fn the_breaker_opens_then_tests_recovery_with_one_trial() {
        let (breaker, down) = (
            Breaker::new(3, Duration::from_secs(30)),
            Flaky::new("", &[503; 5]),
        );
        for _ in 0..3 {
            let _ = breaker.call(down.run()).await;
        }
        assert_eq!(breaker.current(), State::Open);
        assert_eq!(breaker.call(down.run()).await, Err(CallError::CircuitOpen));
        assert_eq!(down.count(), 3); // the refused call's future was built but never run
        sleep(Duration::from_secs(30)).await;
        assert_eq!(breaker.current(), State::HalfOpen);
        let _ = breaker.call(down.run()).await;
        assert_eq!(breaker.current(), State::Open);
        sleep(Duration::from_secs(30)).await;
        assert_eq!(breaker.call(async { Ok("ok") }).await, Ok("ok"));
        assert_eq!(breaker.current(), State::Closed);
    }

    #[tokio::test(start_paused = true)]
    async fn a_400_does_not_trip_the_breaker() {
        let (breaker, bad) = (
            Breaker::new(2, Duration::from_secs(30)),
            Flaky::new("", &[400; 3]),
        );
        for _ in 0..3 {
            let _ = breaker.call(bad.run()).await;
        }
        assert_eq!(breaker.current(), State::Closed);
    }

    #[tokio::test]
    async fn fallback_tries_each_option_and_wont_hide_a_bad_request() {
        let (primary, secondary, failures) = (
            Flaky::new("", &[503]),
            Flaky::new("bug", &[]),
            RefCell::new(vec![]),
        );
        let options: Vec<(&str, Pending<String>)> = vec![
            ("primary", Box::pin(primary.run())),
            ("secondary", Box::pin(secondary.run())),
        ];
        let answer = first_that_works(options, |name, error| {
            failures
                .borrow_mut()
                .push(format!("{name}: {}", error.describe()))
        })
        .await;
        assert_eq!(answer, Ok(("secondary", "bug".to_string())));
        assert_eq!(failures.into_inner(), ["primary: HTTP 503"]);

        let (bad, unused) = (Flaky::new("", &[400]), Flaky::new("x", &[]));
        let options: Vec<(&str, Pending<String>)> = vec![
            ("primary", Box::pin(bad.run())),
            ("secondary", Box::pin(unused.run())),
        ];
        assert_eq!(
            first_that_works(options, |_, _| {}).await,
            Err(CallError::status(400))
        );
        assert_eq!(unused.count(), 0);
    }

    #[tokio::test(start_paused = true)]
    async fn all_the_layers_together() {
        let (model, lines) = (Flaky::new("", &[503; 20]), RefCell::new(vec![]));
        let breaker = Breaker::new(4, Duration::from_secs(30));
        let log = |line: String| lines.borrow_mut().push(line);
        let layers = Layers {
            timeout: MS(1000),
            retry: RetryOptions::new(half),
            breaker: &breaker,
            fallback: Some(evals::keywords),
            log: &log,
        };
        let call = async |_: &str| model.run().await;
        assert_eq!(
            resilient("model", call, &layers, "I was charged twice.").await,
            Ok(("fallback", "billing".into()))
        );
        assert_eq!(model.count(), 3);
        assert_eq!(
            resilient("model", call, &layers, "The app crashes on start.").await,
            Ok(("fallback", "bug".into()))
        );
        assert_eq!(model.count(), 4);
        assert_eq!(
            lines.into_inner(),
            [
                "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
                "model: attempt 2 failed (HTTP 503), retrying in 500 ms",
                "model: gave up (HTTP 503)",
                "model: attempt 1 failed (HTTP 503), retrying in 250 ms",
                "model: gave up (CircuitOpenError)",
            ]
        );
    }

    #[tokio::test(start_paused = true)]
    async fn a_token_bucket_allows_a_burst_then_paces() {
        let (start, bucket) = (Instant::now(), TokenBucket::new(3.0, 1.0));
        let mut started = vec![];
        for _ in 0..6 {
            bucket.take(1.0).await.unwrap();
            started.push(start.elapsed().as_millis());
        }
        assert_eq!(started, [0, 0, 0, 1000, 2000, 3000]);
        assert!(bucket.try_take(5.0).is_err());
    }
}
