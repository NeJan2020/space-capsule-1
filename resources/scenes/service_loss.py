import random

import click

from resources.defects.network import loss
from spacecapsule.k8s import prepare_api, executor_command_inside_namespaced_pod


# case3:node network loss
@click.command()
@click.option('--node-name', 'node_name')
@click.option('--interface', 'interface')
@click.option('--percent', 'percent', default=80)
@click.option('--timeout', 'timeout', default=10000)
@click.option('--kube-config', 'kube_config', default="~/.kube/config")
def case3(node_name, interface, percent, timeout, kube_config):
    node_network_loss(node_name, interface, percent,  None, None, timeout, kube_config)


def node_network_loss(node_name, interface, percent, remote_port, local_port, timeout, kube_config):
    global api_instance, node_ip
    api_instance = prepare_api(kube_config)
    if node_name is None:
        # Choose a node
        pod_list = api_instance.list_namespaced_pod("practice")
        pod = select_pod_from_ready(pod_list.items)
        node_ip = pod.status.host_ip
        node_name = pod.spec.node_name
        print("select node_name:", node_name)
    else:
        node_list = api_instance.list_node()
        node_ip = select_node_ip(node_list.items, node_name)
        if node_ip is None:
            print("illegal node_name:not find node_ip", node_name)
            return

    if interface is None:
        # Choose a interface
        commands = [
            '/bin/sh',
            '-c',
            'ifconfig | grep -B 1 {}'.format(node_ip) + '| awk \'NR==1{print $1}\'',
        ]

        chaosblade_pod_list = api_instance.list_namespaced_pod('chaosblade')
        for chaosblade_pod in chaosblade_pod_list.items:
            if chaosblade_pod.spec.node_name == node_name:
                stdout, stderr = executor_command_inside_namespaced_pod(api_instance, 'chaosblade',
                                                                        chaosblade_pod.metadata.name,
                                                                        commands)
                interface = stdout
                print("select interface:", interface)
                break

    print("interface:", interface, "node_name:", node_name, "percent:", percent)

    loss('node', interface, percent, 'case3', None, remote_port, local_port, timeout,
         None, '22,10250', None, None, node_name, 'Insert a network loss into node {}, percent {}, timeout {}'
         .format(node_name, percent, timeout))

    print("node network loss injected done！")


def select_pod_from_ready(pods):
    ready = []
    for pod in pods:
        if pod_ready(pod):
            ready.append(pod)
    if len(ready) == 0:
        print('缺少合适的Pod')
        return None
    index = random.randint(0, len(ready) - 1)
    return ready[index]


def pod_ready(pod):
    for condition in pod.status.conditions:
        if condition.type == 'Ready' and condition.status == 'True':
            return True
    return False


def select_node_ip(nodes, input_node_name):
    for node in nodes:
        if input_node_name == node.metadata.name:
            for addr in node.status.addresses:
                if addr.type == 'InternalIP':
                    return addr.address
