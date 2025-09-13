
import sys
import os
import subprocess

# Execute the block code
try:
    exec(open("generated_code/blocks/2/v1/block_executor.py").read())
except Exception as e:
    import json
    error_result = {
        "error": True,
        "message": str(e),
        "type": type(e).__name__
    }
    print(json.dumps(error_result, default=str))
    sys.exit(1)
