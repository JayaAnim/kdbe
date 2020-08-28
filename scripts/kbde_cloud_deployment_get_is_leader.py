#!/usr/bin/env python3


from kbde.cloud_deployment.leader import gcp


def check_all_host_providers():
    
    results = [
        gcp.GcpLeader().get_is_leader(),
    ]

    if any(results):
        print("yes")
    else:
        print("no")
        

check_all_host_providers()
