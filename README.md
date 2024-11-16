# `pyo3-python-tracing-subscriber`

![Actions](https://github.com/getsentry/pyo3-python-tracing-subscriber/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/getsentry/pyo3-python-tracing-subscriber/graph/badge.svg?token=Ud70kSEpiu)](https://codecov.io/gh/getsentry/pyo3-python-tracing-subscriber)
[![crates.io](https://img.shields.io/crates/v/pyo3-python-tracing-subscriber.svg)](https://crates.io/crates/pyo3-python-tracing-subscriber)
[![docs.rs](https://docs.rs/pyo3-python-tracing-subscriber/badge.svg)](https://docs.rs/pyo3-python-tracing-subscriber)

A `tracing_subscriber` layer for native extensions that forwards `tracing` data to a Python handler.

See the `demo` folder for working examples.

### Usage
Native extensions that use `tracing` can expose a function to Python to initialize `tracing`:
```rust
#[tracing::instrument]
#[pyfunction]
fn fibonacci(index: usize, use_memoized: bool) -> PyResult<usize> {
    // ...
}

#[pyfunction]
pub fn initialize_tracing(py_impl: Bound<'_, PyAny>) {
    tracing_subscriber::registry()
        .with(pyo3_python_tracing_subscriber::PythonCallbackLayerBridge::new(py_impl))
        .init();
}
```

Python code can pass an implementation of `tracing_subscriber::layer::Layer` (but slightly different) into `initialize_tracing` and then future calls to instrumented Rust functions will forward tracing data to the Python layer.
```python
import rust_extension

class MyPythonLayer:
    def __init__(self):
        pass

    # `on_new_span` can return some state
    def on_new_span(self, span_attrs: str, span_id: str) -> int:
        print(f"[on_new_span]: {span_attrs} | {span_id}")
        return random.randint(1, 1000)

    # The state from `on_new_span` is passed back into other trait methods
    def on_event(self, event: str, state: int):
        print(f"[on_event]: {event} | {state}")

    def on_close(self, span_id: str, state: int):
        print(f"[on_close]: {span_id} | {state}")

    def on_record(self, span_id: str, values: str, state: int):
        print(f"[on_record]: {span_id} | {values} | {state}")

def main():
    rust_extension.initialize_tracing(MyPythonLayer())

    print("10th fibonacci number: ", rust_extension.fibonacci(10, True))
```

Only a subset of `Layer` trait methods are currently forwarded to Python.

### Native extension quirks

Native extensions are self-contained with their own global variables and copies of dependencies. Because of this:
- Each native extension needs to initialize `tracing` separately to forward its data to Python
- `pyo3-python-tracing-subscriber` itself is not a native extension and can't be used from Python
  - This is because the compiled code in its own native extension wouldn't be guaranteed to be ABI-compatible with the compiled code included in other native extensions that want to use it
  - If `pyo3` + `tracing_subscriber` support trait objects then this can change

### Contributing

Test with:
```
$ cargo test
```
