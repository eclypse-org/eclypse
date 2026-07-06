"""Dictionary that calls a hook when selected keys change."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Iterable,
    )

_MISSING = object()


class InvalidatingDict(dict):
    """Dict that invalidates derived state when watched keys are mutated."""

    def __init__(
        self,
        *args: Any,
        on_change: Callable[[tuple[Any, ...]], None],
        watched_keys: Iterable[Any] | None = None,
        **kwargs: Any,
    ):
        """Initialize the dictionary with an invalidation hook.

        Args:
            *args: Initial dictionary data.
            on_change: Callback invoked with changed watched keys.
            watched_keys: Keys that trigger invalidation. ``None`` watches every key.
            **kwargs: Additional initial dictionary data.
        """
        self._on_change = on_change
        self._watched_keys = set(watched_keys) if watched_keys is not None else None
        super().__init__(*args, **kwargs)

    def _changed(self, keys: Iterable[Any]):
        if not hasattr(self, "_on_change") or not hasattr(self, "_watched_keys"):
            return
        changed_keys = tuple(
            k for k in keys if self._watched_keys is None or k in self._watched_keys
        )
        if changed_keys:
            self._on_change(changed_keys)

    def __setitem__(self, key: Any, value: Any):
        """Set a value and invalidate when it changes."""
        old_value = self.get(key, _MISSING)
        super().__setitem__(key, value)
        if old_value != value:
            self._changed((key,))

    def __delitem__(self, key: Any):
        """Delete a key and invalidate."""
        super().__delitem__(key)
        self._changed((key,))

    def update(self, *args: Any, **kwargs: Any):
        """Update values and invalidate when any watched value changes."""
        updates = dict(*args, **kwargs)
        changed_keys = [
            key for key, value in updates.items() if self.get(key, _MISSING) != value
        ]
        super().update(updates)
        if changed_keys:
            self._changed(changed_keys)

    def setdefault(self, key: Any, default: Any = None):
        """Set a default value and invalidate only when a key is inserted."""
        if key in self:
            return self[key]
        super().__setitem__(key, default)
        self._changed((key,))
        return default

    def pop(self, key: Any, default: Any = _MISSING):
        """Remove a key and invalidate when it existed."""
        if key not in self:
            if default is _MISSING:
                raise KeyError(key)
            return default
        value = super().pop(key)
        self._changed((key,))
        return value

    def popitem(self):
        """Remove and return an item, then invalidate."""
        key, value = super().popitem()
        self._changed((key,))
        return key, value

    def clear(self):
        """Remove all items and invalidate when the dictionary was non-empty."""
        changed_keys = list(self)
        super().clear()
        if changed_keys:
            self._changed(changed_keys)
