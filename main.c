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
/* NOTE: We do NOT clear interrupt here because CTS */
/* is shared with UART. We only clear before sleep. */
CY_ISR(SWPin_Control)
{
    /* DO NOT clear interrupt here - shared with UART CTS */
    /* InputPin_ClearInterrupt(); */
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

    /* DISABLE interrupt for now - just testing UART */
    /* InputInterrupt_StartEx(SWPin_Control); */
    /* InputInterrupt_Disable(); */

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

                /* Turn LED off after pattern */
                OutputPinSW_Write(0);
            }
            /* If parse failed, ignore and continue */
        }

        /* Normal operation: 1 Hz blink */
        if(!uartCmdReady)
        {
            OutputPinSW_Write(1);
            CyDelay(500);
            OutputPinSW_Write(0);
            CyDelay(500);
        }
    }
}
