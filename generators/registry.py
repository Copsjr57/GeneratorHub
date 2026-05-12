import importlib
import pkgutil
from typing import Dict, List

from generators.base import GeneratorPlugin
from utils.storage import AppStorage


class GeneratorRegistry:
    def __init__(self, storage: AppStorage) -> None:
        self.storage = storage
        self._plugins: Dict[str, GeneratorPlugin] = {}

    def register(self, plugin: GeneratorPlugin) -> None:
        self._plugins[plugin.meta.id] = plugin

    def discover(self) -> None:
        # auto-discover modules in generators.plugins package
        import generators.plugins  # noqa: F401

        pkg = generators.plugins
        for m in pkgutil.iter_modules(pkg.__path__, pkg.__name__ + "."):
            if m.ispkg:
                continue
            mod = importlib.import_module(m.name)
            
            # Try plugin factory first
            factory = getattr(mod, "create_plugin", None)
            if factory is not None:
                plugin = factory(self.storage)
                self.register(plugin)
                continue
            
            # Fallback to PLUGIN constant
            plugin = getattr(mod, "PLUGIN", None)
            if plugin is not None:
                self.register(plugin)

    def get(self, generator_id: str) -> GeneratorPlugin | None:
        return self._plugins.get(generator_id)

    def list_generators(self) -> List[GeneratorPlugin]:
        return [self._plugins[k] for k in sorted(self._plugins.keys())]
