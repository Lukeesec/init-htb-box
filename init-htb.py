#!/usr/bin/env python3

import argparse
from colorama import Fore, Style
import htb
import os
import subprocess

def error(input):
	return print(f'[{Fore.RED}error{Style.RESET_ALL}] {input}')

def info(input, text='info'):
	return print(f'[{Fore.CYAN}{text}{Style.RESET_ALL}] {input}')

def get_key(key_path):
	if key_path is None:
		key_path = '../../.htb-api'
		return(open_file(key_path))
	else:
		return(open_file(key_path))

def open_file(key_path):
	try:
		with open(key_path,'r') as fs:
			api_key = fs.read().strip()
	except:
		error(f'The file {key_path} does not exist')
		exit()
	else:
		return(api_key)

def get_box(api_key, name):
	try:
		HTB = htb.HTB(api_key)
		boxes = HTB.get_machines()
	except:
		error('The API key is not valid')
		exit()

	for box in boxes:
		if box['name'] == name:
			return(box)

def scan_box(ip_addr, name, nmap, auto_recon):
	if auto_recon and nmap == True:
		error('-r/--autorecon and -s/--nmap cannot be used at the same time')
		exit()
	elif auto_recon == True:
		os.system('python3 /opt/AutoRecon/autorecon.py --only-scans-dir --single-target -o {0}.htb {1}'.format(name, ip_addr))
	elif nmap == True:
		os.makedirs(f'{name}.htb/scans', exist_ok=True)
		os.system(f'nmap -Pn -sC -sV -T4 -p- {ip_addr} -oN {name}.htb/scans/full-tcp-scan.nmap')

def install_hostname(ip_addr, name):
	with open('/etc/hosts', 'r') as fs:
		if name not in fs.read():
			info(f'Installing the hostname {name}.htb into /etc/hosts')
			subprocess.call(f"echo '# HTB\n{ip_addr}	{name}.htb' | sudo tee -a /etc/hosts > /dev/null", shell=True)
		else:
			info(f'The hostname {name} is already in /etc/hosts')

# Look into a better way of printing
def print_box(box_info):
	info(box_info['name'],'Name')
	info(box_info['ip'],'Address')
	info(box_info['os'],'OS')
	info(str(box_info['points']),'Points')
	info(box_info['rating'],'Rating')
	info(box_info['maker']['name'], 'Creator')

def main():
	parser = argparse.ArgumentParser(description='Initate a box in hack the box')
	parser.add_argument('--name', dest='name', help='Machine name to be looked up', required=True)
	parser.add_argument('-k', '--key_path', dest='key_path', help='Hack the box API key location (Default: ../../.htb-api')
	parser.add_argument('-a', '--autorecon', dest='recon', action='store_true', help='Run autorecon /opt/AutoRecon/autorecon.py')
	parser.add_argument('-n', '--nmap', dest='nmap', action='store_true', help='Run a full TCP nmap scan & add the box hostname to /etc/hosts')

	args = parser.parse_args()
	name = args.name
	key_path = args.key_path
	auto_recon = args.recon
	nmap = args.nmap

	name = name.title()

	api_key = get_key(key_path)

	box_info = get_box(api_key, name)
	if box_info == None:
		error(f'The box name {name} does not exist')
		exit()

	print_box(box_info)

	name = box_info['name']
	ip_addr = box_info['ip']
	name = name.lower()

	if nmap or auto_recon != False:
		install_hostname(ip_addr, name)
		scan_box(ip_addr, name, nmap, auto_recon)


if __name__ == '__main__':
	main()
