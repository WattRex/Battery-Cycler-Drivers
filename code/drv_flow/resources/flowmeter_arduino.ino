// Digital pin used for negative flowmeter
#define pin_neg 2

#define FACTOR_MILIS 1000
#define SACLAR_US_2_FREQ 500000 // Factor to convert us to Hz -> 1.000.000/ (2 * semiperiod)
#define FLOW_MAX 10 // 10 L/min 
#define FREQ_MAX 235 // Freq for 10L/min

// Macro to convert freq to flow (Hz -> mL/min)
#define FREQ_2_FLOW(F) (F * FACTOR_MILIS / FREQ_MAX * FLOW_MAX)


volatile uint32_t flow_neg = 0, flow_pos = 0;
volatile uint16_t ov_pos  = 0, ov_neg = 0;
volatile uint32_t rising_ts = 0;
volatile uint8_t is_high_pos = 0;


String REQ_INFO = String("IDN*?");
String REQ_MEAS = String(":MEASure:FLOW?");
String SEND_MEAS = String(":MEASure:FLOW:DATA");
String ERROR = String("SCPI:ERROR");

void edge_isr_neg(void){
  if (is_high_pos){
    uint32_t ts = micros();
    uint32_t freq_neg = (uint32_t) SACLAR_US_2_FREQ / (ts - rising_ts);
    flow_neg = FREQ_2_FLOW(freq_neg); 
  } else{
    rising_ts = micros();
  }
  is_high_pos = 1 - is_high_pos;
}

void setup() {

  Serial.begin(9600);

  while (!Serial) {
    Serial.println("Init flow meter");
  }

  pinMode(pin_neg, INPUT);
  attachInterrupt(digitalPinToInterrupt(pin_neg), edge_isr_neg, CHANGE );

  noInterrupts ();  // protected code
  // reset Timer 1
  // positive flowmeter
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 0;
  TIMSK1 = 0;

  TIFR1 |= _BV(ICF1); // clear Input Capture Flag so we don't get a bogus interrupt
  TIFR1 |= _BV(TOV1); // clear Overflow Flag so we don't get a bogus interrupt

  TCCR1B = _BV(CS10) | // start Timer 1, no prescaler
           _BV(ICES1); // Input Capture Edge Select (1=Rising, 0=Falling)

  TIMSK1 |= _BV(ICIE1); // Enable Timer 1 Input Capture Interrupt
  TIMSK1 |= _BV(TOIE1); // Enable Timer 1 Overflow Interrupt
  interrupts ();
}

ISR(TIMER1_OVF_vect)
{
  ov_pos++;
}

ISR(TIMER1_CAPT_vect)
{
  static uint32_t firstRisingEdgeTime = 0, fallingEdgeTime = 0, secondRisingEdgeTime = 0;
  static uint32_t high_time_pulse = 0, low_time_pulse = 0;
//  ov_pos = 0;
  uint16_t overflows = ov_pos;
  
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
        uint32_t freq_pos = (uint32_t)F_CPU  / (high_time_pulse + low_time_pulse);
      
        flow_pos = FREQ_2_FLOW(freq_pos);
  
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


void process_scpi(void){
    if(Serial.available()) {
      String req = Serial.readStringUntil('\n');
      int res = 0;
      if ( req.equals(REQ_MEAS)){
        String resp = String(SEND_MEAS + ' ' + String(flow_pos) + ' ' + String(flow_neg)+'\n');
        Serial.print(resp);
      } else {
        String resp = String(ERROR + '\n');
        res = Serial.print(resp);
        resp = String(req + '\n');
        res = Serial.print(resp);
      }
  }
}


void loop() {
  process_scpi();
  delay(100);
  
}
