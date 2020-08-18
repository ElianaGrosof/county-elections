import pandas as pd

general_oh18 = pd.read_csv("../openelections-data-oh/2018/20181106__oh__general__precinct.csv")

print(general_oh18.columns)
offices = general_oh18["office"].unique()
print(offices)

#How many votes total were cast in this election (everyone)?
totalvotes = general_oh18["votes"].sum()

#9 things on ballot
#would expect about 22% of the vote to be for those two offices
#it's closer to 23.6, so not much difference

#How many of the votes cast were cast for U.S. House and/or U.S. Senate?
# national_office_votes = general_oh18.loc[(general_oh18["office"] == "U.S. House") | (general_oh18["office"] == "U.S. Senate")]
# nv = national_office_votes["votes"].sum()
# print(nv/totalvotes)

#How what percentage of the votes were cast for each candidate?
for office in offices:
    votesforoffice = general_oh18.loc[(general_oh18["office"] == office)]
    officevotes = votesforoffice["votes"].sum()
    print(office, " got ", round(officevotes/totalvotes, 2), "percent of the total votes")

#How many votes total were cast in Lorain County?
# loraindf = general_oh18.loc[general_oh18["county"] == "Lorain"] #makes a dataframe containing info only for Lorain county
# totallorain = loraindf["votes"].sum()
# print(totallorain)


