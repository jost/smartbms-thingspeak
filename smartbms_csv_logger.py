import sys
from argparse import ArgumentParser
import asyncio
from smartbms.smartbms import BMS
import os
import datetime
import csv

class ComInstance:
    def __init__(self, port, bms):
        self.port = port
        self.bms = bms

async def program():
    loop = asyncio.get_running_loop()
    print('SmartBMS CSV Logger\r\n')

    parser = ArgumentParser(description='SmartBMS CSV Logger')
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

    await asyncio.sleep(10)  # Allow initial connection and data collection time

    # Setup logging directory and initial file
    os.makedirs("bms-logs", exist_ok=True)
    fieldnames = [
        'Timestamp', 'Port',
        'pack_voltage', 'charge_current', 'discharge_current', 'pack_current', 'soc',
        'lowest_cell_voltage', 'lowest_cell_voltage_num',
        'highest_cell_voltage', 'highest_cell_voltage_num',
        'lowest_cell_temperature', 'lowest_cell_temperature_num',
        'highest_cell_temperature', 'highest_cell_temperature_num',
        'cell_count',
        'allowed_to_charge', 'allowed_to_discharge',
        'cell_communication_error', 'serial_communication_error'
    ]

    current_date = datetime.datetime.now().date()
    current_filename = f"bms-logs/bms-{current_date.strftime('%Y%m%d')}.csv"
    file = open(current_filename, 'a', newline='')
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    # Write header if the file is empty
    if file.tell() == 0:
        writer.writeheader()

    try:
        while True:
            new_date = datetime.datetime.now().date()
            if new_date != current_date:
                current_date = new_date
                new_filename = f"bms-logs/bms-{current_date.strftime('%Y%m%d')}.csv"
                file.close()
                file = open(new_filename, 'a', newline='')
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if file.tell() == 0:
                    writer.writeheader()

            # Collect data
            rows = []
            for instance in instances:
                bms = instance.bms
                row = {
                    'Timestamp': datetime.datetime.now().isoformat(),
                    'Port': instance.port,
                    'pack_voltage': bms.pack_voltage,
                    'charge_current': bms.charge_current,
                    'discharge_current': bms.discharge_current,
                    'pack_current': bms.pack_current,
                    'soc': bms.soc,
                    'lowest_cell_voltage': bms.lowest_cell_voltage,
                    'lowest_cell_voltage_num': bms.lowest_cell_voltage_num,
                    'highest_cell_voltage': bms.highest_cell_voltage,
                    'highest_cell_voltage_num': bms.highest_cell_voltage_num,
                    'lowest_cell_temperature': bms.lowest_cell_temperature,
                    'lowest_cell_temperature_num': bms.lowest_cell_temperature_num,
                    'highest_cell_temperature': bms.highest_cell_temperature,
                    'highest_cell_temperature_num': bms.highest_cell_temperature_num,
                    'cell_count': bms.cell_count,
                    'allowed_to_charge': bms.allowed_to_charge,
                    'allowed_to_discharge': bms.allowed_to_discharge,
                    'cell_communication_error': bms.cell_communication_error,
                    'serial_communication_error': bms.serial_communication_error,
                }
                rows.append(row)

            # Write all rows
            for row in rows:
                writer.writerow(row)
            file.flush()  # Ensure data is written immediately

            await asyncio.sleep(60)  # Wait 1 minute

    except Exception as e:
        print(f"Error in logging loop: {str(e)}")
        if file:
            file.close()
    finally:
        if file:
            file.close()

def main():
    asyncio.run(program())

if __name__ == "__main__":
    main()
