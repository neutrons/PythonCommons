====================
Time Utilities (time)
====================

The ``time`` module provides utilities for generating, parsing, and formatting timestamps with high precision and ISO 8601 support.

Overview
========

This module handles timestamp operations with nanosecond precision using NumPy's datetime capabilities. It supports multiple timestamp formats and ensures unique timestamps when needed for event tracking or ordering.

Core Functions
==============

timestamp()
-----------

Generate a timestamp in seconds with optional uniqueness guarantee.

.. code-block:: python

    from commons.time import timestamp
    
    # Get current timestamp as float (seconds since epoch)
    ts = timestamp()
    # Returns: 1709556038.240123
    
    # Generate unique timestamps
    ts1 = timestamp(ensureUnique=True)
    ts2 = timestamp(ensureUnique=True)
    # ts2 > ts1 is guaranteed (at least 1 second difference if called same second)

**Parameters:**

- ``ensureUnique`` (bool, default=False): If True, guarantees each timestamp is greater than the previous one

**Returns:**

- float: Timestamp in seconds since epoch with nanosecond precision

**Behavior:**

- Uses ``time.time_ns()`` internally for high precision (nanosecond resolution)
- Converts nanoseconds to seconds by dividing by 1e9
- When ``ensureUnique=True``, monotonically increases even if called multiple times in the same second

Unique Timestamp Generation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The uniqueness feature is useful for event logs and audit trails:

.. code-block:: python

    from commons.time import timestamp
    
    # Generate multiple timestamps that are guaranteed to be different
    events = []
    for i in range(5):
        events.append({
            'event_id': i,
            'timestamp': timestamp(ensureUnique=True)
        })
    
    # All timestamps are guaranteed to be strictly increasing
    for i in range(len(events) - 1):
        assert events[i]['timestamp'] < events[i + 1]['timestamp']

parseTimestamp()
----------------

Parse timestamps from various formats to a float (seconds).

.. code-block:: python

    from commons.time import parseTimestamp
    
    # Parse ISO 8601 string
    ts = parseTimestamp("2026-03-04T16:00:38.240Z")
    # Returns: 1741100438.24
    
    # Parse float timestamp
    ts = parseTimestamp(1741100438.24)
    # Returns: 1741100438.24
    
    # Parse legacy integer (milliseconds)
    ts = parseTimestamp(1741100438240)
    # Returns: 1741100438.24

**Parameters:**

- ``ts`` (float | str | int): Timestamp in one of the supported formats

**Returns:**

- float: Timestamp in seconds since epoch

**Supported Formats:**

- **ISO 8601 string** (e.g., ``"2026-03-04T16:00:38.240Z"``): Parsed using NumPy's datetime64
- **Float**: Returned as-is (already in seconds)
- **Integer**: Treated as legacy millisecond encoding, divided by 1000
- **Other types**: Raises ``ValueError``

**Examples:**

.. code-block:: python

    from commons.time import parseTimestamp
    
    # Mixed format parsing
    timestamps = [
        parseTimestamp("2026-03-04T16:00:38.240Z"),  # ISO string
        parseTimestamp(1741100438.24),                # Float seconds
        parseTimestamp(1741100438240),                # Legacy milliseconds
    ]
    
    # All return the same value
    assert timestamps[0] == timestamps[1] == timestamps[2]

isoFromTimestamp()
------------------

Convert a float timestamp (seconds) to an ISO 8601 formatted string with timezone and nanosecond precision.

.. code-block:: python

    from commons.time import isoFromTimestamp, timestamp
    
    # Convert current timestamp to ISO format
    ts = timestamp()
    iso_string = isoFromTimestamp(ts)
    # Returns: "2026-03-04T16:00:38.240123456Z"
    
    # Convert arbitrary timestamp
    iso = isoFromTimestamp(1741100438.24)
    # Returns: "2026-03-04T16:00:38.240000000Z"

**Parameters:**

- ``ts`` (float): Timestamp in seconds since epoch

**Returns:**

- str: ISO 8601 formatted timestamp string with local timezone and nanosecond precision

**Format Details:**

- Includes nanosecond precision (9 decimal places)
- Uses local timezone information
- Returns timezone-aware ISO 8601 format

**Examples:**

.. code-block:: python

    from commons.time import isoFromTimestamp, timestamp
    
    # Round-trip conversion
    original_ts = timestamp()
    iso_string = isoFromTimestamp(original_ts)
    print(iso_string)  # "2026-03-04T16:00:38.123456789Z"
    
    # Use in configuration backup
    from commons import Config
    backup_time = isoFromTimestamp(timestamp())
    print(f"Backup created at: {backup_time}")

Use Cases
=========

Event Logging and Audit Trails
-------------------------------

.. code-block:: python

    from commons.time import timestamp, isoFromTimestamp
    
    class AuditLog:
        def __init__(self):
            self.events = []
        
        def record_event(self, event_type, details):
            event = {
                'type': event_type,
                'timestamp': isoFromTimestamp(timestamp(ensureUnique=True)),
                'details': details
            }
            self.events.append(event)
    
    audit = AuditLog()
    audit.record_event("login", {"user": "john"})
    audit.record_event("data_access", {"table": "users"})

