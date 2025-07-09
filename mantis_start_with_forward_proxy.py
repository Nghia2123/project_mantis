import argparse
import sys
import os

from mantis_start import main

def scan_config_options():
	config_dir = "confs"
	config_options = []
	for filename in os.listdir(config_dir):
		if filename.endswith(".py") and not filename.startswith("__"):
			module_name = f"{config_dir}.{filename[:-3]}"
			config_options.append(module_name)
	return config_options

def select_config():
	config_options = scan_config_options()
	if not config_options:
		print("No configuration files found in 'confs' directory.")
		sys.exit(1)

	print("Select configuration:")
	for idx, option in enumerate(config_options, 1):
		print(f"{idx}. {option}")
	while True:
		try:
			choice = int(input("Enter your choice (number): "))
			if 1 <= choice <= len(config_options):
				return config_options[choice - 1]
			else:
				print("Invalid choice. Try again.")
		except ValueError:
			print("Invalid input. Enter a number.")

if __name__ == '__main__':
	print("""
	This script simulates deploying proxy Mantis forward to remote machine.
	1. Select the defense configuration.
	2. Enter the IP of the remote machine (destination_ip).
	3. Enter the ports to forward (space-separated).
	- Example: IP = 10.129.70.160, Ports = 135 139 445
	""")

	parser = argparse.ArgumentParser(description='Run Mantis on the host machine based on the configuration file provided and run a forward proxy on the given ports (to simulate the deployment of Mantis on a remote machine in tests).')

	parser.add_argument('destination_ip', nargs='?', help='Where to redirect the traffic.')

	parser.add_argument(
		'--ports',
		type=int,
		nargs='+',
		help='List of port numbers separated by spaces (e.g., --ports 8080 8081 8082)'
	)

	parser.add_argument(
		'--run_rpc_interface',
		action='store_true',
		help="Run RPC server for external clients"
	)
	
	args = parser.parse_args()

	if not args.destination_ip:
		args.destination_ip = input("Enter destination IP: ").strip()

	if not args.ports:
		while True:
			ports_input = input("Enter ports (separated by spaces): ").strip()
			try:
				args.ports = [int(p) for p in ports_input.split()]
				break
			except ValueError:
				print("Invalid input. Please enter valid port numbers separated by spaces.")

	conf_file = select_config()
	main(args, conf_file, with_forward=True)
