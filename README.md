# Wardriving Warpath Planner

This Python script generates a wardriving route for Wi-Fi networks around a specified location using the Wigle API and the Mapbox Directions API. The route is optimized to cover as many Wi-Fi networks as possible within a specified search radius and is snapped to roads for accuracy. The script generates an HTML file with a map displaying the route, and it prints the start and end locations as addresses, along with the total distance of the route in miles.

## Features

- **GPX File Generation**: Added the ability to generate a GPX file for use with GPS devices, providing an additional format for route data.
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
- **Spinners and Loading Bars**: It gives feedback to the user and also looks super cool.
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
    pip install requests numpy scipy folium cryptography tqdm
    ```

## Usage

For help running the script, use:

    python planner.py --help
<<<<<<< HEAD
<<<<<<< HEAD

=======
>>>>>>> dc7f1852724868e90819e027c1cf5b8632821ac7
=======

## Instructions
>>>>>>> 7fb16669e62e8d79e87b96dd622089ca9ed81105

1. Obtain API credentials:
    - Sign up for a free account on [Wigle](https://wigle.net/) and obtain API keys.
    - Sign up for a free account on [Mapbox](https://www.mapbox.com/) and get an API token.

2. Run the script:
   ```
    python planner.py
   ```
<<<<<<< HEAD

<<<<<<< HEAD
=======
   
>>>>>>> 7fb16669e62e8d79e87b96dd622089ca9ed81105
3. Follow the prompts to enter:
    - **Wigle.net API Name**: Enter your Wigle.net API name.
    - **Wigle.net API Token**: Enter your Wigle.net API token.
    - **Mapbox API Token**: Enter your Mapbox API token.
    - **Starting Location**: Enter the starting location as either an address or latitude, longitude format (e.g., '123 Main St, Las Vegas, NV' or '36.1699,-115.1398').
    - **Search Radius**: Enter the search radius in kilometers (e.g., 2).
    - **Network Type**:
      - 1 - Open (Free networks)
      - 2 - Secure (Encrypted networks)
      - 3 - Both (All networks)
      - Enter your choice for network type (1 for Open, 2 for Secure, 3 for Both).
    - **Maximum Number of Wi-Fi Networks**: Enter the maximum number of Wi-Fi networks to consider (press Enter to use the default value of 2000).
    - **Minimum Signal Strength**: Enter the minimum signal strength to consider in dBm (press Enter to use the default value of -100).
    - **Verbose Output**: Would you like detailed (verbose) output? (yes/no).
    - **Repeat Search**: Do you want to make another search? (yes/no).
<<<<<<< HEAD
=======
=======

>>>>>>> 7fb16669e62e8d79e87b96dd622089ca9ed81105
4. Follow the prompts to enter:
    - Your Wigle.net API name and token (only once, will be saved in `config.json`).
    - Your Mapbox API token (only once, will be saved in `config.json`).
    - The starting location as either an address or latitude, longitude format (e.g., 36.1699,-115.1398).
    - The search radius in kilometers.
    - The type of networks to target (Open, Secure, Both).
>>>>>>> dc7f1852724868e90819e027c1cf5b8632821ac7

5. The script will generate an HTML file with the wardriving route and print the start and end locations, along with the total distance of the route in miles.

6. The script allows continuous querying. After each query, it will ask if you want to make another search.

## Example

```sh
$ python planner.py
Enter the starting location as either an address or latitude, longitude format (e.g., 36.1699,-115.1398).
Enter the starting location (address or lat,lon): 401 n grant st west lafayette in 47906
Enter the search radius in kilometers (e.g., 5): 1
Select the type of networks to target:
1 - Open (Free networks)
2 - Secure (Encrypted networks)
3 - Both (All networks)
Enter your choice for network type (1 for Open, 2 for Secure, 3 for Both): 3
Enter the maximum number of Wi-Fi networks to consider (press Enter to use the default value of 2000): 
Enter the minimum signal strength to consider in dBm (press Enter to use the default value of -100): 
Would you like detailed (verbose) output? (yes/no): yes
Please wait...
Resolved coordinates: 40.427642, -86.911141
Fetching networks... Done!                    Total so far: 2000.
Please wait...
Optimizing route... Done!
Please wait...
Saving HTML file... Done!
Wardriving route saved to 'wardriving_route_1720295065.html'
Turn-by-turn instructions saved to 'turn_by_turn_1720295065.txt'
GPX file saved to 'wardriving_route_1720295065.gpx'
Start location: 401 North Grant Street, West Lafayette, Indiana 47906, United States
End location: 1815 Northwestern Avenue, West Lafayette, Indiana 47906, United States
Total route distance: 0.33 miles

Summary Statistics:
Total networks found: 2000
Open networks: 1500
Secure networks: 500
Total route distance: 0.33 miles

Reminder:
1. Wardriving may require doubling back on the paths you've been on. You will go over some of the same areas more than once.
2. Have fun and be safe. Prep all your gear before getting behind the wheel. Get water for your walk.

Do you want to make another search? (yes/no): no
```

### Thank you!
Thank you to Ark and friends who have tested the script!
