import itertools
import json
from typing import Any, Tuple

from demo_rust_extension import fibonacci, initialize_tracing


class PythonSpan:
    def __init__(
        self, python_span_id: int, rust_span_id: str, span_attrs: dict[Any, Any]
    ):
        self.python_span_id: int = python_span_id
        self.rust_span_id: str = rust_span_id
        self.span_attrs: dict[Any, Any] = span_attrs
        self.events: list[str] = []

        print(f"[new_span] {self}")

    def __str__(self):
        return f"Python span ({self.rust_span_id}, {self.python_span_id}) | {len(self.events)} events | {self.span_attrs}"

    def __repr__(self):
        return self.__str__()

    def new_event(self, event: str):
        self.events.append(event)
        print(f"[new_event] {self} | {event}")

    def update_values(self, values: dict[Any, Any]):
        self.span_attrs.update(values)
        print(f"[update_values] {self}")

    def close(self):
        print(f"[close] {self}")


class DemoTracingLayer:
    def __init__(self):
        self.span_ids = itertools.count()
        self.span_map = {}

    def _update_current_span(
        self, new_current_span: PythonSpan | None
    ) -> PythonSpan | None:
        global current_span
        old_current_span = current_span
        current_span = new_current_span
        print("")
        print(f"New current span: {current_span}")
        print("")
        return old_current_span

    def on_event(self, event: str, state: Tuple[PythonSpan | None, PythonSpan]):
        _parent_span, span = state
        span.new_event(event)

    def on_new_span(
        self, span_attrs: str, span_id: str
    ) -> Tuple[PythonSpan | None, PythonSpan]:
        python_span_id = next(self.span_ids)

        deserialized_span_attrs = json.loads(span_attrs)
        new_span = PythonSpan(python_span_id, span_id, deserialized_span_attrs)
        self.span_map[python_span_id] = new_span

        parent_span = self._update_current_span(new_span)
        return (parent_span, new_span)

    def on_close(self, span_id: str, state: Tuple[PythonSpan | None, PythonSpan]):
        parent_span, span = state
        span.close()
        del self.span_map[span.python_span_id]

        _closed_span = self._update_current_span(parent_span)

    def on_record(
        self, span_id: str, values: str, state: Tuple[PythonSpan | None, PythonSpan]
    ):
        _parent_span, span = state
        deserialized_values = json.loads(values)
        span.update_values(deserialized_values)


current_span: PythonSpan | None = None


def main():
    tracing_layer = DemoTracingLayer()
    initialize_tracing(tracing_layer)

    global current_span
    initial_span = PythonSpan(next(tracing_layer.span_ids), "", {})
    current_span = initial_span

    print("Calling memoized fibonacci generator")
    print(f"PYTHON: fibonacci(10, True) {fibonacci(10, True)}")

    print("Calling naive fibonacci generator")
    print(f"PYTHON: fibonacci(10, False) {fibonacci(10, False)}")

    print("(Intentional error) Calling naive fibonacci generator with too big an index")
    print(f"PYTHON: fibonacci(30, False) {fibonacci(30, False)}")

    print("")
    assert current_span == initial_span
    print(f"Current span: {current_span}")
    print(f"Same as initial span: {current_span == initial_span}")


if __name__ == "__main__":
    main()
