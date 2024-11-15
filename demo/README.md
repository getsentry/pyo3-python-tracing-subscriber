This folder contains working demo projects that use `pyo3-python-tracing-subscriber`.

`demo-py-project` illustrates how a Python `Layer` implementation could incorporate Rust `tracing` data into another tracing system in Python. When a new Rust span is created, `on_new_span()` creates a corresponding `PythonSpan` and updates a global `current_span` variable. It then returns the a tuple containing the previous `current_span` (or, the parent span) and the new span to Rust to be stored inside the Rust span. When that Rust span is later closed, `on_close()` is given the same tuple containing the parent span and the span that is closing. It will set the global `current_span` variable back to the parent span.

To run it, run the following:
```python
python -m venv .venv
source .venv/bin/activate
pip install -r demo-py-project/requirements.in

python demo-py-project/main.py
```

`demo-sentry-project` shows how to use the Sentry SDK's `RustTracingIntegration` to forward Rust `tracing` data to Sentry. It uses a custom `event_type_mapping` to show off exception/event/breadcrumb behavior; the default `event_type_mapping` is much less noisy.

To run it, run the following:
```python
python -v venv .venv
source .venv/bin/activate
pip install -r demo-sentry-project/requirements.in

# Create a dummy Sentry project and get its DSN
export SENTRY_DSN=...
python demo-py-project/main.py
# See the results in the Issues and Traces section of your dummy project's Sentry page
# You may have to wait a few minutes for the transactions to be ingested
```

The `demo-rust-extension` folder contains a native extension built with `maturin`. It exposes two Rust functions to Python:
- `initialize_tracing()`, which takes a Python implementation of `Layer`
- `fibonacci()`, a Rust function with obnoxiously thorough instrumentation
