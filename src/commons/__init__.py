"""Contains the entry point for the application"""

from commons.decorators.singleton import Singleton


try:
    from ._version import __version__  # noqa: F401
except ImportError:
    __version__ = "unknown"
    
@Singleton
class _Spec:
    def __init__(self):
        self.client_package_name: str = None
Spec : _Spec = _Spec()
    
def init(client_package_name: str):
    Spec.client_package_name = client_package_name