//! Connecting to the throwaway database, and reading an error's SQLSTATE.
use postgres::error::SqlState;
use postgres::{Client, Config, NoTls};

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

pub fn code<T>(result: &Result<T, postgres::Error>) -> Option<&SqlState> {
    result.as_ref().err().and_then(postgres::Error::code)
}
