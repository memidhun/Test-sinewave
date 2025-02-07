import streamlit as st
import pandas as pd
import cv2
import datetime
from keras.models import load_model
import numpy as np
import time
import os
import random
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Initialize chatbot pipeline using GPT-2
generator = pipeline('text-generation', model=model, tokenizer=tokenizer)

# Backend: Simulate automatic data fetching (replace with real IoT device data fetching logic)
def fetch_device_status():
    # Simulated CSV data as a pandas DataFrame (replace with actual data source)
    data = {
        "Room": ["Room 1", "Room 2", "Room 3", "Room 4"],
        "Lights": ["On", "Off", "On", "Off"],
        "Fans": ["Off", "Off", "On", "On"],
        "Windows": ["Closed", "Open", "Closed", "Closed"],
        "CleaningRobot": ["Idle", "Active", "Idle", "Active"]
    }
    return pd.DataFrame(data)

# Initialize session state to store user-made changes
if "manual_changes" not in st.session_state:
    st.session_state.manual_changes = {}

# Function to apply manual changes and persist them across modes
def apply_manual_changes(device, room, new_status):
    st.session_state.manual_changes[(device, room)] = new_status

# Fetch current device status (automatic from backend)
device_status_df = fetch_device_status()

# Update the device status DataFrame with any manual changes
for (device, room), new_status in st.session_state.manual_changes.items():
    device_status_df.loc[device_status_df['Room'] == room, device] = new_status

# Sentinel Home Page
st.title("Sentinel")
st.subheader('"An Intelligent Caretaker for Your Sweet Home"')

# Sidebar for navigation
st.sidebar.title("Navigate")
page = st.sidebar.radio("Go to", ["Home", "Surveillance System", "Pet Care System", "Chatbot"])

# Main page: Automatic/Manual mode toggle switch
st.write("### Control Mode")
mode = st.toggle("Manual Mode", key="control_mode")
mode_name = "Manual" if mode else "Automatic"
st.write(f"Current Mode: **{mode_name}**")

# Utility function to handle command inputs for device control
def control_device(command):
    command = command.lower()
    rooms = ["room 1", "room 2", "room 3", "room 4"]
    devices = {"lights": "Lights", "fans": "Fans", "windows": "Windows", "cleaning robot": "CleaningRobot"}

    for room in rooms:
        if room in command:
            for device, device_key in devices.items():
                if device in command:
                    new_status = "on" if "on" in command else "off" if "off" in command else None
                    if new_status:
                        apply_manual_changes(device_key, room.capitalize(), "On" if new_status == "on" else "Off")
                        return f"{device.capitalize()} in {room.capitalize()} turned {new_status}."
                    else:
                        return f"Specify 'on' or 'off' to control the {device} in {room.capitalize()}."
    return "Sorry, I couldn't understand the command. Please specify the device and the room."


if page == "Home":
    st.write("Welcome to Sentinel! Your intelligent all-in-one home monitoring and control system.")
    
    # Display four tiles for Lights, Fans, Windows, and Cleaning Robots control in 4 rooms
    st.write(f"### Smart Device Control for 4 Rooms - Mode: {mode_name}")

    col1, col2 = st.columns(2)
    with col1:
        st.image("light_icon.png", width=50)  # Original icon size
        st.write("#### Lights Control")
        room_lights = st.selectbox("Select Room for Lights", ["Room 1", "Room 2", "Room 3", "Room 4"], key="lights")
        light_status = device_status_df.loc[device_status_df['Room'] == room_lights, 'Lights'].values[0]
        
        if mode:
            if st.button(f"Toggle Lights in {room_lights}", key="lights_button"):
                new_status = "Off" if light_status == "On" else "On"
                apply_manual_changes("Lights", room_lights, new_status)
                light_status = new_status
                st.write(f"Lights toggled in {room_lights}.")
        
        # Status bubble
        st.markdown(f"**Current Light Status:** {'🟢' if light_status == 'On' else '🔴'} {light_status}")

    with col2:
        st.image("fan_icon.png", width=50)  # Original icon size
        st.write("#### Fan Control")
        room_fans = st.selectbox("Select Room for Fan", ["Room 1", "Room 2", "Room 3", "Room 4"], key="fans")
        fan_status = device_status_df.loc[device_status_df['Room'] == room_fans, 'Fans'].values[0]
        
        if mode:
            if st.button(f"Toggle Fan in {room_fans}", key="fans_button"):
                new_status = "Off" if fan_status == "On" else "On"
                apply_manual_changes("Fans", room_fans, new_status)
                fan_status = new_status
                st.write(f"Fan toggled in {room_fans}.")
        
        # Status bubble
        st.markdown(f"**Current Fan Status:** {'🟢' if fan_status == 'On' else '🔴'} {fan_status}")

    col3, col4 = st.columns(2)
    with col3:
        st.image("window_icon.png", width=50)  # Original icon size
        st.write("#### Window Control")
        room_windows = st.selectbox("Select Room for Windows", ["Room 1", "Room 2", "Room 3", "Room 4"], key="windows")
        window_status = device_status_df.loc[device_status_df['Room'] == room_windows, 'Windows'].values[0]
        
        if mode:
            if st.button(f"Toggle Window in {room_windows}", key="windows_button"):
                new_status = "Closed" if window_status == "Open" else "Open"
                apply_manual_changes("Windows", room_windows, new_status)
                window_status = new_status
                st.write(f"Window status changed in {room_windows}.")
        
        # Status bubble
        st.markdown(f"**Current Window Status:** {'🟢' if window_status == 'Closed' else '🔴'} {window_status}")

    with col4:
        st.image("robot_icon.png", width=50)  # Original icon size
        st.write("#### Cleaning Robots")
        cleaning_robot_status = device_status_df.loc[device_status_df['Room'] == room_windows, 'CleaningRobot'].values[0]
        
        if mode:
            if st.button("Deploy Cleaning Robot", key="robot_button"):
                cleaning_robot_status = "Active"
                apply_manual_changes("CleaningRobot", room_windows, "Active")
                st.write("Cleaning robot deployed in all rooms.")
        
        # Status bubble
        st.markdown(f"**Cleaning Robot Status:** {'🟢' if cleaning_robot_status == 'Active' else '🔴'} {cleaning_robot_status}")

