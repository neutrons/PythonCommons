==========================
Singleton Decorator Pattern
==========================

The ``Singleton`` decorator provides a lightweight implementation of the Singleton design pattern, ensuring that only one instance of a decorated class exists throughout the application lifecycle.

Overview
========

The ``@Singleton`` decorator transforms a class so that all calls to its constructor return the same object instance. This is particularly useful for shared resources, configuration objects, and stateful managers where a single instance must be maintained across the application.

Basic Usage
===========

Apply the ``@Singleton`` decorator to any class:

.. code-block:: python

    from commons.decorators.singleton import Singleton
    
    @Singleton
    class DatabaseConnection:
        def __init__(self):
            self.connection = self._connect()
        
        def _connect(self):
            # Initialization happens only once
            return "Connected to database"
    
    # All references point to the same instance
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    
    assert db1 is db2  # True - same object in memory

Key Characteristics
===================

Single Instance Guarantee
-------------------------

Only one instance of the class is ever created:

.. code-block:: python

    @Singleton
    class Logger:
        def __init__(self):
            print("Logger initialized")
    
    logger1 = Logger()  # Prints "Logger initialized"
    logger2 = Logger()  # Does NOT print - reuses existing instance
    logger3 = Logger()  # Does NOT print - reuses existing instance

Initialization Guard
--------------------

The ``__init__`` method only runs during first instantiation:

.. code-block:: python

    @Singleton
    class Counter:
        def __init__(self):
            self.count = 0
            print("Counter created")
        
        def increment(self):
            self.count += 1
    
    c1 = Counter()      # Prints "Counter created", count = 0
    c2 = Counter()      # Does NOT print, reuses c1
    c2.increment()      # Increments shared instance
    
    assert c1.count == 1  # True - same object

API Reference
=============

@Singleton Decorator
--------------------

.. code-block:: python

    from commons.decorators.singleton import Singleton
    
    @Singleton
    class MyClass:
        pass

Decorates a class to ensure only one instance is ever created.

Reset Methods
-------------

Individual Singleton Reset
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Reset a specific Singleton (allows new initialization on next use)
    MyClass._reset_Singleton()
    
    # Reset and fully unwrap the decorator (remove Singleton behavior)
    MyClass._reset_Singleton(fully_unwrap=True)

After resetting, the next instantiation will create a new instance and run ``__init__`` again.

Global Reset
^^^^^^^^^^^^

.. code-block:: python

    from commons.decorators.singleton import reset_Singletons
    
    # Reset all Singletons in the application
    reset_Singletons()
    
    # Reset all and fully unwrap decorators
    reset_Singletons(fully_unwrap=True)

This resets all classes decorated with ``@Singleton``, allowing them to be reinitialized on next use.

Testing and Fixtures
====================

The Singleton decorator provides built-in support for pytest fixtures through reset methods:

.. code-block:: python

    import pytest
    from commons.decorators.singleton import reset_Singletons
    
    @pytest.fixture(autouse=True)
    def reset_singletons():
        """Reset all singletons before each test."""
        reset_Singletons()
        yield
        reset_Singletons()
    
    def test_singleton_independence():
        # Each test gets a fresh instance
        obj1 = MyClass()
        obj1.value = "test1"
        
        # Fixture ensures next test gets new instance
    
    def test_another_singleton():
        # This gets a fresh instance, not the one from previous test
        obj2 = MyClass()
        assert obj2.value != "test1"  # Different instance

For more granular control:

.. code-block:: python

    @pytest.fixture
    def fresh_database():
        """Provide a fresh database instance for this test."""
        DatabaseConnection._reset_Singleton()
        db = DatabaseConnection()
        yield db
        DatabaseConnection._reset_Singleton()

Use Cases
=========

Configuration Management
------------------------

.. code-block:: python

    from commons.decorators.singleton import Singleton
    from commons import Config
    
    # Config is a Singleton - only one configuration object
    from commons import Config
    
    # All parts of the application share the same config
    config1 = Config
    config2 = Config
    assert config1 is config2

Shared Resource Pools
---------------------

.. code-block:: python

    @Singleton
    class ConnectionPool:
        def __init__(self):
            self.connections = []
            self._initialize_pool()
        
        def _initialize_pool(self):
            # Create connection pool once
            for i in range(10):
                self.connections.append(self._create_connection())
        
        def get_connection(self):
            return self.connections.pop() if self.connections else None
    
    # Entire application uses the same pool
    pool = ConnectionPool()

Logging and Monitoring
----------------------

.. code-block:: python

    @Singleton
    class ApplicationLogger:
        def __init__(self):
            self.messages = []
            self.level = "INFO"
        
        def log(self, message):
            self.messages.append(message)
    
    # All modules log to the same instance
    logger = ApplicationLogger()

State Managers
--------------

.. code-block:: python

    @Singleton
    class SessionManager:
        def __init__(self):
            self.sessions = {}
            self.current_user = None
        
        def create_session(self, user_id):
            self.sessions[user_id] = {"created": time.time()}
        
        def get_current_user(self):
            return self.current_user
    
    # Maintains application state across all modules
    session_mgr = SessionManager()

Implementation Details
======================

How It Works
------------

The ``@Singleton`` decorator intercepts the class's ``__new__`` and ``__init__`` methods:

1. **First instantiation**: ``__new__`` creates the instance, ``__init__`` runs
2. **Subsequent instantiations**: ``__new__`` returns existing instance, ``__init__`` is skipped
3. **State preservation**: The instance's state persists between calls

Thread Safety Considerations
----------------------------

The current implementation is **not inherently thread-safe**. For multi-threaded applications:

.. code-block:: python

    import threading
    from commons.decorators.singleton import Singleton
    
    @Singleton
    class ThreadSafeResource:
        def __init__(self):
            self.lock = threading.Lock()
            self.data = []
        
        def append(self, value):
            with self.lock:
                self.data.append(value)

If thread safety is critical, manage locks within the Singleton class itself.

Common Patterns
===============

Lazy Initialization
-------------------

Combine Singleton with lazy loading:

.. code-block:: python

    @Singleton
    class ExpensiveResource:
        def __init__(self):
            self.resource = None
        
        def get_resource(self):
            if self.resource is None:
                self.resource = self._load_expensive_resource()
            return self.resource

Factory Pattern with Singleton
-------------------------------

.. code-block:: python

    @Singleton
    class ServiceFactory:
        def __init__(self):
            self.services = {}
        
        def register_service(self, name, service):
            self.services[name] = service
        
        def get_service(self, name):
            return self.services.get(name)

Best Practices
==============

1. **Use for truly global state**: Only apply Singleton to classes that represent application-wide shared resources
2. **Document singleton behavior**: Clearly mark Singleton classes in documentation and code comments
3. **Reset in tests**: Always reset Singletons between tests to avoid state leakage
4. **Avoid over-use**: Too many Singletons can make code harder to test and reason about
5. **Thread-safe access**: If used in multi-threaded contexts, add synchronization within the Singleton class
6. **Initialization errors**: Handle errors in ``__init__`` carefully—failure prevents proper initialization

Common Pitfalls
===============

Mutable Default State
---------------------

.. code-block:: python

    @Singleton
    class BadCounter:
        count = []  # Shared mutable default - can be modified externally
    
    # Better:
    @Singleton
    class GoodCounter:
        def __init__(self):
            self.count = 0  # Instance variable, not class variable

State Pollution Between Tests
------------------------------

Always reset Singletons in test fixtures to prevent state from one test affecting another.

Hidden Dependencies
-------------------

Avoid Singletons with complex initialization that has side effects, as it can make debugging difficult.
