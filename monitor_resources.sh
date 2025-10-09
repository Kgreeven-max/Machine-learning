#!/bin/bash
# Resource monitor for benchmark tests
# Monitors Docker container resource usage during benchmarks

OUTPUT_FILE="resource_usage_$(date +%Y%m%d_%H%M%S).log"

echo "========================================"
echo "Resource Monitor Started"
echo "Time: $(date)"
echo "Output: $OUTPUT_FILE"
echo "========================================"
echo ""
echo "Monitoring Docker containers every 2 seconds..."
echo "Press Ctrl+C to stop"
echo ""

# Header
echo "Timestamp,Container,CPU%,MemUsage,MemLimit,Mem%,NetI/O,BlockI/O,PIDs" > "$OUTPUT_FILE"

# Monitor loop
while true; do
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    docker stats --no-stream --format "{{.Container}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}},{{.PIDs}}" | while IFS= read -r line; do
        echo "$TIMESTAMP,$line" >> "$OUTPUT_FILE"
    done
    sleep 2
done
