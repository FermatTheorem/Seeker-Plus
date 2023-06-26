from SubDomainFinder import SubDomainFinder

scan = SubDomainFinder()
# scan.setTor()
scan.setRandomUA()
scan.setTarget('https://kantiana.ru/')
if not scan.checkConnection(scan.getTarget()):
    raise "Error connecting to the target"
scan.DNSZoneTransfer(scan.getTarget())
scan.CTLogs(scan.getTarget())
scan.WaybackMachine(scan.getTarget())
print(scan.getSubdomains())
# for domain in scan.getSubdomains():
#     if scan.validateUrl(domain):
#         print(domain)

