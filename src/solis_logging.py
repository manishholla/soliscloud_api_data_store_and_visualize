# working code to get data from solis server, transform it and store it in influxDB.
'''
code updated to restart when "Timeout error occurred" error occurs
'''

import asyncio
import logging
import json
import time
import datetime
import pytz
from aiohttp import ClientSession
from soliscloud_api import SoliscloudAPI
from soliscloud_api.helpers import Helpers
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

logging.basicConfig(level=logging.DEBUG)

refresh_time: int = 180  # in seconds
TZ = pytz.timezone('Asia/Kolkata')
START_TIME = datetime.time(7, 45)
END_TIME = datetime.time(18, 15)

with open('secret.json', 'r') as file:
    creds = json.load(file)

influxDB_token = creds['influxDB_token']
influxDB_org = creds['influxDB_org']
influxDB_bucket = creds['influxDB_bucket']
influxDB_url = creds['influxDB_url']

# InfluxDB configuration
INFLUXDB_URL = influxDB_url  # Change this to your InfluxDB URL
INFLUXDB_TOKEN = influxDB_token # your influxDB token
INFLUXDB_ORG = influxDB_org  # Your organization
INFLUXDB_BUCKET = influxDB_bucket  # Your bucket name


def write_to_influxdb(station_data, inverter_data):
    """Write data to InfluxDB."""
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Write station data
    for station in station_data:
        point = Point("station_metrics") \
            .tag("station_id", station['id']) \
            .tag("station_name", station['stationName']) \
            .field("present_power_value", float(station['power'])) \
            .field("day_gen_hr", float(station['dayPowerGeneration'])) \
            .field("power_gen_today", float(station['dayEnergy'])) \
            .field("power_gen_month", float(station['monthEnergy'])) \
            .field("power_gen_year", float(station['yearEnergy'])) \
            .field("total_power_generated", float(station['allEnergy'])) \
            .field("capacity", float(station['capacity'])) \
            .field("present_power_percent", float(station['capacityPercent'])) \
            .field("grid_purchased_today_energy", float(station['gridPurchasedTodayEnergy'])) \
            .field("grid_sell_today_energy", float(station['gridSellTodayEnergy'])) \
            .field("home_load_today_energy", float(station['homeLoadTodayEnergy'])) \
            .field("grid_switch", float(station['gridSwitch'])) \
            .field("env_condition", str(station['condTxtD'])) \
            .time(datetime.datetime.now(TZ))

        write_api.write(bucket=INFLUXDB_BUCKET, record=point)

    # Write inverter data
    for inverter in inverter_data:
        point = Point("inverter_metrics") \
            .tag("inverter_sn", inverter['sn']) \
            .tag("inverter_name", inverter['name']) \
            .field("inverter_temperature", float(inverter['inverterTemperature'])) \
            .field("reactive_power", float(inverter['reactivePower'])) \
            .field("apparent_power", float(inverter['apparentPower'])) \
            .field("dc_pac", float(inverter['dcPac'])) \
            .field("dc_bus_voltage", float(inverter['dcBus'])) \
            .field("pv_gnd_voltage", float(inverter['uInitGnd'])) \
            .field("pv_voltage", float(inverter['uPv1'])) \
            .field("pv_current", float(inverter['iPv1'])) \
            .field("power", float(inverter['pow1'])) \
            .field("ac_voltage", float(inverter['uAc1'])) \
            .field("ac_current", float(inverter['iAc1'])) \
            .field("power_factor", float(inverter['powerFactor'])) \
            .field("ac_frequency", float(inverter['fac'])) \
            .field("home_load_energy", float(inverter['homeLoadEnergy'])) \
            .field("grid_purchased_energy", float(inverter['gridPurchasedEnergy'])) \
            .field("grid_sell_energy", float(inverter['gridSellEnergy'])) \
            .field("fault_string", str(inverter['faultCodeDesc'])) \
            .time(datetime.datetime.now(TZ))

        write_api.write(bucket=INFLUXDB_BUCKET, record=point)

    client.close()


