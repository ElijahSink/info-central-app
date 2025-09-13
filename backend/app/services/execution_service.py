import asyncio
import subprocess
import tempfile
import os
import json
from typing import Dict, Any
from datetime import datetime
import sys


class ExecutionService:
    """Service for executing AI-generated block code in isolated processes."""
    
    def __init__(self):
        self.generated_code_dir = "generated_code/blocks"
        os.makedirs(self.generated_code_dir, exist_ok=True)
    
    async def execute_block(self, block_id: int, version: int, code: str) -> Dict[str, Any]:
        """Execute block code in an isolated subprocess."""
        
        # Create version-specific directory
        block_dir = os.path.join(self.generated_code_dir, f"{block_id}", f"v{version}")
        os.makedirs(block_dir, exist_ok=True)
        
        # Write code to file
        code_file = os.path.join(block_dir, "block_executor.py")
        with open(code_file, 'w') as f:
            f.write(self._wrap_code(code))
        
        # Create execution script
        exec_script = self._create_execution_script(code_file)
        script_file = os.path.join(block_dir, "execute.py")
        with open(script_file, 'w') as f:
            f.write(exec_script)
        
        try:
            # Execute in subprocess with timeout
            process = await asyncio.create_subprocess_exec(
                sys.executable, script_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd(),  # Restrict to current directory
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=30.0  # 30 second timeout
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown execution error"
                raise Exception(f"Block execution failed: {error_msg}")
            
            # Parse JSON output
            try:
                result = json.loads(stdout.decode())
                return result
            except json.JSONDecodeError:
                raise Exception("Block did not return valid JSON")
                
        except asyncio.TimeoutError:
            raise Exception("Block execution timed out")
        except Exception as e:
            raise Exception(f"Execution error: {str(e)}")
    
    def _wrap_code(self, code: str) -> str:
        """Wrap user code with safety checks and imports."""
        wrapper = '''
import sys
import os
import json
import asyncio
from typing import Dict, Any

# Restrict imports to allowed packages only
ALLOWED_PACKAGES = {
    'requests', 'httpx', 'beautifulsoup4', 'bs4', 'pandas', 'numpy', 
    'dateutil', 'jmespath', 'json', 'datetime', 'time', 'urllib', 're',
    'math', 'statistics', 'collections', 'itertools', 'functools',
    'typing', 'asyncio', 'aiohttp'
}

# Override __import__ to restrict package loading
original_import = __builtins__.__import__

def restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    base_name = name.split('.')[0]
    if base_name not in ALLOWED_PACKAGES and not base_name.startswith('_'):
        # Allow standard library modules that are safe
        try:
            return original_import(name, globals, locals, fromlist, level)
        except ImportError:
            raise ImportError(f"Package '{name}' is not allowed")
    return original_import(name, globals, locals, fromlist, level)

__builtins__.__import__ = restricted_import

# User code starts here
''' + code + '''

# Execution wrapper
async def main():
    try:
        executor = BlockExecutor()
        
        # Fetch data
        raw_data = await executor.fetch_data()
        
        # Process data
        processed_data = await executor.process_data(raw_data)
        
        # Return result as JSON
        print(json.dumps(processed_data, default=str))
        
    except Exception as e:
        error_result = {
            "error": True,
            "message": str(e),
            "type": type(e).__name__
        }
        print(json.dumps(error_result, default=str))
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
'''
        return wrapper
    
    def _create_execution_script(self, code_file: str) -> str:
        """Create a script that executes the block code safely."""
        return f'''
import sys
import os
import subprocess

# Execute the block code
try:
    exec(open("{code_file}").read())
except Exception as e:
    import json
    error_result = {{
        "error": True,
        "message": str(e),
        "type": type(e).__name__
    }}
    print(json.dumps(error_result, default=str))
    sys.exit(1)
'''
    
    def cleanup_old_versions(self, block_id: int, keep_versions: int = 5):
        """Clean up old version directories, keeping only the most recent."""
        block_dir = os.path.join(self.generated_code_dir, str(block_id))
        
        if not os.path.exists(block_dir):
            return
        
        # Get all version directories
        version_dirs = []
        for item in os.listdir(block_dir):
            if item.startswith("v") and os.path.isdir(os.path.join(block_dir, item)):
                try:
                    version_num = int(item[1:])  # Remove 'v' prefix
                    version_dirs.append((version_num, item))
                except ValueError:
                    continue
        
        # Sort by version number and keep only recent ones
        version_dirs.sort(reverse=True)
        to_remove = version_dirs[keep_versions:]
        
        for version_num, dir_name in to_remove:
            import shutil
            dir_path = os.path.join(block_dir, dir_name)
            try:
                shutil.rmtree(dir_path)
            except Exception:
                pass  # Ignore cleanup errors