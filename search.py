import xml.etree.ElementTree as ET
from pathlib import Path

class Vehicle:
    def __init__(self, name, type, brand, store_category, attachments, input_attachments):
        self.name = name
        self.type = type
        self.brand = brand
        self.store_category = store_category
        self.attachments = attachments
        self.input_attachments = input_attachments
        self.file_path = None  # To be set when loading from file

    def get_full_name(self):
        return f"{self.brand} {self.name}"

def get_attacher_joints_from_xml_node(vehicle_root_node):
    attacher_joints = vehicle_root_node.find("attacherJoints")
    if attacher_joints is None:
        return []

    attachments = []
    for joint in attacher_joints.findall("attacherJoint"):
        joint_type = joint.get("jointType")
        if joint_type is None:
            continue
        attachments.append(joint_type)
    return attachments


def get_input_attacher_joints_from_xml_node(vehicle_root_node):
    input_attacher_joints = vehicle_root_node.find("attachable/inputAttacherJoints")
    if input_attacher_joints is None:
        return []

    input_attachments = []
    for joint in input_attacher_joints.findall("inputAttacherJoint"):
        joint_type = joint.get("jointType")
        assert joint_type is not None, "Joint type is missing"
        input_attachments.append(joint_type)
    return input_attachments


def parse_vehicle_xml(root):
    name = root.find("storeData/name").text
    type = root.get("type")
    store_category = root.find('storeData/category').text
    brand = root.find("storeData/brand").text

    attachments = get_attacher_joints_from_xml_node(root)
    input_attachments = get_input_attacher_joints_from_xml_node(root)

    vehicle = Vehicle(name, type, brand, store_category, attachments, input_attachments)

    return vehicle


def parse_vehicle_xmls(file_paths):
    vehicles = []
    current_index = 0
    total_files = len(file_paths)
    for file_path in file_paths:
        tree = ET.parse(file_path)
        root = tree.getroot()
        if root.tag != "vehicle":
            continue # Skip non-vehicle XML files
        vehicle = parse_vehicle_xml(root)
        vehicle.file_path = file_path
        vehicles.append(vehicle)
        current_index += 1
        print(f"Parsed {current_index}/{total_files} files.", end="\r")
    return vehicles

def get_matching_attachment(vehicle, other_vehicle):
    for input_att in other_vehicle.input_attachments:
        if input_att in vehicle.attachments:
            return input_att
    return None

def find_attachments_matching_input_attachments(vehicle_list, vehicle):
    matching_vehicles_by_attachment = {}

    for other_vehicle in vehicle_list:
        matching_attachment = get_matching_attachment(other_vehicle, vehicle)

        if matching_attachment is None:
            continue

        if matching_attachment not in matching_vehicles_by_attachment:
            matching_vehicles_by_attachment[matching_attachment] = []

        matching_vehicles_by_attachment[matching_attachment].append(other_vehicle)

    return matching_vehicles_by_attachment

def find_input_attachments_matching_attachments(vehicle_list, vehicle):
    matching_vehicles_by_input_attachment = {}

    for other_vehicle in vehicle_list:
        matching_attachment = get_matching_attachment(vehicle, other_vehicle)

        if matching_attachment is None:
            continue

        if matching_attachment not in matching_vehicles_by_input_attachment:
            matching_vehicles_by_input_attachment[matching_attachment] = []

        matching_vehicles_by_input_attachment[matching_attachment].append(other_vehicle)

    return matching_vehicles_by_input_attachment

def find_vehicle_by_full_name(vehicle_list, full_name):
    for vehicle in vehicle_list:
        if vehicle.get_full_name() == full_name:
            return vehicle
    return None

def create_map_of_vehicles_by_type(vehicle_list):
    vehicle_map = {}
    for vehicle in vehicle_list:
        if vehicle.type not in vehicle_map:
            vehicle_map[vehicle.type] = []
        vehicle_map[vehicle.type].append(vehicle)
    return vehicle_map

def print_vehicle_info(vehicle):
    print(f"Vehicle: {vehicle.brand} {vehicle.name}")
    print(f"  Type: {vehicle.type}")
    print(f"  File Path: {vehicle.file_path}")
    for att in vehicle.attachments:
        print(f"  Attachment Point: {att}")
    for input_att in vehicle.input_attachments:
        print(f"  Input Attachment Point: {input_att}")

def get_short_vehicle_info(vehicle):
    return f"{vehicle.get_full_name()} - Type: {vehicle.type}, Store Category: {vehicle.store_category}"

def main():
    # Parse command line arguments for vehicle name
    # vehicle_name = "LIZARD Pickup 2017"  # Placeholder for command line argument
    # vehicle_name = "CASEIH Axial-Flow 7150"  # Placeholder for command line argument
    # vehicle_name = "POETTINGER Terradisc 10001T"  # Placeholder for command line argument
    # vehicle_name = "LIZARD S-710"  # Placeholder for command line argument
    vehicle_name = "PFANZELT DW P 186"  # Placeholder for command line argument
    
    # vehicles_directory = Path("./vehicles")  # Placeholder for vehicles directory
    # vehicles_directory = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Farming Simulator 25\data\vehicles")  # Placeholder for vehicles directory
    vehicles_directory = Path(r"Z:\Steam\steamapps\common\Farming Simulator 25\data\vehicles")  # Placeholder for vehicles directory

    # Recursively get a list of all xml files in a directory specified from command line arguments
    xml_files = []
    for f in vehicles_directory.rglob("*.xml"):
        xml_files.append(f.relative_to(vehicles_directory))

    # Create list of vehicle data from XML files
    vehicle_list = parse_vehicle_xmls([vehicles_directory / f for f in xml_files])

    # Search vehicle list for specified vehicle
    vehicle = find_vehicle_by_full_name(vehicle_list, vehicle_name)
    if vehicle is None:
        print(f"Vehicle '{vehicle_name}' not found.")
        return

    # Print information about the specified vehicle
    print(f"Information for vehicle '{vehicle.get_full_name()}':")
    print_vehicle_info(vehicle)

    # Find other vehicles that can attach to these points
    print(f"\nVehicles that can attach to '{vehicle.get_full_name()}':")
    matching_vehicles = find_attachments_matching_input_attachments(vehicle_list, vehicle)
    print_matches(matching_vehicles)

    # Find other vehicles that this vehicle can attach to
    print(f"\nVehicles that '{vehicle.get_full_name()}' can attach to:")
    matching_vehicles = find_input_attachments_matching_attachments(vehicle_list, vehicle)
    print_matches(matching_vehicles)

def print_matches(matching_vehicles):
    for attachment in matching_vehicles:
        print(f"Attachment Point: {attachment}")
        matching_vehicles_by_type = create_map_of_vehicles_by_type(matching_vehicles[attachment])
        for type in matching_vehicles_by_type:
            print(f"  Type: {type}")
            for match in matching_vehicles_by_type[type]:
                print(f'    {get_short_vehicle_info(match)}')
            print()

if __name__ == "__main__":
    main()
