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

import pandas as pd
import argparse
import numpy as np


cols = [('DeploymentTools', 'OtherDeploymentTools'),
        ('NetworkDrivers', 'OtherNetworkDriver')]

dpt_map = {
    'Ansible': ['ansible'],
    'CFEngine': ['cfengine'],
    'Fuel': ['fuel'],
    'Foreman': ['foreman', 'theforeman'],
    'Juju': ['juju'],
    'Anvil': ['anvil'],
    'None': ['manual']
}
net_map = {
    'Custom': ['own', 'patched', 'custom', 'homegrown', 'proprietary'],
    'Juniper': ['juniper'],
    'Arista': ['arista'],
    'Modular Layer 2 Plugin': ['ML2']
}
terms_map = {
    'DeploymentTools': dpt_map,
    'NetworkDrivers': net_map
}
multivalue = [
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

def cleanup(f):
    # preprocess the dataframe to clean up import issues

    #drop empty lines
    f.dropna(axis=0, how='all', inplace=True)

    #drop rows where mandatory params are null:
    for row in ['SurveyCreated', 'SurveyEdited', 'OrgSize']:
        f = f[f[row].notnull()]

    #check that mandatory multiple choice are correct
    c1 = f['OrgSize'].map(lambda x: 'employees' in x)
    c2 = f['UserGroupMember'].map(lambda x: x in ['0', '1'])
    c3 = f['OkToContact'].map(lambda x: x in ['0', '1'])
    f = f.loc[c1 & c2 & c3]

    return f


def map_merge(m, mainterms, otherterms):
    if pd.isnull(otherterms):
        return mainterms
    term = None
    for k, v in m.items():
        for x in v:
            if x in otherterms.lower():
                term = k
    if not term:
        term = 'Other'
    if pd.isnull(mainterms):
        return term
    else:
        return '%s,%s' % (mainterms, term)


def process_other(f):

    for col, othercol in cols:
        oldcol = '%s-orig' % col
        f.rename(columns={col: oldcol}, inplace=True)
        col_map = terms_map[col]
        r = f.apply(lambda row: map_merge(col_map,
                                          row[oldcol],
                                          row[othercol]), axis=1)
        del f[oldcol]
        del f[othercol]
        f[col] = r

    return f

def main():

    parser = argparse.ArgumentParser(description='Pre-process survey')
    parser.add_argument("input",
                    help="Input file")

    parser.add_argument("output",
                    help="Output file")

    args = parser.parse_args()

    df = pd.read_csv(args.input, encoding='utf8')
    df = cleanup(df)

    # merge 'other' sections into normalized column
    df = process_other(df)

    # create dummies (categorization)
    for c in multivalue:
        s = df[c].str.get_dummies(sep=',')
        df = df.join(s.add_prefix('%s:' % c))

    df.to_csv(args.output, encoding='utf8')





if __name__ == "__main__":
    main()