async def fetch_data(soliscloud, api_key, api_secret):
    """Fetch station list and inverter details."""
    # try:
    # Get station list
    station_list = await soliscloud.user_station_list(api_key, api_secret, page_no=1, page_size=100)

    # Filter required fields from station list
    filtered_station = [{
        'id': station['id'],
        'dataTimestamp': station['dataTimestamp'],
        'dataTimestampStr': station['dataTimestampStr'],
        'fullHour': station['fullHour'],
        'dayPowerGeneration': station['dayPowerGeneration'],
        'monthCarbonDioxide': station['monthCarbonDioxide'],
        'stationName': station['stationName'],
        'userId': station['userId'],
        'sno': station['sno'],
        'dip': station['dip'],
        'azimuth': station['azimuth'],
        'power': station['power'],
        'daylight': station['daylight'],
        'powerStr': station['powerStr'],
        'price': station['price'],
        'capacity': station['capacity'],
        'capacityStr': station['capacityStr'],
        'capacityPercent': station['capacityPercent'],
        # 'capacity1': station['capacity1'],
        'dayEnergy': station['dayEnergy'],
        'dayEnergyStr': station['dayEnergyStr'],
        'dayIncome': station['dayIncome'],
        'monthEnergy': station['monthEnergy'],
        'monthEnergyStr': station['monthEnergyStr'],
        'yearEnergy': station['yearEnergy'],
        'yearEnergyStr': station['yearEnergyStr'],
        'allEnergy': station['allEnergy'],
        'allEnergyStr': station['allEnergyStr'],
        # 'allEnergy1': station['allEnergy1'],
        'allIncome': station['allIncome'],
        'updateDate': station['updateDate'],
        'type': station['type'],
        'synchronizationType': station['synchronizationType'],
        'epmType': station['epmType'],
        'gridSwitch': station['gridSwitch'],
        # 'gridSwitch1': station['gridSwitch1'],
        'shareProcess': station['shareProcess'],
        'alarmLongStr': station['alarmLongStr'],
        'dcInputType': station['dcInputType'],
        'stationTypeNew': station['stationTypeNew'],
        'gridPurchasedTotalEnergy': station['gridPurchasedTotalEnergy'],
        'gridSellTotalEnergy': station['gridSellTotalEnergy'],
        'homeLoadTotalEnergy': station['homeLoadTotalEnergy'],
        'oneSelf': station['oneSelf'],
        'gridPurchasedTodayEnergy': station['gridPurchasedTodayEnergy'],
        'gridSellTodayEnergy': station['gridSellTodayEnergy'],
        'homeLoadTodayEnergy': station['homeLoadTodayEnergy'],
        'oneSelfTotal': station['oneSelfTotal'],
        'money': station['money'],
        'condTxtD': station['condTxtD'],
        'jxbType': station['jxbType'],
        'inverterStateOrder': station['inverterStateOrder'],
        'epmCount': station['epmCount'],
        'alarmCount': station['alarmCount']

    } for station in station_list]

    # Get inverter details
    inverter_ids = await Helpers.get_inverter_ids(soliscloud, api_key, api_secret)
    inverter_detail = await soliscloud.inverter_detail(api_key, api_secret, inverter_id=inverter_ids[0])

    # Filter required fields from inverter details
    filtered_inverter = [{
        # 'id': inverter_detail['id'],
        # 'userId': inverter_detail['userId'],
        'sn': inverter_detail['sn'],
        'name': inverter_detail['name'],
        'inverterTemperature': inverter_detail['inverterTemperature'],
        'stationName': inverter_detail['stationName'],
        'stationType': inverter_detail['stationType'],
        'epmType': inverter_detail['epmType'],
        # 'gridSwitch1': inverter_detail['gridSwitch1'],
        # 'money': inverter_detail['money'],
        # 'stationId': inverter_detail['stationId'],
        'version': inverter_detail['version'],
        'reactivePower': inverter_detail['reactivePower'],
        'apparentPower': inverter_detail['apparentPower'],
        'dcPac': inverter_detail['dcPac'],
        'uInitGnd': inverter_detail['uInitGnd'],
        'dcBus': inverter_detail['dcBus'],
        'dcBusHalf': inverter_detail['dcBusHalf'],
        'uPv1': inverter_detail['uPv1'],
        'uPv1Str': inverter_detail['uPv1Str'],
        'iPv1': inverter_detail['iPv1'],
        'iPv1Str': inverter_detail['iPv1Str'],
        'pow1': inverter_detail['pow1'],
        'pow1Str': inverter_detail['pow1Str'],
        'uAc1': inverter_detail['uAc1'],
        'uAc1Str': inverter_detail['uAc1Str'],
        'iAc1': inverter_detail['iAc1'],
        'iAc1Str': inverter_detail['iAc1Str'],
        'powerFactor': inverter_detail['powerFactor'],
        'homeLoadEnergy': inverter_detail['homeLoadEnergy'],
        'homeLoadEnergyStr': inverter_detail['homeLoadEnergyStr'],
        'gridPurchasedEnergy': inverter_detail['gridPurchasedEnergy'],
        'gridPurchasedEnergyStr': inverter_detail['gridPurchasedEnergyStr'],
        'gridSellEnergy': inverter_detail['gridSellEnergy'],
        'gridSellEnergyStr': inverter_detail['gridSellEnergyStr'],
        'fac': inverter_detail['fac'],
        'facStr': inverter_detail['facStr'],
        'pEpmSet': inverter_detail['pEpmSet'],
        'pEpmSetStr': inverter_detail['pEpmSetStr'],
        'epmFailSafe': inverter_detail['epmFailSafe'],
        'epmSafe': inverter_detail['epmSafe'],
        'pEpm': inverter_detail['pEpm'],
        'pEpmStr': inverter_detail['pEpmStr'],
        'afciTypeStr': inverter_detail['afciTypeStr'],
        'g100v2State': inverter_detail['g100v2State'],
        'faultCodeDesc': inverter_detail['faultCodeDesc'],
        'machine': inverter_detail['machine']

    }]

    print("UserStationList call success:")
    print(json.dumps(filtered_station, indent=2))
    print("\nInverterDetails call success:")
    print(json.dumps(filtered_inverter, indent=2))

    write_to_influxdb(filtered_station, filtered_inverter)

    print("Data successfully written to InfluxDB")
    #
    # except (SoliscloudAPI.SolisCloudError, SoliscloudAPI.HttpError,
    #         SoliscloudAPI.TimeoutError, SoliscloudAPI.ApiError) as error:
    #     print(f"Error: {error}")


async def main():
    """Initialize API once and run the loop."""
    api_key = creds['key']
    api_secret = bytearray(creds['secret'], 'utf-8')
    api_url = creds['api_url']

    async with ClientSession() as websession:
        soliscloud = SoliscloudAPI(api_url, websession)
        while True:
            now = datetime.datetime.now(TZ).time()  # current time
            print(now)
            if START_TIME <= now <= END_TIME:
                await fetch_data(soliscloud, api_key, api_secret)
            else:
                print("Outside operational hours. Waiting...")
                # time.sleep(10)

            # time.sleep(refresh_time)
            await asyncio.sleep(refresh_time)


if __name__ == "__main__":
    while True:
        loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(main())

        except KeyboardInterrupt:
            loop.close()
            exit()

        except (SoliscloudAPI.SolisCloudError, SoliscloudAPI.HttpError,
                SoliscloudAPI.ApiError) as error:
            print(error)
            loop.close()

        except SoliscloudAPI.TimeoutError as error:
            print(f"Timeout error occurred: {error}")
            print("Restarting program...")
            loop.close()
            time.sleep(5)  # Wait 5 seconds before restart
            continue

        except Exception as error:
            # loop.run_until_complete(main())
            print(error)
            loop.close()
            break
