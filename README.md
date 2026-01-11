# Energy Flow Wall

PSoC 5 LED control system with interrupt-driven input and power management capabilities.

## Overview

This project demonstrates an embedded system design featuring:
- Interrupt-driven input handling
- Dynamic LED blinking patterns
- Power-efficient deep sleep mode
- Event-based state transitions

## Features

- **Normal Operation**: LED blinks continuously at 1 Hz
- **Event Response**: On button press, LED blinks 3 times at 10 Hz then enters deep sleep
- **Power Management**: Ultra-low power hibernate mode (~1-2µA)
- **Wake on Interrupt**: System wakes from deep sleep on input event
- **Visual Feedback**: Different blink patterns indicate system states

## Hardware Requirements

- **PSoC 5 Development Board**
- **Components (configured in TopDesign.cysch):**
  - Digital Input Pin (InputPin) - connected to button/switch
  - Interrupt Component (InputInterrupt)
  - Digital Output Pin (OutputPinSW) - connected to LED

## Blink Patterns

| Pattern | Frequency | Count | Meaning |
|---------|-----------|-------|---------|
| Power-up | 5 Hz | 2 blinks | System initialized |
| Normal | 1 Hz | Continuous | Active, waiting for input |
| Event | 10 Hz | 3 blinks | Input detected, entering sleep |

## Power Modes

| Mode | Current Draw | Wake Source |
|------|--------------|-------------|
| Active | ~1-20 mA | N/A |
| Hibernate | ~1-2 µA | External interrupt |

## Getting Started

1. Open the project in PSoC Creator
2. Configure hardware components in TopDesign.cysch
3. Build and program the PSoC 5 device
4. Press the input button to trigger event mode

## Project Structure

```
Energy_Flow_Wall/
├── main.c          # Main source code
├── REFERENCE.md    # Detailed technical reference
└── README.md       # This file
```

## Documentation

For detailed technical information, modification guides, and API reference, see [REFERENCE.md](REFERENCE.md).

## Code Overview

```c
// Simple usage example
void main(void) {
    CyGlobalIntEnable;
    InputInterrupt_StartEx(SWPin_Control);
    Blink(2, 5);  // Power-up indication

    for(;;) {
        if(inputEvent == 0) {
            // Normal 1 Hz blinking
        } else {
            // Event handling + deep sleep
        }
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

## License

This project is provided as-is for educational and development purposes.

## Author

Created: 2026-01-12
