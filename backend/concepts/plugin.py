"""
PluginConcept: Runtime plugin system for extensibility
Purpose: Install/uninstall plugins -> Alter core workflows dynamically
"""

import uuid
import json
import importlib
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import asyncio
import inspect
from dataclasses import dataclass, asdict


@dataclass
class PluginMetadata:
    """Plugin metadata and configuration."""
    plugin_id: str
    name: str
    version: str
    description: str
    author: str
    entry_point: str
    dependencies: List[str]
    permissions: List[str]
    hooks: List[str]
    config_schema: dict
    installed_at: datetime
    is_active: bool = True


@dataclass
class PluginHook:
    """Represents a plugin hook point."""
    hook_name: str
    description: str
    parameters: dict
    return_type: str


class PluginRegistry:
    """Central registry for managing plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, PluginMetadata] = {}
        self.plugin_instances: Dict[str, Any] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.hook_definitions: Dict[str, PluginHook] = {}
        
        # Define core hooks
        self._define_core_hooks()
        
    def _define_core_hooks(self):
        """Define core application hooks."""
        core_hooks = [
            PluginHook(
                hook_name="before_upload",
                description="Called before image upload processing",
                parameters={"file_content": "bytes", "filename": "str"},
                return_type="dict"
            ),
            PluginHook(
                hook_name="after_upload",
                description="Called after image upload processing",
                parameters={"upload_result": "dict"},
                return_type="dict"
            ),
            PluginHook(
                hook_name="before_prompt_parse",
                description="Called before prompt parsing",
                parameters={"prompt": "str", "image_id": "str"},
                return_type="dict"
            ),
            PluginHook(
                hook_name="after_prompt_parse",
                description="Called after prompt parsing",
                parameters={"requirements": "dict", "prompt": "str"},
                return_type="dict"
            ),
            PluginHook(
                hook_name="before_mockup_generate",
                description="Called before mockup generation",
                parameters={"image_bytes": "bytes", "prompt": "str", "requirements": "dict"},
                return_type="dict"
            ),
            PluginHook(
                hook_name="after_mockup_generate",
                description="Called after mockup generation",
                parameters={"mockup_html": "str", "mockup_id": "str"},
                return_type="dict"
            ),
            PluginHook(
                hook_name="before_export",
                description="Called before mockup export",
                parameters={"mockup_html": "str", "export_format": "str"},
                return_type="dict"
            ),
            PluginHook(
                hook_name="custom_ai_provider",
                description="Custom AI provider for mockup generation",
                parameters={"image_bytes": "bytes", "prompt": "str"},
                return_type="str"
            ),
            PluginHook(
                hook_name="custom_voice_provider",
                description="Custom voice synthesis provider",
                parameters={"text": "str", "voice_config": "dict"},
                return_type="bytes"
            )
        ]
        
        for hook in core_hooks:
            self.hook_definitions[hook.hook_name] = hook
            self.hooks[hook.hook_name] = []


class PluginConcept:
    """
    Manages plugin lifecycle and execution.
    Supports runtime installation, uninstallation, and hook execution.
    """

    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.registry = PluginRegistry()
        self.plugin_configs: Dict[str, dict] = {}
        
        # Load existing plugins
        self._load_installed_plugins()

    def _load_installed_plugins(self):
        """Load plugins that are already installed."""
        plugins_manifest = self.plugins_dir / "manifest.json"
        if plugins_manifest.exists():
            try:
                with open(plugins_manifest, 'r') as f:
                    manifest = json.load(f)
                    
                for plugin_data in manifest.get("plugins", []):
                    metadata = PluginMetadata(**plugin_data)
                    self.registry.plugins[metadata.plugin_id] = metadata
                    
                    if metadata.is_active:
                        asyncio.create_task(self._load_plugin(metadata.plugin_id))
            except Exception as e:
                print(f"Error loading plugins manifest: {e}")

    async def install_plugin(
        self,
        plugin_package: bytes,
        plugin_metadata: dict,
        user_id: str
    ) -> dict:
        """
        Install a new plugin at runtime.
        
        Args:
            plugin_package: Plugin code as bytes (zip or python file)
            plugin_metadata: Plugin metadata
            user_id: User installing the plugin
            
        Returns:
            Installation result
        """
        plugin_id = str(uuid.uuid4())
        
        # Validate plugin metadata
        required_fields = ["name", "version", "description", "author", "entry_point"]
        for field in required_fields:
            if field not in plugin_metadata:
                raise ValueError(f"Missing required field: {field}")
        
        # Create plugin metadata
        metadata = PluginMetadata(
            plugin_id=plugin_id,
            name=plugin_metadata["name"],
            version=plugin_metadata["version"],
            description=plugin_metadata["description"],
            author=plugin_metadata["author"],
            entry_point=plugin_metadata["entry_point"],
            dependencies=plugin_metadata.get("dependencies", []),
            permissions=plugin_metadata.get("permissions", []),
            hooks=plugin_metadata.get("hooks", []),
            config_schema=plugin_metadata.get("config_schema", {}),
            installed_at=datetime.now()
        )
        
        # Save plugin files
        plugin_dir = self.plugins_dir / plugin_id
        plugin_dir.mkdir(exist_ok=True)
        
        # Extract and save plugin package
        if plugin_metadata.get("type") == "python_file":
            plugin_file = plugin_dir / "plugin.py"
            with open(plugin_file, 'wb') as f:
                f.write(plugin_package)
        else:
            # Handle zip packages
            import zipfile
            import io
            
            with zipfile.ZipFile(io.BytesIO(plugin_package)) as zip_file:
                zip_file.extractall(plugin_dir)
        
        # Save metadata
        metadata_file = plugin_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(asdict(metadata), f, indent=2, default=str)
        
        # Register plugin
        self.registry.plugins[plugin_id] = metadata
        
        # Load plugin
        await self._load_plugin(plugin_id)
        
        # Update manifest
        await self._save_manifest()
        
        return {
            "plugin_id": plugin_id,
            "status": "installed",
            "message": f"Plugin '{metadata.name}' installed successfully"
        }

    async def uninstall_plugin(self, plugin_id: str, user_id: str) -> dict:
        """Uninstall a plugin at runtime."""
        if plugin_id not in self.registry.plugins:
            raise ValueError("Plugin not found")
        
        metadata = self.registry.plugins[plugin_id]
        
        # Unload plugin
        await self._unload_plugin(plugin_id)
        
        # Remove from registry
        del self.registry.plugins[plugin_id]
        if plugin_id in self.registry.plugin_instances:
            del self.registry.plugin_instances[plugin_id]
        
        # Remove plugin files
        plugin_dir = self.plugins_dir / plugin_id
        if plugin_dir.exists():
            import shutil
            shutil.rmtree(plugin_dir)
        
        # Update manifest
        await self._save_manifest()
        
        return {
            "plugin_id": plugin_id,
            "status": "uninstalled",
            "message": f"Plugin '{metadata.name}' uninstalled successfully"
        }

    async def activate_plugin(self, plugin_id: str) -> dict:
        """Activate an installed plugin."""
        if plugin_id not in self.registry.plugins:
            raise ValueError("Plugin not found")
        
        metadata = self.registry.plugins[plugin_id]
        metadata.is_active = True
        
        await self._load_plugin(plugin_id)
        await self._save_manifest()
        
        return {
            "plugin_id": plugin_id,
            "status": "activated",
            "message": f"Plugin '{metadata.name}' activated"
        }

    async def deactivate_plugin(self, plugin_id: str) -> dict:
        """Deactivate a plugin without uninstalling."""
        if plugin_id not in self.registry.plugins:
            raise ValueError("Plugin not found")
        
        metadata = self.registry.plugins[plugin_id]
        metadata.is_active = False
        
        await self._unload_plugin(plugin_id)
        await self._save_manifest()
        
        return {
            "plugin_id": plugin_id,
            "status": "deactivated",
            "message": f"Plugin '{metadata.name}' deactivated"
        }

    async def _load_plugin(self, plugin_id: str):
        """Load and initialize a plugin."""
        metadata = self.registry.plugins[plugin_id]
        plugin_dir = self.plugins_dir / plugin_id
        
        # Add plugin directory to Python path
        if str(plugin_dir) not in sys.path:
            sys.path.insert(0, str(plugin_dir))
        
        try:
            # Import plugin module
            module_name = metadata.entry_point.split('.')[0]
            spec = importlib.util.spec_from_file_location(
                module_name,
                plugin_dir / f"{module_name}.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get plugin class
            class_name = metadata.entry_point.split('.')[1] if '.' in metadata.entry_point else 'Plugin'
            plugin_class = getattr(module, class_name)
            
            # Initialize plugin
            plugin_instance = plugin_class()
            
            # Register plugin hooks
            await self._register_plugin_hooks(plugin_id, plugin_instance, metadata.hooks)
            
            # Store plugin instance
            self.registry.plugin_instances[plugin_id] = plugin_instance
            
            # Call plugin initialization
            if hasattr(plugin_instance, 'initialize'):
                await plugin_instance.initialize()
                
        except Exception as e:
            print(f"Error loading plugin {plugin_id}: {e}")
            raise

    async def _unload_plugin(self, plugin_id: str):
        """Unload a plugin and remove its hooks."""
        if plugin_id in self.registry.plugin_instances:
            plugin_instance = self.registry.plugin_instances[plugin_id]
            
            # Call plugin cleanup
            if hasattr(plugin_instance, 'cleanup'):
                await plugin_instance.cleanup()
            
            # Remove plugin hooks
            await self._unregister_plugin_hooks(plugin_id)
            
            del self.registry.plugin_instances[plugin_id]

    async def _register_plugin_hooks(self, plugin_id: str, plugin_instance: Any, hook_names: List[str]):
        """Register plugin hooks with the registry."""
        for hook_name in hook_names:
            if hook_name in self.registry.hook_definitions:
                # Check if plugin has the hook method
                hook_method_name = f"on_{hook_name}"
                if hasattr(plugin_instance, hook_method_name):
                    hook_method = getattr(plugin_instance, hook_method_name)
                    
                    # Add plugin ID to method for tracking
                    hook_method._plugin_id = plugin_id
                    
                    self.registry.hooks[hook_name].append(hook_method)

    async def _unregister_plugin_hooks(self, plugin_id: str):
        """Remove all hooks for a plugin."""
        for hook_name, hook_methods in self.registry.hooks.items():
            self.registry.hooks[hook_name] = [
                method for method in hook_methods
                if not hasattr(method, '_plugin_id') or method._plugin_id != plugin_id
            ]

    async def execute_hook(self, hook_name: str, **kwargs) -> dict:
        """Execute all plugins registered for a hook."""
        if hook_name not in self.registry.hooks:
            return kwargs
        
        result = kwargs.copy()
        
        for hook_method in self.registry.hooks[hook_name]:
            try:
                # Execute hook method
                if inspect.iscoroutinefunction(hook_method):
                    hook_result = await hook_method(**result)
                else:
                    hook_result = hook_method(**result)
                
                # Update result with hook output
                if isinstance(hook_result, dict):
                    result.update(hook_result)
                    
            except Exception as e:
                print(f"Error executing hook {hook_name}: {e}")
                # Continue with other hooks
        
        return result

    async def _save_manifest(self):
        """Save plugins manifest to disk."""
        manifest = {
            "plugins": [asdict(metadata) for metadata in self.registry.plugins.values()]
        }
        
        manifest_file = self.plugins_dir / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)

    def list_plugins(self, active_only: bool = False) -> List[dict]:
        """List all installed plugins."""
        plugins = list(self.registry.plugins.values())
        
        if active_only:
            plugins = [p for p in plugins if p.is_active]
        
        return [asdict(plugin) for plugin in plugins]

    def get_plugin(self, plugin_id: str) -> Optional[dict]:
        """Get specific plugin information."""
        if plugin_id in self.registry.plugins:
            return asdict(self.registry.plugins[plugin_id])
        return None

    def list_hooks(self) -> List[dict]:
        """List all available hooks."""
        return [asdict(hook) for hook in self.registry.hook_definitions.values()]

    async def configure_plugin(self, plugin_id: str, config: dict) -> dict:
        """Configure plugin settings."""
        if plugin_id not in self.registry.plugins:
            raise ValueError("Plugin not found")
        
        self.plugin_configs[plugin_id] = config
        
        # Notify plugin of config change
        if plugin_id in self.registry.plugin_instances:
            plugin_instance = self.registry.plugin_instances[plugin_id]
            if hasattr(plugin_instance, 'configure'):
                await plugin_instance.configure(config)
        
        return {"status": "configured", "plugin_id": plugin_id}