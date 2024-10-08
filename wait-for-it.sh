#!/bin/bash
set -o errexit # Exit on any command that returns a non-zero status.

: "${LOCALSTACK:=localhost:4566}"
: "${TIMEOUT:=500}" # 500 seconds timeout


echo "Waiting for LocalStack..."
wait-for-it --service $LOCALSTACK/health --timeout $TIMEOUT

echo "Checking LocalStack readiness..."
start_time=$(date +%s)

while true; do
    # Using wget to fetch the init status
    if wget -q -O - "http://$LOCALSTACK/_localstack/init" | grep '"READY": true' > /dev/null; then
        echo "LocalStack is ready."
        break
    else
        echo "Waiting for LocalStack to become ready..."
        sleep 5
    fi

    current_time=$(date +%s)
    if (( current_time - start_time >= TIMEOUT )); then
        echo "Timeout reached. LocalStack did not become ready in time."
        exit 1
    fi
done

# Execute the passed command
exec "$@"
