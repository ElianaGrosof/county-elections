'''
This script takes data about the 2018 midterm elections in several swing states,
maps each county to its FIPS code so that it can plotted on a map, and
calculates various metrics about each county.

The data comes from static openelections.net data downloaded sometime in May 2020.
The county-FIPS data comes from census.gov.
'''

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

fipsmap = {} # dictionary of dictionaries of states mapped to counties mapped to fips codes - see mapsfipsmap()
statecountymap = {}

'''
This function makes a dictionary of dictionaries of states mapped to counties mapped to fips codes.
The dictionary is saved into a global variable called fipsmap.
To access county FIPS code: fipsmap[STATEABBREVIATION][county] = FIPS
'''
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


'''

This function takes a DataFrame containing information about a single state, and
re-categorizes various party abbreviations into 3 parties: DEM (Democrat), REP (Republican), OTHER

returns: cleaned DataFrame
'''

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

'''
This function is a function that helps determine how to clean the offices and parties for each state.
It was a precursor to cleanparty().

The function prints out the possible parties and offices for each state
'''
def viewpartyofficeinfo():
    for state in statenames:
        filename = swinggeneral18[state]
        df = pd.read_csv('../'+filename)
        offices = df["office"].unique()
        candidates = df["candidate"].unique()
        parties = df["party"].unique()
        print(state)
        print("Offices", offices)
        print("Parties", parties)

'''
This function calculates various metrics from the raw data, and saves that information into a new DataFrame for each state.
'''
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
            dem_total = countydf[(countydf["party"] == 'DEM') & (countydf['office'] == office)]["votes"].sum(skipna=True)
            rep_total = countydf[(countydf["party"] == 'REP') & (countydf['office'] == office)]["votes"].sum(skipna=True)
            other_total = countydf[(countydf["party"] == 'OTHER') & (countydf['office'] == office)]["votes"].sum(skipna=True)

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

    return offices, statsnooffice

def main():

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

        print(state)

        offices, statsnooffice = makeaggregated(df, counties, state)

        officesheet = state+'stats'
        noofficesheet = officesheet+'_county'


        #note: I made a blank .xlsx with the 090320_county_elections_sansoffice.xlsx before running the program
        with pd.ExcelWriter('../stats/090320_county_elections_sansoffice.xlsx', mode='a') as writer: statsnooffice.to_excel(writer, sheet_name=noofficesheet)


main()