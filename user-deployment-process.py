#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

__author__ = 'jcmartin'

import csv
import re
import argparse

deployments = []

multivalues = [
    'OpenStackInvolvement',
    'InformationSources',
    'BusinessDrivers',
    'ProjectsUsed',
    'CurrentReleases',
    'APIFormats',
    'Hypervisors',
    'BlockStorageDrivers',
    'NetworkDrivers',
    'IdentityDrivers',
    'SupportedFeatures',
    'DeploymentTools',
    'OperatingSystems',
    'DeploymentStage'
]
skip = [
    'SurveyCreated',
    'SurveyEdited',
    'DeploymentCreated',
    'DeploymentEdited',
    'FirstName',
    'Surname',
    'Email',
    'Title',
    'OtherIndustry',
    'PrimaryCity',
    'PrimaryState',
    'OtherInformationSources',
    'FurtherEnhancement',
    'FoundationUserCommitteePriorities',
    'UserGroupName',
    'OtherBusinessDrivers',
    'WhatDoYouLikeMost',
    'OkToContact',
    'OtherHypervisor',
    'OtherBlockStorageDriver',
    'OtherNetworkDriver',
    'WhyNovaNetwork',
    'OtherIdentityDriver',
    'WorkloadsDescription',
    'OtherWorkloadsDescription',
    'OtherDeploymentTools',
    'OtherOperatingSystems',
    'BusinessDrivers',
    'Label'
]
keep = [
    'SurveyID',
    'DeploymentID',
    'NumCloudUsers',
    'Industry',
    'PrimaryCountry',
    'OrgSize',
    'UserGroupMember',
    'IsPublic',
    'DeploymentType',
    'ComputeNodes',
    'ComputeCores',
    'ComputeInstances',
    'BlockStorageTotalSize',
    'ObjectStorageNumObjects',
    'NetworkNumIPs'
]

newfields = {}
# need to normalize NumCloudUsers, PrimaryState(for US)
# make single value : DeploymentStage, CurrentReleases


def process_other_os(otheros, currentos):
    """
    Attempt to take the OtherOperatingSystems column, and merge it
    with the OperatingSystem column"
    """
    found_os = False
    newos = currentos
    os_mapping = {}
    os_mapping["CentOS"] = "CentOS"
    os_mapping["Fedora"] = "Fedora"
    os_mapping["FreeBSD"] = "FreeBSD"
    os_mapping["RHEL"] = "Red Hat Enterprise Linux"
    os_mapping["Red Hat"] = "Red Hat Enterprise Linux"
    os_mapping["RedHat"] = "Red Hat Enterprise Linux"
    os_mapping["Scientific Linux"] = "Scientific Linux"

    for os in os_mapping.keys():
        if os in otheros and os not in newos:
            if newos == "":
                newos = os_mapping[os]
            else:
                newos = newos + "," + os_mapping[os]
            found_os = True
            print "adding " + os_mapping[os] + " for \"" + otheros + "\""

    if not found_os:
        if newos == "":
            newos = "Other"
        else:
            newos = newos + ",Other"
        print "Did not find a match for OtherOperatingSystems: ", otheros

    return newos

def process_other_hypervisor(otherhyp, currenthyp):
    """
    Attempt to take the OtherHypervisor column, and merge it
    with the Hypervisor column"
    """
    found_hyp = False
    newhyp = currenthyp
    hyp_mapping = {}
    hyp_mapping["ESXi"] = "esx"
    hyp_mapping["OpenVZ"] = "OpenVZ"
    hyp_mapping["XCP"] = "xenserver"
    hyp_mapping["QEMU"] = "QEMU"
    hyp_mapping["PowerVM"] = "PowerVM"
    hyp_mapping["Bare metal"] = "Bare Metal"
    hyp_mapping["Baremetal"] = "Bare Metal"
    hyp_mapping["baremetal"] = "Bare Metal"
    hyp_mapping["Docker"] = "Docker"
    hyp_mapping["docker.io"] = "Docker"

    for hyp in hyp_mapping.keys():
        if hyp in otherhyp and hyp not in newhyp:
            if newhyp == "":
                newhyp = hyp_mapping[hyp]
            else:
                newhyp = newhyp + "," + hyp_mapping[hyp]
            found_hyp = True
            print "adding " + hyp_mapping[hyp] + " for \"" + otherhyp + "\""

    if not found_hyp:
        if newhyp == "":
            newhyp = "Other"
        else:
            newhyp = newhyp + ",Other"
        print "Did not find a match for OtherHypervisor: ", otherhyp

    return newhyp

