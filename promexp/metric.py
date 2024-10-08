"""Implementation of a metric"""

from typing import Iterator

from .metric_inst import MetricInstance
from .types import MetricTypeEnum
from .utils import _get_label_string


class Metric:
    """Represents a Prometheus metric, i.e. a metric name with its helptext and type
    information."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        name: str,
        datatype: MetricTypeEnum,
        helpstr: str,
        timeout: int = 0,
        with_update_counter: bool = False,
    ) -> None:
        self._name = name
        self._datatype = datatype
        self._helpstr = helpstr
        self._timeout = timeout
        self._data: dict[str, "MetricInstance"] = {}
        self._with_update_counter = with_update_counter

    def clone(self) -> "Metric":
        """Clone this instance, i.e. duplicate the metric definition, but not
        its instances"""

        return Metric(
            name=self._name,
            datatype=self._datatype,
            helpstr=self._helpstr,
            timeout=self._timeout,
            with_update_counter=self._with_update_counter,
        )

    @property
    def name(self) -> str:
        """Return the metric name"""
        return self._name

    @property
    def datatype(self) -> MetricTypeEnum:
        """Return the metric datatype (gauge, counter, ...)"""
        return self._datatype

    @property
    def helptext(self) -> str:
        """Return the metric help text"""

        return self._helpstr

    @property
    def timeout(self) -> int:
        """Return the timeout in seconds for this metric. Metric instances are removed
        from the metric after the timeout is expired."""

        return self._timeout

    @property
    def with_update_counter(self) -> bool:
        """Returns true if this metric has an associated update counter metric."""

        return self._with_update_counter

    def set(self, labels: dict[str, str], value: float | None):
        """Set a value for a metric instance"""

        labelstr = _get_label_string(labels)

        # If we do not know this instance yet
        if labelstr not in self._data:
            # we do not add new metrics without assigned value
            if value is None:
                return

            # we don't know this instance yet, so we create a new one
            self._data[labelstr] = MetricInstance(
                metric=self, labels=labels, value=value
            )

        # we already know this instance
        else:
            # if the value is None, we remove it
            if value is None:
                del self._data[labelstr]
            else:
                # we know this instance, so we update its value
                instance = self._data[labelstr]
                instance.value = value

    def clear(self) -> None:
        """Clear all metric instances"""
        self._data.clear()

    def get(self, labels: dict[str, str]) -> float | None:
        """Return the last stored value of a metric instance. Returns None if
        the instance does not exist."""

        labelstr = _get_label_string(labels)

        # If we do not know this instance yet
        if labelstr not in self._data:
            return None

        inst = self._data[labelstr]
        return inst.value

    def inc(self, labels: dict[str, str]):
        """Increases the value of the metric instance by one."""

        val = self.get(labels)

        if val is None:
            val = 0

        val += 1

        self.set(labels, val)

    @property
    def has_timeout(self) -> bool:
        """Return true if this metric has an timeout assigned."""

        return bool(self.timeout)

    def check_timeout(self) -> None:
        """Check all metric instances for timeout and remove the timed out instances."""

        # find all timed out metric instances
        to_delete = [
            labelstr
            for labelstr, instance in self._data.items()
            if instance.is_timed_out
        ]

        # remove the metric instances
        for labelstr in to_delete:
            del self._data[labelstr]

    def render_iter(self) -> Iterator[str]:
        """Return an iterator returning separate lines in Prometheus format"""

        yield f"# HELP {self.name} {self.helptext}"
        yield f"# TYPE {self.name} {self.datatype.value}"

        yield from (str(instance) for instance in self._data.values())

        yield ""  # empty line for better readability

    def render(self) -> str:
        """Render the metric to Prometheus format"""

        return "\n".join(self.render_iter())

    def __str__(self) -> str:
        return self._name

    def __len__(self) -> int:
        """Returns the number of metric instances."""
        return len(self._data)
