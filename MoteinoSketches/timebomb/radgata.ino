int analogPin1 = 0;     // potentiometer wiper (middle terminal) connected to analog pin 3
int analogPin2 = 1;     // potentiometer wiper (middle terminal) connected to analog pin 3
int analogPin3 = 2;     // potentiometer wiper (middle terminal) connected to analog pin 3
int analogPin4 = 3;     // potentiometer wiper (middle terminal) connected to analog pin 3
int analogPin5 = 4;     // potentiometer wiper (middle terminal) connected to analog pin 3

int val1,val2,val3,val4,val5;           // variable to store the value read


//beint á móti:
//695 896 414 43  931
//nytt random: 89 896 931 92 892

int rett1=685;
int rett2=882;
int rett3=402;
int rett4=93;
int rett5=829;


// her byrjar ljosadaemid
  
  
  // þennan tima fae eg fra pafanum, timinn sem er eftir af leiknum
  unsigned long TimeLeft = 10;  
  unsigned long TimeToSplit = TimeLeft/ 2; // hofum 2 tvi tad eru adeins t led perur
  unsigned long Timibyrjar, Timataka;
  // her er breyta sem seigir hvort eigi ad kvekja eda slokkva a led, fyrir blik
  int witchLED = 0;
  int blikka = false; // byrjum a ad slokva
  int pinniTilAdSlokva = 12;



void setup()
{
  Serial.begin(9600);          //  setup serial

   pinMode(13,OUTPUT);
   pinMode(12,OUTPUT);
   //pinMode(8,OUTPUT);
      
      // Keikjum a ollum perunum
    digitalWrite(13, HIGH);
    digitalWrite(12, HIGH);
    //digitalWrite(8, HIGH);
    Serial.println("hellow");

Timibyrjar= millis();

    while(1){
      Timataka=floor((millis() - Timibyrjar)/1000);
val1 = analogRead(analogPin1);    // read the input pin
  val2 = analogRead(analogPin2);    // read the input pin
val3 = analogRead(analogPin3);    // read the input pin
val4 = analogRead(analogPin4);    // read the input pin
val5 = analogRead(analogPin5);    // read the input pin

  Serial.print(val1);             // debug value
  Serial.print("  ");             // debug value
    Serial.print(val2);             // debug value
  Serial.print("  ");             // debug value
    Serial.print(val3);             // debug value
  Serial.print("  ");             // debug value
    Serial.print(val4);             // debug value
      Serial.print("  ");             // debug value
    Serial.println(val5);

if(rett1-10< val1 && val1 <rett1+10 && val2>rett2-10 && val2<rett2+10
&& val3>rett3-10 && val3<rett3+10 && val4>rett4-10 && val4<rett4+10
&& val5>rett5-10 && val5<rett5+10 )
{
  Serial.print("meistaraverk");
}

 

  //Serial.print(Timataka);
  // lykjja tul ad blikka, kveikjum
  
  
  // slokvum a pinna 12
  if(Timataka >= TimeToSplit){
      //Serial.println("LED number 12 LOW");
      digitalWrite(12,LOW);
      
      pinniTilAdSlokva = 13;
    }
    
  
  // latum pina 13 blika, kveikjum  
    if(Timataka % 2 == 0 ){
     digitalWrite(pinniTilAdSlokva, HIGH);
   }
   else{
     digitalWrite(pinniTilAdSlokva, LOW);
   }
  
  /*
    // latum pinna 13 blikka, slokkvum
   if(Timataka > TimeToSplit && Timataka < 2*TimeToSplit &&  Timataka % 100 == 0 && witchLED == 0){
      digitalWrite(13,LOW);
      witchLED = 1;
  }
  
  */
  if(Timataka >= 2*TimeToSplit){
    //Serial.println("LED number 13 LOW");
    digitalWrite(13,LOW);
    
    }   
    }
}

void loop()
{
  
    
}
