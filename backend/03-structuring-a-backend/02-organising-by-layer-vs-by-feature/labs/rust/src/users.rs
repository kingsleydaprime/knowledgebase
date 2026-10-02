// The users feature.
pub struct Users {
    ids: Vec<&'static str>,
}

impl Users {
    pub fn new() -> Self {
        Users { ids: vec!["u1"] }
    }

    pub fn exists(&self, id: &str) -> bool {
        self.ids.contains(&id)
    }
}