Configuration File Backups
---------------------------

.. code-block:: python

    from commons.time import isoFromTimestamp, timestamp
    from pathlib import Path
    
    def backup_config(config_file):
        backup_time = isoFromTimestamp(timestamp())
        backup_path = Path(config_file).parent / f"config-{backup_time}.bak"
        shutil.copy(config_file, backup_path)
        return backup_path

Database Timestamp Fields
-------------------------

.. code-block:: python

    from commons.time import parseTimestamp, isoFromTimestamp
    
    class DatabaseRecord:
        def __init__(self, data):
            self.data = data
            self.created_at = isoFromTimestamp(timestamp())
        
        def to_db(self):
            return {
                **self.data,
                'created_at': self.created_at
            }
        
        @classmethod
        def from_db(cls, db_row):
            record = cls(db_row)
            # Parse timestamp from database
            record.created_at = parseTimestamp(db_row['created_at'])
            return record

Performance Monitoring
----------------------

.. code-block:: python

    from commons.time import timestamp
    
    class Timer:
        def __init__(self):
            self.start = timestamp()
        
        def elapsed(self):
            return timestamp() - self.start
    
    # Measure operation duration
    timer = Timer()
    perform_operation()
    print(f"Operation took {timer.elapsed()} seconds")

Time Series Data
----------------

.. code-block:: python

    from commons.time import parseTimestamp, isoFromTimestamp, timestamp
    
    class TimeSeries:
        def __init__(self):
            self.data = []
        
        def add_point(self, value):
            self.data.append({
                'timestamp': timestamp(ensureUnique=True),
                'value': value
            })
        
        def export_csv(self):
            lines = ["timestamp,value"]
            for point in self.data:
                iso_ts = isoFromTimestamp(point['timestamp'])
                lines.append(f"{iso_ts},{point['value']}")
            return "\n".join(lines)

API Reference
=============

Precision and Accuracy
======================

Nanosecond Precision
--------------------

All timestamp operations maintain nanosecond precision:

.. code-block:: python

    from commons.time import timestamp, isoFromTimestamp
    
    ts = timestamp()
    iso = isoFromTimestamp(ts)
    # ISO string includes 9 decimal places: "2026-03-04T16:00:38.123456789Z"

Monotonic Uniqueness
--------------------

When using ``ensureUnique=True``, timestamps are guaranteed to be monotonically increasing:

.. code-block:: python

    from commons.time import timestamp
    
    timestamps = [timestamp(ensureUnique=True) for _ in range(100)]
    
    # All timestamps are strictly increasing
    for i in range(len(timestamps) - 1):
        assert timestamps[i] < timestamps[i + 1]

Format Reference
================

ISO 8601 Format
---------------

The standard ISO 8601 format returned by ``isoFromTimestamp()``:

.. code-block:: text

    2026-03-04T16:00:38.123456789Z
    │         │ │  │  │  │          │
    │         │ │  │  │  │          └─ UTC indicator (Z)
    │         │ │  │  │  └─────────── Nanoseconds (9 digits)
    │         │ │  │  └──────────── Seconds
    │         │ │  └─────────────── Minutes
    │         │ └────────────────── Hours
    │         └──────────────────── Time separator (T)
    └────────────────────────────── Date (YYYY-MM-DD)

Timestamp Value Examples
------------------------

.. code-block:: text

    Current timestamp (as of docs generation):
    Float seconds:    1741100438.240123
    ISO 8601:         2026-03-04T16:00:38.240123Z
    Milliseconds:     1741100438240
    Nanoseconds:      1741100438240123000

Best Practices
==============

1. **Use ensureUnique for event ordering**: When tracking sequences of events, use ``timestamp(ensureUnique=True)`` to guarantee ordering

2. **Store as ISO strings for readability**: Use ``isoFromTimestamp()`` when storing timestamps in logs or exports for human readability

3. **Parse consistently**: Always use ``parseTimestamp()`` for flexible input handling rather than manual conversions

4. **Preserve precision**: Avoid converting to/from string formats multiple times; keep as floats internally

5. **Timezone awareness**: Remember that ``isoFromTimestamp()`` includes local timezone information

6. **Round-trip testing**: When testing time-dependent code, verify round-trip conversions work correctly

Example: Complete Time Handling
================================

.. code-block:: python

    from commons.time import timestamp, isoFromTimestamp, parseTimestamp
    
    # Generate unique timestamp for event
    event_ts = timestamp(ensureUnique=True)
    
    # Convert to ISO for storage/display
    iso_string = isoFromTimestamp(event_ts)
    print(f"Event occurred at: {iso_string}")
    
    # Parse back from string for processing
    parsed_ts = parseTimestamp(iso_string)
    assert abs(parsed_ts - event_ts) < 0.001  # Allow small rounding error
    
    # Measure elapsed time
    start = timestamp()
    # ... perform operation ...
    elapsed = timestamp() - start
    print(f"Operation took {elapsed} seconds")
