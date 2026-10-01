//! Three layers. Domain errors are an enum; `match` maps every case to a status,
//! and the compiler complains if a new variant isn't handled.
use std::collections::HashMap;

pub struct Item {
    pub sku: &'static str,
    pub quantity: u32,
}

#[derive(Debug, PartialEq)]
pub enum PlaceError {
    EmptyOrder,
    OutOfStock { sku: String },
}

/// The only code that knows how data is stored.
pub struct Repository {
    pub stock: HashMap<String, u32>,
    orders: usize,
}

impl Repository {
    pub fn new(stock: HashMap<String, u32>) -> Self {
        Repository { stock, orders: 0 }
    }
}

/// Business rules. Returns `Result`; never a status code.
pub fn place(repo: &mut Repository, items: &[Item]) -> Result<usize, PlaceError> {
    if items.is_empty() {
        return Err(PlaceError::EmptyOrder);
    }
    for item in items {
        if repo.stock.get(item.sku).copied().unwrap_or(0) < item.quantity {
            return Err(PlaceError::OutOfStock {
                sku: item.sku.into(),
            });
        }
    }
    for item in items {
        *repo.stock.get_mut(item.sku).unwrap() -= item.quantity;
    }
    repo.orders += 1;
    Ok(repo.orders)
}

/// The controller's mapping. In Axum this is `impl IntoResponse for PlaceError`.
pub fn status_for(result: &Result<usize, PlaceError>) -> u16 {
    match result {
        Ok(_) => 201,
        Err(PlaceError::EmptyOrder) => 400,
        Err(PlaceError::OutOfStock { .. }) => 409,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn errors_map_to_statuses() {
        let mut repo = Repository::new(HashMap::from([("mug".to_string(), 1)]));
        assert_eq!(status_for(&place(&mut repo, &[])), 400);
        let out = place(
            &mut repo,
            &[Item {
                sku: "mug",
                quantity: 5,
            }],
        );
        assert_eq!(out, Err(PlaceError::OutOfStock { sku: "mug".into() }));
        assert_eq!(status_for(&out), 409);
        let ok = place(
            &mut repo,
            &[Item {
                sku: "mug",
                quantity: 1,
            }],
        );
        assert_eq!((status_for(&ok), ok), (201, Ok(1)));
        assert_eq!(repo.stock["mug"], 0);
    }
}
