import sys
import time
import argparse
import importlib
import os

from Mantis.InjectionManager.default import DefaultInjectionManager
from Mantis.utils import get_local_ip, get_public_ip
from Mantis.utils.logger import logger
from Mantis.InjectionManager.interface import InterfaceClientRPC
from Mantis.utils.Paper import forward_proxy

def scan_config_options():
    config_dir = "confs"
    config_options = []
    for filename in os.listdir(config_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"{config_dir}.{filename[:-3]}"  # remove .py
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


def main(args, conf_file, with_forward=False):
	conf = importlib.import_module(conf_file)
	
	local_ip = get_local_ip()
	public_ip = get_public_ip()

	if with_forward:
		if not args.ports:
			print("No ports to forward provided.")
			sys.exit(1)
		forward_proxy.forward_multiple_ports(local_ip, args.destination_ip, args.ports)

	if hasattr(conf, 'IP_partial_block'):
		IP_partial_block = conf.IP_partial_block
	else:
		IP_partial_block = False

	inj_manager = DefaultInjectionManager(
		conf.TRIGGER_EVENTS,
		local_ip,
		public_ip,
		IP_partial_block=IP_partial_block,
	)
	
	inj_manager.spawn_decoys(conf.DECOYS)

	if args.run_rpc_interface:
		ic = InterfaceClientRPC(inj_manager)
		ic()

	try:
		print("Mantis is running. Press Ctrl-C to exit.")
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		logger.info("KeyboardInterrupt caught — cleaning up")
		inj_manager.cleanup()
	


if __name__ == '__main__':
	print("""
	This script simulates deploying Mantis on a remote machine.
	- Select the defense configuration.
	""")

	parser = argparse.ArgumentParser(description='Run Mantis on the host machine based on the configuration file provided')

	parser.add_argument(
		'--run_rpc_interface',
		action='store_true',
		help="Run RPC server for external clients"
	)
	args = parser.parse_args()
	conf_file = select_config()
	main(args, conf_file, with_forward=False)
