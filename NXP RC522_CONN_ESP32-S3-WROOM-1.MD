NXP RC522 與 ESP32-S3-WROOM-1 連接線



參考ESP32-S3 引腳 連接 專案文章 ： https://yhsbj.cn/index.php/2024/12/26/466/

![mfrc522_PIN_REMARKS](./README_IMGs/NXP%20RC522_CONN_ESP32-S3-WROOM-1/mfrc522_PIN_REMARKS.jpg)

![NXP RC522_CONN_ESP32-S3-WROOM-1_VER1](./README_IMGs/NXP%20RC522_CONN_ESP32-S3-WROOM-1/NXP%20RC522_CONN_ESP32-S3-WROOM-1_VER1.png)

### ESP32-S3-WROOM-1 引脚分析

| 您选择的引脚    | 功能          | 是否可用         | 建议     |
| :-------------- | :------------ | :--------------- | :------- |
| GPIO14 (SCK) X  | SPI1 时钟     | ✅ 可用           | 保持     |
| GPIO13 (MOSI) X | SPI1 主出从入 | ✅ 可用           | 保持     |
| GPIO12 (MISO) X | SPI1 主入从出 | ⚠️ 受限 改 GPIO11 | **更换** |
| GPIO15 (SDA) X  | 片选(CS)      | ✅ 可用           | 保持     |
| GPIO16 (RST) X  | 复位          | ✅ 可用           | 保持     |

## 单片机esp32 s3+RFID RC522读写标签

 

![img](https://yhsbj.cn/wp-content/uploads/2024/12/FF39E1A5755372009DC5547C5E02909A-968x1024.jpg)

![img](https://yhsbj.cn/wp-content/uploads/2024/12/IMG_5827-1024x768.jpg)

## **Esp32 S3接线：**

RDID-RC522的SDA -> esp32-s3的引脚10

RDID-RC522的SCK -> esp32-s3的引脚12

RDID-RC522的MOSI -> esp32-s3的引脚11

RDID-RC522的MISO -> esp32-s3的引脚13

RDID-RC522的GUN -> esp32-s3的引脚GUN

RDID-RC522的RST -> esp32-s3的引脚46

RDID-RC522的3.3V -> esp32-s3的引脚3.3V

## **单片机esp32代码：**

 

```
#include <MFRC522.h>
#include <SPI.h>
#define SS_PIN 10     //SDA引脚
#define RST_PIN 46    //RST（复位信号）, 任意一个可用的引脚即可
#define SCK_PIN 12    //SCK（时钟接口）
#define MOSI_PIN 11   //MOSI（SPI 接口主出从入）
#define MISO_PIN 13   //MISO（SPI 接口主入从出）
MFRC522 mfrc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;
void setup() {
  Serial.begin(115200);                             //开启串口打印信息
  while (!Serial);                                  //等待串口打开
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN);   //开启SPI总线通信
  mfrc522.PCD_Init();                               //初始化MFRC522模块
  //设置密钥全部为0xFF，卡片默认全部是0xFF
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
}
void loop() {
  //等待串口发送消息
  if (Serial.available() > 0) {
    //读取一个字节
    int command = Serial.read();
    //检测是否有卡并且读取卡片
    if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
      Serial.println("no card!");
      return;
    }
    //打印卡的UID
    Serial.print(F("Card UID:"));
    dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size);
    Serial.println();
    //打印卡的类型
    MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
    Serial.println(mfrc522.PICC_GetTypeName(piccType));
    //判断兼容性
    if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI
        && piccType != MFRC522::PICC_TYPE_MIFARE_1K
        && piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
      Serial.println(F("This sample only works with MIFARE Classic cards."));
      return;
    }
    //读取第四个块的数据，每个扇区由 4 个数据块 组成
    byte blockAddr = 4;
    //认证第四个数据块
    byte trailerBlock = 4;
    MFRC522::StatusCode status;
    //保存读取的数据
    byte buffer[18];
    byte size = sizeof(buffer);
    //写入的数据
    byte dataBlock[] = {
      0x01, 0x02, 0x03, 0x04,  //  1,  2,   3,  4,
      0x05, 0x06, 0x07, 0x08,  //  5,  6,   7,  8,
      0x09, 0x0a, 0xff, 0x0b,  //  9, 10, 255, 11,
      0x0c, 0x0d, 0x0e, 0x0f   // 12, 13, 14, 15
    };
    //认证Key A
    status = (MFRC522::StatusCode)mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
      Serial.print(F("PCD_Authenticate() failed(A): "));
      Serial.println(mfrc522.GetStatusCodeName(status));
      return;
    }
    //读取数据库
    status = (MFRC522::StatusCode)mfrc522.MIFARE_Read(blockAddr, buffer, &size);
    if (status != MFRC522::STATUS_OK) {
      Serial.print(F("MIFARE_Read() failed: "));
      Serial.println(mfrc522.GetStatusCodeName(status));
    }
    Serial.print(F("Read Data in block :"));
    dump_byte_array(buffer, 16);
    Serial.println();
    //认证Key B
    status = (MFRC522::StatusCode)mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_B, trailerBlock, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
      Serial.print(F("PCD_Authenticate() failed: "));
      Serial.println(mfrc522.GetStatusCodeName(status));
      return;
    }
    //打印写入数据
    Serial.print(F("Write Data in block :"));
    dump_byte_array(dataBlock, 16);
    Serial.println();
    //写入数据
    status = (MFRC522::StatusCode)mfrc522.MIFARE_Write(blockAddr, dataBlock, 16);
    if (status != MFRC522::STATUS_OK) {
      Serial.print(F("MIFARE_Write() failed: "));
      Serial.println(mfrc522.GetStatusCodeName(status));
    }
    //停止卡片通信
    mfrc522.PICC_HaltA();
    //停止卡片加密通信
    mfrc522.PCD_StopCrypto1();
  }
}
//打印数据
void dump_byte_array(byte* buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}
```

![img](https://yhsbj.cn/wp-content/uploads/2024/12/QQ%E6%88%AA%E5%9B%BE20241226004109.png)

[esp32](https://yhsbj.cn/index.php/tag/esp32/)[rfid](https://yhsbj.cn/index.php/tag/rfid/)

【淘宝】7天无理由退货 https://e.tb.cn/h.hjiXvzJrEzy4JlY?tk=9noy4XD2uVu MF937 「MFRC-522 RC522 RFID射频板 IC卡感应模块 送S50复旦卡 钥匙扣」
点击链接直接打开 或者 淘宝搜索直接打开