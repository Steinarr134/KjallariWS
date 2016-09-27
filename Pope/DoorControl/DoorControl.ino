

byte pins[] = {4, 5, 6, 7, 9, 10, 11, 12};

void setup(){

  for (int i = 0; i<8; i++)
  {
    pinMode(pins[i], OUTPUT);
  }

  Serial.begin(115200);
}

byte buff[20] = {0};
byte nextpos = 0;

bool serial_fuck = false;


void loop()
{
  if (Serial.available() > 0)
  {
    byte incoming = Serial.read();
    if (!serial_fuck)
    {
      if (!((incoming == '0')||(incoming == '1')))
      {
        if (incoming != '\n')
        {
          serial_fuck = true;
        }
      }
      else
      {
        buff[nextpos] = incoming - '0';
        nextpos++;
      }
    }
    if (incoming == '\n')
    {
      if ((nextpos == 8)&&(!serial_fuck))
      {
        print_buffer();
        write_buffer();
      }
      serial_fuck = false;
      nextpos = 0;
    }
  }
}


void print_buffer()
{
  for (int i = 0; i<8; i++)
  {
    Serial.print(buff[i]);
    Serial.print(" ");
  } 
  Serial.println();
}
void write_buffer()
{
  for (int i = 0; i<8; i++)
  {
    digitalWrite(pins[i], buff[i]);
  }
}
