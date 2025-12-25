from pathlib import Path
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
import search

# filepath: c:\Users\gris_\Developer\Internal\fs25-attachment-search\table_gui.py

def create_vehicle_table_widget(vehicles):
    table = QTableWidget()
    table.setColumnCount(5)
    table.setHorizontalHeaderLabels(["Name", "Type", "Store Category", "Attachments", "Input Attachments"])
    
    table.setRowCount(len(vehicles))
    for row, vehicle in enumerate(vehicles):
        # table.setItem(row, 0, QTableWidgetItem(vehicle.brand))
        # table.setItem(row, 1, QTableWidgetItem(vehicle.name))
        table.setItem(row, 0, QTableWidgetItem(vehicle.get_full_name()))
        table.setItem(row, 1, QTableWidgetItem(vehicle.type))
        table.setItem(row, 2, QTableWidgetItem(vehicle.store_category))
        table.setItem(row, 3, QTableWidgetItem(", ".join(vehicle.attachments)))
        table.setItem(row, 4, QTableWidgetItem(", ".join(vehicle.input_attachments)))
    
    table.resizeColumnsToContents()
    table.setSortingEnabled(True)
    table.sortItems(0, Qt.SortOrder.AscendingOrder)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    return table

class AttachableVehiclesTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Name", "Type", "Store Category", "Attachment Point"])
        self.setSortingEnabled(True)

    def set_vehicle_to_attach_to(self, attachable_vehicles):
        self.clearContents()
        self.setRowCount(0)

        for attachment, vehicle_list in attachable_vehicles.items():
            for vehicle in vehicle_list:
                row = self.rowCount()
                self.insertRow(row)
                self.setItem(row, 0, QTableWidgetItem(vehicle.get_full_name()))
                self.setItem(row, 1, QTableWidgetItem(vehicle.type))
                self.setItem(row, 2, QTableWidgetItem(vehicle.store_category))
                self.setItem(row, 3, QTableWidgetItem(attachment))
        
        self.resizeColumnsToContents()

        self.sortItems(0, Qt.SortOrder.AscendingOrder)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vehicle List")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)        

        # Create table widget
        vehicles_directory = Path(r"Z:\Steam\steamapps\common\Farming Simulator 25\data\vehicles")
        self.all_vehicles = search.parse_vehicle_xmls(vehicles_directory)
        self.all_vehicles_table = create_vehicle_table_widget(self.all_vehicles)

        # Create attachable vehicles table widget
        self.attachable_table = AttachableVehiclesTableWidget()
        self.input_attachable_table = AttachableVehiclesTableWidget()

        layout.addWidget(self.all_vehicles_table)
        self.can_be_attached_label = QLabel("Vehicles that can be attached to selected vehicle:")
        layout.addWidget(self.can_be_attached_label)
        layout.addWidget(self.attachable_table)
        self.can_attach_label = QLabel("Vehicles that selected vehicle can attach to:")
        layout.addWidget(self.can_attach_label)
        layout.addWidget(self.input_attachable_table)

        self.all_vehicles_table.currentCellChanged.connect(self.on_row_selected)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def on_row_selected(self, row):
        vehicle_full_name  = self.all_vehicles_table.item(row, 0)
        assert vehicle_full_name is not None

        vehicle = search.find_vehicle_by_full_name(self.all_vehicles, vehicle_full_name.text())
        assert vehicle is not None

        attachable_vehicles = search.find_attachments_matching_input_attachments(self.all_vehicles, vehicle)
        self.attachable_table.set_vehicle_to_attach_to(attachable_vehicles)
        self.can_attach_label.setText(f"Vehicles that can be attached to {vehicle.get_full_name()}")

        input_attachable_vehicles = search.find_input_attachments_matching_attachments(self.all_vehicles, vehicle)
        self.input_attachable_table.set_vehicle_to_attach_to(input_attachable_vehicles)
        self.can_be_attached_label.setText(f"Vehicles that {vehicle.get_full_name()} can be attached to:")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())