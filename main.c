#include "project.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Set by ISR when input event occurs */
volatile uint8 inputEvent = 0;

/* UART command buffer */
#define CMD_BUFFER_SIZE 32
char cmdBuffer[CMD_BUFFER_SIZE];
uint8 cmdIndex = 0;
volatile uint8 uartCmdReady = 0;

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
/* UART Command Parser                               */
/* ------------------------------------------------- */
/* Parses "LED:X:Y" format where X=blink count, Y=freq */
uint8 ParseLEDCommand(char* cmd, uint8* blinkCount, uint16* freqHz)
{
    char* token;
    char cmdCopy[CMD_BUFFER_SIZE];

    /* Make a copy since strtok modifies the string */
    strncpy(cmdCopy, cmd, CMD_BUFFER_SIZE - 1);
    cmdCopy[CMD_BUFFER_SIZE - 1] = '\0';

    /* Parse device identifier */
    token = strtok(cmdCopy, ":");
    if(token == NULL || strcmp(token, "LED") != 0)
        return 0;  /* Invalid device */

    /* Parse blink count */
    token = strtok(NULL, ":");
    if(token == NULL)
        return 0;  /* Missing blink count */
    *blinkCount = (uint8)atoi(token);

    /* Parse frequency */
    token = strtok(NULL, ":");
    if(token == NULL)
        return 0;  /* Missing frequency */
    *freqHz = (uint16)atoi(token);

    /* Validate ranges */
    if(*blinkCount == 0 || *blinkCount > 100)
        return 0;  /* Invalid blink count */
    if(*freqHz == 0 || *freqHz > 100)
        return 0;  /* Invalid frequency */

    return 1;  /* Success */
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
    uint8 blinkCount;
    uint16 freqHz;
    char rxChar;

    CyGlobalIntEnable;

    /* Start interrupt component */
    InputInterrupt_StartEx(SWPin_Control);

    /* Start UART */
    UART_1_Start();

    /* Power-up indication: 2 blinks @ 5 Hz */
    Blink(2, 5);

    for(;;)
    {
        /* Check for UART data */
        if(UART_1_GetRxBufferSize() > 0)
        {
            rxChar = UART_1_GetChar();

            /* Check for end of command (newline or carriage return) */
            if(rxChar == '\n' || rxChar == '\r')
            {
                if(cmdIndex > 0)
                {
                    cmdBuffer[cmdIndex] = '\0';  /* Null terminate */
                    uartCmdReady = 1;
                    cmdIndex = 0;
                }
            }
            /* Add character to buffer */
            else if(cmdIndex < CMD_BUFFER_SIZE - 1)
            {
                cmdBuffer[cmdIndex++] = rxChar;
            }
            else
            {
                /* Buffer overflow, reset */
                cmdIndex = 0;
            }
        }

        /* Handle UART command */
        if(uartCmdReady)
        {
            uartCmdReady = 0;

            /* Try to parse LED command */
            if(ParseLEDCommand(cmdBuffer, &blinkCount, &freqHz))
            {
                /* Execute the commanded pattern */
                Blink(blinkCount, freqHz);

                /* Prepare for DeepSleep */
                OutputPinSW_Write(0);          /* LED off */
                InputPin_ClearInterrupt();     /* clear pending edge */

                /* -------- ENTER DEEPSLEEP (PSoC 5 WAY) -------- */
                CyPmSaveClocks();
                CyPmHibernate();
                //CyPmSleep(PM_SLEEP_TIME_NONE, PM_SLEEP_SRC_PICU);
                CyPmRestoreClocks();
                /* -------- WAKES HERE -------- */

                /* Restart UART after wake */
                UART_1_Start();
            }
            /* If parse failed, ignore command and continue */
        }

        /* Handle button input event */
        if(inputEvent)
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

            /* Restart UART after wake */
            UART_1_Start();
        }

        /* Normal operation: 1 Hz blink */
        if(!uartCmdReady && !inputEvent)
        {
            OutputPinSW_Write(1);
            CyDelay(500);
            OutputPinSW_Write(0);
            CyDelay(500);
        }
    }
}
