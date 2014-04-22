__author__ = 'jemartin'

import pandas as pd
import numpy as np
import argparse

def main():

    parser = argparse.ArgumentParser(description='Analyse survey')
    parser.add_argument("input",
                    help="Input file")

    parser.add_argument("output",
                    help="Output file")

    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    frame.fillna(value=0)
    stages = [x for x in frame.columns if 'DeploymentStage' in x]
    releases = list((x for x in frame.columns if 'CurrentReleases' in x))

    # Generate the stats per deployment Stage for scale factors
    cols = ['NetworkNumIPs',
            'BlockStorageTotalSize',
            'ObjectStorageNumObjects',
            'ComputeCores',
            'ComputeInstances',
            'ComputeNodes',
            'NumCloudUsers']

    writer = pd.ExcelWriter(args.output)
    start = 0
    for col in cols:
        pv = pd.pivot_table(frame, rows=col, aggfunc=sum)
        p = pv[stages]
        # TODO when generating the table, the label added in the rows, messing
        # up graphics - Need to remove the second line from the sheet.
        p.to_excel(writer, 'scale', startcol=start)
        start += 6

    # combining the above with DeploymentType can be done with:
    # x = pd.pivot_table(f,rows=['NetworkNumIPs'], cols='DeploymentType', aggfunc=sum)
    # and then select the combination through
    # x['DeploymentStage:Proof of Concept','On-Premise Private Cloud']

    # Generate the release stats per deployment type

    pv = pd.pivot_table(frame, values=releases,
                        cols='DeploymentType', aggfunc=sum)
    pv.to_excel(writer, 'releases')


    start = 15
    for stage in stages:
        prod = pd.pivot_table(frame, values=releases, cols=stage,
                              aggfunc=sum)
        header = [stage.split(':')[1]]

        prod.to_excel(writer, 'releases', startrow=start, header=header)
        start += 15

    writer.save()


if __name__ == "__main__":
    main()
