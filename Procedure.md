## API Access

1. Register an account with Solis Cloud and raise a ticket for API access. Within 2 days they will provide the access for it. [Learn more](https://solis-service.solisinverters.com/en/support/solutions/articles/44002212561-api-access-soliscloud)
2. Go to [SolisCloud API Manage](https://www.soliscloud.com/#/apiManage).
3. Activate API management and agree with the usage conditions and do the rest.
4. Note down the API Key, API Secret and URL in a notepad and keep it safe for later.

## Preparing Environment

### Docker

1. Install Docker Engine. In my case it is running on top of Debian (Proxmox container). [For more](https://docs.docker.com/engine/install/debian/)
2. Update apt repository and upgrade packages if available:

   `sudo apt update && sudo apt upgrade -y`

4. Install Portainer for ease of use. [For more](https://docs.portainer.io/start/install-ce/server/docker/linux)

### InfluxDB

1. Open Portainer & Deploy a New Container

	1. Log in to **Portainer**.
	2. Go to **Containers → Add Container**.
	3. Set **Name:** `influxdb`.
	4. In **Image**, enter:    
		`influxdb:latest`

2. Configure Ports

	In **"Advanced container settings" → "Network"**, add:
    - **Host Port:** `8086`
    - **Container Port:** `8086`

3. Set Up Persistent Storage (Recommended)

	In **Volumes**, create a bind mount:
    - **Container Path:** `/var/lib/influxdb2`
    - **Host Path:** `/path/to/influxdb/data` (choose a directory on your VM)

4.  Add Environment Variables (for InfluxDB 2.x)

	In the **"Env"** tab, add:
	- `DOCKER_INFLUXDB_INIT_MODE` → `setup`
	- `DOCKER_INFLUXDB_INIT_USERNAME` → `admin`
	- `DOCKER_INFLUXDB_INIT_PASSWORD` → `yourpassword`
	- `DOCKER_INFLUXDB_INIT_ORG` → `yourorg`
	- `DOCKER_INFLUXDB_INIT_BUCKET` → `yourbucket`
	- `DOCKER_INFLUXDB_INIT_RETENTION` → `30d` _(optional, sets retention policy to 30 days)_

5. Deploy the Container

	Click **Deploy the container** and wait for it to start.

6.  Access InfluxDB Web UI

	- Open your browser and go to:
	    `http://<your_vm_ip>:8086`
	- Log in with the username and password you set.

7. Navigate to `Load Data > API Tokens > Generate API Token > Custom API Token > "Name the token"> Buckets > "Select appropriate bucket" > "give read and write access"`. Click "Generate". Copy the generated token into a notepad.

`Note: Don't use the "Copy to Clipboard" button to copy the token. You may face issues later. Just use the cursor to copy.`

## Python Code

1. Check if python3 is installed in your Docker Engine:
		`python3 --version`
	If this returns value like '3.xx.x' then the python interpreter is available else install it
		`sudo apt install python3 python3-pip`
2. If you get `error: externally-managed-environment` refer [Jeff Geerling blog](https://www.jeffgeerling.com/blog/2023/how-solve-error-externally-managed-environment-when-installing-pip3)
3. 4. Create a directory in `/home` called `solis_logging` (you may keep anything). Copy `requirements.txt,` `solis_logging.py`, `secret.json` and `Dockerfile`.
4. Install dependencies and libraries using requirements.txt:
		`pip install -r requirements.txt`
5. Modify the [Dockerfile](/src/Dockerfile) with appropriate Python version, python script name (if filename is changed) and working directory.
6. Modify [secret.json](/src/secret.json) with appropriate details that you copied earlier.
7. Modify [solis_logging.py](/src/solis_logging.py) with appropriate `TZ`,`START_TIME`,`END_TIME` and `refresh_time`.
8. Comment / Uncomment necessary parameters. You may even add / remove as per your use case.
9. Run the script within docker and check whether it is able to add the data retrieved from Solis Cloud to the InfluxDB database.
		`python3 solis_logging.py`
10. If the script is successfully adding the data to InfluxDB, then proceed to configure Grafana for data visualization.

## Grafana

1. First, create a Docker network (if you haven't already):
		`docker network create monitoring`
2. In portainer, click `Container`> `Add Container`
	Name: `grafana`
	Image: `grafana/grafana-oss:latest`
	Port mapping: `3000:3000`
	Network: `monitoring`
	Volume: Create a new volume
	    `/var/lib/grafana`
3. After containers are running:
	1. Access Grafana at [http://your-ip:3000](http://your-ip:3000)
	2. Default login: admin/admin
	3. You'll be prompted to change password
4. To connect InfluxDB to Grafana:
	1. Go to Configuration > Data Sources
	2. Add data source > Select InfluxDB
	3. Set these fields:
			URL: `http://{your_influxdb_IP_address}:8086`
			Organization: `yourorg`
			Token: `token_that_you_generated_earlier`
			Default Bucket: `yourbucket`
			Version: Flux
	4. Click "Save & Test"
5. Go to `Dashboard` > `New` >`New Dashboard` > `Add Visualization`. Select your InfluxDB bucket as data source. 
6. Now you can create dashboards in Grafana to visualize your solar data. Some example queries to get you started: 
```
from(bucket: "solar_metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "station_metrics")
  |> filter(fn: (r) => r._field == "power")
```
	Here 'solar_metrics' is taken as an example bucket name, 'station_metrics' as example point name and 'power' as example field name.
	
7. Alternatively you can also import [[solis_grafana.json]] and set up the visualization.
8. Go to `Dashboard` > `New` > `Import Dashboard`. Select `solis_grafana.json` file . Choose appropriate dashboard name, and InfluxDB source.
9. Remember to change UID with appropriate values (some random characters+numbers except special values).

	![grafana_json_uid](/img/grafana_json_uid.png)

10. Click `Import`

You will now be able to visualize the data from your InfluxDB.

## Resources

[You will find all the required files here](/src/)
