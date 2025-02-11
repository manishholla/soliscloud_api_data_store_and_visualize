# SolisCloud API Data Graphing Panel

![grafana_panel](/img/grafana_panel.png)

## How?

Python implementation of SolisCloud data using `hultenvp\soliscloud_api` library, ``Docker`` container, `InfluxDB` and `Grafana`. The Python code running in a Docker container will periodically request data from the Solis Cloud using the API. This code will execute within a specific time frame, for example from 07:00  to 18:00 IST, and pause. It will resume the same process again the next day.

## Why?

I needed to gather and save my solar system data so I could track the power generation, check performance and monitor the drop in efficiency over time. With this approach, I am able to accomplish that.

## What to Expect

The data received from the Solis Cloud API contains a lot of information like current power output, inverter status, alarm status, IGBT temperature, daily power generation and on. To extract only the essential data that I need, I have parsed the returned data into JSON and kept only the necessary parameters. 

You may include any parameters that is supported by this API. For more: [SolisCloud API Docs](https://github.com/hultenvp/soliscloud_api/blob/main/doc/SolisCloud%20Platform%20API%20Document%20V2.0.pdf)

## Technical Details

### Solar System

I have a Solis on-grid (grid-tie) 3kW 1Phase inverter installed, along with 5 panels of Waaree 540W mono-perc monocrystalline solar panels, adding up to a total of 2.7kW of solar capacity. There is no CT or zero-export device attached to it. I have a bi-directional meter installed by my DISCOM and no RS485 communication feature in that.

> Solis inverter datasheet (GR1P3K-M): [Solis Inverter Datasheet](https://www.solisinverters.com/uploads/file/Solis_datasheet_S6-GR1P(1-3)K-M_IND_V2,1_202409.pdf)

> Solar panel datasheet (WSMD540): [Waaree Panel Datasheet](https://waaree.com/wp-content/uploads/2024/11/ARKA-SERIES-WSMD-520-550-WEL-EPD-520-550-144-MP-HC-11-14.06.2024.pdf)

### Inverter Data Logging

The solar inverter is connected to my home Wi-Fi network using the Solis Datalogger that came bundled with the package. The datalogger communicates with the inverter through the RS485 protocol and uploads the data to Alibaba Cloud at an interval of 300 seconds (5 minutes).

### API Data Store & Visualize

For logging and storing the data, I have an old PC connected to internet running Proxmox with multiple containers, one running Docker Engine CE.


## Procedure

Refer [Procedure](/Procedure.md)

## Issues

No known issues. [Create one](https://github.com/manishholla/soliscloud_api_data_store_and_visualize/issues)

## Credits

[hultenvp](https://github.com/hultenvp/soliscloud_api/) for the python implementation of SolisCloud API.

[Docker Community](https://github.com/docker)

[Portainer Community](https://github.com/portainer/portainer)

[Grafana Community](https://github.com/grafana/grafana)

[InfluxDB Community](https://github.com/influxdata/influxdb)

[Python Community](https://github.com/python)
