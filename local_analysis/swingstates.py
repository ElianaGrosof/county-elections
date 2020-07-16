import pandas as pd
import numpy as np

#results of Nov, 6 2018 election for each swing state
swinggeneral18 = {'Colorado' : 'openelections/openelections-data-co/2018/20181106__co__general__precinct.csv',
                'Iowa': "openelections/openelections-data-ia/2018/20181106__ia__general__precinct.csv",
                'Michigan' : "openelections/openelections-data-mi/2018/20181106__mi__general__precinct.csv",
                'Minnesota' : "openelections/openelections-data-mn/2018/20181106__mn__general__precinct.csv",
                'New Hampshire' : "openelections/openelections-data-nh/2018/20181106__nh__general__precinct.csv",
                'Nevada' : "openelections/openelections-data-nv/2018/20181106__nv__general__precinct.csv",
                'Ohio' : "openelections/openelections-data-oh/2018/20181106__oh__general__precinct.csv",
                'Pennsylvania' : "openelections/openelections-data-pa/2018/20181106__pa__general__county.csv",
                'Wisconsin' : "openelections/openelections-data-wi/2018/20181106__wi__general__ward.csv",
                'Florida' : "openelections/openelections-results-fl/modified/20181106__fl__general__precinct__raw.csv",
                'North Carolina' : "openelections/openelections-results-nc/modified/20181106__nc__general__precinct__raw.csv",
                'Virginia' : 'openelections/openelections-results-va/modified/20181106__va__general__precinct__raw.csv' }

statenames = ['Colorado', 'Iowa', 'Michigan', 'Minnesota', 'New Hampshire', 'Nevada', 'Ohio', 'Pennsylvania', 'Wisconsin', 'Florida', 'North Carolina', 'Virginia']
stateabbs = {'Colorado':'CO', "Iowa":'IA', "Michigan":'MI', "Minnesota":'MN', "New Hampshire": 'NH', "Nevada": 'NV', "Ohio":'OH', "Pennsylvania": 'PA', "Wisconsin":'WI', "Florida":'FL', "North Carolina":'NC', "Virginia":'VA'}

#removing states that will not actually be included in this analysis
statenames.remove('Nevada')
del stateabbs['Nevada']

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
    df["party"] = np.where(((df.party == 'Democratic') | (df.party == 'DFL')), 'DEM', df.party)
    df["party"] = np.where(((df.party == 'Republican') | (df.party == 'R')), 'REP', df.party)
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
        parties = df["party"].unique()
        print(state)
        print("Offices", offices)
        print("Parties", parties)

def makeaggregated(df, counties):
    statsnooffice = pd.DataFrame(columns=["State","County", "FIPS","dem_total","rep_total","other_total","margin", "% margin"])
    stats = pd.DataFrame(columns=["State","County", "Office", "FIPS","dem_total","rep_total","other_total","margin"])

    for county in counties:
        countydf = df[((df["county"] == county) & (df["party"].str.contains("DEM") | df["party"].str.contains("REP")))]
        offices = countydf["office"].unique()
        totalmargin = 0
        totaldem = 0
        totalrep = 0
        totalother = 0
        for office in offices:
            #dem_total, rep_total, other_total
            dem_total = countydf[(countydf["party"] == 'DEM') & (countydf['office'] == office)]["votes"].sum(skipna=True)
            rep_total = countydf[(countydf["party"] == 'REP') & (countydf['office'] == office)]["votes"].sum(skipna=True)
            other_total = countydf[(countydf["party"] == 'OTHER') & (countydf['office'] == office)]["votes"].sum(skipna=True)

            margin = dem_total - rep_total

            totalmargin += margin
            totaldem += dem_total
            totalrep += rep_total
            totalother += other_total

            new_row = {"State":state,"County":county,"Office":office,"FIPS":fipsmap[state][county],"dem_total":dem_total,"rep_total":rep_total,
                       "other_total":other_total,"margin":margin}

            stats = stats.append(new_row, ignore_index=True)

        percentmargin = (totalmargin/(totaldem+totalrep+totalother))*100

        new_row_nooffice = {"State": state, "County": county, "FIPS": fipsmap[state][county], "dem_total": totaldem, "rep_total": totalrep,
                   "other_total": totalother, "margin": totalmargin, "% margin": percentmargin}

        statsnooffice = statsnooffice.append(new_row_nooffice, ignore_index=True)

    return stats, offices, statsnooffice

makefipsmap()

for state in statenames:
    filename = swinggeneral18[state]
    df = pd.read_csv('../'+filename)

    cleandf = cleanparty(df)
    #This is a New Hampshire-specific dataset cleaning thing
    cleandf = cleandf[~(cleandf.county == state.lower())]

    df = cleandf

    stateabb = stateabbs[state]
    counties = df["county"].unique()

    #stats is for counts and preliminary metrics, one line per county per office
    #aggregatedstats = pd.DataFrame(columns=["State","County", "Office", "FIPS","dem_total","rep_total","other_total","margin"])
    print(state)

    stats, offices, statsnooffice = makeaggregated(df, counties)

    officesheet = state+'stats'
    noofficesheet = officesheet+'_county'

    #with pd.ExcelWriter('../stats/statsgen18_1.xlsx',mode='a') as writer: stats.to_excel(writer, sheet_name=officesheet)
    with pd.ExcelWriter('../stats/county_stats.xlsx', mode='a') as writer: statsnooffice.to_excel(writer, sheet_name=noofficesheet)
