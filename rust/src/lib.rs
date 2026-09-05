pub mod session_store;

use pyo3::prelude::*;

#[pymodule]
fn miralas_core(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(session_store::session_set, m)?)?;
    m.add_function(wrap_pyfunction!(session_store::session_get, m)?)?;
    m.add_function(wrap_pyfunction!(session_store::session_sweep, m)?)?;
    Ok(())
}