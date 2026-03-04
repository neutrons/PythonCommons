================================
Configuration Management (Config)
================================

The ``Config`` module provides a robust configuration management system for loading, managing, and accessing application settings from YAML configuration files.

Overview
========

The ``Config`` singleton manages all application configuration through a hierarchical YAML-based system. It supports multiple environments, token substitution, automatic backup, and dot-delimited key lookups for easy access to nested configuration values.

Key Features
============

Dot-Delimited Lookup
--------------------

Access nested configuration values using dot-separated keys without manually navigating dictionaries:

.. code-block:: python

    from commons import Config
    
    # Access nested values with dot notation
    home_dir = Config["instrument.home"]
    sample_home = Config["samples.home"]
    
    # Works recursively through multiple levels
    value = Config["level1.level2.level3.value"]

The lookup automatically raises a ``KeyError`` if the key doesn't exist, allowing for safe configuration access.

Token Substitution
------------------

Configuration values can reference other configuration keys using the ``${key.subkey}`` syntax. This allows for dynamic composition of configuration values:

.. code-block:: yaml

    # application.yml
    paths:
      base: /data
      input: ${paths.base}/input
      output: ${paths.base}/output
      
    module:
      root: /app

Tokens are recursively resolved and support nested references. Non-string values that reference dictionary keys will return the value unchanged.

Configuration Environments
--------------------------

Load different configuration files for different deployment environments:

.. code-block:: python

    # Load a specific environment configuration
    Config.loadEnv("production.yml")
    
    # Get the current environment
    current_env = Config.getCurrentEnv()

Supported environments can be specified via:

- Environment variable: ``env=environment_name``
- YAML property: ``environment: environment_name``
- User configuration file: ``~/.{package_name}-user.yml``

Configuration Layering and Deep Merging
----------------------------------------

The configuration system uses a layered approach with deep merging:

1. **Default Configuration**: ``application.yml`` is loaded first as the base configuration
2. **Environment Override**: Environment-specific configuration files (e.g., ``qa.yml``, ``production.yml``) are merged on top
3. **Deep Merge**: Nested dictionaries are recursively merged, allowing partial overrides

.. code-block:: python

    # Reload process:
    # 1. Load application.yml (base)
    # 2. If env is specified, load and merge env file
    Config.reload()
    Config.loadEnv("production.yml")

Example of deep merging behavior:

**application.yml (base):**

.. code-block:: yaml

    database:
      host: localhost
      port: 5432
      credentials:
        username: user
        password: pass
    
    logging:
      level: INFO
      file: app.log

**production.yml (override):**

.. code-block:: yaml

    database:
      host: prod-db.example.com
      credentials:
        password: secure-prod-pass
    
    logging:
      level: WARNING

**Resulting merged configuration:**

.. code-block:: yaml

    database:
      host: prod-db.example.com          # Overridden
      port: 5432                         # From base
      credentials:
        username: user                   # From base
        password: secure-prod-pass       # Overridden
    
    logging:
      level: WARNING                     # Overridden
      file: app.log                      # From base

The key point: nested properties are merged recursively, so only the values you explicitly override are changed—the rest of the configuration from the base file is preserved.

Deep Update Algorithm
^^^^^^^^^^^^^^^^^^^^^

The ``deep_update()`` function implements the merging logic:

.. code-block:: python

    # Pseudocode of the merge process
    def deep_update(base_config, override_config):
        for key, value in override_config.items():
            if key exists in base_config AND both are dicts:
                # Recursively merge nested dictionaries
                deep_update(base_config[key], value)
            else:
                # Scalar values or new keys are overwritten
                base_config[key] = value

This means:

- **Dictionary values** are merged recursively
- **Scalar values** (strings, numbers, booleans) are replaced entirely
- **New keys** from the environment file are added to the configuration
- **Removed keys** are not deleted (only base + overrides, never subtracts)

Configuration Backup
--------------------

Configuration backups are automatically created for disaster recovery and audit trails:

.. code-block:: python

    # Backup is automatically created during reload()
    Config.reload()

Backups are stored in the user home directory at ``~/.{package_name}/application.yml.bak`` with a timestamp and version information. The system also archives outdated user configurations with version and ISO timestamp suffixes:

.. code-block:: text

    ~/.{package_name}/
    ├── application.yml.bak
    └── {package_name}-user-1.0.0-2024-03-04T15:53:42.885Z.yml.bak

Configuration Reload and Refresh
---------------------------------

Reload the entire configuration with optional environment switching:

.. code-block:: python

    # Reload with default environment
    Config.reload()
    
    # Reload with a specific environment
    Config.reload(env_name="qa.yml")
    
    # Refresh configuration (lower-level operation)
    Config.refresh("production.yml")

The ``reload()`` method clears the configuration, reloads defaults, and optionally switches environments. The ``refresh()`` method merges new configuration without clearing existing values.

User Configuration Management
-----------------------------

The system automatically detects and uses user-specific configuration files when available:

.. code-block:: python

    # Check if user config should be loaded
    if Config.shouldSwapToUserYml():
        Config.swapToUserYml()

If a user configuration file exists at ``~/.{package_name}/{package_name}-user.yml`` and no explicit environment is specified, it will be used by default. When the application version changes, old user configurations are automatically archived.

