#include <M5Stack.h>
 
void setup() {
 
  // M5Stackの初期化
  M5.begin();
 
  M5.Lcd.clear(TFT_BLACK);
  // テキストサイズ指定
  M5.Lcd.setTextSize(2);
  M5.Lcd.setCursor(60, 80);
  M5.Lcd.printf("JPEG SWITCH");
}
 
void loop() {
  M5.update();
 
  if (M5.BtnA.wasReleased()) {
    M5.Lcd.clear(TFT_BLACK);
    M5.Lcd.drawJpgFile(SD,"/1.jpg");
  } else if (M5.BtnB.wasReleased()) {
    M5.Lcd.clear(TFT_BLACK);
    M5.Lcd.drawJpgFile(SD,"/2.jpg");
  } else if (M5.BtnC.wasReleased()) {
    M5.Lcd.clear(TFT_BLACK);
    M5.Lcd.drawJpgFile(SD,"/3.jpg");
  }
}
