import sys
from argparse import ArgumentParser
import asyncio
from smartbms.smartbms import BMS

class ComInstance:
    def __init__(self, port, bms):
        self.port = port
        self.bms = bms

async def program():
    loop = asyncio.get_running_loop()
    print('SmartBMS Data Viewer\r\n')

    parser = ArgumentParser(description='SmartBMS Data Viewer')
    parser.add_argument('-p', '--port',
                      nargs='+',
                      default=['/dev/ttyUSB0'],
                      help='Serial port(s). For multiple BMS, separate the ports with a space. Defaults to /dev/ttyUSB0 if not specified.')

    args = parser.parse_args()

    ports = ' '.join(args.port).split(' ')
    instances = []

    # Initialize BMS connections
    for port in ports:
        bms = BMS(loop, port)
        await bms.connect()
        instances.append(ComInstance(port, bms))

    await asyncio.sleep(10)  # Allow time for initial data collection

    try:
        for instance in instances:
            print(f"\nData from port {instance.port}:")
            print(f"Pack Voltage: {instance.bms.pack_voltage} V")
            print(f"Charge Current: {instance.bms.charge_current} A")
            print(f"Discharge Current: {instance.bms.discharge_current} A")
            print(f"Pack Current: {instance.bms.pack_current} A")
            print(f"State of Charge (SOC): {instance.bms.soc}%")
            print(f"Lowest Cell Voltage: {instance.bms.lowest_cell_voltage} V (Cell {instance.bms.lowest_cell_voltage_num})")
            print(f"Highest Cell Voltage: {instance.bms.highest_cell_voltage} V (Cell {instance.bms.highest_cell_voltage_num})")
            print(f"Lowest Cell Temperature: {instance.bms.lowest_cell_temperature}°C (Cell {instance.bms.lowest_cell_temperature_num})")
            print(f"Highest Cell Temperature: {instance.bms.highest_cell_temperature}°C (Cell {instance.bms.highest_cell_temperature_num})")
            print(f"Cell Count: {instance.bms.cell_count}")
            print(f"Allowed to Charge: {'Yes' if instance.bms.allowed_to_charge else 'No'}")
            print(f"Allowed to Discharge: {'Yes' if instance.bms.allowed_to_discharge else 'No'}")
            print(f"Cell Communication Error: {'Yes' if instance.bms.cell_communication_error else 'No'}")
            print(f"Serial Communication Error: {'Yes' if instance.bms.serial_communication_error else 'No'}")
            print('-' * 80)

        print("\nData retrieval complete")
    except Exception as e:
        print(f"Error retrieving data: {str(e)}")

def main():
    asyncio.run(program())

if __name__ == "__main__":
    main()
