//! A B+ tree you can watch, the arithmetic of its height, and the leftmost-prefix rule. Same model as the Python
//! lab. The nodes live in one Vec (an arena) and point at each other by index: a leaf is pointed to by its parent
//! and by the leaf before it, which Rust's ownership rules make awkward with references, and easy with indexes.

pub fn levels(rows: u64, keys_per_leaf: u64, fanout: u64) -> u32 {
    let leaves = rows.div_ceil(keys_per_leaf) as f64;
    1 + ((leaves.ln() / (fanout as f64).ln()) - 1e-12)
        .ceil()
        .max(0.0) as u32
}

enum Node {
    Leaf {
        keys: Vec<u32>,
        values: Vec<String>,
        next: Option<usize>,
    },
    Internal {
        keys: Vec<u32>,
        children: Vec<usize>,
    },
}

pub struct BPlusTree {
    nodes: Vec<Node>,
    root: usize,
    pub height: u32,
    max_keys: usize,
}

impl BPlusTree {
    pub fn new(max_keys: usize) -> Self {
        assert!(max_keys >= 3, "max_keys must be at least 3");
        BPlusTree {
            nodes: vec![Node::Leaf {
                keys: vec![],
                values: vec![],
                next: None,
            }],
            root: 0,
            height: 1,
            max_keys,
        }
    }

    pub fn root_keys(&self) -> &[u32] {
        match &self.nodes[self.root] {
            Node::Leaf { keys, .. } | Node::Internal { keys, .. } => keys,
        }
    }

    /// The leaf holding `key`, and the pages read to get there.
    fn descend(&self, key: u32) -> (usize, u32) {
        let (mut at, mut pages) = (self.root, 1);
        while let Node::Internal { keys, children } = &self.nodes[at] {
            at = children[keys.partition_point(|&k| key >= k)];
            pages += 1;
        }
        (at, pages)
    }

    /// The value, if present, and the pages read: always the height.
    pub fn search(&self, key: u32) -> (Option<&str>, u32) {
        let (at, pages) = self.descend(key);
        let Node::Leaf { keys, values, .. } = &self.nodes[at] else {
            unreachable!("descend stops at a leaf")
        };
        (
            keys.binary_search(&key).ok().map(|i| values[i].as_str()),
            pages,
        )
    }

    pub fn range(&self, lo: u32, hi: u32) -> (Vec<&str>, u32) {
        let (mut at, mut pages) = self.descend(lo);
        let mut found = Vec::new();
        loop {
            let Node::Leaf { keys, values, next } = &self.nodes[at] else {
                unreachable!()
            };
            for (k, v) in keys.iter().zip(values) {
                if *k > hi {
                    return (found, pages);
                }
                if *k >= lo {
                    found.push(v.as_str());
                }
            }
            match next {
                Some(n) => (at, pages) = (*n, pages + 1),
                None => return (found, pages),
            }
        }
    }

    pub fn insert(&mut self, key: u32, value: String) {
        if let Some((separator, right)) = self.insert_at(self.root, key, value) {
            self.nodes.push(Node::Internal {
                keys: vec![separator],
                children: vec![self.root, right],
            }); // a new level
            self.root = self.nodes.len() - 1;
            self.height += 1;
        }
    }

    fn insert_at(&mut self, at: usize, key: u32, value: String) -> Option<(u32, usize)> {
        let new_index = self.nodes.len(); // where a split's right half will go
        match &mut self.nodes[at] {
            Node::Leaf { keys, values, next } => {
                match keys.binary_search(&key) {
                    Ok(i) => {
                        values[i] = value;
                        return None;
                    }
                    Err(i) => {
                        keys.insert(i, key);
                        values.insert(i, value);
                    }
                }
                if keys.len() <= self.max_keys {
                    return None;
                }
                let mid = keys.len() / 2; // the right half's first key is copied up
                let right = Node::Leaf {
                    keys: keys.split_off(mid),
                    values: values.split_off(mid),
                    next: next.replace(new_index),
                };
                let separator = match &right {
                    Node::Leaf { keys, .. } => keys[0],
                    Node::Internal { .. } => unreachable!(),
                };
                self.nodes.push(right);
                Some((separator, new_index))
            }
            Node::Internal { keys, children } => {
                let i = keys.partition_point(|&k| key >= k);
                let child = children[i];
                let (separator, right) = self.insert_at(child, key, value)?;
                let new_index = self.nodes.len();
                let Node::Internal { keys, children } = &mut self.nodes[at] else {
                    unreachable!()
                };
                keys.insert(i, separator);
                children.insert(i + 1, right);
                if keys.len() <= self.max_keys {
                    return None;
                }
                let mid = keys.len() / 2; // an internal split moves the middle key up
                let sibling_keys = keys.split_off(mid + 1);
                let up = keys.pop().expect("the middle key");
                let sibling = Node::Internal {
                    keys: sibling_keys,
                    children: children.split_off(mid + 1),
                };
                self.nodes.push(sibling);
                Some((up, new_index))
            }
        }
    }
}

/// The index columns that narrow a search: equality columns from the left, then at most one range column.
pub fn usable_prefix<'a>(index: &[&'a str], equal: &[&str], ranges: &[&str]) -> Vec<&'a str> {
    let mut used = Vec::new();
    for &column in index {
        if equal.contains(&column) {
            used.push(column);
        } else {
            if ranges.contains(&column) {
                used.push(column);
            }
            break;
        }
    }
    used
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn why_not_a_binary_tree() {
        assert_eq!((1e8_f64).log2().ceil(), 27.0);
        assert_eq!(
            (levels(100_000_000, 367, 400), levels(1_000_000, 367, 400)),
            (4, 3)
        );
    }

    #[test]
    fn splits_and_page_reads() {
        let mut tree = BPlusTree::new(3);
        for k in 1..=10 {
            tree.insert(k, format!("v{k}"));
        }
        assert_eq!((tree.height, tree.root_keys()), (3, &[7][..]));
        assert_eq!(tree.search(7), (Some("v7"), 3));
        assert_eq!(tree.search(99), (None, 3));
        assert_eq!(tree.range(4, 8), (vec!["v4", "v5", "v6", "v7", "v8"], 6));
    }

    #[test]
    fn a_million_keys_three_pages() {
        let mut tree = BPlusTree::new(400);
        for i in 0..1_000_000_u64 {
            tree.insert((i * 7919 % 1_000_000) as u32, String::new()); // every key once, in a scrambled order
        }
        assert_eq!((tree.height, tree.search(424_242).1), (3, 3));
    }

    #[test]
    fn the_leftmost_prefix_rule() {
        let index = ["a", "b", "c"];
        assert_eq!(usable_prefix(&index, &["a"], &[]), ["a"]);
        assert_eq!(
            usable_prefix(&index, &["a", "b", "c"], &[]),
            ["a", "b", "c"]
        );
        assert!(usable_prefix(&index, &["b"], &[]).is_empty());
        assert_eq!(usable_prefix(&index, &["a", "c"], &[]), ["a"]);
        assert_eq!(usable_prefix(&index, &["b"], &["a"]), ["a"]);
        assert_eq!(usable_prefix(&index, &["a"], &["b"]), ["a", "b"]);
    }
}
