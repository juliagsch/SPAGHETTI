# This script allows for fine-graines control over non-commuting trips.
import argparse
import numpy as np
import csv
import random

class ElectricVehicle:
    def __init__(self, battery_size, max_soc, min_soc, consumption):
        self.battery_size = battery_size
        self.max_soc = max_soc
        self.min_soc = min_soc
        self.consumption = consumption

    def compute_SOC_arr(self, dist_km):
        used_kwh = (dist_km * self.consumption) / 1000  
        soc_change = used_kwh / self.battery_size
        return max(self.max_soc * self.battery_size - soc_change, self.min_soc * self.battery_size)

class DayTrips:
    def __init__(self, num_trips: int, t_dep: float, t_arr: float, dist: float):
        self.num_trips = num_trips
        self.t_dep = t_dep
        self.t_arr = t_arr
        self.dist = dist

def validate_input(args):
    if not (0 <= args.max_soc <= 1 and 0 <= args.min_soc <= 1):
        raise ValueError("SOC values must be between 0 and 1")
    if args.max_soc < args.min_soc:
        raise ValueError("Max SOC must be greater than Min SOC")
    if args.ev_battery <= 0:
        raise ValueError("EV battery size must be a positive number")
    if args.consumption <= 0:
        raise ValueError("EV consumption must be a positive number")
    if not (0 <= args.C_dept < 24 and 0 <= args.C_arr < 24):
        raise ValueError("Departure and arrival times must be within 24-hour range")
    if args.C_dept >= args.C_arr:
        raise ValueError("Departure time must be before arrival time")
    for day in [args.wfh_monday, args.wfh_tuesday, args.wfh_wednesday, args.wfh_thursday, args.wfh_friday]:
        if day not in [0, 1]:
            raise ValueError("WFH day inputs must be either 0 or 1")
    if args.days <= 0:
        raise ValueError("Number of days must be a positive number")
    if args.C_dist <= 0 :
        raise ValueError("Commute distance must be positive")
    if args.N_nc < 0:
        raise ValueError("Number of weekly non-commuting trips must be non-negative")

def generate_trip_data(args, ev, day_trips):
    trip_data = []
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    wfh_days = {
        0: args.wfh_monday,
        1: args.wfh_tuesday,
        2: args.wfh_wednesday,
        3: args.wfh_thursday,
        4: args.wfh_friday
    }

    def reduce_soc(distance_km, current_soc):
        energy_used = (distance_km * ev.consumption) / 1000  
        soc_after_trip = current_soc - energy_used
        return max(ev.min_soc * ev.battery_size, soc_after_trip)

    average_speed_kmh = 50
    average_non_commute_trips_per_day = (args.N_nc / 2) / 7

    for day in range(args.days):
        week_day = day % 7
        is_wfh_day = wfh_days.get(week_day, 0) == 1
        is_weekend = week_day in [5, 6]
        current_soc = ev.max_soc * ev.battery_size
        trips_today = []

        # Add commuting trips on non-WFH weekdays
        if not is_wfh_day and not is_weekend:
            commute_dist = random.uniform(args.C_dist - args.C_dist * 0.1, args.C_dist + args.C_dist * 0.1)
            t_dep, t_arr = sample_commute_times(args)
            soc_start = current_soc
            soc_end = reduce_soc(commute_dist, soc_start)
            trips_today.append((weekdays[week_day], format_time(t_dep), soc_start, format_time(t_arr), soc_end))
            current_soc = soc_end

        # Non-commuting trips
        day_trip = day_trips[week_day]
        if day_trip is not None:
            for _ in range(day_trip.num_trips):
                t_dep, t_arr = day_trip.t_dep, day_trip.t_arr
                travel_time_hours = t_arr - t_dep
                non_commute_dist = day_trip.dist
                soc_start = current_soc
                soc_end = reduce_soc(non_commute_dist, soc_start)
                trips_today.append((weekdays[week_day], format_time(t_dep), soc_start, format_time(t_arr), soc_end))
                current_soc = soc_end
        else:
            # Existing logic for non-commuting trips
            num_non_commute_trips = np.random.poisson(average_non_commute_trips_per_day)
            for _ in range(num_non_commute_trips):
                t_dep, t_arr = sample_non_commute_times(args)
                travel_time_hours = t_arr - t_dep
                non_commute_dist = travel_time_hours * average_speed_kmh
                soc_start = current_soc
                soc_end = reduce_soc(non_commute_dist, soc_start)
                trips_today.append((weekdays[week_day], format_time(t_dep), soc_start, format_time(t_arr), soc_end))
                current_soc = soc_end
                
        if not trips_today:
            max_soc_value = ev.max_soc * ev.battery_size
            trips_today.append((weekdays[week_day], "No trips", f"{max_soc_value:.2f}", "", f"{max_soc_value:.2f}"))


        trip_data.append((day + 1, trips_today))

    return trip_data

