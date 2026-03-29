import subprocess
import json
import os
import stat

def handler(event, context):
    try:
        # Find the binary relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        kubectl_path = os.path.join(script_dir, 'kubectl')
        
        # Diagnostic logging
        print(f"Script dir: {script_dir}")
        print(f"Kubectl path: {kubectl_path}")
        print(f"Exists: {os.path.exists(kubectl_path)}")
        
        if not os.path.exists(kubectl_path):
            print(f"Contents of {script_dir}: {os.listdir(script_dir)}")
            # Try searching for it in common locations or subdirs
            found = False
            for root, dirs, files in os.walk(os.environ.get('LAMBDA_TASK_ROOT', script_dir)):
                if 'kubectl' in files:
                    kubectl_path = os.path.join(root, 'kubectl')
                    print(f"Found kubectl at: {kubectl_path}")
                    found = True
                    break
            if not found:
                 # Last resort: try just 'kubectl' if it's in PATH
                 kubectl_path = 'kubectl'

        # Ensure the binary is executable if it's a file path
        if os.path.isabs(kubectl_path) and os.path.exists(kubectl_path):
            st = os.stat(kubectl_path)
            os.chmod(kubectl_path, st.st_mode | stat.S_IEXEC)

        # Execute kubectl version command
        result = subprocess.run(
            [kubectl_path, "version", "--client", "-o", "json"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
             return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "kubectl execution failed",
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "path": kubectl_path,
                    "exists": os.path.exists(kubectl_path) if os.path.isabs(kubectl_path) else "N/A"
                })
            }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": result.stdout
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": str(e),
                "trace": str(type(e)),
                "dir_contents": os.listdir(os.getcwd()) if os.path.exists(os.getcwd()) else "N/A",
                "script_dir": os.path.dirname(os.path.abspath(__file__))
            })
        }
