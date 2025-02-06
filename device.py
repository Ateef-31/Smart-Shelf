import asyncio
import qasync
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from bleak import BleakScanner
from datetime import datetime
import csv

# Map JDY-19 MAC addresses to store sections
JDY_19_SECTIONS = {
    "98:90:00:00:34:F3": "Chocolates Section",
    "98:90:00:00:34:F2": "Books Section",
    "98:90:00:00:34:F5": "Electronics Section",
    "98:90:00:00:34:F1": "Clothing Section",
    "98:90:00:00:34:F4": "Toys Section",
}

class BluetoothScanner(QThread):
    devices_scanned = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.running = True

    async def scan_ble(self):
        while self.running:
            devices = await BleakScanner.discover()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            device_list = []
            for device in devices:
                rssi = device.metadata.get("rssi", device.rssi)
                section = JDY_19_SECTIONS.get(device.address, "Unknown Section")  # Identify section
                device_list.append((timestamp, device.address, device.name or "Unknown", rssi, section))

            self.devices_scanned.emit(device_list)
            await asyncio.sleep(5)

    def stop_scan(self):
        self.running = False

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.scan_ble())


class BluetoothScannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JDY-19 RSSI Scanner")
        self.setGeometry(300, 200, 700, 400)
        self.layout = QVBoxLayout()

        self.label = QLabel("Press 'Start Scanning' to begin scanning for Bluetooth devices.")
        self.layout.addWidget(self.label)

        self.scan_button = QPushButton("Start Scanning")
        self.scan_button.clicked.connect(self.scan_bluetooth)
        self.layout.addWidget(self.scan_button)

        self.stop_button = QPushButton("Stop Scanning")
        self.stop_button.clicked.connect(self.stop_bluetooth)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Added column for Section
        self.table.setHorizontalHeaderLabels(["Timestamp", "Device Name", "MAC Address", "RSSI (dBm)", "Section"])
        self.layout.addWidget(self.table)

        self.save_button = QPushButton("Save as CSV")
        self.save_button.clicked.connect(self.save_to_csv)
        self.save_button.setEnabled(False)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        self.scanner_thread = BluetoothScanner()
        self.scanner_thread.devices_scanned.connect(self.update_display)
        self.device_data = []

    def scan_bluetooth(self):
        self.device_data.clear()
        self.table.setRowCount(0)
        self.label.setText("Scanning for Bluetooth devices...")
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.scanner_thread.start()

    def stop_bluetooth(self):
        self.scanner_thread.stop_scan()
        self.label.setText("Scanning stopped.")
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_display(self, devices):
        if not devices:
            self.label.setText("No devices found.")
            return

        self.device_data.extend(devices)
        self.table.setRowCount(len(self.device_data))

        for i, (timestamp, addr, name, rssi, section) in enumerate(self.device_data):
            self.table.setItem(i, 0, QTableWidgetItem(timestamp))
            self.table.setItem(i, 1, QTableWidgetItem(name))
            self.table.setItem(i, 2, QTableWidgetItem(addr))
            self.table.setItem(i, 3, QTableWidgetItem(str(rssi)))
            self.table.setItem(i, 4, QTableWidgetItem(section))
            self.table.item(i, 3).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.save_button.setEnabled(True)

    def save_to_csv(self):
        if not self.device_data:
            QMessageBox.information(self, "No Data", "No data to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            if not file_path.endswith('.csv'):
                file_path += '.csv'

            df = pd.DataFrame(self.device_data, columns=["Timestamp", "MAC Address", "Device Name", "RSSI", "Section"])
            df = df[["Timestamp", "Device Name", "MAC Address", "RSSI", "Section"]]
            df.to_csv(file_path, index=False, encoding='utf-8')
            self.label.setText(f"Data successfully saved to {file_path}")


if __name__ == "__main__":
    app = QApplication([])
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = BluetoothScannerApp()
    window.show()

    with loop:
        loop.run_forever()