def format_time(time_float):
    """Converts time in float format to HH:MM format"""
    hours = int(time_float)
    minutes = int((time_float - hours) * 60)
    return f"{hours:02d}:{minutes:02d}"

def sample_commute_times(args):
    """Sample departure and arrival times for commuting, ensuring consistency"""
    t_dep_hour = random.uniform(args.C_dept - 0.25, args.C_dept + 0.25)  # Departure time with small variance
    t_arr_hour = random.uniform(args.C_arr - 0.25, args.C_arr + 0.25)  # Arrival time with small variance
    
    # Ensure arrival is after departure
    while t_arr_hour <= t_dep_hour:
        t_arr_hour = random.uniform(args.C_arr - 0.25, args.C_arr + 0.25)

    return t_dep_hour, t_arr_hour

def sample_non_commute_times(args):
    """Randomly sample departure and arrival times for non-commuting trips, ensuring consistency"""
    t_dep_hour = random.uniform(8, 20)  # Assuming non-commuting trips can start between 8 AM and 8 PM
    trip_duration = random.uniform(0.5, 2)  # Duration between 30 minutes and 2 hours
    t_arr_hour = t_dep_hour + trip_duration

    return t_dep_hour, t_arr_hour

def write_to_csv(file_name, data):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Day", "Weekday", "Departure Time", "SOC on Departure", "Arrival Time", "SOC on Arrival"])
        for day, trips in data:
            for trip in trips:
                if len(trip) == 5:  # Ensure trip data has all necessary elements
                    writer.writerow([day, *trip])
                else:
                    writer.writerow([day, *trip, ""])  # Add empty string for missing SOC on Arrival

