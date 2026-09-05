use dashmap::DashMap;
use pyo3::prelude::*;
use std::sync::OnceLock;
use std::time::Instant;

static STORE: OnceLock<DashMap<String, (Instant, String)>> = OnceLock::new();

fn get_store() -> &'static DashMap<String, (Instant, String)> {
    STORE.get_or_init(DashMap::new)
}

#[pyfunction]
pub fn session_set(session_id: String, messages_json: String) -> PyResult<()> {
    get_store().insert(session_id, (Instant::now(), messages_json));
    Ok(())
}

#[pyfunction]
pub fn session_get(session_id: String) -> PyResult<Option<String>> {
    match get_store().get(&session_id) {
        Some(entry) => Ok(Some(entry.value().1.clone())),
        None => Ok(None),
    }
}

/// Suresi gecmis session'lari DashMap'ten gercekten siler. Donen deger: silinen sayisi.
#[pyfunction]
pub fn session_sweep(ttl_secs: u64) -> PyResult<usize> {
    let now = Instant::now();
    let store = get_store();
    let before = store.len();
    store.retain(|_, (ts, _)| now.duration_since(*ts).as_secs() <= ttl_secs);
    Ok(before - store.len())
}