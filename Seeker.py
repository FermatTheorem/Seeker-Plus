#!/usr/bin/env python3
from Scanner import Scanner
import argparse


def print_banner():
    banner = """

 _____         _                _   
|   __|___ ___| |_ ___ ___    _| |_ 
|__   | -_| -_| '_| -_|  _|  |_   _|
|_____|___|___|_,_|___|_|      |_|  

    Seeker Plus - Subdomain Enumeration Tool
    Made by @FermatTheorem
    """
    print(banner)

def print_techniques():
    help = """
Subdomain enumeration techniques:
* DNS Zone Transfer (Z)
* CT Logs (C)
* Archive of Wayback Machine (A)
* Bruteforce (B)
* Hackertarget reverse IP lookup API: https://api.hackertarget.com/reverseiplookup (R) 
* Hackertarget hostsearch API: https://api.hackertarget.com/hostsearch (H)

Neighbor enumeration techniques:
* Hackertarget API: https://api.hackertarget.com/reverseiplookup (H)
"""
    print(help)

def main():
    epilog = """
Usage Examples:
./Seeker.py -u example.com --tor
python3 Seeker.py -u https://www.example.com --timeout 30
python3 Seeker.py -url example.com --proxy localhost:8080 --bruteforce
        """
    parser = argparse.ArgumentParser(description='Seeker Plus - subdomain enumeration tool', epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-u', '--url', help='The target domain to enumerate subdomains for', required=True)
    parser.add_argument('-m', '--mode', help='Subdomains (s), Neighbors (n), All (a)', default='s')
    parser.add_argument('-o', '--output-dir', help='Output directory', default='Output')
    parser.add_argument('-a', '--agent', help='User-Agent to use in requests')
    parser.add_argument('-H', '--headers', help='Headers to use in requests')
    parser.add_argument('--proxy', help='Http proxy address:port (127.0.0.1:8080)')  # maybe we need a protocol split
    parser.add_argument('--timeout', help='Request timeout in seconds', default=15, type=int)
    parser.add_argument('-t', '--threads', help='Number of threads for concurrent requests (not used atm)', default=10,
                        type=int)
    parser.add_argument('--tor', help='Use Tor proxy for requests', action='store_true')
    parser.add_argument('--tor-port', help='Tor proxy port', default=9050, type=int)
    parser.add_argument('--check-tor', help='Check whether tor is configured correctly', action='store_true')
    parser.add_argument('--rua', '--randomua', help='Use random User-Agent every request', action='store_true')
    parser.add_argument('--s-techniques', help='Techniques to use for subdomain enumeration. Default: "ZCA". More about techniques: --techniques', default="ZCRHA")
    parser.add_argument('--n-techniques', help='Techniques to use for searching sites on the same server. Default: "HA". More about techniques: --techniques', default="H")
    parser.add_argument('--techniques', help='Print information about available techniques and exit', action='store_true')
    parser.add_argument('--bruteforce', help='Use bruteforce ("B" technique)', action='store_true')
    parser.add_argument('-w', '--wordlist', help='Path to the wordlist for bruteforce')
    parser.add_argument('-v', '--validate', help='Validate found websites', action='store_true')
    parser.add_argument('-T', '--sThreads', help='Number of threads for bruteforce and validation', default=1000, type=int)
    parser.add_argument('--print', help='Print the results in console', action='store_true')
    args = parser.parse_args()
    print_banner()
    if args.techniques:
        print_techniques()
        return

    # setting everything up
    scan = Scanner()
    scan.setTarget(args.url)
    scan.setOutputDir(args.output_dir)
    scan.setTimeout(args.timeout)
    scan.setThreads(args.threads)
    scan.setSysThreads(args.sThreads)
    scan.setZoneTransfer("Z" in args.s_techniques.upper())
    scan.setCrt("C" in args.s_techniques.upper())
    scan.setHackertargetReverseS("R" in args.s_techniques.upper())
    scan.setHackertargetHost("H" in args.s_techniques.upper())
    scan.setArchive("A" in args.s_techniques.upper())
    scan.setHackertargetReverse("H" in args.n_techniques.upper())
    if args.tor:
        scan.setTor()
    if args.tor_port:
        scan.setTor(args.tor_port)
    if args.agent:
        scan.setUserAgent(args.agent)
    if args.headers:
        scan.setHeaders(args.headers)
    if args.proxy:
        scan.setProxy(args.proxy)
    if args.rua:
        scan.setRandomUA()
    if args.bruteforce or "B" in args.s_techniques.upper():
        scan.bruteForce = args.bruteforce
        scan.setWordlist(args.wordlist)
    if args.tor and args.timeout < 15:
        print("Automatically raising up the timeout to 15 sec since the --tor key is provided")
        scan.setTimeout(15)
    if args.check_tor:
        scan.checkTor()

    # processing
    if args.mode == 's' or args.mode == 'a':
        scan.subDomainProcess(scan.getTarget())
        fileWrite(f"{scan.getOutputDir()}/Unvalidated_subdomains.txt", scan.getSubdomains())
        if args.validate:
            scan.subdomains = scan.validateUrls(scan.getSubdomains())
            fileWrite(f"{scan.getOutputDir()}/Validated_subdomains.txt", scan.getSubdomains())

    if args.mode == 'n' or args.mode == 'a':
        scan.neighborProcess(scan.getTarget())
        fileWrite(f"{scan.getOutputDir()}/Unvalidated_neighbors.txt", scan.getNeighbors())
        if args.validate:
            scan.neighbors = scan.validateUrls(scan.getNeighbors())
            fileWrite(f"{scan.getOutputDir()}/Validated_neighbors.txt", scan.getNeighbors())

    if args.print:
        if args.mode == 's' or args.mode == 'a':
            print(f"{'-'*50}\n{' '*20}Subdomains\n{'-'*50}")
            for subdomain in scan.getSubdomains():
                print(subdomain)
        if args.mode == 'n' or args.mode == 'a':
            print(f"{'-'*50}\n{' '*20}Neighbors\n{'-'*50}")
            for neighbor in scan.getNeighbors():
                print(neighbor)

def fileWrite(file, list):
    with open(file, 'w') as f:
        f.write('\n'.join(list))

if __name__ == "__main__":
    main()