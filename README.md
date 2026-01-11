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
- **Button Response**: On button press, LED blinks 3 times at 10 Hz then enters deep sleep
- **Power Management**: Ultra-low power hibernate mode (~1-2µA)
- **Wake on Interrupt**: System wakes from deep sleep on button press
- **Visual Feedback**: Different blink patterns indicate system states
- **Extensible Protocol**: Device-based command format supports future expansion

## Hardware Requirements

- **PSoC 5 Development Board**
- **Serial connection** (USB-UART or direct UART, 115200 baud)
- **Components (configured in TopDesign.cysch):**
  - Digital Input Pin (InputPin) - connected to button/switch
  - Interrupt Component (InputInterrupt)
  - Digital Output Pin (OutputPinSW) - connected to LED
  - UART_1 Component - serial communication (115200 baud, 8N1)

## Blink Patterns

| Pattern | Frequency | Count | Meaning |
|---------|-----------|-------|---------|
| Power-up | 5 Hz | 2 blinks | System initialized |
| Normal | 1 Hz | Continuous | Active, waiting for input |
| Button Event | 10 Hz | 3 blinks | Button pressed, entering sleep |
| UART Command | Variable | Variable | Executes LED:X:Y command, then sleep |

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
