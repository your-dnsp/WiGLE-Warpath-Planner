import requests
import base64
import numpy as np
from scipy.spatial.distance import cdist
import folium
import time
import re
import json
import sys
import os
import math
import threading
import itertools
import argparse
import logging
from cryptography.fernet import Fernet

CONFIG_FILE = 'config.json'
KEY_FILE = 'secret.key'
RETRY_LIMIT = 3  # Number of retries for network errors

# Set up logging
logging.basicConfig(filename='planner-log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def generate_key():
    """
    Generate a key for encryption and save it to a file.
    """
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def load_key():
    """
    Load the encryption key from the file.
    """
    return open(KEY_FILE, 'rb').read()

def encrypt_message(message, key):
    """
    Encrypt a message using the provided key.
    """
    f = Fernet(key)
    return f.encrypt(message.encode()).decode()

def decrypt_message(encrypted_message, key):
    """
    Decrypt an encrypted message using the provided key.
    """
    f = Fernet(key)
    return f.decrypt(encrypted_message.encode()).decode()

def load_config():
    """
    Load API credentials from a configuration file.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            encrypted_config = json.load(f)
        key = load_key()
        config = {
            'wigle_api_name': decrypt_message(encrypted_config['wigle_api_name'], key),
            'wigle_api_token': decrypt_message(encrypted_config['wigle_api_token'], key),
            'mapbox_token': decrypt_message(encrypted_config['mapbox_token'], key)
        }
        return config
    return {}

def save_config(config):
    """
    Save API credentials to a configuration file.
    """
    key = load_key()
    encrypted_config = {
        'wigle_api_name': encrypt_message(config['wigle_api_name'], key),
        'wigle_api_token': encrypt_message(config['wigle_api_token'], key),
        'mapbox_token': encrypt_message(config['mapbox_token'], key)
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(encrypted_config, f)

def parse_arguments():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Wardriving Route Planner")
    parser.add_argument('--wigle_api_name', type=str, help='Wigle.net API name')
    parser.add_argument('--wigle_api_token', type=str, help='Wigle.net API token')
    parser.add_argument('--mapbox_token', type=str, help='Mapbox API token')
    parser.add_argument('--start_location', type=str, help='Starting location (address or lat,long)')
    parser.add_argument('--radius_km', type=float, help='Search radius in kilometers')
    parser.add_argument('--network_type', type=str, choices=['open', 'secure', 'both'], help='Type of networks to target')
    parser.add_argument('--max_points', type=int, default=2000, help='Maximum number of points to consider')
    parser.add_argument('--min_signal_strength', type=int, default=-100, help='Minimum signal strength to consider')
    args = parser.parse_args()

    if any(arg in sys.argv for arg in ['--help', '--h', '-h', '-help', 'man']):
        parser.print_help()
        print("\nAdditional Information:")
        print("This script helps you plan a wardriving route by fetching Wi-Fi network data from Wigle.net and optimizing the route.")
        print("You can specify various parameters such as API credentials, starting location, search radius, network type, maximum points, and minimum signal strength.")
        print("Example Usage:")
        print("python planner.py --wigle_api_name your_username --wigle_api_token your_token --mapbox_token your_mapbox_token --start_location '123 Main St, Las Vegas, NV 89109, USA' --radius_km 5 --network_type both --max_points 2000 --min_signal_strength -80")
        sys.exit(0)

    return args

def get_user_input(config):
    """
    Get user input for starting location, area to cover, and network parameters.
    """
    if 'wigle_api_name' not in config or 'wigle_api_token' not in config:
        config['wigle_api_name'] = input("Enter your Wigle.net API name: ")
        config['wigle_api_token'] = input("Enter your Wigle.net API token: ")
    if 'mapbox_token' not in config:
        config['mapbox_token'] = input("Enter your Mapbox API token: ")

    print("Enter the starting location as either an address or latitude, longitude format (e.g., 36.1699,-115.1398).")
    start_location = input("Enter the starting location: ")
    search_radius_km = float(input("Enter the search radius in kilometers: "))
    search_radius_m = search_radius_km * 1000  # Convert kilometers to meters
    print("Select the type of networks to target:")
    print("1 - Open")
    print("2 - Secure")
    print("3 - Both")
    network_type_choice = input("Enter your choice (1, 2, or 3): ")
    network_type = "both" if network_type_choice == "3" else ("free" if network_type_choice == "1" else "secure")
    max_points = int(input("Enter the maximum number of points to consider (default 2000): ") or "2000")
    min_signal_strength = int(input("Enter the minimum signal strength to consider (default -100): ") or "-100")
    print("Please wait...")
    return start_location, search_radius_m, network_type, max_points, min_signal_strength

def reverse_haversine(lat, lon, distance, bearing):
    """
    Calculate the latitude and longitude of a point given a starting point, distance, and bearing.
    
    Args:
    lat (float): Latitude of the starting point.
    lon (float): Longitude of the starting point.
    distance (float): Distance from the starting point in meters.
    bearing (float): Bearing in degrees from north.
    
    Returns:
    tuple: Latitude and longitude of the calculated point.
    """
    R = 6371e3  # Earth radius in meters
    bearing = math.radians(bearing)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    
    lat2 = math.asin(math.sin(lat1) * math.cos(distance / R) + math.cos(lat1) * math.sin(distance / R) * math.cos(bearing))
    lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(distance / R) * math.cos(lat1), math.cos(distance / R) - math.sin(lat1) * math.sin(lat2))
    
    return math.degrees(lat2), math.degrees(lon2)

def fetch_wifi_data(lat, lon, radius, network_type, api_name, api_token, max_points, min_signal_strength, verbose=True):
    """
    Fetch Wi-Fi network data from Wigle.net API.
    
    Args:
    lat (float): Latitude of the center point.
    lon (float): Longitude of the center point.
    radius (int): Radius in meters to search for networks.
    network_type (str): Type of networks to target.
    api_name (str): API name (username) for Wigle.net.
    api_token (str): API token for Wigle.net.
    max_points (int): Maximum number of points to fetch.
    min_signal_strength (int): Minimum signal strength to consider.
    verbose (bool): Enable verbose output.
    
    Returns:
    list: List of Wi-Fi networks.
    """
    url = "https://api.wigle.net/api/v2/network/search"
    
    # Calculate bounding box using reverse haversine
    southwest = reverse_haversine(lat, lon, radius, 225)  # Southwest corner
    northeast = reverse_haversine(lat, lon, radius, 45)   # Northeast corner
    
    params = {
        "latrange1": southwest[0],
        "latrange2": northeast[0],
        "longrange1": southwest[1],
        "longrange2": northeast[1],
        "resultsPerPage": 100,  # Maximum results per page for Wigle API
        "offset": 0
    }
    
    if network_type == "free":
        params["freenet"] = "true"
    elif network_type == "secure":
        params["freenet"] = "false"
    
    auth = base64.b64encode(f"{api_name}:{api_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}"
    }
    
    networks = []
    retry_count = 0

    def spinner():
        for char in itertools.cycle('|/-\\'):
            if not loading:
                break
            sys.stdout.write(f'\rFetching networks... {char} ')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rFetching networks... Done!                    \n')
    
    # Start spinner
    loading = True
    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.start()

    while len(networks) < max_points:
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            results = response.json().get('results', [])
            if not results:
                break
            filtered_results = [r for r in results if r.get('signal', -100) >= min_signal_strength]
            networks.extend(filtered_results)
            params["offset"] += 100
            retry_count = 0  # Reset retry count after a successful fetch
            sys.stdout.write(f'\rFetched {len(filtered_results)} networks,  Total so far: {len(networks)}.')
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data: {e}")
            retry_count += 1
            if retry_count >= RETRY_LIMIT:
                break
            time.sleep(1)  # Wait for a second before retrying
    
    # Stop spinner
    loading = False
    spinner_thread.join()
    
    return networks[:max_points]

def optimize_route(networks, start_lat, start_lon, verbose=True):
    """
    Optimize the route to cover all target Wi-Fi networks.
    
    Args:
    networks (list): List of Wi-Fi networks.
    start_lat (float): Starting latitude.
    start_lon (float): Starting longitude.
    verbose (bool): Enable verbose output.
    
    Returns:
    list: Ordered list of Wi-Fi networks for the route.
    """
    def spinner():
        for char in itertools.cycle('|/-\\'):
            if not loading:
                break
            sys.stdout.write('\rOptimizing route... ' + char)
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rOptimizing route... Done!                    \n')
    
    coordinates = [(start_lat, start_lon)] + [(network['trilat'], network['trilong']) for network in networks]
    distance_matrix = cdist(coordinates, coordinates, metric='euclidean')
    
    # Start spinner
    loading = True
    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.start()
    
    # Use a greedy algorithm for simplicity, prioritize closest networks first
    route = [0]
    while len(route) < len(coordinates):
        last = route[-1]
        next_distances = distance_matrix[last]
        next_node = np.argmin([next_distances[j] if j not in route else np.inf for j in range(len(coordinates))])
        route.append(next_node)
    
    ordered_networks = [networks[i - 1] for i in route[1:]]
    
    # Stop spinner
    loading = False
    spinner_thread.join()
    
    return ordered_networks

def get_snapped_route_chunk(chunk, mapbox_token, verbose=True):
    """
    Get a snapped route for a chunk of coordinates using the Mapbox Directions API.
    
    Args:
    chunk (list): List of (lat, lon) tuples.
    mapbox_token (str): Mapbox API token.
    verbose (bool): Enable verbose output.
    
    Returns:
    list: List of (lat, lon) tuples for the snapped route.
    """
    url = "https://api.mapbox.com/directions/v5/mapbox/driving"
    coordinates = ";".join([f"{lon},{lat}" for lat, lon in chunk])
    params = {
        "access_token": mapbox_token,
        "geometries": "geojson"
    }
    
    try:
        response = requests.get(f"{url}/{coordinates}", params=params)
        response.raise_for_status()
        data = response.json()
        return [(point[1], point[0]) for point in data["routes"][0]["geometry"]["coordinates"]]
    except requests.exceptions.RequestException as e:
        if verbose:
            logging.error(f"Failed to fetch snapped route: {e}")
        return chunk

def get_snapped_route(route_coordinates, mapbox_token, verbose=True):
    """
    Get a snapped route for the full list of coordinates using the Mapbox Directions API.
    
    Args:
    route_coordinates (list): List of (lat, lon) tuples.
    mapbox_token (str): Mapbox API token.
    verbose (bool): Enable verbose output.
    
    Returns:
    list: List of (lat, lon) tuples for the snapped route.
    """
    snapped_route = []
    chunk_size = 25
    for i in range(0, len(route_coordinates), chunk_size - 1):
        chunk = route_coordinates[i:i + chunk_size]
        if len(chunk) < 2 and len(snapped_route) > 0:
            # Combine with previous chunk if not enough coordinates
            snapped_route[-1].extend(chunk)
        else:
            snapped_chunk = get_snapped_route_chunk(chunk, mapbox_token, verbose)
            snapped_route.append(snapped_chunk)
    
    # Flatten the list of snapped route chunks
    return [coord for chunk in snapped_route for coord in chunk]

def get_lat_lon_from_address(address, mapbox_token, verbose=True):
    """
    Get latitude and longitude from an address using Mapbox Geocoding API.
    
    Args:
    address (str): Address string.
    mapbox_token (str): Mapbox API token.
    verbose (bool): Enable verbose output.
    
    Returns:
    tuple: Latitude and longitude of the address.
    """
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json?access_token={mapbox_token}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["features"]:
            return data["features"][0]["center"][1], data["features"][0]["center"][0]
        else:
            raise ValueError("Address not found")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching coordinates: {e}")
        sys.exit(1)

def get_address(lat, lon, mapbox_token, verbose=True):
    """
    Get address for a given latitude and longitude using Mapbox Geocoding API.
    
    Args:
    lat (float): Latitude.
    lon (float): Longitude.
    mapbox_token (str): Mapbox API token.
    verbose (bool): Enable verbose output.
    
    Returns:
    str: Address for the given coordinates.
    """
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{lon},{lat}.json?access_token={mapbox_token}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["features"]:
            return data["features"][0]["place_name"]
        else:
            return "Address not found"
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching address: {e}")
        return "Address not found"

def calculate_total_distance(route_coordinates):
    """
    Calculate the total distance of the route in miles.
    
    Args:
    route_coordinates (list): List of (lat, lon) tuples.
    
    Returns:
    float: Total distance in miles.
    """
    total_distance = 0.0
    for i in range(1, len(route_coordinates)):
        total_distance += np.linalg.norm(np.array(route_coordinates[i]) - np.array(route_coordinates[i-1]))
    return total_distance * 0.621371  # Convert kilometers to miles

def plot_route(route, start_lat, start_lon, mapbox_token, verbose=True):
    """
    Plot the route on a map using Folium.
    
    Args:
    route (list): Ordered list of Wi-Fi networks for the route.
    start_lat (float): Starting latitude.
    start_lon (float): Starting longitude.
    mapbox_token (str): Mapbox API token.
    verbose (bool): Enable verbose output.
    
    Returns:
    None
    """
    map_ = folium.Map(location=[start_lat, start_lon], zoom_start=13)
    
    # Get the snapped route using Mapbox Directions API
    snapped_route = get_snapped_route([(start_lat, start_lon)] + [(network['trilat'], network['trilong']) for network in route], mapbox_token, verbose)
    
    colors = [
        "#FF0000", "#FF4000", "#FF7F00", "#FFBF00", "#FFFF00", "#BFFF00", "#7FFF00", "#40FF00",
        "#00FF00", "#00FF40", "#00FF7F", "#00FFBF", "#00FFFF", "#00BFFF", "#007FFF", "#0040FF",
        "#0000FF", "#4000FF", "#7F00FF", "#BF00FF", "#FF00FF", "#FF00BF", "#FF007F", "#FF0040"
    ]
    
    num_points = len(snapped_route)
    for i in range(num_points - 1):
        color_index = int((i / num_points) * len(colors))
        folium.PolyLine(
            locations=[snapped_route[i], snapped_route[i + 1]],
            color=colors[color_index], weight=5  # Dynamic color change for path segments, less thick lines
        ).add_to(map_)
    
    # Add start and end markers
    folium.Marker(
        location=[start_lat, start_lon],
        popup="Start",
        icon=folium.Icon(color='green')
    ).add_to(map_)
    
    if snapped_route:
        folium.Marker(
            location=snapped_route[-1],
            popup="End",
            icon=folium.Icon(color='blue')
        ).add_to(map_)
    
    # Get the current time in epoch format
    epoch_time = int(time.time())
    
    def spinner():
        for char in itertools.cycle('|/-\\'):
            if not loading:
                break
            sys.stdout.write('\rSaving HTML file... ' + char)
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rSaving HTML file... Done!                    \n')
    
    filename = f"wardriving_route_{epoch_time}.html"

    # Start spinner
    loading = True
    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.start()
    
    map_.save(filename)

    # Stop spinner
    loading = False
    spinner_thread.join()
    
    print(f"Wardriving route saved to '{filename}'")

    # Print the first and last locations
    if route:
        start_address = get_address(route[0]['trilat'], route[0]['trilong'], mapbox_token, verbose)
        end_address = get_address(route[-1]['trilat'], route[-1]['trilong'], mapbox_token, verbose)
        print(f"Start location: {start_address}")
        print(f"End location: {end_address}")
        
        total_distance = calculate_total_distance(snapped_route)
        print(f"Total route distance: {total_distance:.2f} miles")

def is_lat_lon(location):
    """
    Check if the location string is in latitude, longitude format.
    
    Args:
    location (str): Location string.
    
    Returns:
    bool: True if the string is in latitude, longitude format, else False.
    """
    return bool(re.match(r"^-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?$", location))

def print_rubber_duck_ascii_art():
    """
    Print ASCII art of a rubber duck.
    """
    duck_art = r"""
    >(')____,  >(')____,  >(')____,  >(')____,  >(') ___,
      (` =~~/    (` =~~/    (` =~~/    (` =~~/    (` =~~/
    ~~~^~^`---'~^~^~^`---'~^~^~^`---'~^~^~^`---'~^~^~^`---'
    """
    print(duck_art)

def main():
    """
    Main function to run the Wardriving Route Planner.
    """
    config = load_config()
    
    args = parse_arguments()
    
    if args.wigle_api_name:
        config['wigle_api_name'] = args.wigle_api_name
    if args.wigle_api_token:
        config['wigle_api_token'] = args.wigle_api_token
    if args.mapbox_token:
        config['mapbox_token'] = args.mapbox_token
    
    while True:
        # Get user input for route planning
        if args.start_location:
            start_location = args.start_location
            search_radius = args.radius_km * 1000  # Convert kilometers to meters
            network_type = args.network_type
            max_points = args.max_points
            min_signal_strength = args.min_signal_strength
        else:
            start_location, search_radius, network_type, max_points, min_signal_strength = get_user_input(config)
        
        # Ensure configuration is saved after getting inputs
        save_config(config)
        
        try:
            # Handle either address or latitude, longitude input
            if is_lat_lon(start_location):
                start_lat, start_lon = map(float, start_location.split(","))
            else:
                start_lat, start_lon = get_lat_lon_from_address(start_location, config['mapbox_token'], True)
        
            # Fetch Wi-Fi network data
            networks = fetch_wifi_data(start_lat, start_lon, search_radius, network_type, config['wigle_api_name'], config['wigle_api_token'], max_points, min_signal_strength, True)
            
            if not networks:
                print("No networks found in the specified area. Try increasing the search radius or checking the network type.")
                continue
        
            # Optimize the route
            print("Please wait...")
            optimized_route = optimize_route(networks, start_lat, start_lon, True)
        
            # Plot the route on a map
            plot_route(optimized_route, start_lat, start_lon, config['mapbox_token'], True)
        
            print("\nReminder:")
            print("1. Wardriving may require doubling back on the paths you've been on. You will go over some of the same areas more than once.")
            print("2. Have fun and be safe. Prep all your gear before getting behind the wheel. Get water for your walk.\n")
        
            # Prompt the user if they want to make another search
            another_search = input("Do you want to make another search? (yes/no): ").strip().lower()
            if another_search not in ["yes", "y"]:
                print_rubber_duck_ascii_art()
                break
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    if not os.path.exists(KEY_FILE):
        generate_key()
    main()
