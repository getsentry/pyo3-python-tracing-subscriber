import os
import sys

import sentry_sdk
from sentry_sdk.integrations.rust_tracing import (
    RustTracingIntegration,
    EventTypeMapping,
    RustTracingLevel,
)
from demo_rust_extension import fibonacci, initialize_tracing

sentry_dsn = os.environ.get("SENTRY_DSN")
if not sentry_dsn:
    print("Must set a Sentry DSN in `$SENTRY_DSN` env var")
    sys.exit(1)


def event_type_mapping(metadata: dict) -> EventTypeMapping:
    match RustTracingLevel(metadata.get("level")):
        case RustTracingLevel.Error:
            return EventTypeMapping.Exc
        case RustTracingLevel.Warn | RustTracingLevel.Info:
            return EventTypeMapping.Breadcrumb
        case RustTracingLevel.Debug:
            return EventTypeMapping.Event
        case RustTracingLevel.Trace:
            return EventTypeMapping.Ignore


sentry_sdk.init(
    dsn=sentry_dsn,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    integrations=[
        RustTracingIntegration(
            "demo_rust_extension",
            initialize_tracing,
            include_tracing_fields=True,
            event_type_mapping=event_type_mapping,
        )
    ],
)


def main():
    with sentry_sdk.api.start_transaction(name="memoized fibonacci", sampled=True):
        print("Calling memoized fibonacci inside transaction")
        print(f"PYTHON: fibonacci(10, True) {fibonacci(10, True)}")

    with sentry_sdk.api.start_transaction(name="naive fibonacci", sampled=True):
        print("Calling naive fibonacci inside transaction")
        print(f"PYTHON: fibonacci(6, False) {fibonacci(6, False)}")

    with sentry_sdk.api.start_transaction(name="naive fibonacci", sampled=True):
        print("Calling naive fibonacci with too big an index inside a transaction")
        try:
            print(f"PYTHON: fibonacci(30, False) {fibonacci(30, False)}")
        except Exception:
            print("Caught exception")


if __name__ == "__main__":
    main()
