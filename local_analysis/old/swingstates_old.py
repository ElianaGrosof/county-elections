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
                'Pennsylvania' : "openelections/openelections-data-pa/2018/20181106__pa__general__precinct.csv",
                'Wisconsin' : "openelections/openelections-data-wi/2018/20181106__wi__general__ward.csv",
                'Florida' : "openelections/openelections-results-fl/raw/20181106__fl__general__precinct__raw.csv",
                'North Carolina' : "openelections/openelections-results-nc/raw/20181106__nc__general__precinct__raw.csv",
                'Virginia' : 'openelections/openelections-results-va/raw/20181106__va__general__precinct__raw.csv' }

statenames = ['Colorado', 'Iowa', 'Michigan', 'Minnesota', 'New Hampshire', 'Nevada', 'Ohio', 'Pennsylvania', 'Wisconsin', 'Florida', 'North Carolina', 'Virginia']
stateabbs = {'Colorado':'CO', "Iowa":'IA', "Michigan":'MI', "Minnesota":'MN', "New Hampshire": 'NH', "Nevada": 'NV', "Ohio":'OH', "Pennsylvania": 'PA', "Wisconsin":'WI', "Florida":'FL', "North Carolina":'NC', "Virginia":'VA'}

#removing states that will not actually be included in this analysis
statenames.remove('Nevada')
statenames.remove('Pennsylvania')
statenames.remove('Michigan') #temporary
del stateabbs['Nevada']
del stateabbs['Pennsylvania']

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
    aggregatedstats = pd.DataFrame(columns=["State","County", "Office", "FIPS","dem_total","rep_total","other_total","margin"])
    for county in counties:
        countydf = df[((df["county"] == county) & (df["party"].str.contains("DEM") | df["party"].str.contains("REP")))]
        offices = countydf["office"].unique()
        for office in offices:
            #dem_total, rep_total, other_total
            dem_total = countydf[(countydf["party"] == 'DEM') & (countydf['office'] == office)]["votes"].sum(skipna=True)
            rep_total = countydf[(countydf["party"] == 'REP') & (countydf['office'] == office)]["votes"].sum(skipna=True)
            other_total = countydf[(countydf["party"] == 'OTHER') & (countydf['office'] == office)]["votes"].sum(skipna=True)

            margin = dem_total - rep_total

            new_row = {"State":state,"County":county,"Office":office,"FIPS":fipsmap[state][county],"dem_total":dem_total,"rep_total":rep_total,
                       "other_total":other_total,"margin":margin}

            aggregatedstats = aggregatedstats.append(new_row, ignore_index=True)
    return aggregatedstats, offices

