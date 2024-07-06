# NEW
- More verbose messaging
- A config file so you only need to enter your API keys once!
- Denser path creation

# Wardriving Route Planner

This Python script generates a wardriving route for Wi-Fi networks around a specified location using the Wigle API and the Mapbox Directions API. The route is optimized to cover as many Wi-Fi networks as possible within a specified search radius and is snapped to roads for accuracy. The script generates an HTML file with a map displaying the route, and it prints the start and end locations as addresses, along with the total distance of the route in miles.

## Features

- Generates a wardriving route for Wi-Fi networks around a specified location.
- Uses the Wigle API to fetch Wi-Fi network data.
- Uses the Mapbox Directions API to snap the route to roads.
- Displays the route on a map with thick orange lines for visibility.
- Prints the start and end locations as addresses.
- Calculates and prints the total distance of the route in miles.
- Prompts the user for API credentials and search parameters.
- Supports verbose mode by default for detailed output.
- Stores API credentials in a configuration file (`config.json`) to avoid repeated input.
- Allows continuous querying without restarting the script.

## Requirements

- Python 3.x
- Requests
- Numpy
- Scipy
- Folium

## Installation

1. Clone the repository or download the script file.
2. Install the necessary dependencies:

    ```sh
    pip install requests numpy scipy folium
    ```

## Usage

1. Obtain API credentials:
    - Sign up for a free account on [Wigle](https://wigle.net/).
    - Sign up for a free account on [Mapbox](https://www.mapbox.com/) and get an API token.

2. Run the script:

    ```sh
    python planner.py
    ```

3. Follow the prompts to enter:
    - Your Wigle.net API name and token (only once, will be saved in `config.json`).
    - Your Mapbox API token (only once, will be saved in `config.json`).
    - The starting location as either an address or latitude, longitude format (e.g., 36.1699,-115.1398).
    - The search radius in kilometers.
    - The type of networks to target (Open, Secure, Both).

4. The script will generate an HTML file with the wardriving route and print the start and end locations, along with the total distance of the route in miles.

5. The script allows continuous querying. After each query, it will ask if you want to make another search.

## Example

```sh
Enter your Wigle.net API name: your_wigle_username
Enter your Wigle.net API token: your_wigle_token
Enter your Mapbox API token: your_mapbox_token
Enter the starting location: 123 Main St, Las Vegas, NV 89109, USA
Enter the search radius in kilometers: 5
Select the type of networks to target:
1 - Open
2 - Secure
3 - Both
Enter your choice (1, 2, or 3): 3
Please wait...
Fetched 500 networks.
Wardriving route saved to 'wardriving_route_XXXXXXXXXX.html'
Start location: 123 Main St, Las Vegas, NV 89109, USA
End location: 456 Elm St, Las Vegas, NV 89109, USA
Total route distance: 4.23 miles
Do you want to make another search? (yes/no): yes
```