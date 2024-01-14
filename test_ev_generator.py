# this test file tests the generator
import unittest
from ev_simulation import main, ElectricVehicle, generate_trip_data , run_simulation
import tempfile
import os
import argparse
import random

class TestEVGenerator(unittest.TestCase):
    def setUp(self):
        self.args = argparse.Namespace(
            output='test_ev_usage.csv',
            days=365,
            ev_battery=40,
            max_soc=0.8,
            min_soc=0.2,
            consumption=164,
            wfh_monday=0,
            wfh_tuesday=1,
            wfh_wednesday=0,
            wfh_thursday=1,
            wfh_friday=0,
            C_dist=20.0,
            C_dept=7.45,
            C_arr=17.30,
            N_nc=5
        )
    
    def test_input_format(self):
        # Test that all inputs have the correct format
        with tempfile.NamedTemporaryFile(suffix='.csv') as temp_output:
            self.args.output = temp_output.name
            main(self.args)  # Assuming main does not return a value

    def test_ev_soc_limits(self):
        # Test that EV SOC never goes below SOC min or above SOC max
        ev = ElectricVehicle(self.args.ev_battery, self.args.max_soc, self.args.min_soc, self.args.consumption)
        trip_data = generate_trip_data(self.args, ev)
        for day, trips in trip_data:
            for trip in trips:
                soc_start = float(trip[2])  # Convert SOC on Departure to float
                soc_end = float(trip[4])    # Convert SOC on Arrival to float
                if soc_start < ev.min_soc * ev.battery_size or soc_end < ev.min_soc * ev.battery_size:
                    self.fail(f"EV SOC below SOC min on Day {day}, Trip: {trip}")
                if soc_start > ev.max_soc * ev.battery_size or soc_end > ev.max_soc * ev.battery_size:
                    self.fail(f"EV SOC above SOC max on Day {day}, Trip: {trip}")

    def test_non_commuting_trips_generation(self):
        ev = ElectricVehicle(self.args.ev_battery, self.args.max_soc, self.args.min_soc, self.args.consumption)
        trip_data = generate_trip_data(self.args, ev)

        total_non_commuting_trips = sum(len(trips) for _, trips in trip_data if trips[0][1] != "No trips")
        expected_trips = self.args.N_nc * self.args.days / 7
        self.assertGreaterEqual(total_non_commuting_trips, expected_trips, "Not enough non-commuting trips generated")

    def test_charging_only_when_needed(self):
        ev = ElectricVehicle(self.args.ev_battery, self.args.max_soc, self.args.min_soc, self.args.consumption)
        trip_data = generate_trip_data(self.args, ev)

        for day, trips in trip_data:
            for trip in trips:
                soc_start = float(trip[2])
                if soc_start > ev.max_soc * ev.battery_size:
                    self.fail(f"Charged too much on Day {day}, Trip: {trip}")

    def test_invalid_input_handling(self):
        with self.assertRaises(ValueError):
            invalid_args = self.args
            invalid_args.max_soc = 1.5  # Invalid SOC
            run_simulation(invalid_args)


    def tearDown(self):
        if os.path.exists(self.args.output):
            os.remove(self.args.output)

if __name__ == '__main__':
    unittest.main()
