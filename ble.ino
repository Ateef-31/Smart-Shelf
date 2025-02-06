#include "BLEDevice.h"

void setup() {
    Serial.begin(115200);
    BLEDevice::init("");

    Serial.println("Scanning for Bluetooth devices...");
}

void loop() {
    BLEScan* pBLEScan = BLEDevice::getScan();
    pBLEScan->setActiveScan(true);
    BLEScanResults foundDevices = pBLEScan->start(5); // Scan for 5 seconds

    Serial.println("Devices found:");
    for (int i = 0; i < foundDevices.getCount(); i++) {
        BLEAdvertisedDevice d = foundDevices.getDevice(i);
        Serial.printf("Device: %s, RSSI: %d dBm\n", d.getAddress().toString().c_str(), d.getRSSI());
    }

    delay(5000);
}
