# Electric Vehicle Usage Data Simulation

## Overview

This script generates synthetic data for electric vehicle (EV) usage over a specified number of days. It simulates both commuting and non-commuting trips, taking into account the state of charge (SOC), battery capacity, and energy consumption of the vehicle. The script is designed to be flexible, allowing users to specify various parameters to tailor the simulation to their specific needs.

## Features

- Simulation of daily EV usage based on commuting and non-commuting patterns.
- Customisable parameters for EV characteristics such as battery size, SOC, and consumption.
- Options to specify work-from-home days, and typical commuting times and distances.
- Ability to define non-commuting trips for each day of the week with optional parameters for the number of trips, typical departure and arrival times, and distances.

## Usage

To use the EV Usage Data Generator, follow these steps:

1. Clone the repository or download the tool to your local machine.
 
2. Modify the input parameters in the `ev_generator.py` file to match your desired settings. These parameters include EV battery size, SOC limits, consumption rate, commuting patterns, and more.

3. Run the tool with the following command:

   ```
   python ev_generator.py
   ```

   By default, the tool will generate synthetic EV usage data for 365 days and save it to a CSV file named `ev_usage.csv`. You can specify different parameters and output filenames by providing command-line arguments. For example:

## Arguments

The ev_simulation.py script accepts several command-line arguments to customise the EV usage simulation:

- `--output`: Specifies the name of the output CSV file where the simulation data will be stored. Default is `ev_usage.csv`.
- `--days`: Sets the number of days for which the simulation will run. Default is `365`.
- `--ev_battery`: Defines the battery size of the EV in kWh. No default value.
- `--max_soc`: The maximum state of charge as a fraction (0 to 1) of the EV. Default is `0.8`.
- `--min_soc`: The minimum state of charge as a fraction (0 to 1) of the EV. Default is `0.2`.
- `--consumption`: The EV's energy consumption in Wh/km. The default value is `164`.
- `--wfh_[day]`: Indicates whether the day is a work-from-home day (`1` for yes, `0` for no). Replace `[day]` with `monday`, `tuesday`, etc. Default is `0` for all days.
- `--C_dist`: Typical commute distance in kilometers. The default value is `20.0`.
- `--C_dept`: Typical departure time for commuting. The default value is `7.45`, which correponds to 7h45.
- `--C_arr`: Typical arrival time from commuting. The default value is `17.30`, which correponds to 17h30.
- `--N_nc`: Weekly number of non-commuting one-way trips. Default is `5`.

### Non-Commuting Trip Parameters (Optional)

For each day of the week, the following optional parameters can be set in the file ev_simulation_extended.py (replace `[day]` with `mon`, `tue`, `wed`, `thu`, `fri`, `sat` or `sun`):

- `--[day]_nc`: Number of non-commuting trips for the day.
- `--[day]_dept`: Typical departure time for non-commuting trips.
- `--[day]_arr`: Typical arrival time for non-commuting trips.
- `--[day]_dist`: Typical distance for non-commuting trips in kilometers.

If these parameters are not provided for a specific day, random values are used to generate non-commuting trip data for that day.

### Example Commands

1. **Without Non-Commuting Trip Inputs:**
python ev_simulation.py --output ev_data_simple.csv --days 365 --ev_battery 40 --max_soc 0.8 --min_soc 0.2 --consumption 164 --wfh_monday 1 --C_dist 20 --C_dept 7.45 --C_arr 17.30 --N_nc 5

This command runs the simulation for 30 days with specified parameters for EV characteristics and commuting details, but without specific non-commuting trip details.

2. **With Detailed Non-Commuting Trip Inputs:**
python ev_simulation.py --output ev_data_detailed.csv --days 365 --ev_battery 50 --max_soc 0.9 --min_soc 0.3 --consumption 150 --wfh_monday 1 --C_dist 20 --C_dept 8.00 --C_arr 18.00 --N_nc 4 --mon_nc 2 --mon_dept 10.00 --mon_arr 14.00 --mon_dist 15 --tue_nc 1 --tue_dept 11.00 --tue_arr 13.00 --tue_dist 10 --wed_nc 3 --wed_dept 9.00 --wed_arr 15.00 --wed_dist 20

This command runs the simulation for 30 days with detailed input parameters for both commuting and non-commuting trips, including specific trip counts, times, and distances for Monday, Tuesday, and Wednesday.


4. Review the generated CSV file to analyse the EV usage data.

## Commands for the 3 WFH Type

# WFH T1: The Classic Commuter

python ev_simulation.py --output ev_data_detailed.csv --days 365 --ev_battery 40 --max_soc 0.8 --min_soc 0.2 --consumption 164 --wfh_monday 0 --wfh_tuesday 0 --wfh_wednesday 0 --wfh_thursday 0  --wfh_friday 0 --C_dist 13.4 --C_dept 8.00 --C_arr 18.00 --N_nc 2 

# WFH T2: The Hybrid Commuter

Here, we provide the command for T2.3, who works from home 3 days per week.

python ev_simulation.py --output ev_data_detailed.csv --days 365 --ev_battery 40 --max_soc 0.8 --min_soc 0.2 --consumption 164 --wfh_monday 1 --wfh_tuesday 0 --wfh_wednesday 1 --wfh_thursday 0  --wfh_friday 1 --C_dist 11.3 --C_dept 8.00 --C_arr 18.00 --N_nc 2 

# WFH T3: The Freelancer

python ev_simulation.py --output ev_data_detailed.csv --days 365 --ev_battery 40 --max_soc 0.8 --min_soc 0.2 --consumption 164 --wfh_monday 1 --wfh_tuesday 1 --wfh_wednesday 1 --wfh_thursday 1  --wfh_friday 1 --C_dist 9.6 --C_dept 8.00 --C_arr 18.00 --N_nc 2 

## Testing

The tool includes a test suite to ensure the correctness of the generated data and adherence to the specified assumptions. You can run the tests using the `unittest` framework. Use the following command to run the tests:

```
python test_ev_generator.py
```

The test suite covers various aspects, including input validation, SOC limits, EV charging, and randomness of traces.

## Assumptions

The tool is built based on several assumptions, including:

1. Input parameters are correctly formatted.
2. The EV is fully charged at departure time in the morning.
3. The EV's SOC never goes below the specified minimum SOC or above the maximum SOC.
4. The tool generates different traces every time due to a random component.

## Merge Overlapping Trips

Depending on the configuration of the input parameters, the tool can generate multiple trips per day. If you want to merge overlapping trips to single trips in the output file (e.g. merge a commuting trip with a shopping trip on the way home), you can run the file merge_trips.py .

## License

This tool is provided under the [MIT License](LICENSE). You are free to use, modify, and distribute it as needed. Refer to the LICENSE file for more details.

## Author

Anaïs Berkes

## Contact

If you have any questions or feedback, please feel free to contact the author at [amcb6@cl.cam.ac.uk].

---
