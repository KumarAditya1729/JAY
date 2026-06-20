from typing import Dict, Callable, Any
from jay.tools.schemas import ToolManifest
from jay.tools.core_tools import read_file, write_file, search_files, git_status

class ToolRegistry:
    def __init__(self):
        self.manifests: Dict[str, ToolManifest] = {}
        self.executables: Dict[str, Callable[[dict], str]] = {}
        self._register_core_tools()

    def register(self, manifest: ToolManifest, executable: Callable[[dict], str]):
        self.manifests[manifest.name] = manifest
        self.executables[manifest.name] = executable

    def execute(self, tool_name: str, arguments: dict) -> str:
        if tool_name not in self.executables:
            return f"Error: Tool '{tool_name}' not found."
        return self.executables[tool_name](arguments)

    def get_manifest(self, tool_name: str) -> ToolManifest:
        return self.manifests.get(tool_name)

    def _register_core_tools(self):
        self.register(
            ToolManifest(
                name="read_file",
                description="Read the contents of a file.",
                risk_score=0.1,
                reversibility_score=1.0
            ),
            read_file
        )
        self.register(
            ToolManifest(
                name="write_file",
                description="Write content to a file. Overwrites if exists.",
                risk_score=0.6,
                reversibility_score=0.5
            ),
            write_file
        )
        self.register(
            ToolManifest(
                name="search_files",
                description="Search for files in a directory by glob pattern.",
                risk_score=0.1,
                reversibility_score=1.0
            ),
            search_files
        )
        self.register(
            ToolManifest(
                name="git_status",
                description="Check the git status of the repository.",
                risk_score=0.1,
                reversibility_score=1.0
            ),
            git_status
        )

# Global registry
registry = ToolRegistry()
