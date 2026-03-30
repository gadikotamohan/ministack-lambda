import subprocess
import json
import os
import stat

def handler(event, context):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        kubectl_path = os.path.join(script_dir, 'kubectl')
        
        # Ensure the binary is executable
        if os.path.exists(kubectl_path):
            st = os.stat(kubectl_path)
            os.chmod(kubectl_path, st.st_mode | stat.S_IEXEC)

        # Execute kubectl version command
        result = subprocess.run(
            [kubectl_path, "version", "--client", "-o", "json"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # If kubectl succeeded, we return its JSON output as the body
        if result.returncode == 0:
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": result.stdout.strip()
            }
        else:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "kubectl failed",
                    "stderr": result.stderr,
                    "stdout": result.stdout
                })
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
