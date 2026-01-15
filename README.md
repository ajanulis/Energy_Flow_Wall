# Energy Flow Wall

PSoC 5 LED control system with interrupt-driven input and power management capabilities.

## Overview

This project demonstrates an embedded system design featuring:
- Interrupt-driven input handling
- UART command protocol for remote control
- Dynamic LED blinking patterns
- Power-efficient deep sleep mode
- Event-based state transitions

## Features

- **Normal Operation**: LED blinks continuously at 1 Hz
- **UART Control**: Send "LED:X:Y" commands via serial to control blink patterns
- **Visual Feedback**: Different blink patterns indicate system states
- **Extensible Protocol**: Device-based command format supports future expansion
- **Mesh Network Integration**: Works with NC1000 mesh network nodes via UART

## Current Status

✅ **Working**: UART command parsing and LED control
⏸️ **Not implemented yet**: Sleep mode and interrupt-based wake (disabled for testing)

## Hardware Requirements

- **PSoC 5 Development Board** (CY8C5888LTQ-LP097)
- **NC1000 Mesh Network Module**
- **Components (configured in TopDesign.cysch):**
  - Digital Output Pin (OutputPinSW) - connected to LED
  - UART_1 Component - serial communication (115200 baud, 8N1)
  - Digital Input Pin (InputPin) - for CTS/wake (currently disabled)
  - Interrupt Component (InputInterrupt) - for wake from sleep (currently disabled)

## Hardware Connections

**CRITICAL:** Common ground is required for UART communication!

```
NC1000          PSoC 5
------          ------
GND      -----> GND     (MUST be connected!)
TX       -----> RX      (UART receive)
CTS      -----> InputPin (Interrupt/wake - currently disabled)
```

## Blink Patterns

| Pattern | Frequency | Count | Meaning |
|---------|-----------|-------|---------|
| Power-up | 5 Hz | 2 blinks | System initialized |
| Normal | 1 Hz | Continuous | Active, waiting for UART command |
| UART Command | Variable | Variable | Executes LED:X:Y command, then resumes normal |

## UART Commands

Send commands via serial port (115200 baud) in this format:
```
LED:X:Y
```

**Examples:**
- `LED:5:10` - Blink 5 times at 10 Hz, then sleep
- `LED:1:1` - Single slow blink, then sleep
- `LED:10:20` - 10 fast blinks, then sleep

**Parameters:**
- X = Blink count (1-100)
- Y = Frequency in Hz (1-100)
- Commands must end with newline (`\n`) or carriage return (`\r`)

See [REFERENCE.md](REFERENCE.md) for complete command protocol documentation.

## Power Modes

| Mode | Current Draw | Wake Source |
|------|--------------|-------------|
| Active | ~1-20 mA | N/A |
| Hibernate | ~1-2 µA | External interrupt |

## Getting Started

### Hardware Setup
1. Open the project in PSoC Creator
2. Configure hardware components in TopDesign.cysch
3. Build and program the PSoC 5 device
4. Connect UART pins to serial interface (115200 baud)

### Usage
- **Normal Mode**: Device blinks LED at 1 Hz continuously
- **Button Control**: Press input button for 3 blinks @ 10 Hz, then sleep
- **UART Control**: Send commands like `LED:5:10\n` via serial terminal

### Testing UART Commands
```bash
# Linux/Mac terminal
echo "LED:5:10" > /dev/ttyUSB0

# Python
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200)
ser.write(b'LED:5:10\n')
```

## Project Structure

```
Energy_Flow_Wall/
├── main.c           # Main source code with UART parsing
├── TopDesign.cysch  # PSoC Creator hardware configuration
├── REFERENCE.md     # Detailed technical reference
└── README.md        # This file
```

## Documentation

For detailed technical information, modification guides, and API reference, see [REFERENCE.md](REFERENCE.md).

## Code Overview

```c
// Simple usage example
void main(void) {
    CyGlobalIntEnable;
    InputInterrupt_StartEx(SWPin_Control);
    UART_1_Start();  // Initialize UART
    Blink(2, 5);     // Power-up indication

    for(;;) {
        // Check for UART commands
        if(UART_1_GetRxBufferSize() > 0) {
            // Parse "LED:X:Y" commands
        }

        // Handle button events
        if(inputEvent) {
            // Event handling + deep sleep
        }

        // Normal operation
        // 1 Hz blinking
    }
}
```

## Future Development

This repository serves as a reference for future modifications and enhancements. See [REFERENCE.md](REFERENCE.md) for modification guides including:
- Changing blink patterns
- Adjusting sleep modes
- Adding multiple input events
- Implementing state machines
- Input debouncing
- Adding new device types (MOTOR, SENSOR, etc.) to command protocol
- UART response/acknowledgment messages
- Command queuing and scheduling

## License

This project is provided as-is for educational and development purposes.

## Author

Created: 2026-01-12
