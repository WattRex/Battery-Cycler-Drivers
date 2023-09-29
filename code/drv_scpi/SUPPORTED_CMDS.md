# EXAMPLE COMMAND DICTIONARY

## 1. MULTIMETER
|nº| Action | Command
---|--- | ---
1.1 | Information                        | '*IDN?'
1.2 | Read screen                        | 'FETC?'
1.3 | Change voltage DC mode             | 'FUNC VOLT:DC'
1.4 | Change voltage AC mode             | 'FUNC VOLT:AC'
1.5 | Change current DC mode             | 'FUNC CURR:DC'
1.6 | Change current AC mode             | 'FUNC CURR:AC'
1.7 | Send medium value 	             | 'FUNC:VOLT:DC:NPLC 1'
1.8 | Send slow value 	                 | 'FUNC:VOLT:DC:NPLC 10'
1.9 | Send fast value 	                 | 'FUNC:VOLT:DC:NPLC 0.1'
1.10 | Change auto on range voltage DC   | 'FUNC:VOLT:DC:RANGE:AUTO ON'
1.11 | Change auto off range voltage DC  | 'FUNC:VOLT:DC:RANGE:AUTO OFF'
1.12 | Change 200mV   range voltage DC   | 'FUNC:VOLT:DC:RANGE 0.2'
1.13 | Change 2V      range voltage DC   | 'FUNC:VOLT:DC:RANGE 2'
1.14 | Change 20V     range voltage DC   | 'FUNC:VOLT:DC:RANGE 20'
1.15 | Change 200V    range voltage DC   | 'FUNC:VOLT:DC:RANGE 200'
1.16 | Change 1000V   range voltage DC   | 'FUNC:VOLT:DC:RANGE 1000'
1.17 | Change auto on range current DC   | 'FUNC:CURR:DC:RANGE:AUTO ON'
1.18 | Change auto off range current DC  | 'FUNC:CURR:DC:RANGE:AUTO OFF'
1.19 | Change 2mA     range current DC   | 'FUNC:CURR:DC:RANGE 0.002'
1.20 | Change 20mA    range current DC   | 'FUNC:CURR:DC:RANGE 0.02'
1.21 | Change 200mA   range current DC   | 'FUNC:CURR:DC:RANGE 0.2'
1.22 | Change 2A      range current DC   | 'FUNC:CURR:DC:RANGE 2'
1.23 | Change 20A     range current DC   | 'FUNC:CURR:DC:RANGE 20'
1.24 | Change auto on range voltage AC   | 'FUNC:VOLT:AC:RANGE:AUTO ON'
1.25 | Change auto off range voltage AC  | 'FUNC:VOLT:AC:RANGE:AUTO OFF'
1.26 | Change 200mV   range voltage AC   | 'FUNC:VOLT:AC:RANGE 0.2'
1.27 | Change 2V      range voltage AC   | 'FUNC:VOLT:AC:RANGE 2'
1.28 | Change 20V     range voltage AC   | 'FUNC:VOLT:AC:RANGE 20'
1.29 | Change 200V    range voltage AC   | 'FUNC:VOLT:AC:RANGE 200'
1.30 | Change 1000V   range voltage AC   | 'FUNC:VOLT:AC:RANGE 1000'
1.31 | Change auto on range current AC   | 'FUNC:CURR:AC:RANGE:AUTO ON'
1.32 | Change auto off range current AC  | 'FUNC:CURR:AC:RANGE:AUTO OFF'
1.33 | Change 2mA     range current AC   | 'FUNC:CURR:AC:RANGE 0.002'
1.34 | Change 20mA    range current AC   | 'FUNC:CURR:AC:RANGE 0.02'
1.35 | Change 200mA   range current AC   | 'FUNC:CURR:AC:RANGE 0.2'
1.36 | Change 2A      range current AC   | 'FUNC:CURR:AC:RANGE 2'
1.37 | Change 20A     range current AC   | 'FUNC:CURR:AC:RANGE 20'
1.38 | Query auto range voltage DC       | 'FUNC:VOLT:DC:RANGE:AUTO?'
1.39 | Query auto range voltage AC       | 'FUNC:VOLT:AC:RANGE:AUTO?'
1.40 | Query auto range current DC       | 'FUNC:CURR:DC:RANGE:AUTO?'
1.41 | Query auto range current AC       | 'FUNC:CURR:AC:RANGE:AUTO?'


## 2. SOURCE
|nº| Action | Command (principal channel) | Command channel
:---|:--- | :--- | :---
2.1     | Information        | '*IDN?'                  |
2.2     | Lock on     		 | 'SYSTem:LOCK: ON'        | 'SYSTem:LOCK: ON (@**channel**)'
2.3     | Lock off   		 | 'SYSTem:LOCK: OFF'       | 'SYSTem:LOCK: OFF (@**channel**)'
2.4     | Lock? 		     | 'SYSTem:LOCK:Own?'       | 'SYSTem:LOCK:Own? (@**channel**)'
2.5     | Output on 		 | 'OUTPut: ON'             | 'OUTPut: ON (@**channel**)'
2.6     | Ourput off 		 | 'OUTPut: OFF'            | 'OUTPut: OFF (@**channel**)'
2.7     | Output?   		 | 'OUTPut?'                | 'OUTPut? (@**channel**)'
2.8     | Voltaje measure 	 | 'MEASure:VOLTage?'       | 'MEASure:VOLTage? (@**channel**)'
2.9     | Corriente measure  | 'MEASure:CURRent?'       | 'MEASure:CURRent? (@**channel**)'
2.10    | Read current       | 'SYSTem:NOMinal:CURRent?'| 'SYSTem:NOMinal:CURRent? (@**channel**)'
2.11    | Read voltaje       | 'SYSTem:NOMinal:VOLTage?'| 'SYSTem:NOMinal:VOLTage? (@**channel**)'
2.12    | Read power         | 'SYSTem:NOMinal:POWer?'  | 'SYSTem:NOMinal:POWer? (@**channel**)'
2.13    | Read all           | 'MEASure:ARRay?'         | 'MEASure:ARRay? (@**channel**)'
2.14    | Send current value | 'CURRent **value**'    | 'CURRent {current} (@**channel**)'
2.15    | Send voltaje value | 'VOLTage **value**'    | 'VOLTage {voltage} (@**channel**)'

- Value: is equivalent to the value you want to send.
- channel = number of channel


## 3. RS LOAD
|nº| Action | Command
---|--- | ---
3.1 | Information   | '*IDN?'
3.2 | Lock on       | ':SYST:LOCK 1'




## 4. PORTS
Source: /dev/ttyACM0
Multimeter: /dev/tty
RS Pro: /dev/ttyACM1