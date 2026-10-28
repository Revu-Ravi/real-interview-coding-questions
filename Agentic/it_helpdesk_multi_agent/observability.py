
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.trace import Status, StatusCode

# Configure the provider once for this application.
_provider = TracerProvider()
_provider.add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

# Avoid replacing a provider that has already been configured.
try:
    trace.set_tracer_provider(_provider)
except Exception:
    pass

tracer = trace.get_tracer("it-helpdesk")


class TracedSpan:
    """Context manager that records and ends an OpenTelemetry span."""

    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes
        self.span = None

    def __enter__(self):
        self.span = tracer.start_span(self.name)

        for key, value in self.attributes.items():
            if value is not None:
                self.span.set_attribute(key, str(value))

        self.span.__enter__()
        return self.span

    def __exit__(self, exc_type, exc_value, traceback):
        if self.span is None:
            return False

        if exc_type is not None:
            self.span.record_exception(exc_value)
            self.span.set_status(
                Status(StatusCode.ERROR, str(exc_value))
            )

        self.span.end()
        return False


def traced(name, **attributes):
    """Use with traced(...) to record a completed span."""
    return TracedSpan(name, attributes)
