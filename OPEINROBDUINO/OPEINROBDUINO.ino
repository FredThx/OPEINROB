#include "SerialCommand.h"

#define L_MASQUES 50 //255
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
int position_haut_monte_baisse=0;
int distance_pistolet[NB_PISTOLETS];
int seuil_bas_cellules[NB_CELLULES];
int seuil_haut_cellules[NB_CELLULES];
int compteur_avance = 0; // Utilisé pour diviser la frequence de l'avance par RATIO_AVANCE
bool etat_fin_course = false;

SerialCommand sCmd;

void setup() {
  Serial.begin(9600);
  //Config pins
  pinMode(PIN_AVANCE, INPUT);
  pinMode(PIN_MONTE_BAISSE, INPUT);
  pinMode(PIN_FIN_COURSE, INPUT);
  for (int p=0;p<NB_PISTOLETS;p++){
    pinMode(pin_pistolets[p], OUTPUT);
  }
  // Interuptions sur PIN_AVANCE et PIN_MONTE_BAISSE
  attachInterrupt(digitalPinToInterrupt(PIN_AVANCE), interuption_avance, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_MONTE_BAISSE), interuption_monte_baisse, RISING);
  // valeurs par defauts pour debug
  distance_pistolet[0] = 10;
  distance_pistolet[1] = 20;
  distance_pistolet[2] = 30;
  seuil_bas_cellules[0] = 0;
  seuil_bas_cellules[1] = 30;
  seuil_bas_cellules[2] = 60;
  seuil_haut_cellules[0] = 30;
  seuil_haut_cellules[1] = 60;
  seuil_haut_cellules[2] = 75;

  //Config des commandes serial
  sCmd.addCommand("SC", set_cells); // 1 argument(cells)
  sCmd.addCommand("SHS", set_hauteur_seuil); // 3 arguments(n° cellule, "H"|"B", hauteur)
  sCmd.addCommand("SDP", set_distance_pistolet); // 2 arguments(n° pistolet, distance)
  sCmd.addCommand("INIT", init_masques); // Init
  sCmd.setDefaultHandler(unrecognized);// Handler for command that isn't matched
  sCmd.addCommand("DEBUG", debug);
  sCmd.addCommand("INFO", send_infos);
  Serial.println("Ready!");
}

void loop() {
  sCmd.readSerial();
  //Ce serait bien de mettre ça dans interuption (mais UNO = uniquement2
  if (digitalRead(PIN_FIN_COURSE) == HIGH){
    if (!etat_fin_course){
      etat_fin_course = true;
      interuption_fin_course();
    }
  }else{
    etat_fin_course = false;
  }
}

///////////////////////////////////////
// FUNCTIONS DU PARSER SERIAL
//////////////////////////////////////

void set_cells(){
  /* reponse à SC
   *  1 argument :   "7" pour 0b111
   */
  char *arg;
  int int_val;
  arg = sCmd.next();
  if (arg != NULL && sscanf(arg, "%i", &int_val)){
    cells = int_val; //Globale var
    Serial.print("Set status cells : ");
    printBinary(cells);
    Serial.println();
  } else{
    Serial.println("Error on set_cells.");
  }
}

void set_hauteur_seuil(){
  /* Reponse à SHS
      3 argument :
     - no_cellule   :   ex "1"
     - haut_bas     :   "H" ou "B"
     - hauteur      :   ex "125"
  */
  int no_cellule;
  char haut_bas;
  int hauteur;
  char *arg;
  arg = sCmd.next();
  if (arg != NULL && sscanf(arg,"%i", &no_cellule)){
    arg = sCmd.next();
    if (arg != NULL){
      haut_bas = arg[0];
      arg = sCmd.next();
      if (arg != NULL && sscanf(arg, "%i", &hauteur)){
        Serial.print("Set hauteur seuil cell N°");
        Serial.print(no_cellule);
        if (haut_bas == 'B'){
          Serial.print(" BAS");
          seuil_bas_cellules[no_cellule] = hauteur;
        } else{
          Serial.print(" HAUT");
          seuil_haut_cellules[no_cellule] = hauteur;
        }
        Serial.print(" = ");
        Serial.println(hauteur);
        return;
      }
    }
  }
 Serial.println("Error on set_hauteur seuil");
}

void set_distance_pistolet(){
    /* Reponse à SDP
      2 argument :
     - no_pistolet   :   ex "1"
     - distance      :   ex "125"
  */
  int no_pistolet;
  int distance;
  char *arg;
  arg = sCmd.next();
  if (arg !=  NULL && sscanf(arg, "%i", &no_pistolet)){
    arg = sCmd.next();
    if (arg != NULL && sscanf(arg, "%i", &distance)){
      Serial.print("Set distance pistolet n°");
      Serial.print(no_pistolet);
      Serial.print(" = ");
      Serial.println(distance);
      distance_pistolet[no_pistolet]=distance;
      return;
    }
  }
  Serial.println("Error on set_distance_pistolet");
}

void init_masques(){
  Serial.println("INIT.");
  for(int i=0;i<L_MASQUES;i++){
    masques[i]=0;
  }
}

void unrecognized(const char *command) {
  Serial.print("Unknown cmd : ");
  Serial.println(command);
}

// Envoie des infos sur une ligne vers le serial
// "{hauteur} {etat_pistolet0} {etat_pistolet1} ....." ex : "42 1 0 1"
void send_infos(){
  char buf[255];
  sprintf(buf, "%i", get_hauteur());
  for (int p=0;p<NB_PISTOLETS;p++){
    if (digitalRead(pin_pistolets[p])){
      strcat(buf, " 1" );
    }else{
      strcat(buf, " 0" );
    }
  }
  Serial.println(buf);
}

/////////////////////////////////
// INTERRUPTIONS
/////////////////////////////////

void interuption_avance(){
  compteur_avance++;
  if (compteur_avance == RATIO_AVANCE){
    tore_shift();
    tore_set(0,cells);
    compteur_avance = 0;
  }
}

void interuption_monte_baisse(){
  byte cells_avant;
  int hauteur;
  position_monte_baisse++;
  //Serial.println(position_monte_baisse);
  test_pistolets();
}

void interuption_fin_course(){
    // recalcule la position haute = le centre entre 2 fin de course.
    position_haut_monte_baisse = position_monte_baisse /2;
    position_monte_baisse = 0;
  }

/////////////////////////////////
// FONCTIONS METIERS
/////////////////////////////////

void test_pistolets(){
  bool allume;
  int hauteur;
  byte masque;
  hauteur = get_hauteur();
  for (int p=0;p<NB_PISTOLETS;p++){
    masque = tore_get(distance_pistolet[p]);
    allume = false;
    for (int c=0;c<NB_CELLULES;c++){
      if (get_cell(masque, c)){
        allume = allume || (hauteur > seuil_bas_cellules[c] && hauteur < seuil_haut_cellules[c]);
      }
    }
    if (allume){
      digitalWrite(pin_pistolets[p], HIGH);
    }else{
      digitalWrite(pin_pistolets[p], LOW);
    }
  }
}

//Renvoie un boolean selon masque et index de cellule
bool get_cell(byte masque, int cell_no){
   return (masque & (1 << cell_no)) != 0;
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

void debug(){
  Serial.print("pos_masques: ");
  Serial.println(pos_masques);
  Serial.print("masques: ");
  print_masques();
  Serial.print("hauteur :");
  Serial.println(get_hauteur());
  Serial.print("Masque pistolet 0 : ");
  Serial.print("(");
  Serial.print(distance_pistolet[0]);
  Serial.print(")");
  Serial.println(tore_get(distance_pistolet[0]));
}
