#!/bin/bash
set -e

ENA_PIN=2
ENB_PIN=16
IN1_PIN=5
IN2_PIN=7
IN3_PIN=8
IN4_PIN=13

PINS=($ENA_PIN $ENB_PIN $IN1_PIN $IN2_PIN $IN3_PIN $IN4_PIN)

ensure_pins_low() {
    for pin in "${PINS[@]}"; do
        gpio mode $pin out 2>/dev/null || true
        gpio write $pin 0 2>/dev/null || true
    done
}

check_service() {
    systemctl is-active --quiet kalembang.service
    return $?
}

case "${1:-check}" in
    reset)
        echo "Resetting all motor control pins to LOW..."
        ensure_pins_low
        echo "Done."
        ;;
    check)
        if ! check_service; then
            echo "Service not running - ensuring GPIO pins are LOW..."
            ensure_pins_low
            echo "Safety check complete."
        else
            echo "Service is running - GPIO managed by application."
        fi
        ;;
    watch)
        echo "Starting GPIO safety watch (Ctrl+C to stop)..."
        while true; do
            if ! check_service; then
                ensure_pins_low
            fi
            sleep 10
        done
        ;;
    *)
        echo "Usage: $0 {reset|check|watch}"
        echo "  reset - Force all motor pins LOW immediately"
        echo "  check - Check service and reset pins if not running"
        echo "  watch - Continuously monitor and reset pins if service stops"
        exit 1
        ;;
esac
