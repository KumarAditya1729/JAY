import csv
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable, Any

@dataclass
class ImportResult:
    imported: int = 0
    rejected: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

class ImportEngine:
    """Core Import Engine for parsing, validating, and reporting."""

    def __init__(self):
        self.result = ImportResult()

    def load_csv(self, file_path: str | Path) -> list[dict]:
        path = Path(file_path)
        if not path.exists():
            self.result.errors.append(f"File not found: {file_path}")
            return []
        
        try:
            with open(path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            self.result.errors.append(f"Failed to read CSV {file_path}: {str(e)}")
            return []

    def load_json(self, file_path: str | Path) -> Any:
        path = Path(file_path)
        if not path.exists():
            self.result.errors.append(f"File not found: {file_path}")
            return None
        
        try:
            with open(path, mode="r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.result.errors.append(f"Failed to read JSON {file_path}: {str(e)}")
            return None

    def run_import(self, items: list[Any], processor: Callable[[Any], None]) -> ImportResult:
        """Runs the import processor on each item and catches errors."""
        for i, item in enumerate(items):
            try:
                processor(item)
                self.result.imported += 1
            except ValueError as e:
                self.result.rejected += 1
                self.result.warnings.append(f"Row {i} rejected: {str(e)}")
            except Exception as e:
                self.result.rejected += 1
                self.result.errors.append(f"Row {i} error: {str(e)}")
                
        return self.result

    def print_report(self):
        print("\n=== IMPORT REPORT ===")
        print(f"Imported: {self.result.imported}")
        print(f"Rejected: {self.result.rejected}")
        
        if self.result.warnings:
            print("\nWarnings:")
            for w in self.result.warnings[:10]:
                print(f" - {w}")
            if len(self.result.warnings) > 10:
                print(f" ... and {len(self.result.warnings) - 10} more.")
                
        if self.result.errors:
            print("\nErrors:")
            for e in self.result.errors[:10]:
                print(f" - {e}")
            if len(self.result.errors) > 10:
                print(f" ... and {len(self.result.errors) - 10} more.")
        print("=====================\n")
