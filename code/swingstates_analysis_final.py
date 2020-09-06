#modified and fixed August 31, 2020

import pandas as pd
import numpy as np

#results of Nov, 6 2018 election for each swing state
swinggeneral18 = {'Colorado' : 'openelections_data/openelections-data-co/2018/20181106__co__general__county.csv',
                'Iowa': "openelections_data/openelections-data-ia/2018/20181106__ia__general__county.csv",
                'Michigan' : "openelections_data/openelections-data-mi/2018/20181106__mi__general__precinct.csv",
                'Minnesota' : "openelections_data/openelections-data-mn/2018/20181106__mn__general__precinct.csv",
                'New Hampshire' : "openelections_data/openelections-data-nh/2018/20181106__nh__general__precinct.csv",
                'Nevada' : "openelections_data/openelections-data-nv/2018/20181106__nv__general__precinct.csv",
                'Ohio' : "openelections_data/openelections-data-oh/2018/20181106__oh__general__precinct.csv",
                'Pennsylvania' : "openelections_data/openelections-data-pa/2018/20181106__pa__general__county.csv",
                'Wisconsin' : "openelections_data/openelections-data-wi/2018/20181106__wi__general__ward.csv",
                'Florida' : "openelections_data/openelections-results-fl/modified/20181106__fl__general__precinct__raw.csv",
                'North Carolina' : "openelections_data/openelections-results-nc/modified/20181106__nc__general__precinct__raw.csv",
                'Virginia' : 'openelections_data/openelections-results-va/modified/20181106__va__general__precinct__raw.csv' }


statenames = ['Colorado', 'Iowa', 'Michigan', 'Minnesota', 'New Hampshire', 'Ohio', 'Pennsylvania', 'Wisconsin', 'Florida', 'North Carolina', 'Virginia']
stateabbs = {'Colorado':'CO', "Iowa":'IA', "Michigan":'MI', "Minnesota":'MN', "New Hampshire": 'NH', "Ohio":'OH', "Pennsylvania": 'PA', "Wisconsin":'WI', "Florida":'FL', "North Carolina":'NC', "Virginia":'VA'}

fipsmap = {}
statecountymap = {}

#makes a dictionary of dictionaries of states mapped to counties mapped to fips codes
# to access county FIPS code: fipsmap[STATEABBREVIATION][county] = FIPS
def makefipsmap():
    fipsdf = pd.read_csv("UScounties_UScounties.csv")
    for state in statenames:
        statefipsdf = fipsdf[fipsdf['State Name'] == state]

        #string cleaning
        statefipsdf["Name"] = statefipsdf["Name"].str.replace(r'[^\w\s]+', '')
        statefipsdf["Name"] = statefipsdf["Name"].str.lower()
        statecounties = statefipsdf["Name"]

        fipsmap[state] = {}
        for county in statecounties:
            fipscode = statefipsdf[statecounties == county]["Fips"].values[0]
            fipsmap[state][county] = fipscode


#clean party names up - categorize as DEM, REP, and OTHER
def cleanparty(df):
    #clean up non-democrat/republican
    df = df.dropna(subset=['party'])
    dropstrings = ["nan", 'Kevin', "'nan'",'Unaffiliated', 'Approval Voting', 'illegible last name', 'Bob Rasmussen', 'blank', "NP", "NPA", "UST", "Write-In", "WI", "UA", " r&l","r&l", "  r&l'","wri"]
    df = df[~df.party.isin(dropstrings)]
    #categorize as DEM, REP, OTHER
    df["party"] = np.where(((df.party == 'Democratic') | (df.party == 'DFL') | (df.party == 'Democratic Party') | (df.party == 'Dem')), 'DEM', df.party)
    df["party"] = np.where(((df.party == 'Republican') | (df.party == 'R') | (df.party == 'Republican Party') | (df.party == 'Rep')), 'REP', df.party)
    df["party"] = np.where(((df.party != 'REP') & (df.party != 'DEM')), 'OTHER', df.party)
    #also make the counties lowercase and remove punctuation
    df['county'] = df['county'].str.replace(r'[^\w\s]+', '')
    df['county'] = df['county'].str.lower()
    #make sure votes are read as ints
    df['votes'] = df['votes'].fillna(0)
    df['votes'] = df['votes'].astype(int)
    return df

#for use in determining how one needs to clean the data
#print out the possible parties and offices for each state
def viewpartyofficeinfo():
    # florida, nc, va data is significantly different from the others (raw) and likely needs to be handled separately
    for state in statenames:
        filename = swinggeneral18[state]
        df = pd.read_csv('../'+filename)
        offices = df["office"].unique()
        candidates = df["candidate"].unique()
        parties = df["party"].unique()
        print(state)
        print("Offices", offices)
        print("Parties", parties)