def makesummary(counties, offices, aggregatedstats):

    summarymetrics = pd.DataFrame(columns=["State","County", "FIPS", "dem_natl_wins", "rep_natl_wins","other_natl_wins","dem_state_wins","rep_state_wins","other_state_wins", "percent_dem_wins", "percent_rep_wins","percent_other_wins"])

    #make summary metrics
    for county in counties:
        dem_natl_wins = 0
        rep_natl_wins = 0
        other_natl_wins = 0

        dem_state_wins = 0
        rep_state_wins = 0
        other_state_wins = 0

        natlstrings = ['U.S.', 'US', 'United States']
        if state == 'Wisconsin':
            natlstrings = 1 #TO DO: something else, figure out how

        for office in offices:
            national = [True for x in natlstrings if x in office]
            print("National is", national, "for Office", office)

            df = aggregatedstats[((aggregatedstats["County"] == county) & (aggregatedstats["Office"] == office))]
            if df.empty: break
            rowdict = df.to_dict('records')
            row = rowdict[0]
            print(row)

            margin = row['margin']
            other_total = row['rep_total']
            dem_total = row['dem_total']
            rep_total = row['rep_total']

            if national == [True]:
                if (other_total > dem_total) & (other_total > rep_total):
                    other_natl_wins += 1
                else:
                    if margin > 0:
                        dem_natl_wins += 1
                    else:
                        rep_natl_wins += 1
            else:
                if (other_total > dem_total) & (other_total > rep_total):
                    other_state_wins += 1
                else:
                    if margin > 0:
                        dem_state_wins +=1
                    else:
                        rep_state_wins += 1
        print("dem_natl_wins",dem_natl_wins)
        print("rep_natl_wins", rep_natl_wins)
        print("other_natl_wins", other_natl_wins)
        #percent_wins
        totaloffices = len(offices)
        percent_dem_total_wins = (dem_natl_wins + dem_state_wins) / totaloffices
        percent_rep_total_wins = (rep_natl_wins + rep_state_wins) / totaloffices
        percent_other_total_wins = (other_natl_wins + other_state_wins) / totaloffices
        #national percent
        national_races = (dem_natl_wins + rep_natl_wins + other_natl_wins)
        if national_races == 0:
            national_races = -2  # make it so not dividing by 0, but all state_wins will equal 0 in this case
        percent_dem_natl_wins = dem_natl_wins / national_races
        percent_rep_natl_wins = rep_natl_wins / national_races
        percent_other_natl_wins = other_natl_wins / national_races
        #state percent
        state_races = (dem_state_wins + rep_state_wins + other_state_wins)
        if state_races == 0:
            state_races = -2 #make it so not dividing by 0, but all state_wins will equal 0 in this case
        percent_dem_state_wins = dem_state_wins / state_races
        percent_rep_state_wins = rep_state_wins / state_races
        percent_other_state_wins = other_state_wins / state_races


        new_row = {"State": state, "County": county, "Office": office, "FIPS": fipsmap[stateabb][county],
                       "dem_natl_wins":dem_natl_wins, "rep_natl_wins":rep_natl_wins, "other_natl_wins":other_natl_wins, "dem_state_wins":dem_state_wins,
                      "rep_state_wins":rep_state_wins, "other_state_wins":other_state_wins, "percent_dem_total_wins":percent_dem_total_wins, "percent_rep_total_wins":percent_rep_total_wins,
                      "percent_other_total_wins":percent_other_total_wins,"percent_dem_natl_wins":percent_dem_natl_wins, "percent_rep_natl_wins":percent_rep_natl_wins,
                      "percent_other_natl_wins":percent_other_natl_wins, "percent_dem_state_wins":percent_dem_state_wins, "percent_rep_state_wins":percent_rep_state_wins,
                      "percent_other_state_wins":percent_other_state_wins}

        summarymetrics = summarymetrics.append(new_row, ignore_index=True)
    return summarymetrics

makefipsmap()

for state in statenames:
    filename = swinggeneral18[state]
    df = pd.read_csv('../'+filename)

    cleandf = cleanparty(df)
    #This is a New Hampshire-specific dataset cleaning thing
    cleandf = cleandf[~(cleandf.county == state.lower())]

    uniquec = cleandf["county"].unique()

    df = cleandf

    stateabb = stateabbs[state]
    counties = df["county"].unique()

    # dfs to write to file - two dfs per state
    # aggregatedstats is for counts and preliminary metrics, one line per county per office
    # summarymetrics depends on aggregatedstats, one line per county
    #aggregatedstats = pd.DataFrame(columns=["State","County", "Office", "FIPS","dem_total","rep_total","other_total","margin"])
    #summarymetrics = pd.DataFrame(columns=["State","County", "FIPS", "dem_natl_wins", "rep_natl_wins","other_natl_wins","dem_state_wins","rep_state_wins","other_state_wins", "percent_dem_wins", "percent_rep_wins","percent_other_wins"])
    print(state)

    aggregatedstats, offices = makeaggregated(df, counties)
    #summarymetrics = makesummary(counties, offices, aggregatedstats)

    sheetnameagg = state+'aggstats'#state+'_aggregatedstats_20181106'
    #sheetnamesum = state+'_summarymetrics_20181106'

    with pd.ExcelWriter('../stats/other_stats.xlsx',mode='a') as writer: aggregatedstats.to_excel(writer, sheet_name=sheetnameagg)
    #with pd.ExcelWriter('../stats/stats.xlsx',mode='a') as writer: summarymetrics.to_excel(writer, sheet_name=sheetnamesum)
