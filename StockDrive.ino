#include <AccelStepper.h>

// Define a stepper and the pins it will use
int homeSwitch = 4;
int limitSwitch = 11;
int enable = 7;                     //Note that the enabled being low means 
//define the speeds used
long mSpeed = 4000;                 //move 4000 steps per sec; regular speed for moving to cut lengths
long Acc = 2000;                    // normal acc used for moving to cut lengths
long MoveToHomeSpeed = -2000;       //used for moving to home
long MoveFromHomeSpeed = 50;        //used for moving away from home

AccelStepper stepper(AccelStepper::DRIVER, 9, 8); //step = pin 9, dir = pin 8

boolean stopped = 0; 
 
float inchPerRev = .25;                     //.25 inch per rev

int stepsPerRev = 400;                    //steps per rev
long pos  = 0;
String inString = "";

long ConvertInchPos(float Inch){                //creates a number of steps out of given inches 
  long pos = Inch*stepsPerRev/inchPerRev;
  return pos;
}


float getInchPos(){
  float inches = stepper.currentPosition()*inchPerRev/(stepsPerRev);
  return inches;
}


void stopMotor(){
  stepper.stop();                 //Stops the motor as quickly as possible
  digitalWrite(enable, HIGH);     //disengauge the coils
  if(!stopped){                   //let the user know the motor is stopped
    Serial.println("Stopped");  
  }
  stopped = 1;                    //set machine to stopped
}


void serialEvent() {              //happens when the arduino receives a message
  while (Serial.available() > 0){ //while there is data available at the serial port
    int inChar = Serial.read();   //take the first character available and store it in inChar 
    switch((char)inChar){         //check to see is inChar is any of the following 
      case 'S':                   //if inChar is an 'S'
        stopMotor();              //stop the motor
        break;                    
      case 'H':                   //if inChar is an 'H'
        FindHome();               //recalibrate the home position
        break;
      case 'R':                   //if inChar is an 'R'
         sendLength();            //send the current length back
      default:                    //if none of the above
        if(inChar != '\n'){       //check to see if this is the end of the message; If not  
          inString += (char)inChar;//put the character into a string
        }else{                     //if that was the end of the message
          float dist = inString.toFloat();//convert the string to a number
          pos = ConvertInchPos(dist);//set the number as the new target position
          inString = "";             //clear the string for next time
        }
    }
 }

}


void FindHome(){// routine used to find the home position
  stopped = 0;
  digitalWrite(enable, LOW);
  stepper.setSpeed(MoveToHomeSpeed);                        //Travel in reverse at a slow speed
  Serial.println("Moving to home");                         //lower acceleration
  while(digitalRead(homeSwitch) == LOW){                    //while the home switch is not pushed in continue moving backwards
    stepper.runSpeed();
  }
  delay(100);
  stepper.setSpeed(MoveFromHomeSpeed);                       //Travel in reverse at a slow speed
  Serial.println("Moving from home");                        //lower Speed Change Direction
  while(digitalRead(homeSwitch) == HIGH){                    //while the home switch is pushed in continue forward
    stepper.runSpeed();
  }
  Serial.println("Found Home");
  stepper.setCurrentPosition(0);                              //set the new position to 0
  stepper.moveTo(0);
  stepper.setMaxSpeed(mSpeed);                                //return max speed to normal
  stepper.setAcceleration(Acc);                               //return Acceleration to normal
  stopped = 0;
}


void sendLength(){
   Serial.println(getInchPos());                              //send the current length to the computer
}


void setup()
{
  stepper.setPinsInverted(true, false, false);                //sets the direction to inverted
  pinMode(limitSwitch, INPUT);                                //limit switch as an input
  pinMode(homeSwitch, INPUT);                                 //homeswitch as an input
  pinMode(enable, OUTPUT);                                    //set the enable as an output
  Serial.begin(9600);                                         //turns on the serial port
  stopped = 1;                                                //makes sure the machine is stopped when started
  stepper.setMaxSpeed(mSpeed);                                //set the normal speed
  stepper.setAcceleration(Acc);                               //set the normal acc
  digitalWrite(enable, LOW);                                  //turn the coils on
  
  digitalWrite(homeSwitch, HIGH);                             //connect pin to an internal pull up resistor
  digitalWrite(limitSwitch,HIGH);                             //connect pin to an internal pull up resistor
  pos = 0;                                                    //set position to 0
  Serial.println("Stopped");
  stepper.moveTo(pos);                                        //tells machine to move to position
}


void loop(){
  if (stepper.distanceToGo() == 0){                           //if the stepper is at the location
    stepper.moveTo(pos);                                      //move to next pos
  }

//  if(digitalRead(homeSwitch)){
//    stopMotor();
//  }
  //if(!stopped){
    stepper.run();                                            //move one step
  //}
  
}