def process_other_blockstorage(otherbs, currentbs):
    """
    Attempt to take the OtherBlockStorageDriver column, and merge it
    with the BlockStorageDriver column"
    """
    found_bs = False
    newbs = currentbs
    bs_mapping = {}
    bs_mapping["Own"] = "Custom"
    bs_mapping["my own"] = "Custom"
    bs_mapping["Patched"] = "Custom"
    bs_mapping["Custom"] = "Custom"
    bs_mapping["custom"] = "Custom"
    bs_mapping["Homegrown"] = "Custom"
    bs_mapping["Direct to disk"] = "Custom"
    bs_mapping["Propriatary"] = "Custom"
    bs_mapping["Proprietary"] = "Custom"
    bs_mapping["proprietary"] = "Custom"
    bs_mapping["ISCSI"] = "iSCSI"
    bs_mapping["iSCSI"] = "iSCSI"
    bs_mapping["MooseFS"] = "MooseFS"
    bs_mapping["based"] = "Custom"
    bs_mapping["Equallogic"] = "EqualLogic"
    bs_mapping["EqualLogic"] = "EqualLogic"
    bs_mapping["ZFS"] = "ZFS"
    bs_mapping["Violin"] = "Violin"
    bs_mapping["HP MSA"] = "SAN/HP"

    for bs in bs_mapping.keys():
        if bs in otherbs and bs not in newbs:
            if newbs == "":
                newbs = bs_mapping[bs]
            else:
                newbs = newbs + "," + bs_mapping[bs]
            found_bs = True
            print "adding " + bs_mapping[bs] + " for \"" + otherbs + "\""

    if not found_bs:
        if newbs == "":
            newbs = "Other"
        else:
            newbs = newbs + ",Other"
        print "Did not find a match for OtherBlockStorageDriver: ", otherbs

    return newbs

def process_other_networkdriver(othernet, currentnet):
    """
    Attempt to take the OtherNetworkDriver column, and merge it
    with the NetworkDrivers column"
    """
    found_net = False
    newnet = currentnet
    net_mapping = {}
    net_mapping["Own"] = "Custom"
    net_mapping["our own"] = "Custom"
    net_mapping["Patched"] = "Custom"
    net_mapping["Custom"] = "Custom"
    net_mapping["custom"] = "Custom"
    net_mapping["Homegrown"] = "Custom"
    net_mapping["Home made"] = "Custom"
    net_mapping["Propriatary"] = "Custom"
    net_mapping["Proprietary"] = "Custom"
    net_mapping["proprietary"] = "Custom"
    net_mapping["Juniper"] = "Juniper"
    net_mapping["juniper"] = "Juniper"
    net_mapping["Arista"] = "Arista"
    net_mapping["Arista Networks"] = "Arista"
    net_mapping["ML2"] = "ML2"
    net_mapping["nova-network"] = "nova-network"
    net_mapping["Not sure"] = "Other"

    for net in net_mapping.keys():
        if net in othernet and net not in newnet:
            if newnet == "":
                newnet = net_mapping[net]
            else:
                newnet = newnet + "," + net_mapping[net]
            found_net = True
            print "adding " + net_mapping[net] + " for \"" + othernet + "\""

    if not found_net:
        if newnet == "":
            newnet = "Other"
        else:
            newnet = newnet + ",Other"
        print "Did not find a match for OtherNetworkDriver: ", othernet

    return newnet

def process_other_deptool(otherdt, currentdt):
    """
    Attempt to take the OtherDeploymentTool column, and merge it
    with the DeploymentTools column"
    """
    found_dt = False
    newdt = currentdt
    dt_mapping = {}
    dt_mapping["Own"] = "Custom"
    dt_mapping["our own"] = "Custom"
    dt_mapping["own script"] = "Custom"
    dt_mapping["based on"] = "Custom"
    dt_mapping["Patched"] = "Custom"
    dt_mapping["Custom"] = "Custom"
    dt_mapping["custom"] = "Custom"
    dt_mapping["Homegrown"] = "Custom"
    dt_mapping["Home made"] = "Custom"
    dt_mapping["own tool"] = "Custom"
    dt_mapping["Propriatary"] = "Custom"
    dt_mapping["Proprietary"] = "Custom"
    dt_mapping["proprietary"] = "Custom"
    dt_mapping["scripts"] = "Custom"
    dt_mapping["bcfg2"] = "bcfg2"
    dt_mapping["dodai"] = "dodai"
    dt_mapping["Substratum"] = "Substratum"
    dt_mapping["SwiftStack"] = "SwiftStack"
    dt_mapping["Cfengine"] = "CFEngine"
    dt_mapping["CFengine"] = "CFEngine"
    dt_mapping["CFEngine"] = "CFEngine"
    dt_mapping["cfengine"] = "CFEngine"
    dt_mapping["Foreman"] = "Foreman"
    dt_mapping["theforeman"] = "Foreman"
    dt_mapping["Fuel"] = "Fuel"
    dt_mapping["FA"] = "FAI"
    dt_mapping["by hand"] = "None"
    dt_mapping["Manual"] = "None"
    dt_mapping["manual"] = "None"
    dt_mapping["ansible"] = "Ansible"
    dt_mapping["Ansible"] = "Ansible"
    dt_mapping["Anvil"] = "Anvil"
    dt_mapping["StackOps"] = "StackOps"
    dt_mapping["Juju"] = "Juju"
    dt_mapping["juju"] = "Juju"

    for dt in dt_mapping.keys():
        if dt in otherdt and dt not in newdt:
            if newdt == "":
                newdt = dt_mapping[dt]
            else:
                newdt = newdt + "," + dt_mapping[dt]
            found_dt = True
            print "adding " + dt_mapping[dt] + " for \"" + otherdt + "\""

    if not found_dt:
        if newdt == "":
            newdt = "Other"
        else:
            newdt = newdt + ",Other"
        print "Did not find a match for OtherDeploymentTool: ", otherdt

    return newdt

