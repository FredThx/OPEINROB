#define L_MASQUES 255
#define PIN_AVANCE 2
#define PIN_MONTE_BAISSE 3
#define PIN_FIN_COURSE 4

#define RATIO_AVANCE 10 // Rapport de division du signal de l'avance
#define NB_CELLULES 3 //max 8
#define NB_PISTOLETS 3 //max 8
int pin_pistolets[NB_PISTOLETS] = {8,9,10};



byte masques[L_MASQUES]; // On va l'utiliser comme un tore
int pos_masques = 0; //position dans le tableau masques
byte cells;
int position_monte_baisse=0;
int position_haut_monte_baisse = 100;
int distance_pistolet[NB_PISTOLETS];
int seuil_bas_cellules[NB_CELLULES];
int seuil_haut_cellules[NB_CELLULES];
int compteur_avance = 0; // Utilisé pour diviser la frequence de l'avance par RATIO_AVANCE

void setup() {
  Serial.begin(9600);
  //Config pins
  pinMode(PIN_AVANCE, INPUT);
  pinMode(PIN_MONTE_BAISSE, INPUT);
  pinMode(PIN_FIN_COURSE, INPUT);
  // Interuptions sur PIN_AVANCE et PIN_MONTE_BAISSE
  attachInterrupt(digitalPinToInterrupt(PIN_AVANCE), interuption_avance, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_MONTE_BAISSE), interuption_monte_baisse, RISING);
}

void loop() {
  read_serial();
  //Ce serait bien de mettre ça dans interuption (mais UNO = uniquement2
  if (digitalRead(PIN_FIN_COURSE) == HIGH){
    position_monte_baisse = 0;
  }
}

//lecture port série
// Protocole :
// On lit 2 bytes
// [0,a0,a1,a2,b0,b1,b2,d0][1,d1,d2,d3,d4,d5,d6,d7]
//
// a = type de message
// a=000 : etat cellules
// a=010 : set hauteur cellule seuil bas
// a=011 : set hauteur cellule seuil haut
// a=110 : set distance pistolet
// a=001 : INIT
//
// b = index (de la cellule, du pistolet)
//
// d = valeur
//
void read_serial(){
  byte b0, b1, a, b, d;
  if (Serial.available() > 1){
    b0 = Serial.read();
    if (bitRead(b0,0)==1){
      // Si lecture du byte n°2 => on passe
      Serial.println("Invalid 1 st byte received.");
    }else{
      b1 = Serial.read();
      if (bitRead(b1,0)==0){
        // Si lecture du byte n°1 => on passe
      Serial.println("Invalid 2nd byte received.");
      }else{
        Serial.print("2 bytes received : ");
        Serial.print(b0);
        Serial.print(" ");
        Serial.println(b1);
        a = (b0 >> 1) & B00000111;
        Serial.print("Order (a): ");
        Serial.println(a);
        b = (b0 >> 4) & B00000111;
        Serial.print("Index (b): ");
        Serial.println(b);
        d = b1;
        bitWrite(d,0,bitRead(b0,7));
        Serial.print("data (d): ");
        Serial.println(d);

        switch(a){
          case B000:
            //Set cells state
            Serial.print("Set status cells : ");
            printBinary(d);
            Serial.println();
            cells = d;
            break;
          case B010:
            //Set hauteur cellules seuil bas
            Serial.print("Set hauteur seuil bas cell N°");
            Serial.print(b);
            Serial.print(" = ");
            Serial.println(d);
            seuil_bas_cellules[b] = d;
            break;
          case B011:
            //Set hauteur cellules seuil haut
            Serial.print("Set hauteur seuil haut cell N°");
            Serial.print(b);
            Serial.print(" = ");
            Serial.println(d);
            seuil_haut_cellules[b] = d;
            break;
          case B110:
            //Set distance pistolets
            Serial.print("Set distance pistolet n°");
            Serial.print(b);
            Serial.print(" = ");
            Serial.println(d);
            distance_pistolet[b]=d;
            break;
          case B001:
            //INIT
            Serial.println("INIT.");
            for(int i=0;i<L_MASQUES;i++){
              masques[i]=0;
            }
            break;
           default:
            Serial.println("Unknow order!");
        }
      }
    }
  }
}



void interuption_avance(){
  compteur_avance++;
  if (compteur_avance == RATIO_AVANCE){
    tore_shift();
    tore_set(0,cells);
    //Serial.println(pos_masques);
    compteur_avance = 0;
  }
}

void interuption_monte_baisse(){
  byte cells_avant;
  int hauteur;
  position_monte_baisse++;
  //Serial.print(position_monte_baisse);
  for (int p=0;p<NB_PISTOLETS;p++){
    cells_avant = tore_get(distance_pistolet[p]);
    for (int c=0;c<NB_CELLULES;c++){
      if (bitRead(cells_avant,c)==1){
        hauteur = get_hauteur();
        if (hauteur > seuil_bas_cellules[c] && hauteur < seuil_haut_cellules[c] ){
          digitalWrite(pin_pistolets[p], HIGH);
        } else{
          digitalWrite(pin_pistolets[p], LOW);
        }
      } else{
        digitalWrite(pin_pistolets[p], LOW);
      }
    }
  }
}

int get_hauteur(){
  if (position_monte_baisse<position_haut_monte_baisse){
    return position_monte_baisse;
  }else{
    return 2*position_haut_monte_baisse - position_monte_baisse;
  }
}



void print_masques(){
  Serial.print("masque : ");
  for (int i=0;i<L_MASQUES;i++){
    Serial.print(tore_get(i));
    Serial.print("-");
  }
  Serial.println();
}


void tore_shift(){
  pos_masques--;
  if (pos_masques < 0){
    pos_masques = L_MASQUES;
  }
}

byte tore_get(int index){
  return masques[(pos_masques + index)%L_MASQUES];
}

void tore_set(int index, byte val){
  masques[(pos_masques + index)%L_MASQUES]= val;
}


// Pour DEBUG
void printBinary(byte b) {
  for (int i = 7; i >= 0; i-- )
  {
    Serial.print((b >> i) & 0X01);//shift and select first bit
  }
}
