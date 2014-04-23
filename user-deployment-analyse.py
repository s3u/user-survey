__author__ = 'jemartin'

import pandas as pd
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
    releases = [x for x in frame.columns if 'CurrentReleases' in x]
    businessdrivers = [x for x in frame.columns if 'BusinessDrivers' in x]
    involvements = [x for x in frame.columns if 'OpenStackInvolvement' in x]

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
        p = pv[stages].rename(columns=lambda x: x.split(':')[1])

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
    pv.rename(index=lambda x: x.split(':')[1], inplace=True)

    pv.to_excel(writer, 'releases')

    start = 15
    df = pd.DataFrame(index=releases)

    for stage in stages:
        prod = pd.pivot_table(frame, values=releases, cols=stage,
                              aggfunc=sum)
        header = [stage.split(':')[1]]
        prod.rename(index=lambda x: x.split(':')[1], inplace=True)
        prod.columns = [header]
        df = pd.merge(df, prod,
                      right_index=True,
                      left_index=True,
                      how='right')

    df.to_excel(writer, 'releases', startrow=start)

    # Generate the stats by technologies.
    # Remember that the survey allows for multiple values in several places
    # this results in sums across dimension that are higher than number of
    # entries.

    technologies = [
        'DeploymentTools',
        'Hypervisors',
        'IdentityDrivers',
        'NetworkDrivers',
        'OperatingSystems',
        'ProjectsUsed',
        'SupportedFeatures',
        'BlockStorageDrivers',
        'APIFormats'
    ]

    start = 0
    # hack : I need to have a group that is selecting all the rows
    frame['All'] = pd.Series([1 for i in range(len(frame.index))],
                             index=frame.index)

    for tech in technologies:
        tech_values = [x for x in frame.columns if tech in x]

        # create the first row to have no stage selection
        # note: this is not the sum of the stage values.

        df = pd.pivot_table(frame, values=tech_values, cols='All',
                            aggfunc=sum)
        df.columns = ['Any']

        df.rename(index=lambda x: x.split(':')[1], inplace=True)

        # Accumulate the columns for each stage by doing a right join.
        for stage in stages:
            pv = pd.pivot_table(frame, values=tech_values, cols=stage,
                                aggfunc=sum)
            pv.rename(index=lambda x: x.split(':')[1], inplace=True)
            header = [stage.split(':')[1]]
            pv.columns = [header]
            df = pd.merge(df, pv,
                          right_index=True,
                          left_index=True,
                          how='right')

        df.to_excel(writer, 'technologies', startcol=start)
        start += 6

    frame.to_excel(writer, 'data')

    pv = pd.pivot_table(frame, values=businessdrivers, cols='All', aggfunc=sum)
    pv.columns = ['Count']

    pv.rename(index=lambda x: x.split(':')[1], inplace=True)

    pv.to_excel(writer, 'general')

    cols = ['PrimaryCountry', 'OrgSize', 'Industry']
    start = 4
    for col in cols:
        series = frame.groupby(col).size()
        pv = pd.DataFrame(series)
        pv.columns = ['Count']
        pv.to_excel(writer, 'general', startcol=start)
        start += 4

    pv = pd.pivot_table(frame, values=involvements, cols='All', aggfunc=sum)
    pv.columns = ['Count']

    pv.rename(index=lambda x: x.split(':')[1], inplace=True)

    pv.to_excel(writer, 'general', startcol=start)

    writer.save()


if __name__ == "__main__":
    main()
