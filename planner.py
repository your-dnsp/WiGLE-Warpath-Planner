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

CONFIG_FILE = 'config.json'

def load_config():
    """
    Load API credentials from a configuration file.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """
    Save API credentials to a configuration file.
    """
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

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
    print("Please wait...")
    return start_location, search_radius_m, network_type

def fetch_wifi_data(lat, lon, radius, network_type, api_name, api_token, verbose=True):
    """
    Fetch Wi-Fi network data from Wigle.net API.
    
    Args:
    lat (float): Latitude of the center point.
    lon (float): Longitude of the center point.
    radius (int): Radius in meters to search for networks.
    network_type (str): Type of networks to target.
    api_name (str): API name (username) for Wigle.net.
    api_token (str): API token for Wigle.net.
    verbose (bool): Enable verbose output.
    
    Returns:
    list: List of Wi-Fi networks.
    """
    url = "https://api.wigle.net/api/v2/network/search"
    params = {
        "latrange1": lat - (radius / 111320),  # Convert radius to lat/lon degrees
        "latrange2": lat + (radius / 111320),
        "longrange1": lon - (radius / 111320),
        "longrange2": lon + (radius / 111320),
        "resultsPerPage": 500  # Fetch up to 500 results for denser path
    }
    
    if network_type == "free":
        params["freenet"] = "true"
    elif network_type == "secure":
        params["freenet"] = "false"
    
    auth = base64.b64encode(f"{api_name}:{api_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json().get('results', [])
        if verbose:
            print(f"Fetched {len(results)} networks.")
        return results
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"Error fetching data: {e}")
        sys.exit(1)

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
    coordinates = [(start_lat, start_lon)] + [(network['trilat'], network['trilong']) for network in networks]
    distance_matrix = cdist(coordinates, coordinates, metric='euclidean')
    
    # Use a greedy algorithm for simplicity, prioritize closest networks first
    route = [0]
    while len(route) < len(coordinates):
        last = route[-1]
        next_distances = distance_matrix[last]
        next_node = np.argmin([next_distances[j] if j not in route else np.inf for j in range(len(coordinates))])
        route.append(next_node)
    
    ordered_networks = [networks[i - 1] for i in route[1:]]
    if verbose:
        print(f"Optimized route with {len(ordered_networks)} points.")
    return ordered_networks

def get_snapped_route_chunk(route_chunk, mapbox_token, verbose=True):
    """
    Get a snapped route for a chunk of coordinates using Mapbox Directions API.
    
    Args:
    route_chunk (list): List of (lat, lon) tuples for a chunk.
    mapbox_token (str): Mapbox API token.
    verbose (bool): Enable verbose output.
    
    Returns:
    list: List of (lat, lon) tuples for the snapped route chunk.
    """
    if len(route_chunk) < 2:
        return route_chunk
    
    coords = ";".join([f"{lon},{lat}" for lat, lon in route_chunk])
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coords}?geometries=geojson&access_token={mapbox_token}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        route = response.json()["routes"][0]["geometry"]["coordinates"]
        return [(lat, lon) for lon, lat in route]
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"Error fetching snapped route: {e}")
        sys.exit(1)

def get_snapped_route(route_coordinates, mapbox_token, verbose=True):
    """
    Get a route snapped to the roads using Mapbox Directions API in chunks.
    
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
        if verbose:
            print(f"Error fetching coordinates: {e}")
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
        if verbose:
            print(f"Error fetching address: {e}")
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
    
    folium.PolyLine(
        locations=snapped_route,
        color="orange", weight=10  # Make the line orange and very thick for visibility
    ).add_to(map_)
    
    # Get the current time in epoch format
    epoch_time = int(time.time())
    filename = f"wardriving_route_{epoch_time}.html"
    map_.save(filename)
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

def main():
    """
    Main function to run the Wardriving Route Planner.
    """
    config = load_config()
    while True:
        # Get user input for route planning
        start_location, search_radius, network_type = get_user_input(config)
        
        # Ensure configuration is saved after getting inputs
        save_config(config)
        
        try:
            # Handle either address or latitude, longitude input
            if is_lat_lon(start_location):
                start_lat, start_lon = map(float, start_location.split(","))
            else:
                start_lat, start_lon = get_lat_lon_from_address(start_location, config['mapbox_token'], True)
        
            # Fetch Wi-Fi network data
            networks = fetch_wifi_data(start_lat, start_lon, search_radius, network_type, config['wigle_api_name'], config['wigle_api_token'], True)
            
            if not networks:
                print("No networks found.")
                continue
            
            # Optimize the route to cover all networks
            route = optimize_route(networks, start_lat, start_lon, True)
            
            # Plot and save the route to an HTML file
            plot_route(route, start_lat, start_lon, config['mapbox_token'], True)
        
        except ValueError as e:
            print(e)
        
        # Ask the user if they want to make another query
        requery = input("Do you want to make another search? (yes/no): ").lower()
        if requery not in ['yes', 'y']:
            break

if __name__ == "__main__":
    main()
