#!/bin/bash

  
# Start the second process
python3 -m director &
  
# Start the first process
uvicorn webapi.main:app --host 0.0.0.0 --port 3000 --reload &

# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?