def main(args):
    validate_input(args)
    ev = ElectricVehicle(args.ev_battery, args.max_soc, args.min_soc, args.consumption)

    day_trips = [
    DayTrips(args.mon_nc, args.mon_dept, args.mon_arr, args.mon_dist) if args.mon_nc is not None else None,
    DayTrips(args.tue_nc, args.tue_dept, args.tue_arr, args.tue_dist) if args.tue_nc is not None else None,
    DayTrips(args.wed_nc, args.wed_dept, args.wed_arr, args.wed_dist) if args.wed_nc is not None else None,
    DayTrips(args.thu_nc, args.thu_dept, args.thu_arr, args.thu_dist) if args.thu_nc is not None else None,
    DayTrips(args.fri_nc, args.fri_dept, args.fri_arr, args.fri_dist) if args.fri_nc is not None else None,
    DayTrips(args.sat_nc, args.sat_dept, args.sat_arr, args.sat_dist) if args.sat_nc is not None else None,
    DayTrips(args.sun_nc, args.sun_dept, args.sun_arr, args.sun_dist) if args.sun_nc is not None else None
]


    trip_data = generate_trip_data(args, ev, day_trips)
    write_to_csv(args.output, trip_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sample synthetic EV usage data.')
    parser.add_argument('--output', type=str, default='ev_usage.csv', help='Output file name')
    parser.add_argument('--days', type=int, default=365, help='Desired number of days sampled')
    parser.add_argument('--ev_battery', type=float, default=40, help='EV battery size in kWh')
    parser.add_argument('--max_soc', type=float, default=0.8, help='Maximum state of charge')
    parser.add_argument('--min_soc', type=float, default=0.2, help='Minimum state of charge')
    parser.add_argument('--consumption', type=float, default=164, help='Consumption in Wh/km')
    parser.add_argument('--wfh_monday', type=int, default=0, choices=[0, 1], help='WFH on Monday')
    parser.add_argument('--wfh_tuesday', type=int, default=0, choices=[0, 1], help='WFH on Tuesday')
    parser.add_argument('--wfh_wednesday', type=int, default=0, choices=[0, 1], help='WFH on Wednesday')
    parser.add_argument('--wfh_thursday', type=int, default=0, choices=[0, 1], help='WFH on Thursday')
    parser.add_argument('--wfh_friday', type=int, default=0, choices=[0, 1], help='WFH on Friday')
    parser.add_argument('--C_dist', type=float, default=20.0, help='Typical commute distance in km')
    parser.add_argument('--C_dept', type=float, default=7.45, help='Departure time for commuting')
    parser.add_argument('--C_arr', type=float, default=17.30, help='Arrival time from commuting')
    parser.add_argument('--N_nc', type=int, default=5, help='Weekly number of non-commuting one-way trips')
    parser.add_argument('--mon_nc', type=int, help='Number of non-commuting trips on Monday')
    parser.add_argument('--mon_dept', type=float, help='Typical non-commuting departure time on Monday')
    parser.add_argument('--mon_arr', type=float, help='Typical non-commuting arrival time on Monday')
    parser.add_argument('--mon_dist', type=float, help='Typical non-commuting distance on Monday')
    parser.add_argument('--tue_nc', type=int, help='Number of non-commuting trips on Tuesday')
    parser.add_argument('--tue_dept', type=float, help='Typical non-commuting departure time on Tuesday')
    parser.add_argument('--tue_arr', type=float, help='Typical non-commuting arrival time on Tuesday')
    parser.add_argument('--tue_dist', type=float, help='Typical non-commuting distance on Tuesday')
    parser.add_argument('--wed_nc', type=int, help='Number of non-commuting trips on Wednesday')
    parser.add_argument('--wed_dept', type=float, help='Typical non-commuting departure time on Wednesday')
    parser.add_argument('--wed_arr', type=float, help='Typical non-commuting arrival time on Wednesday')
    parser.add_argument('--wed_dist', type=float, help='Typical non-commuting distance on Wednesday')
    parser.add_argument('--thu_nc', type=int, help='Number of non-commuting trips on Thursday')
    parser.add_argument('--thu_dept', type=float, help='Typical non-commuting departure time on Thursday')
    parser.add_argument('--thu_arr', type=float, help='Typical non-commuting arrival time on Thursday')
    parser.add_argument('--thu_dist', type=float, help='Typical non-commuting distance on Thursday')
    parser.add_argument('--fri_nc', type=int, help='Number of non-commuting trips on Friday')   
    parser.add_argument('--fri_dept', type=float, help='Typical non-commuting departure time on Friday')
    parser.add_argument('--fri_arr', type=float, help='Typical non-commuting arrival time on Friday')
    parser.add_argument('--fri_dist', type=float, help='Typical non-commuting distance on Friday')
    parser.add_argument('--sat_nc', type=int, help='Number of non-commuting trips on Saturday')
    parser.add_argument('--sat_dept', type=float, help='Typical non-commuting departure time on Saturday')
    parser.add_argument('--sat_arr', type=float, help='Typical non-commuting arrival time on Saturday')
    parser.add_argument('--sat_dist', type=float, help='Typical non-commuting distance on Saturday')
    parser.add_argument('--sun_nc', type=int, help='Number of non-commuting trips on Sunday')
    parser.add_argument('--sun_dept', type=float, help='Typical non-commuting departure time on Sunday')
    parser.add_argument('--sun_arr', type=float, help='Typical non-commuting arrival time on Sunday')
    parser.add_argument('--sun_dist', type=float, help='Typical non-commuting distance on Sunday')

    args = parser.parse_args()
    try:
        main(args)
    except ValueError as e:
        print(f"Input Error: {e}")
