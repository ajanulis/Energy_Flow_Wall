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
- **Event-Triggered Mode**: On input interrupt, blink 3x @ 10 Hz then enter deep sleep
- **Power Management**: Uses PSoC 5 deep sleep (hibernate) mode
- **Interrupt-Driven Input**: Uses external interrupt for input detection

---

## Hardware Components

### Input Components
- **InputPin**: Digital input pin connected to external switch/button
- **InputInterrupt**: Interrupt component triggered by InputPin edge detection

### Output Components
- **OutputPinSW**: Digital output pin controlling LED

### Configuration
- Input interrupt triggers on edge (rising/falling - set in TopDesign)
- Global interrupts must be enabled for ISR operation

---

## Global Variables

### `volatile uint8 inputEvent`
- **Type:** `volatile uint8` (must be volatile for ISR communication)
- **Purpose:** Flag set by ISR when input event occurs
- **Values:**
  - `0`: No event, normal operation
  - `1`: Event detected, trigger special mode
- **Access:** Read/write from main loop, written by ISR

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
Blink(2, 5);                          // Power-up indication
```

**Main Loop Logic:**
- **If no event** (`inputEvent == 0`):
  - Blink LED at 1 Hz manually (500ms ON, 500ms OFF)

- **If event detected** (`inputEvent == 1`):
  1. Clear event flag
  2. Blink 3x at 10 Hz (event indication)
  3. Turn LED off
  4. Clear any pending interrupts
  5. Enter deep sleep (hibernate)
  6. Wake on next interrupt
  7. Resume normal operation

---

## Program Flow

```
START
  ↓
Enable Global Interrupts
  ↓
Start Input Interrupt (ISR attached)
  ↓
Power-up Blink (2x @ 5Hz)
  ↓
┌─────────────────────────────────┐
│   MAIN LOOP                     │
│                                 │
│  inputEvent == 0?               │
│    YES → Normal 1Hz Blink       │
│    NO  → Event Handler:         │
│           • 3 Blinks @ 10Hz     │
│           • Enter Deep Sleep    │
│           • Wake on Interrupt   │
│                                 │
└─────────────────────────────────┘
       ↑                    │
       └────────────────────┘
           (infinite loop)

ISR (async): InputPin edge → set inputEvent = 1
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
