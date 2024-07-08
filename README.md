# NEW
- API keys are stored encrypted in a config file
- Use -h to get a list of arguments
- Denser path creation (for best results, keep your radius smaller)
- Snazzy looking stuff

# Wardriving Warpath Planner

This Python script generates a wardriving route for Wi-Fi networks around a specified location using the Wigle API and the Mapbox Directions API. The route is optimized to cover as many Wi-Fi networks as possible within a specified search radius and is snapped to roads for accuracy. The script generates an HTML file with a map displaying the route, and it prints the start and end locations as addresses, along with the total distance of the route in miles.

## Features

- **Fetch Wi-Fi Networks**: Fetch Wi-Fi network data from Wigle.net based on a specified search radius and network type (open, secure, or both).
- **Route Optimization**: Optimize the route to cover all target Wi-Fi networks using a greedy algorithm for simplicity.
- **Interactive Map**: Generate an interactive map with the optimized route using Folium and visualize it with dynamic color changes for path segments.
- **API Credentials Encryption**: Encrypt and store API credentials securely in a configuration file using the cryptography library.
- **Command-Line Arguments**: Support for command-line arguments to specify API credentials, starting location, search radius, network type, maximum points, and minimum signal strength.
- **Verbose Logging**: Enable verbose logging for detailed information and error handling.
- **Loading Spinners**: Display loading spinners during data fetching and route optimization to indicate progress.
- **Customizable Parameters**: Allow users to customize route parameters such as the maximum number of points and minimum signal strength.
- **Reminder Messages**: Remind users about wardriving best practices and safety tips after generating the route.

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
    pip install requests numpy scipy folium cryptography argparse
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
