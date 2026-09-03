pub mod http_client;
pub mod session_store;
pub mod streaming;

use pyo3::prelude::*;

#[pymodule]
fn miralas_core(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(http_client::llm_generate_sync, m)?)?;
    m.add_function(wrap_pyfunction!(session_store::session_set, m)?)?;
    m.add_function(wrap_pyfunction!(session_store::session_get, m)?)?;
    Ok(())
}
