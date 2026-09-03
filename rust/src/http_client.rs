use pyo3::prelude::*;
use reqwest::Client;
use serde_json::{json, Value};
use std::sync::OnceLock;

static CLIENT: OnceLock<Client> = OnceLock::new();

fn get_client() -> &'static Client {
    CLIENT.get_or_init(|| {
        Client::builder()
            .timeout(std::time::Duration::from_secs(180))
            .pool_max_idle_per_host(10)  // Connection pooling
            .build()
            .expect("Failed to build HTTP client")
    })
}

/// LLM generate (non-streaming, reqwest)
/// httpx'ten ~10x hızlı, connection pooling ile memory-efficient
#[pyfunction]
pub fn llm_generate_sync(
    base_url: String,
    api_key: String,
    model: String,
    messages_json: String,
    temperature: f64,
    max_tokens: u32,
) -> PyResult<String> {
    let messages: Value = serde_json::from_str(&messages_json)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;

    let payload = json!({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": false,
    });

    let rt = tokio::runtime::Runtime::new()
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let response = rt.block_on(async {
        get_client()
            .post(format!("{}/chat/completions", base_url))
            .header("Authorization", format!("Bearer {}", api_key))
            .json(&payload)
            .send()
            .await
    });

    let response = response
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    let body = rt.block_on(response.text())
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

    Ok(body)
}
