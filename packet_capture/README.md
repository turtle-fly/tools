This tool packet_capture is used to start packet capture on capture point you care about.

Steps
=====
1. SSH to corresponding environment by credential you specify at inventory file

2. Start capture by tcpdump or pktcap-uw (on ESXi>=5.5)

3. This file is temporarily recorded as <HOME>/.pakcap.pcapng

4. Then this file is capture back to utility folder, renamed accordingly