elif page == "Chatbot":
    st.subheader("Smart Home Chatbot")
    st.write("Ask about your home status or perform actions through the chatbot.")
    
    user_input = st.text_input("You: ", "")
    if st.button("Send"):
        # Simulate sensor data (replace with actual sensor API if available)
        def get_temperature():
            return random.uniform(18.0, 35.0)  # Simulate temperature (Celsius)

        def get_humidity():
            return random.uniform(30.0, 80.0)  # Simulate humidity (percentage)

        def get_gas_level():
            return random.choice(["normal", "elevated", "high"])  # Simulate gas level

        # Get all sensor data as a dictionary
        def get_sensor_data():
            return {
                "temperature": get_temperature(),
                "humidity": get_humidity(),
                "gas_level": get_gas_level()
            }

        # Chatbot processing
        def chatbot_response(user_input):
            sensor_data = get_sensor_data()
            if any(x in user_input.lower() for x in ["turn on", "turn off"]):
                return control_device(user_input)
            else:
                # Generate response using sensor data (as you had earlier)
                return f"Current conditions - Temperature: {sensor_data['temperature']:.2f}°C, Humidity: {sensor_data['humidity']:.2f}%, Gas Level: {sensor_data['gas_level']}."
        
        response = chatbot_response(user_input)
        st.write(f"House Insight Bot: {response}")
# Function to check device status based on room and device
def check_device_status(room, device):
    # Fetch the current status from the DataFrame
    status = device_status_df.loc[device_status_df['Room'] == room, device].values[0]
    return status

# Function to parse user commands and check for device status or control requests
def parse_device_command(user_input):
    user_input = user_input.lower()
    rooms = ["room 1", "room 2", "room 3", "room 4"]
    devices = ["lights", "fans", "windows", "cleaning robot"]

    # Check if user is asking for device status
    for room in rooms:
        for device in devices:
            if f"status of {device}" in user_input and room in user_input:
                status = check_device_status(room.title(), device.title())
                return f"The current status of {device} in {room} is: {status}."

    # Check if user is asking to turn a device on or off
    for room in rooms:
        for device in devices:
            if f"turn on {device}" in user_input and room in user_input:
                apply_manual_changes(device.title(), room.title(), "On")
                return f"{device.title()} in {room.title()} has been turned ON."
            elif f"turn off {device}" in user_input and room in user_input:
                apply_manual_changes(device.title(), room.title(), "Off")
                return f"{device.title()} in {room.title()} has been turned OFF."

    return None  # No matching command found

# Modified chatbot response function to handle device commands
#def chatbot_response(user_input, sensor_data):
    # First, check if the user input is related to device control or status
    #device_command_response = parse_device_command(user_input)
    #if device_command_response:
        #return device_command_response

    # If not a device command, continue with house status response
    #prompt = f"User: {user_input}\nThis house currently has the following conditions:\nTemperature: {sensor_data['temperature']:.2f}°C, Humidity: {sensor_data['humidity']:.2f}%, Gas Level: {sensor_data['gas_level']}."
def chatbot_response(user_input, sensor_data):
    # First, check if the user input is related to device control or status
    device_command_response = parse_device_command(user_input)
    if device_command_response:
        return device_command_response  # Return the device command response immediately

    # If not a device command, generate sensor status response
    return f"Current conditions - Temperature: {sensor_data['temperature']:.2f}°C, Humidity: {sensor_data['humidity']:.2f}%, Gas Level: {sensor_data['gas_level']}."
    generated_text = generator(
        prompt,
        max_length=50,  # Limit the length of the generated text
        num_return_sequences=1,
        temperature=0.7,  # Control randomness
        top_p=0.9,  # Use nucleus (top-p) sampling
        top_k=50  # Consider only the top 50 words for each generation step
    )[0]['generated_text']

    # Extract bot's reply
    bot_reply = generated_text.split("House Bot:")[-1].strip()

    # Add custom insights based on sensor data
    if sensor_data["temperature"] > 30:
        bot_reply += " The house feels quite warm. You might want to turn on the AC or fans to cool it down."
    elif sensor_data["temperature"] < 20:
        bot_reply += " The house feels cold. Consider increasing the heating or using a heater."

    if sensor_data["humidity"] > 60:
        bot_reply += " The humidity level in the house is high, which might feel uncomfortable. A dehumidifier could help."
    elif sensor_data["humidity"] < 40:
        bot_reply += " The air in the house is dry. Using a humidifier would improve comfort."

    if sensor_data["gas_level"]=="normal":
        bot_reply += " Caution: The gas levels are slightly elevated in the house. Ensure windows are open for proper ventilation."
    elif sensor_data["gas_level"] == "high":
        bot_reply += " WARNING: High gas levels detected! Take immediate action, ventilate the house, and ensure gas appliances are checked."

    return bot_reply
