const int pinNegativo = 2; // El pin digital donde está conectada la salida del caudalímetro del electrolito negativo.
const int pinPositivo = 3; // El pin digital donde está conectada la salida del caudalímetro del electrolito positivo.

volatile unsigned int contadorPulsosNegativo = 0;
volatile unsigned int contadorPulsosPositivo = 0;

unsigned long tiempoAnterior = 0;
unsigned long intervalo = 1000000; // Intervalo en usegundos para calcular la frecuencia

int caudalnegativo = 0;
int caudalpositivo = 0;
const unsigned int FACTOR_MILIS = 1000;
const unsigned int MSG_SIZE = 1000;


String REQ_INFO = String("IDN*?");
String REQ_MEAS = String(":MEASure:FLOW?");
String SEND_MEAS = String(":MEASure:FLOW:DATA");
String ERROR = String("SCPI:ERROR");

char msg[MSG_SIZE];

void setup() {

  Serial.begin(9600);

  while (!Serial) {
    Serial.println("Init flow meter");
  }
  pinMode(pinNegativo, INPUT_PULLUP);
  pinMode(pinPositivo, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(pinNegativo), contadorPulsosNegativo, FALLING);
  attachInterrupt(digitalPinToInterrupt(pinPositivo), contadorPulsosPositivo, FALLING);

}
void process_scpi(void){
    if(Serial.available()) {
      String req = Serial.readStringUntil('\n');
      int res = 0;
      if ( req.equals(REQ_MEAS)){
        String resp = String(SEND_MEAS + ' ' + String(caudalpositivo) + ' ' + String(caudalnegativo)+'\n');
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

 unsigned long tiempoActual = micros();

  if (tiempoActual - tiempoAnterior >= intervalo) {

    unsigned int pulsosNegativo = contadorPulsosNegativo; 
    unsigned int pulsosPositivo = contadorPulsosPositivo; 
    contadorPulsosNegativo = 0;
    contadorPulsosPositivo = 0;
    tiempoAnterior = tiempoActual;
    caudalnegativo = (pulsosNegativo*60/1420.0) * FACTOR_MILIS;
    caudalpositivo = (pulsosPositivo*60/1420.0) * FACTOR_MILIS;
    
  }

  process_scpi();
  
}

  /*
  //if (Serial.available() > 0 && softSerial.available() > 0){
    String mensaje = softSerial.readStringUntil('\n');

    if (mensaje == ":MEASure:FLOW?"){
      softSerial.println("Caudal positivo: ");
      Serial.println(caudalpositivo);
      softSerial.println("Caudal negativo: ");
      Serial.println(caudalnegativo);
    }
  }
  */

void contadorNeg() {
  contadorPulsosNegativo++;
}

void contadorPos() {
  contadorPulsosPositivo++;
}