def process_numusers(v):
    normalized_values = ['Prefer not to say',
                         '1-100 users',
                         '101-1,000 users',
                         '1,001-5,000 users',
                         '5,001-10,000 users',
                         '10,001-50,000 users',
                         '50,001-100,000 users',
                         'More than 100,000 users']
    if v in normalized_values:
        return v

    if v == '':
        return normalized_values[0]

    if isinstance(v, basestring):
        try:
            v = int(re.sub('[+~<>]', '', v))
        except ValueError as e:
            pass

    if isinstance(v, int):
        if v < 101:
            return normalized_values[1]
        if v < 1001:
            return normalized_values[2]
        if v < 5001:
            return normalized_values[3]
        if v < 10001:
            return normalized_values[4]
        if v < 50001:
            return normalized_values[5]
        if v < 100001:
            return normalized_values[6]
        if v > 100001:
            return normalized_values[7]

    return normalized_values[0]

def normalize(d, otheros=None, otherhyp=None, otherbs=None, othernet=None,
              otherdt=None):
    new_dict = {}
    for k, v in d.items():
        if k in keep:
            newfields[k] = ''
            new_dict[k] = v
        if k in multivalues:
            if v != '':
                if k == "OperatingSystems" and otheros is not None:
                    values = otheros.split(',')
                elif k == "Hypervisors" and otherhyp is not None:
                    values = otherhyp.split(',')
                elif k == "BlockStorageDrivers" and otherbs is not None:
                    values = otherbs.split(',')
                elif k == "NetworkDrivers" and othernet is not None:
                    values = othernet.split(',')
                elif k == "DeploymentTools" and otherdt is not None:
                    values = otherdt.split(',')
                else:
                    values = v.split(',')
                for mv in values:
                    field = k + ':' + mv
                    newfields[field] = ''
                    new_dict[k + ':' + mv] = 1
    return new_dict


def process_row(r):
    otheros = None
    otherhyp = None
    otherbs = None
    othernet = None
    otherdt = None
    if r.get('DeploymentID', '') != '':
        # it's a deployment
        if r.get('OtherOperatingSystems', '') != '':
            otheros = process_other_os(r.get('OtherOperatingSystems', ''),
                                   r.get('OperatingSystems', ''))
        if r.get('OtherHypervisor', '') != '':
            otherhyp = process_other_hypervisor(r.get('OtherHypervisor', ''),
                                               r.get('Hypervisors', ''))
        if r.get('OtherBlockStorageDriver', '') != '':
            otherbs = process_other_blockstorage(r.get('OtherBlockStorageDriver', ''),
                                                  r.get('BlockStorageDrivers', ''))
        if r.get('OtherNetworkDriver', '') != '':
            othernet = process_other_networkdriver(r.get('OtherNetworkDriver', ''),
                                                   r.get('NetworkDrivers', ''))
        if r.get('OtherDeploymentTools', '') != '':
            otherdt = process_other_deptool(r.get('OtherDeploymentTools', ''),
                                             r.get('DeploymentTools', ''))

        r['NumCloudUsers'] = process_numusers(r.get('NumCloudUsers', ''))

        x = normalize(r, otheros, otherhyp, otherbs, othernet, otherdt)
        #print x.get('DeploymentID')

        deployments.append(x)


def main():

    parser = argparse.ArgumentParser(description='Pre-process survey')
    parser.add_argument("input",
                    help="Input file")
    parser.add_argument("output",
                    help="Output file")

    args = parser.parse_args()
    with open(args.input, 'rU') as f:
        r = csv.DictReader(f)
        for row in r:
            process_row(row)

    # force some field position / assuming that those keys are not changing
    keys = ['SurveyID',
            'DeploymentID',
            'IsPublic',
            'PrimaryCountry',
            'OrgSize',
            'Industry',
            'DeploymentType',
            'NumCloudUsers']

    for k in sorted(newfields.keys()):
        if k not in keys:
            keys.append(k)

    print keys

    with open(args.output, 'w') as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(deployments)

if __name__ == "__main__":
    main()
