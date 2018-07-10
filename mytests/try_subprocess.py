import subprocess
print('nslookup www.python.org')
r = subprocess.call(['nslookup', 'www.python.org'])
print(r)

'''
output:

Server:		211.137.130.3
Address:	211.137.130.3#53

Non-authoritative answer:
www.python.org	canonical name = dualstack.python.map.fastly.net.
Name:	dualstack.python.map.fastly.net
Address: 151.101.40.223

0

'''

