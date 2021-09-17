Overview
============

This repoository contains CircuitPython code for logging carbon dioxide data from a Winsen MH-Z14A carbon dioxide sensor with an AdaFruit PyPortal Titano display. The code is a work in progress.  

The objective of the project is to communicated with the MH-Z14A over UART, write results to the Titano's display, and log the data to a Google Sheet.

Wiring is:  

PyPortal Titano ---  MH-Z14A
GND             ---  16 (this is the pin located on the far end of the connector D3 from the D3 label on the silkscreen)
5V              ---  17 (note that with the default PyPortal wiring, there is 5V output on the pin immediately abov pin D3) 
D3              ---  18
D4              ---  19 (note that D4 is actually the fartest pin from the label D4 on the D4 connector)
