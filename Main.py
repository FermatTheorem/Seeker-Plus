from SubDomainFinder import SubDomainFinder

if __name__ == "__main__": #todo: proper cli
    scan = SubDomainFinder() #todo: change the relationships so the super class inherits others and not the otherwise?
    scan.setTor()
    scan.setRandomUA()
    scan.setThreads(32)
    scan.setTimeout(15) #todo: auto setting timeout higher if tor is enabled
    scan.setBruteThreads(1000)
    scan.setWordlist('/home/user/Subdomain.txt')
    scan.setTarget('https://www.kantiana.ru/')
    scan.setZoneTransfer(False)
    scan.setCrt(False)
    scan.setArchive(False)
    scan.setBruteForce(True)

    if not scan.validateUrl(scan.getTarget()):
        print("Error connecting to the target") #todo: error handling is the pain
        exit(1) #todo: why?

    scan.subDomainProcess(scan.getTarget())
    print(scan.getSubdomains())