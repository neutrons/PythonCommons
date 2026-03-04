================================
Configuration Management (Config)
================================

YAML-based configuration system with environment layering, deep merging, token substitution, and automatic backup.

Quick Reference
===============

.. code-block:: python

    from commons import Config
    
    # Access values
    Config["database.host"]                      # Dot-delimited lookup
    Config.exists("optional.key")                # Check if key exists
    
    # Environment management
    Config.loadEnv("production.yml")             # Load environment config
    Config.reload(env_name="qa.yml")             # Reload with environment
    Config.getCurrentEnv()                       # Get current environment name
    
    # User config
    Config.swapToUserYml()                       # Use ~/.{package_name}-user.yml
    Config.shouldSwapToUserYml()                 # Check if user config available
    
    # Backup
    Config.persistBackup()                       # Backup to ~/.{package_name}/application.yml.bak
    Config.archiveUserYml()                      # Archive versioned user config

Dot-Delimited Lookup
--------------------

Access nested values with dot notation. Automatically resolves token substitutions:

.. code-block:: python

    Config["database.host"]              # localhost
    Config["paths.input"]                # /data/input (resolved from ${paths.base}/input)
    Config.exists("optional.setting")    # Returns bool

Configuration Layering
----------------------

Base configuration (``application.yml``) + environment override (e.g., ``production.yml``) merged recursively:

**Base (application.yml):**

.. code-block:: yaml

    database:
      host: localhost
      port: 5432
      credentials:
        username: user
        password: pass

**Override (production.yml):**

.. code-block:: yaml

    database:
      host: prod-db.example.com
      credentials:
        password: secure-pass

**Result (merged):**

.. code-block:: yaml

    database:
      host: prod-db.example.com    # Overridden
      port: 5432                   # From base (preserved)
      credentials:
        username: user             # From base (preserved)
        password: secure-pass       # Overridden

**Merge rules:** Dictionaries merge recursively; scalar values replace entirely; new keys added; nothing deleted.

Token Substitution
------------------

Reference other config values with ``${key.subkey}`` syntax:

.. code-block:: yaml

    paths:
      base: /data
      input: ${paths.base}/input         # Resolves to /data/input
      output: ${paths.base}/output
    
    module:
      root: /app                         # Auto-set by Config

Environment Configuration
--------------------------

Specify environment via:

- Environment variable: ``env=environment_name``
- YAML property: ``environment: environment_name``
- Auto-detect user config: ``~/.{package_name}-user.yml``

User Configuration Management
-----------------------------

User config (``~/.{package_name}-user.yml``) auto-loads if present and no explicit ``env`` specified. Old configs archived with version + timestamp when app version changes.

Configuration Backup
--------------------

Backups created automatically during ``Config.reload()``:

.. code-block:: text

    ~/.{package_name}/
    ├── application.yml.bak                          # Latest backup
    └── {package_name}-user-1.0.0-2026-03-04T16:10:34.817Z.yml.bak  # Versioned

Deployment Configuration
------------------------

Auto-select environment based on app version:

.. code-block:: python

    Config.configureForDeploy()

- Contains ``dev`` → NEXT environment
- Contains ``rc`` → QA environment  
- Otherwise → PROD environment

Merges and exports to ``application.yml``.

Directory Path Expansion
------------------------

Home directory ``~`` automatically expands:

.. code-block:: yaml

    instrument:
      home: ~/instruments        # Expands to /home/user/instruments
    samples:
      home: ~/samples

Error Handling
--------------

Failed config loading automatically restores previous state:

.. code-block:: python

    try:
        Config.loadEnv("invalid.yml")  # Fails, restores previous
    except Exception:
        pass  # Config unchanged
    
    try:
        value = Config["nonexistent"]  # Raises KeyError
    except KeyError:
        pass

Examples
========

Basic Usage
-----------

.. code-block:: python

    from commons import Config
    
    # Read values
    host = Config["database.host"]
    
    # Safe access with check
    if Config.exists("optional.feature"):
        feature_dir = Config["optional.feature"]
    
    # Switch environment
    Config.loadEnv("production.yml")
    prod_host = Config["database.host"]

Configuration File Example
--------------------------

.. code-block:: yaml

    application:
      version: 1.0.0
    
    environment: default
    
    database:
      host: localhost
      port: 5432
      credentials:
        username: app_user
        password: app_pass
    
    paths:
      base: /data
      input: ${paths.base}/input
      output: ${paths.base}/output
      resources: ${module.root}/resources
    
    logging:
      level: INFO
      file: app.log
    
    # Set automatically
    module:
      root: /app