def makeaggregated(df, counties, state):
    statsnooffice = pd.DataFrame(columns=["State", "County", "FIPS","dem_total","rep_total","other_total","margin", "% margin"])
    stats = pd.DataFrame(columns=["State","County", "Office", "FIPS","dem_total","rep_total","other_total","margin"])

    totalvotes = 0

    for county in counties:
        countydf = df[((df["county"] == county) & (df["party"].str.contains("DEM") | df["party"].str.contains("REP") | df["party"].str.contains("OTHER")))]
        offices = countydf["office"].unique()
        totalmargin = 0
        totaldem = 0
        totalrep = 0
        totalother = 0

        #keeping track of races within each county
        racesdemswon = 0
        racesrepswon = 0
        totalraces = 0

        for office in offices:
            #dem_total, rep_total, other_total
            dem_total = countydf[(countydf["party"] == 'DEM') & (countydf['office'] == office)]["votes"].sum(skipna=True)
            rep_total = countydf[(countydf["party"] == 'REP') & (countydf['office'] == office)]["votes"].sum(skipna=True)
            other_total = countydf[(countydf["party"] == 'OTHER') & (countydf['office'] == office)]["votes"].sum(skipna=True)

            #print("dem_total %d, rep_total %d, other_total %d" % ( dem_total, rep_total, other_total))

            #if (other_total > dem_total) and (other_total > rep_total):
            #    print("Other party won with %d votes" % (other_total))


            otherwon = (other_total > dem_total) and (other_total > rep_total)
            otherdidwell = (other_total > dem_total) or (other_total > rep_total)

            if not otherdidwell:
                margin = dem_total - rep_total
                percentmarginoffice = (margin/(dem_total+rep_total))

                totalmargin += margin
                totaldem += dem_total
                totalrep += rep_total
                totalother += other_total

                # if a non-Democrat or non-Republican won, just increment total races but don't increment the races either party won
                if otherwon == False:
                    if totalmargin > 0:
                        racesdemswon += 1
                    else:
                        racesrepswon += 1
                else:
                    totalraces += 1

                totalvotes += (totaldem + totalrep + totalother)


        percentmargin = (totalmargin/(totaldem+totalrep))

        totalraces += (racesdemswon + racesrepswon)

        new_row_nooffice = {"State": state, "County": county, "FIPS": fipsmap[state][county], "dem_total": totaldem, "rep_total": totalrep,
                            "margin": totalmargin, "% margin": percentmargin, "total_races": totalraces, "dem_races_won": racesdemswon, "rep_races_won": racesrepswon}

        statsnooffice = statsnooffice.append(new_row_nooffice, ignore_index=True)

    print("total votes: ", totalvotes)
    #write_totals(state, totaldem, totalrep, totalother, totalraces, racesrepswon, racesdemswon)

    return offices, statsnooffice

# write a csv file with total votes cast in each state for Dems, Reps, Other
# also with a row for total races won, at the county level, for Dems, Reps, Other
def write_totals(state, totaldem, totalrep, totalother, totalraces, racesrepswon, racesdemswon):

    totalvotes = totaldem + totalrep + totalother
    racesotherwon = totalraces - (racesdemswon + racesrepswon)

    import csv
    with open('../stats/vote_totals_090320.csv', 'a') as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow([state])
        writer.writerow(['Total_votes_Dem','Total_votes_Rep', 'Total_votes_Other', 'Total_votes', 'Total_races', 'Races_Dem', 'Races_Rep', 'Races_Other'])
        writer.writerow([totaldem, totalrep, totalother, totalvotes, totalraces, racesdemswon, racesrepswon, racesotherwon])
        writer.writerow(['\n'])

    return

def main_0():

    makefipsmap()

    for state in statenames:
        filename = swinggeneral18[state]
        df = pd.read_csv('../'+filename)

        cleandf = cleanparty(df)
        #This is a New Hampshire-specific dataset cleaning thing
        cleandf = cleandf[~(cleandf.county == state.lower())]

        df = cleandf

        stateabb = stateabbs[state]
        counties = list(df["county"].unique())
        if 'total' in counties:
            counties.remove('total') # dataframe might have a row that says "total" in it, and I want to remove that

        #stats is for counts and preliminary metrics, one line per county per office
        #aggregatedstats = pd.DataFrame(columns=["State","County", "Office", "FIPS","dem_total","rep_total","other_total","margin"])
        print(state)

        offices, statsnooffice = makeaggregated(df, counties, state)

        officesheet = state+'stats'
        noofficesheet = officesheet+'_county'

        #with pd.ExcelWriter('../stats/090220_county_elections_office.xlsx', mode='a') as writer: stats.to_excel(writer, sheet_name=noofficesheet)
        #actually used this one
        #with pd.ExcelWriter('../stats/090320_county_elections_sansoffice.xlsx', mode='a') as writer: statsnooffice.to_excel(writer, sheet_name=noofficesheet)

def main():
    for state in statenames:
        print(state)
        filename = swinggeneral18[state]
        df = pd.read_csv('../'+filename)

        cleandf = cleanparty(df)
        #This is a New Hampshire-specific dataset cleaning thing
        cleandf = cleandf[~(cleandf.county == state.lower())]

        df = cleandf

        print((df["party"] == "OTHER").count())

        viewpartyofficeinfo()


main_0()