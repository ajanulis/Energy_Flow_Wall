# PSoC 5 Project Reference - LED Control with Power Management

**Last Updated:** 2026-01-12
**Platform:** PSoC 5
**Source File:** main.c

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Hardware Components](#hardware-components)
3. [Global Variables](#global-variables)
4. [Functions Reference](#functions-reference)
5. [Program Flow](#program-flow)
6. [PSoC API Reference](#psoc-api-reference)
7. [Modification Guide](#modification-guide)

---

## Project Overview

This project implements an LED control system with:
- **Normal Operation Mode**: LED blinks at 1 Hz continuously
- **UART Command Mode**: Receives "LED:X:Y" commands via UART to control blink patterns
- **Button Event Mode**: On input interrupt, blink 3x @ 10 Hz then enter deep sleep
- **Power Management**: Uses PSoC 5 deep sleep (hibernate) mode after command execution
- **Interrupt-Driven Input**: Uses external interrupt for button detection
- **Serial Communication**: 115200 baud UART for remote control

---

## Hardware Components

### Input Components
- **InputPin**: Digital input pin connected to external switch/button
- **InputInterrupt**: Interrupt component triggered by InputPin edge detection
- **UART_1**: Serial communication component for receiving commands

### Output Components
- **OutputPinSW**: Digital output pin controlling LED

### Configuration
- Input interrupt triggers on edge (rising/falling - set in TopDesign)
- UART_1 configured for 115200 baud, 8 data bits, no parity, 1 stop bit (8N1)
- Global interrupts must be enabled for ISR operation

---

## Global Variables

### `volatile uint8 inputEvent`
- **Type:** `volatile uint8` (must be volatile for ISR communication)
- **Purpose:** Flag set by ISR when button input event occurs
- **Values:**
  - `0`: No event, normal operation
  - `1`: Event detected, trigger special mode
- **Access:** Read/write from main loop, written by ISR

### `char cmdBuffer[CMD_BUFFER_SIZE]`
- **Type:** `char` array (size 32 bytes)
- **Purpose:** Stores incoming UART command characters
- **Access:** Written by UART receive logic, read by parser

### `uint8 cmdIndex`
- **Type:** `uint8`
- **Purpose:** Tracks current position in command buffer
- **Range:** 0 to CMD_BUFFER_SIZE-1

### `volatile uint8 uartCmdReady`
- **Type:** `volatile uint8`
- **Purpose:** Flag indicating complete UART command received
- **Values:**
  - `0`: No command ready
  - `1`: Command ready for parsing
- **Access:** Set when newline/carriage return received

---

## Functions Reference

### `Blink(uint8 times, uint16 freqHz)`

**Description:** Helper function to blink LED a specified number of times at given frequency.

**Parameters:**
- `times` (uint8): Number of blinks to perform
- `freqHz` (uint16): Blink frequency in Hz

**Behavior:**
- Calculates delay as `delayMs = 500 / freqHz`
- Each blink = ON + OFF cycle
- Blocking function (uses CyDelay)

**Example Usage:**
```c
Blink(2, 5);   // 2 blinks at 5 Hz (100ms ON, 100ms OFF)
Blink(3, 10);  // 3 blinks at 10 Hz (50ms ON, 50ms OFF)
```

**Notes:**
- Delay calculation: 500ms / freq = half-period in ms
- For 5 Hz: 500/5 = 100ms per half-cycle
- For 10 Hz: 500/10 = 50ms per half-cycle

---

### `ParseLEDCommand(char* cmd, uint8* blinkCount, uint16* freqHz)`

**Description:** Parses UART command string in "LED:X:Y" format to extract blink parameters.

**Parameters:**
- `cmd` (char*): Null-terminated command string to parse
- `blinkCount` (uint8*): Pointer to store parsed blink count
- `freqHz` (uint16*): Pointer to store parsed frequency

**Returns:**
- `1`: Command parsed successfully
- `0`: Parse failed (invalid format or out of range)

**Command Format:**
```
LED:X:Y
```
Where:
- **LED**: Device identifier (for future multi-device support)
- **X**: Blink count (1-100)
- **Y**: Frequency in Hz (1-100)

**Example Usage:**
```c
uint8 blinks;
uint16 freq;
if(ParseLEDCommand("LED:5:20", &blinks, &freq)) {
    Blink(blinks, freq);  // Execute 5 blinks at 20 Hz
}
```

**Validation:**
- Device identifier must be "LED"
- Blink count: 1-100 (0 invalid)
- Frequency: 1-100 Hz (0 invalid)
- Missing fields return parse error

**Notes:**
- Uses `strtok()` for parsing (requires string.h)
- Makes internal copy to avoid modifying original command
- Invalid commands are silently ignored

---

### `CY_ISR(SWPin_Control)`

**Description:** Interrupt Service Routine triggered by InputPin edge detection.

**Trigger:** InputPin edge (configured in TopDesign schematic)

**Behavior:**
1. Clear interrupt flag: `InputPin_ClearInterrupt()`
2. Set event flag: `inputEvent = 1`

**Notes:**
- Keep ISR short and fast
- Only sets flag, actual handling in main loop
- Must clear interrupt before exiting

---

### `main()`

**Description:** Main program entry point and infinite loop.

**Initialization:**
```c
CyGlobalIntEnable;                    // Enable global interrupts
InputInterrupt_StartEx(SWPin_Control); // Attach ISR to interrupt
UART_1_Start();                       // Start UART component
Blink(2, 5);                          // Power-up indication
```

**Main Loop Logic:**

1. **UART Receive Handler:**
   - Check for incoming UART data (`UART_1_GetRxBufferSize()`)
   - Build command string character by character
   - Detect command termination (`\n` or `\r`)
   - Set `uartCmdReady` flag when complete

2. **UART Command Handler** (`uartCmdReady == 1`):
   - Parse command using `ParseLEDCommand()`
   - If valid LED:X:Y format:
     1. Execute blink pattern (X blinks at Y Hz)
     2. Turn LED off
     3. Clear pending interrupts
     4. Enter deep sleep (hibernate)
     5. Wake on button interrupt
   - If invalid, ignore and continue

3. **Button Event Handler** (`inputEvent == 1`):
   1. Clear event flag
   2. Blink 3x at 10 Hz (event indication)
   3. Turn LED off
   4. Clear any pending interrupts
   5. Enter deep sleep (hibernate)
   6. Wake on next interrupt

4. **Normal Operation** (no events):
   - Blink LED at 1 Hz manually (500ms ON, 500ms OFF)

---

## Program Flow

```
START
  ↓
Enable Global Interrupts
  ↓
Start Input Interrupt (ISR attached)
  ↓
Start UART_1 (115200 baud)
  ↓
Power-up Blink (2x @ 5Hz)
  ↓
┌──────────────────────────────────────────────────┐
│   MAIN LOOP                                      │
│                                                  │
│  1. Check UART RX Buffer                        │
│     • Receive chars → Build command string      │
│     • On '\n'/'\r' → Set uartCmdReady           │
│                                                  │
│  2. UART Command Ready?                         │
│     YES → Parse "LED:X:Y"                       │
│           Valid?                                │
│             YES → Blink X times @ Y Hz          │
│                   Enter Deep Sleep              │
│             NO  → Ignore, continue              │
│                                                  │
│  3. Button Event (inputEvent == 1)?             │
│     YES → Event Handler:                        │
│           • 3 Blinks @ 10Hz                     │
│           • Enter Deep Sleep                    │
│           • Wake on Interrupt                   │
│                                                  │
│  4. Normal Operation:                           │
│     → 1Hz Blink (500ms ON/OFF)                  │
│                                                  │
└──────────────────────────────────────────────────┘
       ↑                              │
       └──────────────────────────────┘
              (infinite loop)

ISR (async): InputPin edge → set inputEvent = 1
UART (async): Receives characters from serial port
```

---

## PSoC API Reference

### Power Management Functions

#### `CyPmSaveClocks()`
- **Purpose:** Save clock configuration before sleep
- **When:** Call before entering deep sleep
- **Returns:** void

#### `CyPmHibernate()`
- **Purpose:** Enter hibernate (deep sleep) mode
- **Power:** Lowest power mode, ~1-2µA
- **Wake:** External interrupt only
- **Notes:** Execution continues after this call on wake

#### `CyPmRestoreClocks()`
- **Purpose:** Restore clock configuration after wake
- **When:** Call immediately after wake from sleep
- **Returns:** void

#### `CyPmSleep(PM_SLEEP_TIME_NONE, PM_SLEEP_SRC_PICU)`
- **Purpose:** Alternative sleep mode (currently commented out)
- **Power:** Higher power than hibernate, ~2-200µA
- **Wake:** Multiple sources possible
- **Notes:** Faster wake time than hibernate

---

### Timing Functions

#### `CyDelay(uint32 milliseconds)`
- **Purpose:** Blocking delay in milliseconds
- **Accuracy:** Based on system clock
- **Notes:** CPU halted during delay

---

### GPIO Functions

#### `OutputPinSW_Write(uint8 value)`
- **Purpose:** Set output pin state
- **Parameters:**
  - `0`: Logic LOW (LED off)
  - `1`: Logic HIGH (LED on)

#### `InputPin_ClearInterrupt()`
- **Purpose:** Clear pending interrupt flag
- **When:** In ISR and before sleep to avoid immediate wake

---

### Interrupt Functions

#### `CyGlobalIntEnable`
- **Purpose:** Enable global interrupt system (macro)
- **When:** Early in main() before using any interrupts

#### `InputInterrupt_StartEx(CY_ISR_FUNCTION)`
- **Purpose:** Start interrupt component with custom ISR
- **Parameters:** Function pointer to ISR
- **Example:** `InputInterrupt_StartEx(SWPin_Control);`

---

### UART Functions

#### `UART_1_Start()`
- **Purpose:** Initialize and start UART component
- **When:** Call in main() before using UART
- **Configuration:** 115200 baud, 8N1 (configured in TopDesign)
- **Returns:** void

#### `UART_1_GetRxBufferSize()`
- **Purpose:** Check number of bytes in receive buffer
- **Returns:** uint8 - number of unread bytes available
- **Usage:** Poll to check for incoming data

#### `UART_1_GetChar()`
- **Purpose:** Read one character from receive buffer
- **Returns:** char - next character from buffer
- **Notes:** Check buffer size first to avoid blocking

**Example UART Usage:**
```c
UART_1_Start();
while(1) {
    if(UART_1_GetRxBufferSize() > 0) {
        char c = UART_1_GetChar();
        // Process character
    }
}
```

---

## UART Command Protocol

### Command Format

Commands must follow this exact format:
```
LED:X:Y\n
```

Where:
- **LED** - Device identifier (case-sensitive)
- **X** - Blink count (1-100)
- **Y** - Frequency in Hz (1-100)
- **\n** - Newline terminator (or \r)

### Command Examples

| Command | Blink Count | Frequency | Result |
|---------|-------------|-----------|---------|
| `LED:1:1\n` | 1 | 1 Hz | 1 slow blink then sleep |
| `LED:5:10\n` | 5 | 10 Hz | 5 fast blinks then sleep |
| `LED:10:2\n` | 10 | 2 Hz | 10 medium blinks then sleep |
| `LED:3:20\n` | 3 | 20 Hz | 3 very fast blinks then sleep |

### Invalid Commands

These commands will be ignored:
- `led:5:10\n` - Wrong case (must be "LED")
- `LED:5\n` - Missing frequency
- `LED:0:10\n` - Zero blink count
- `LED:5:200\n` - Frequency out of range (>100)
- `MOTOR:5:10\n` - Wrong device ID
- `LED:5:10` - Missing terminator

### Sending Commands

**From terminal (Linux/Mac):**
```bash
echo "LED:5:10" > /dev/ttyUSB0
```

**From Python:**
```python
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200)
ser.write(b'LED:5:10\n')
```

**From Arduino Serial Monitor:**
- Set baud rate to 115200
- Set line ending to "Newline" or "Both NL & CR"
- Type: `LED:5:10`

---

## Modification Guide

### Change Blink Patterns

**Normal mode blink rate:**
```c
// Current: 1 Hz (500ms on, 500ms off)
// To change to 2 Hz:
CyDelay(250);  // Change both delays from 500 to 250
```

**Event blink pattern:**
```c
// Current: 3 blinks @ 10 Hz
Blink(3, 10);

// Change to 5 blinks @ 20 Hz:
Blink(5, 20);
```

**Power-up indication:**
```c
// Current: 2 blinks @ 5 Hz
Blink(2, 5);

// Change as needed
```

---

### Change Sleep Mode

**Use standard sleep instead of hibernate:**
```c
// Comment out hibernate mode:
// CyPmHibernate();

// Uncomment sleep mode:
CyPmSleep(PM_SLEEP_TIME_NONE, PM_SLEEP_SRC_PICU);
```

**Trade-offs:**
- Hibernate: Lower power, slower wake, fewer wake sources
- Sleep: Higher power, faster wake, more wake sources

---

### Add Multiple Input Events

**Example: Different patterns for different buttons:**
```c
volatile uint8 button1Event = 0;
volatile uint8 button2Event = 0;

// In main loop:
if(button1Event) {
    button1Event = 0;
    Blink(3, 10);  // Pattern 1
}
else if(button2Event) {
    button2Event = 0;
    Blink(5, 5);   // Pattern 2
}
```

---

### Add State Machine

**Example: Multiple operating modes:**
```c
typedef enum {
    MODE_NORMAL,
    MODE_FAST_BLINK,
    MODE_SLOW_BLINK,
    MODE_SLEEP
} OperationMode_t;

OperationMode_t currentMode = MODE_NORMAL;

// Change modes based on input events
```

---

### Debounce Input

**Add debouncing to ISR:**
```c
CY_ISR(SWPin_Control)
{
    InputPin_ClearInterrupt();
    CyDelay(50);  // Simple 50ms debounce
    if(InputPin_Read()) {  // Verify still pressed
        inputEvent = 1;
    }
}
```

**Note:** Long delays in ISR are not recommended. Better approach is to debounce in main loop.

---

## Hardware Configuration Notes

### TopDesign.cysch Components Needed:
1. **Digital Input Pin** → InputPin
2. **Interrupt Component** → InputInterrupt (connected to InputPin)
3. **Digital Output Pin** → OutputPinSW
4. **Clock Component** (if using specific timing requirements)

### Pin Configuration:
- InputPin: Configure interrupt type (rising/falling/both edges)
- OutputPinSW: Configure as strong drive for LED

---

## Timing Calculations

### Blink Frequency Formula:
```
delayMs = 500 / freqHz
```

**Examples:**
- 1 Hz → 500ms per half-cycle → 1000ms total period ✓
- 5 Hz → 100ms per half-cycle → 200ms total period ✓
- 10 Hz → 50ms per half-cycle → 100ms total period ✓

### Custom Frequencies:
```c
// 2 Hz (500ms period)
Blink(n, 2);  // 250ms delays

// 0.5 Hz (2 second period)
Blink(n, 0.5);  // Be careful with integer division!
// Better: Use floating point or fixed delays for <1Hz
```

---

## Current Consumption Estimates

| Mode | Typical Current |
|------|----------------|
| Active (LED on) | ~5-20 mA |
| Active (LED off) | ~1-8 mA |
| Hibernate | ~1-2 µA |
| Sleep (alternate) | ~2-200 µA |

---

## Common Issues & Solutions

### Issue: LED doesn't blink
- Check OutputPinSW connection in TopDesign
- Verify LED polarity and current-limiting resistor
- Check if global interrupts enabled

### Issue: Interrupt not triggering
- Verify InputPin interrupt type configuration
- Check `InputInterrupt_StartEx()` called
- Confirm `CyGlobalIntEnable` present

### Issue: Device won't wake from sleep
- Ensure interrupt source configured for wake
- Check `InputPin_ClearInterrupt()` before sleep
- Verify wake source enabled in sleep function parameters

### Issue: Erratic behavior
- Add debouncing to input
- Check for noise on input pin (add pull-up/pull-down)
- Verify power supply stability

---

## Version History

- **1.0.0** (2026-01-12): Initial reference from working main.c
