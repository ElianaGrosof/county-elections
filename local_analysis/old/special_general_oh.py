import pandas as pd

#general_oh16 = pd.read_csv("../openelections-data-oh/2014/20141104__oh__general.csv")
general_oh16 = pd.read_csv("../openelections-data-oh/2014/20141104__oh__general__precinct.csv")

print(general_oh16.columns)

offices = general_oh16["office"].unique()
totalvotes = general_oh16["votes"].sum()
counties = general_oh16["county"].unique()
counties = ["Adams"]
precincts = general_oh16["Precinct Name"].unique()

for office in offices:
    for county in counties:
        for precinct in precincts:
            totalprecinct = general_oh16.loc[(general_oh16["county"] == county) & (general_oh16["Precinct Name"] == precinct)]
            print(totalprecinct["office"], totalprecinct["votes"])
            break
            totalprecinctvotes = totalprecinct["votes"].sum()
            print("Total Votes for ", precinct, ":", totalprecinctvotes)
            precinctoffice = general_oh16.loc[(general_oh16["office"] == office) & (general_oh16["county"] == county) & (general_oh16["Precinct Name"] == precinct)]
            precinctofficevotes = precinctoffice["votes"].sum()
            print("For precinct", precinct, " in ", county, "county", office, " got ", round(precinctofficevotes / totalprecinctvotes, 2),
                  "percent of the total votes")

            # totalcounty = general_oh16.loc[general_oh16["county"] == county]
            # totalcountyvotes = totalcounty["votes"].sum()
            # countyoffice = general_oh16.loc[(general_oh16["office"] == office) & (general_oh16["county"] == county)]
            # countyofficevotes = countyoffice["votes"].sum()
            # print("For: ", county, office, " got ", round(countyofficevotes/totalcountyvotes, 2), "percent of the total votes")

