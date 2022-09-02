
import random
import time
import json
import collections


from azure.iot.device import IoTHubDeviceClient, Message

# The device connection string to authenticate the device with your IoT hub.
# Using the Azure CLI:l
# az iot hub device-identity show-connection-string \
#   --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table

CONNECTION_STRING=(
    "HostName=agl21005.azure-devices.net";
    "DeviceId=agl21005";
    "SharedAccessKey=9Le3WcApKn+G1xvWHQ0tsc43c6hSvkkCoPwvTXCGYH0="
    )

# Set seed to make simulation data reproducible
random.seed(123)

# Simulation parameters --------------------------------------------------------

# temperatures are in degrees Celsius
AVG_TEMP = 25.0
TEMP_RANGE = 10.0

# humidity is relative humidity in percentages
AVG_HUMID = 60.0
HUMID_RANGE = 10.0


# Position is relative position in percentages
AVG_POSITION = 50.0
POSITION_RANGE = 10.0

# an increase of one degree will increase the number of customers by 2 
TEMP_COEFF = 2
BASE_N_CUSTOMERS = 10

# Items  and their prices
MENU = {'Ice_creams': 150.0,
        'Chocolates': 100.0,
        'Cool Drinks': 60.0,
        'Pastry':85.0,
        'Bread':40.0}
PRICES = MENU.values()
ITEMS = MENU.keys()

#-------------------------------------------------------------------------------

def simulate_telemetry(client):
    '''
    Simulates telemetry output from a point-of-sale machine in an small firm
    shop. Sends temperature, humidity, and number of purchases data as a json
    string to the given IoT Hub client every second endlessly.
    '''
    while True:
        msg_json = {}

        # randomise daily temperature and relative humidity
        temperature_diff = (random.random() * TEMP_RANGE) - TEMP_RANGE/2
        temperature = AVG_TEMP + temperature_diff

        humidity_diff = (random.random() * HUMID_RANGE) - HUMID_RANGE/2
        humidity = AVG_HUMID + humidity_diff

        # The higher the humidity is above the average, the more customers.
        # Low humidity leads to fewer customers.
        humidity_factor = humidity / AVG_HUMID
        
        position_diff = (random.random() * POSITION_RANGE) - POSITION_RANGE/2
        position = AVG_POSITION + position_diff


        # the hotter and more humid it is, the more customers will come
        n_customers = max(BASE_N_CUSTOMERS + TEMP_COEFF * temperature_diff, 0)
        n_customers = int(n_customers * humidity_factor)

        daily_revenue = 0
        items_counts = collections.defaultdict(int)

        for customer in range(n_customers):
            # The customer chooses a random item, more expensive item
            # are more likely to be picked.
            choice = random.choices(
                population=list(MENU.items()),
                weights=[price/max(PRICES) for price in PRICES])
            
            items, price = choice[0]
            
            # add to count and daily revenue
            items_counts[items] += 1
            daily_revenue += price

        # build the json message
        msg_json['temperature'] = temperature
        msg_json['humidity'] = humidity
        msg_json['position']=position
        msg_json['revenue'] = daily_revenue
        for items_name in MENU.keys():
            msg_json[items_name] = items_counts[items_name]

        msg_json_text = json.dumps(msg_json)
        message = Message(msg_json_text)

        # Send the message.
        print("Sending message: {}".format(message))
        client.send_message(message)
        print ("Message successfully sent")
        time.sleep(1)

def iothub_client_init():
    '''Creates and returns an IoT Hub client.'''
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

def iothub_client_telemetry_sample_run():
    '''
    Starts the telemetry simulation loop, until stopped with KeyboardInterrupt
    (Ctrl-C).
    '''
    try:
        client = iothub_client_init()
        print("IoT Hub device sending periodic messages, press Ctrl-C to exit")

        # Start endless telemetry simulation loop
        simulate_telemetry(client)

    except KeyboardInterrupt:
        print("IoTHubClient sample stopped")

if __name__ == '__main__':
    print("Press Ctrl-C to exit")

    iothub_client_telemetry_sample_run()
