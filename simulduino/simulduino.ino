#define PIN_AVANCE 3
#define PIN_MONTE_BAISSE 5
#define PIN_FIN_COURSE 6
#define PIN_LECTURE_MONTE_BAISSE 2

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(PIN_AVANCE, OUTPUT);
  setPwmFrequency(PIN_AVANCE, 1024); // 30Hz cad 3 fois plus que la réalité.
  analogWrite(PIN_AVANCE, 128);
  
  pinMode(PIN_MONTE_BAISSE, OUTPUT);
  setPwmFrequency(PIN_MONTE_BAISSE, 1024); // 60Hz cad comme la réalité
  analogWrite(PIN_MONTE_BAISSE, 128);
  pinMode(PIN_MONTE_BAISSE, OUTPUT);
  
  pinMode(PIN_FIN_COURSE, OUTPUT);
  analogWrite(PIN_FIN_COURSE,LOW);

  pinMode(PIN_LECTURE_MONTE_BAISSE, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_LECTURE_MONTE_BAISSE), interuption, RISING);
}

int compteur = 0;

void interuption(){
  compteur++;
  if (compteur == 150){
    digitalWrite(PIN_FIN_COURSE, HIGH);
    Serial.println("FIN DE COURSE");
  }
  if (compteur == 160){
    digitalWrite(PIN_FIN_COURSE, LOW);
    compteur = 0;
  }
}

void loop() {
  // put your main code here, to run repeatedly:

}


void setPwmFrequency(int pin, int divisor) {
   byte mode;
   if(pin == 5 || pin == 6 || pin == 9 || pin == 10) {
      switch(divisor) {
         case 1: mode = 0x01; break;
         case 8: mode = 0x02; break;
         case 64: mode = 0x03; break;
         case 256: mode = 0x04; break;
         case 1024: mode = 0x05; break;
         default: return;
      }
      if(pin == 5 || pin == 6) {
         TCCR0B = TCCR0B & 0b11111000 | mode;
      } else {
         TCCR1B = TCCR1B & 0b11111000 | mode;
      }
   } else if(pin == 3 || pin == 11) {
      switch(divisor) {
         case 1: mode = 0x01; break;
         case 8: mode = 0x02; break;
         case 32: mode = 0x03; break;
         case 64: mode = 0x04; break;
         case 128: mode = 0x05; break;
         case 256: mode = 0x06; break;
         case 1024: mode = 0x7; break;
         default: return;
      }
      TCCR2B = TCCR2B & 0b11111000 | mode;
   }
}
