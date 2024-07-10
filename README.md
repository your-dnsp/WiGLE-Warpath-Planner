# Wardriving Warpath Planner

This Python script generates a wardriving route for Wi-Fi networks around a specified location using the Wigle API and the Mapbox Directions API. The route is optimized to cover as many Wi-Fi networks as possible within a specified search radius and is snapped to roads for accuracy. The script generates an HTML file with a map displaying the route, and it prints the start and end locations as addresses, along with the total distance of the route in miles.

## Features

- **API Integration**: Fetches Wi-Fi network data from Wigle.net and maps routes using Mapbox API.
- **Customizable Route Parameters**: Allows users to specify starting location, search radius, network type, maximum points, and minimum signal strength.
- **Route Optimization**: Uses a greedy algorithm to prioritize the closest networks and optimize the route.
- **Dynamic Route Plotting**: Plots the route on a map with dynamic color changes based on the progress of the route.
- **Snapped Routes**: Utilizes Mapbox Directions API to snap the route to roads, ensuring a realistic driving path.
- **Turn-by-Turn Instructions**: Generates a text file with turn-by-turn driving instructions for the optimized route.
- **Verbose Mode**: Provides detailed output and feedback during the execution of the script.
- **Error Handling**: Includes robust error handling and logging to ensure smooth execution.
- **Configuration File**: Stores API credentials securely in an encrypted configuration file.
- **Command-Line Arguments**: Supports various command-line arguments for flexibility and ease of use.
- **User-Friendly Prompts**: Interactive prompts guide the user through the setup and execution of the script.
- **Spinners**: Because loading spinners are cool.
- **Rainbow Path Lines**: Colors the path lines in a rainbow gradient for better visualization and cuteness.
- **Route Distance Calculation**: Calculates and displays the total route distance in miles.

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
    pip install requests numpy scipy folium geopy cryptography argparse
    ```

## Usage

For help running the script, use:

    ```sh
    python planner.py --help
    ```

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
Fetching networks... Done!
Optimizing route... Done!
Saving HTML file... Done!
Wardriving route saved to 'wardriving_route_1720295065.html'
Start location: 123 Main St, Las Vegas, NV 89109, USA
End location: 456 Another St, Las Vegas, NV 89109, USA
Total route distance: 3.75 miles

Reminder:
1. Wardriving may require doubling back on the paths you've been on. You will go over some of the same areas more than once.
2. Have fun and be safe. Prep all your gear before getting behind the wheel. Get water for your walk.

Do you want to make another search? (yes/no):
```

### Thank you!
Thank you to Ark and friends who have tested the script!
