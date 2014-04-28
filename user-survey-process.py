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
import argparse

responses = []

multivalues = [
    'OpenStackInvolvement',
    'InformationSources',
    'BusinessDrivers'
]
skip = [
    'DeploymentCreated',
    'DeploymentEdited',
    'FirstName',
    'Surname',
    'Email',
    'Title',
    'OtherIndustry',
    'PrimaryCity',
    'PrimaryState',
    'NumCloudUsers',
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
    'Industry',
    'PrimaryCountry',
    'OrgSize',
    'UserGroupMember',
    'SurveyCreated',
    'SurveyEdited'
]

newfields = {}
# need to normalize NumCloudUsers, PrimaryState(for US)
# make single value : DeploymentStage, CurrentReleases




def normalize(d):
    new_dict = {}
    for k, v in d.items():
        if k in keep:
            newfields[k] = ''
            new_dict[k] = v
        if k in multivalues:
            if v != '':
                values = v.split(',')
                for mv in values:
                    field = k + ':' + mv
                    newfields[field] = ''
                    new_dict[k + ':' + mv] = 1
    return new_dict


def process_row(r):

    x = normalize(r)

    responses.append(x)


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
            'IsPublic',
            'PrimaryCountry',
            'OrgSize',
            'Industry']

    for k in sorted(newfields.keys()):
        if k not in keys:
            keys.append(k)

    print keys
    print keys

    with open(args.output, 'w') as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(responses)

if __name__ == "__main__":
    main()
