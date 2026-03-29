import subprocess
import json
import os
import stat

def handler(event, context):
    try:
        # Use LAMBDA_TASK_ROOT if available, otherwise current directory
        root = os.environ.get('LAMBDA_TASK_ROOT', os.getcwd())
        kubectl_path = os.path.join(root, 'kubectl')
        
        # Log basic info to help debug (will appear in MiniStack/Lambda logs)
        print(f"Kubectl path: {kubectl_path}")
        print(f"Exists: {os.path.exists(kubectl_path)}")
        
        # Ensure the binary is executable
        if os.path.exists(kubectl_path):
            st = os.stat(kubectl_path)
            os.chmod(kubectl_path, st.st_mode | stat.S_IEXEC)

        # Execute kubectl version command
        # --client=true ensures we don't try to connect to a cluster
        result = subprocess.run(
            [kubectl_path, "version", "--client", "-o", "json"],
            capture_output=True,
            text=True,
            check=False  # Don't throw error automatically to capture output
        )
        
        if result.returncode != 0:
             return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "kubectl execution failed",
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
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
                "trace": str(type(e))
            })
        }
