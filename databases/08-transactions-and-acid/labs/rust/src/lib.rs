//! Connecting to the throwaway database, and the retry loop every Repeatable Read or Serializable transaction needs.
use postgres::error::SqlState;
use postgres::{Client, Config, NoTls};
use std::time::Duration;

/// The crate doesn't read PG* variables itself, so the settings are passed in. A host starting with "/" is a socket.
pub fn connect() -> Client {
    let host = std::env::var("PGHOST").expect("run through ../shared/with-postgres.sh");
    let port = std::env::var("PGPORT")
        .expect("PGPORT")
        .parse()
        .expect("a port number");
    Config::new()
        .host(&host)
        .port(port)
        .user("postgres")
        .dbname("postgres")
        .connect(NoTls)
        .expect("connect")
}

/// The SQLSTATE a PostgreSQL error carries, if any: `SqlState` has a named constant for every code.
pub fn code(result: &Result<impl Sized, postgres::Error>) -> Option<&SqlState> {
    result.as_ref().err().and_then(postgres::Error::code)
}

/// Runs `work` again while PostgreSQL says the transaction should be retried, backing off each time.
pub fn with_retry<T>(
    attempts: u32,
    mut work: impl FnMut() -> Result<T, postgres::Error>,
) -> Result<T, postgres::Error> {
    for attempt in 1.. {
        let result = work();
        let retry = matches!(code(&result), Some(c) if *c == SqlState::T_R_SERIALIZATION_FAILURE || *c == SqlState::T_R_DEADLOCK_DETECTED);
        if !retry || attempt == attempts {
            return result;
        }
        std::thread::sleep(Duration::from_millis(10 << attempt));
    }
    unreachable!("the loop returns")
}
