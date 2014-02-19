#!/usr/bin/python
################################################################
##Made by Joe                                                  #
##date: 22 aug 2013                                            #
##                                                             #
##Mac tracking in Cisco network                                #
##reqs:                                                        #
##    clogin from Rancid package (brew install rancid)         #
##    pexpect (http://www.noah.org/wiki/pexpect)               #
##                                                             #
## You can use part of the mac, or the whole thing.            #
## Syntax:                                                     #
## ex1: python mactrack_joe.py 10.0.0.10 b123                  #
## ex2: python mactrack_joe.py 10.0.0.10 1q2w.3e4r.5t56        #
################################################################

import sys,pexpect,re,time
ip = sys.argv[1]
mac = sys.argv[2]
end_ip = ''

while ip:
    if end_ip != '': 
        ip = end_ip
    child = pexpect.spawn('/usr/local/bin/clogin ' + ip ) #using clogin in Rancid from shrubbery
    child.logfile = sys.stdout #display on screen
    child.expect('[#>]') #expect prompt
    sw = child.before
    swfix = sw.split(' ')[-1].split()[-1] #sw-name without spaces as a list [-1] is there to make sure it's the last item in the list which gets picked
    sw1 = ''.join(swfix) + '#\r\n' #switchname with # and CR/LF
    sw2 = ''.join(swfix) + '#'
    child.send('show mac addr | inc ' + mac.lower()+'\r\n ')
       i = child.expect([pexpect.TIMEOUT, sw1])
    if i == 0: #timeout
        print 'ERROR ERROR ERROR' #print statements for testing
        print child.before, child.after
    output = re.findall('(Gi|Fa|Ten)(\d*/\d*/\d*|\d*/\d*)', child.before) #Get interface from from child.before
    if len(output) <= 0: #make sure there's atleast one match in output
        child.sendline('exit')
        sys.exit('Mac address has no relations to this switch')
    else:
        interface = ''.join(output[0]) #add the output item to interface
    if len(output) > 1:
        print "WARNING several matches: " + str(output) #warning, more matches found.
    child.sendline('show cdp neighbors '+ interface + ' d' ) #get details of the interface

    try:
        c = child.expect('--More--', timeout=2)
        cdp_ip = re.findall("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", child.before) #Find IP for next switch in child.before
        end_ip = ''.join(cdp_ip[0]) #add first item from cdp_ip to end_ip
        print '::::::'
        print end_ip
        print '::::::'
        child.sendline('\x03') #send space
        child.sendline('\rexit') #send exit
    except: # cast exception if end_ip is empty and display the mac, switch ip and interface
        print "Exception thrown" 
        print "debug info:"
        print str(child) #Not really needed anymore
        print "\nException thrown, goal reached:" #This is what you're after.
        print 'mac:', mac, '\nswitch IP:', ip, '\ninterface:', interface
        ip = '' #empty the IP for the while loop