Directory Path Expansion
------------------------

Home directory shortcuts (``~``) are automatically expanded to absolute paths:

.. code-block:: yaml

    # application.yml
    instrument:
      home: ~/instruments
    samples:
      home: ~/samples

Configuration values starting with ``~`` will be automatically expanded to the user's home directory during configuration loading.

Sensitive Property Warnings
---------------------------

Track changes to sensitive configuration properties and issue warnings:

.. code-block:: python

    # Properties marked as sensitive will trigger warnings if changed
    # Example: version.start is flagged for warnings

The system compares sensitive properties before and after loading to detect unauthorized or accidental changes and logs warnings when they occur.

Deployment Environment Configuration
-------------------------------------

Configure different settings based on deployment environment (NEXT, QA, PROD):

.. code-block:: python

    # Automatically select environment based on version
    Config.configureForDeploy()
    
    # Merge and export configuration for a specific environment
    Config.mergeAndExport("production_prod")

The version string determines the target deployment environment:
- Contains ``dev`` → NEXT environment
- Contains ``rc`` → QA environment  
- Otherwise → PROD environment

The merged configuration is exported back to ``application.yml``.

API Reference
=============

Config Object
-------------

The ``Config`` singleton provides the following methods:

.. code-block:: python

    from commons import Config
    
    # Access configuration values
    value = Config[key]                          # Dot-delimited key lookup
    exists = Config.exists(key)                  # Check if key exists
    
    # Configuration management
    Config.reload(env_name=None)                 # Reload configuration
    Config.refresh(env_name, clearPrevious)      # Refresh configuration
    Config.loadEnv(env_name)                     # Load environment config
    Config.getCurrentEnv()                       # Get current environment
    
    # User configuration
    Config.swapToUserYml()                       # Use user config
    Config.shouldSwapToUserYml()                 # Check if user config available
    Config.getUserYmlVersionDisk()               # Get user config version
    
    # Backup and archival
    Config.persistBackup()                       # Create backup
    Config.archiveUserYml()                      # Archive user config
    
    # Deployment
    Config.configureForDeploy()                  # Configure for deployment
    Config.mergeAndExport(envName)               # Merge and export config
    
    # Validation
    Config.validate()                            # Validate configuration
    
    # Utilities
    Config.packageVersion()                      # Get application version

Configuration File Format
==========================

Configuration files are written in YAML format. The standard application configuration file is ``application.yml``:

.. code-block:: yaml

    # application.yml
    application:
      version: 1.0.0
    
    environment: default
    
    instrument:
      home: ~/instruments
      timeout: 30
    
    samples:
      home: ~/samples
      batch_size: 100
    
    paths:
      base: /data
      input: ${paths.base}/input
      output: ${paths.base}/output
    
    module:
      root: /app  # Set automatically by Config

Environment-specific configurations can be loaded from files like:

- ``application.yml`` (default)
- ``development.yml`` (development environment)
- ``qa.yml`` (QA environment)
- ``production.yml`` (production environment)
- ``{package_name}-user.yml`` (user home directory)

Module Root Reference
=====================

The configuration automatically provides the module root directory through the internal ``module.root`` key, which can be used in token substitution:

.. code-block:: yaml

    resources:
      path: ${module.root}/resources
      templates: ${module.root}/templates

This allows for relative path references that work regardless of where the application is installed.

Testing
=======

When running in a test environment (detected by the presence of ``conftest.py`` and ``test`` in the ``env`` variable), the configuration system uses test-specific configuration files:

.. code-block:: python

    if isTestEnv():
        # Uses test.yml or integration_test.yml depending on env value
        Config.reload()

This allows different test categories to use their own configuration profiles.

Error Handling
==============

Configuration errors are handled gracefully:

.. code-block:: python

    try:
        value = Config["nonexistent.key"]
    except KeyError as e:
        print(f"Configuration key not found: {e}")
    
    # Configuration loading failures restore previous state
    try:
        Config.refresh("invalid.yml")
    except Exception:
        # Previous configuration is restored automatically
        print("Failed to load configuration, using previous state")

If configuration loading fails, the system automatically restores the previous valid configuration state to prevent application breakage.

Best Practices
==============

1. **Use dot notation for all lookups**: Always use the dot-delimited syntax rather than manually accessing nested dictionaries.

2. **Leverage token substitution**: Use ``${key}`` references to avoid repeating values and maintain consistency.

3. **Check existence before access**: Use ``Config.exists(key)`` to safely check for optional configuration values.

4. **Load environments early**: Call ``Config.loadEnv()`` at application startup to switch to the appropriate environment configuration.

5. **Handle KeyError**: Wrap configuration access in try-except blocks for optional configuration values.

6. **Version your user configs**: The system automatically manages versioning, so keep your user configuration in the standard location.

Example Usage
=============

.. code-block:: python

    from commons import Config
    
    # Basic usage
    base_path = Config["paths.base"]
    
    # Safe access with existence check
    if Config.exists("optional.feature"):
        feature_path = Config["optional.feature"]
    
    # Load environment-specific configuration
    Config.loadEnv("production.yml")
    
    # Access configuration after loading
    timeout = Config["instrument.timeout"]
    
    # Get current environment
    env = Config.getCurrentEnv()
