import pandas as pd
import numpy as np

swinggeneral18 = {'Colorado' : 'openelections/openelections-data-co/2018/20181106__co__general__precinct.csv',
                'Iowa': "openelections/openelections-data-ia/2018/20181106__ia__general__precinct.csv",
                'Michigan' : "openelections/openelections-data-mi/2018/20181106__mi__general__precinct.csv",
                'Minnesota' : "openelections/openelections-data-mn/2018/20181106__mn__general__precinct.csv",
                'New Hampshire' : "openelections/openelections-data-nh/2018/20181106__nh__general__precinct.csv",
                'Nevada' : "openelections/openelections-data-nv/2018/20181106__nv__general__precinct.csv",
                'Ohio' : "openelections/openelections-data-oh/2018/20181106__oh__general__precinct.csv",
                'Pennsylvania' : "openelections/openelections-data-pa/2018/20181106__pa__general__county.csv",
                'Wisconsin' : "openelections/openelections-data-wi/2018/20181106__wi__general__ward.csv",
                'Florida' : "openelections/openelections-results-fl/raw/20161108__fl__general__county__raw.csv", #"openelections/openelections-results-fl/raw/20181106__fl__general__precinct__raw.csv",
                'North Carolina' : "openelections/openelections-results-nc/raw/20161108__nc__general__county__raw.csv", #"openelections/openelections-results-nc/raw/20181106__nc__general__precinct__raw.csv",
                'Virginia' : 'openelections/openelections-results-va/raw/20181106__va__general__precinct__raw.csv' }

states = ["Florida", "North Carolina", "Virginia"]

for state in states:
    df = pd.read_csv('../'+swinggeneral18[state])
    print(state)
    print(df.columns)

    #party
    #votes
    #office
