#include "project.h"

/* Set by ISR when input event occurs */
volatile uint8 inputEvent = 0;

/* ------------------------------------------------- */
/* Helper: LED blinking                              */
/* ------------------------------------------------- */
void Blink(uint8 times, uint16 freqHz)
{
    uint16 delayMs = 500 / freqHz;

    for(uint8 i = 0; i < times; i++)
    {
        OutputPinSW_Write(1);
        CyDelay(delayMs);
        OutputPinSW_Write(0);
        CyDelay(delayMs);
    }
}

/* ------------------------------------------------- */
/* Interrupt Service Routine                         */
/* ------------------------------------------------- */
CY_ISR(SWPin_Control)
{
    InputPin_ClearInterrupt();
    inputEvent = 1;
}

/* ------------------------------------------------- */
/* Main                                              */
/* ------------------------------------------------- */
int main(void)
{
    CyGlobalIntEnable;

    /* Start interrupt component */
    InputInterrupt_StartEx(SWPin_Control);

    /* Power-up indication: 2 blinks @ 5 Hz */
    Blink(2, 5);

    for(;;)
    {
        if(inputEvent == 0)
        {
            /* Normal operation: 1 Hz blink */
            OutputPinSW_Write(1);
            CyDelay(500);
            OutputPinSW_Write(0);
            CyDelay(500);
        }
        else
        {
            inputEvent = 0;

            /* Event indication: 3 blinks @ 10 Hz */
            Blink(3, 10);

            /* Prepare for DeepSleep */
            OutputPinSW_Write(0);          /* LED off */
            InputPin_ClearInterrupt();     /* clear pending edge */

            /* -------- ENTER DEEPSLEEP (PSoC 5 WAY) -------- */
            CyPmSaveClocks();
            CyPmHibernate();
            //CyPmSleep(PM_SLEEP_TIME_NONE, PM_SLEEP_SRC_PICU);
            CyPmRestoreClocks();
            /* -------- WAKES HERE -------- */
        }
    }
}
