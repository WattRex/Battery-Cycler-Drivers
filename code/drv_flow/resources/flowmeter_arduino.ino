// Digital pin used for auxiliar flowmeter
#define pin_aux 2
#define FACTOR_MILIS 1000
#define SACLAR_US_2_FREQ 500000 // Factor to convert us to Hz -> 1.000.000/ (2 * semiperiod)
#define FLOW_MAX 10 // 10 L/min 
#define FREQ_MAX 235 // Freq for 10L/min
#define DEVICE_NUMBER "001"
#define FIRMWARE_VERSION "1"
#define ENDING_CHARS "\n"
#define BAUDRATE 19200
#define MAX_BUFFER_SIZE 100

// Macro to convert freq to flow (Hz -> mL/min)
#define FREQ_2_FLOW(F) (F * FACTOR_MILIS / FREQ_MAX * FLOW_MAX)

volatile uint32_t flow_aux = 0, flow_main = 0;
volatile uint16_t ov_main = 0, ov_aux = 0;
volatile uint32_t rising_ts = 0;
volatile uint8_t is_high_main= 0;
char cadena[MAX_BUFFER_SIZE];
int indice = 0;

char REQ_INFO[] = ":IDN*?";
char REQ_MEAS[] = ":MEASure:FLOW?";
char SEND_INFO[] = ":IDN:FLOWmeter";
char SEND_MEAS[] = ":MEASure:FLOW:DATA:";
char SEND_ERROR[] = ":SCPI:ERROR:";

void edge_isr_aux(void){
  if (is_high_main){
    uint32_t ts = micros();
    uint32_t freq_aux = (uint32_t) SACLAR_US_2_FREQ / (ts - rising_ts);
    flow_aux = FREQ_2_FLOW(freq_aux); 
  } else{
    rising_ts = micros();
  }
  is_high_main = 1 - is_high_main;
}

void setup() {

  Serial.begin(BAUDRATE);

  while (!Serial) {
    Serial.println("Init flow meter");
  }
}

ISR(TIMER1_OVF_vect)
{
  ov_main++;
}

ISR(TIMER1_CAPT_vect)
{
  static uint32_t firstRisingEdgeTime = 0, fallingEdgeTime = 0, secondRisingEdgeTime = 0;
  static uint32_t high_time_pulse = 0, low_time_pulse = 0;
//  ov_main = 0;
  uint16_t overflows = ov_main;
  
  // If an overflow happened but has not been handled yet
  // and the timer count was close to zero, count the
  // overflow as part of this time.
  if ((TIFR1 & _BV(TOV1)) && (ICR1 < 1024))
    overflows++;

  if (low_time_pulse == 0)
  {
    if (TCCR1B & _BV(ICES1))
    {
      // Interrupted on Second Rising Edge
      if (firstRisingEdgeTime)  // Already have the first rising edge...
      {
        // ... so this is the second rising edge, ending the low part
        // of the cycle.
        secondRisingEdgeTime = overflows; // Upper 16 bits
        secondRisingEdgeTime = (secondRisingEdgeTime << 16) | ICR1;
        low_time_pulse = secondRisingEdgeTime - fallingEdgeTime;

        // Reset counters
        uint32_t freq_main = (uint32_t)F_CPU  / (high_time_pulse + low_time_pulse);
      
        flow_main = FREQ_2_FLOW(freq_main);
  
        firstRisingEdgeTime = 0;
        high_time_pulse = 0;
        low_time_pulse = 0;
      }
      else
      {
        // Interrupted on First Rising Edge
        // digitalWrite(4, HIGH);
        firstRisingEdgeTime = overflows; // Upper 16 bits
        firstRisingEdgeTime = (firstRisingEdgeTime << 16) | ICR1;
        TCCR1B &= ~_BV(ICES1); // Switch to Falling Edge
      }
    }
    else
    {
      // Interrupted on Falling Edge
      fallingEdgeTime = overflows; // Upper 16 bits
      fallingEdgeTime = (fallingEdgeTime << 16) | ICR1;
      TCCR1B |= _BV(ICES1); // Switch to Rising Edge
      high_time_pulse = fallingEdgeTime - firstRisingEdgeTime;  
    }
  }
}

void MEAS(char resultado[]) {
  char f_main[20];
  sprintf(f_main, "%lu", flow_main);
  
  char f_aux[20];
  sprintf(f_aux, "%lu", flow_aux);

  strcpy(resultado, SEND_MEAS);
  strcat(resultado, f_main);
  strcat(resultado, ":");
  strcat(resultado, f_aux);
}

void INFO(char resultado[]) {
  strcpy(resultado, SEND_INFO);
  strcat(resultado, ":DEVice:");
  strcat(resultado, DEVICE_NUMBER);
  strcat(resultado, ":VERsion:");
  strcat(resultado, FIRMWARE_VERSION);
}

void ERROR(char resultado[], char msg[]) {
  strcpy(resultado, SEND_ERROR);
  strcat(resultado, msg);
}

void process_scpi(void) {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      char resultado[MAX_BUFFER_SIZE];
      if (strcmp(cadena, REQ_MEAS) == 0) {
        MEAS(resultado);
      } else if (strcmp(cadena, REQ_INFO) == 0) {
        INFO(resultado);
      } else {
        ERROR(resultado, cadena);
      }
      strcat(resultado, ENDING_CHARS);
      resultado[MAX_BUFFER_SIZE - 1] = '\0';
      Serial.print(resultado);
      indice = 0;
      memset(cadena, '\0', sizeof(cadena));
    } else {
      cadena[indice] = c;
      indice++;
    }
  }
}


void loop() {
  process_scpi();
  delay(10);
}