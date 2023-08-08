import snowflake.connector
import streamlit as st
from streamlit_echarts import st_echarts
import altair as alt
import pandas as pd
import numpy as np
import plotly.express as px

rank_tier_names = ["Low Ranks", "Medium Ranks", "High Ranks"]
rank_tiers = ["3 AND 11", "12 AND 20", "21 AND 27"]


conn = snowflake.connector.connect(
    user='******',
    password='*******',
    account='*******',
    warehouse='COMPUTE_WH',
    database='VALORANT_DATABASE',
    schema='VALORANT_SCHEMA'
)


def map_atk_win_prcnt():
    cursor = conn.cursor()
    raw_map_data = []
    for rank_tier_num in range(0, len(rank_tiers)):
        query = "SELECT MAP_NAME as \"map_name\",AVG(ATK_RND_WIN_PRCNT) as \"avg_win_percent\" FROM MAP_STATS " \
        f"WHERE NUM_RANK BETWEEN {rank_tiers[rank_tier_num]} AND LIST_DATE = CURRENT_DATE() GROUP BY MAP_NAME ORDER BY MAP_NAME;"
        cursor.execute(query)
        raw_map_data.append(cursor.fetchall()) 


    map_names = []
    low_rank_win_prcnt = []
    med_rank_win_prcnt = []
    high_rank_win_prcnt = []
    for row in raw_map_data[0][:]:
        map_names.append(row[0])
        low_rank_win_prcnt.append(row[1])
    for row in raw_map_data[1][:]:
        med_rank_win_prcnt.append(row[1])
    for row in raw_map_data[2][:]:
        high_rank_win_prcnt.append(row[1])
    formatted_map_data = {
        'Maps': map_names,
        'Low Ranks': low_rank_win_prcnt,
        'Medium Ranks': med_rank_win_prcnt,
        'High Ranks': high_rank_win_prcnt
    }

    df = pd.DataFrame(formatted_map_data)

    # Convert the DataFrame from wide to long format
    df_melt = df.melt(id_vars='Maps', var_name='Ranks', value_name='Atk Win Percentage')

    # Create the grouped bar chart
    fig = px.bar(df_melt, x='Maps', y='Atk Win Percentage', color='Ranks', barmode='group')

    
    fig.update_layout(
        yaxis_range=[45, 55],
        title = "Attack Round Win Percentage by Map & Rank"
    )

    st.plotly_chart(fig)
    st.caption("This is a grouped bar graph showing the round win rate of attackers on each map, for each tier of rank.")

    # formatted_map_data = {'Category': ['Low Ranks', 'Medium Ranks', 'High Ranks']}
    # formatted_map_data = {}
    # for map_num in range(0, len(raw_map_data[0])):
    #     specific_map_data = []
    #     for num_tiers in range(0, len(rank_tiers)):
    #         specific_map_data.append(raw_map_data[num_tiers][map_num][1]) 
    #     formatted_map_data.update({raw_map_data[0][map_num][0]: specific_map_data}) 


    cursor.close()


def win_pick_scatter():
    cursor = conn.cursor()
    agent_names = []
    agent_type = []
    avg_win_prcnt = []
    avg_pick_prcnt = []
    rank = []
    for rank_tier_num in range(0, len(rank_tiers)):
        query = "SELECT "\
                    "AST.AGENT_NAME "\
                    ",AT.AGENT_TYPE "\
                    ",AVG(AST.WIN_PRCNT) "\
                    ",AVG(AST.PICK_PRCNT) "\
                "FROM "\
                    "AGENT_STATS as AST "\
                    ",AGENT_TYPE as AT "\
                "WHERE "\
                    "AST.AGENT_NAME = AT.AGENT_NAME "\
                    f"AND AST.NUM_RANK BETWEEN {rank_tiers[rank_tier_num]} "\
                    "AND AST.LIST_DATE = CURRENT_DATE() "\
                "GROUP BY "\
                    "AST.AGENT_NAME "\
                    ",AT.AGENT_TYPE "\
                "ORDER BY "\
                    "AST.AGENT_NAME"\
                ";"
        
        cursor.execute(query)
        for row in cursor.fetchall():
            agent_names.append(row[0])
            agent_type.append(row[1])
            avg_win_prcnt.append(row[2])
            avg_pick_prcnt.append(row[3])   
            rank.append(rank_tier_names[rank_tier_num]) 

    formatted_agent_data = {
        'Agent Name': agent_names,
        'Agent Type': agent_type,
        'Avg Win Percentage': avg_win_prcnt,
        'Avg Pick Percentage': avg_pick_prcnt,
        'Rank': rank
    }

    df = pd.DataFrame(formatted_agent_data)

    fig = px.scatter(df, x='Avg Win Percentage', y='Avg Pick Percentage', color = 'Rank', symbol='Agent Type', hover_data=['Agent Name'])

    fig.update_layout(
        title = "Agent Win Percentage v Pick Percentage by Rank & Type"
    )

    st.plotly_chart(fig)
    st.caption("Add caption here.")

    cursor.close()


def num_matches_histogram():
    cursor = conn.cursor()

    query = "SELECT "\
        "SUM(CASE WHEN NUM_RANK BETWEEN 3 AND 5 THEN NUM_MATCHES END) as \"Iron\""\
        ",SUM(CASE WHEN NUM_RANK BETWEEN 6 AND 8 THEN NUM_MATCHES END) as \"Bronze\""\
        ",SUM(CASE WHEN NUM_RANK BETWEEN 9 AND 11 THEN NUM_MATCHES END) as \"Silver\""\
        ",SUM(CASE WHEN NUM_RANK BETWEEN 12 AND 14 THEN NUM_MATCHES END) as \"Gold\""\
        ",SUM(CASE WHEN NUM_RANK BETWEEN 15 AND 17 THEN NUM_MATCHES END) as \"Platinum\""\
        ",SUM(CASE WHEN NUM_RANK BETWEEN 18 AND 20 THEN NUM_MATCHES END) as \"Diamond\""\
        ",SUM(CASE WHEN NUM_RANK BETWEEN 21 AND 23 THEN NUM_MATCHES END) as \"Ascendant\""\
        ",SUM(CASE WHEN NUM_RANK BETWEEN 24 AND 26 THEN NUM_MATCHES END) as \"Immortal\""\
        ",SUM(CASE WHEN NUM_RANK = 27 THEN NUM_MATCHES END) as \"Radiant\""\
        " FROM MAP_STATS WHERE LIST_DATE = CURRENT_DATE();"
    
    cursor.execute(query)

    bar_data = {
        'Rank': ['Iron', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Ascendant', 'Immortal', 'Radiant'],
        'Number of Matches': cursor.fetchall()[0]
    }

    df = pd.DataFrame(bar_data)

    fig = px.histogram(df, x='Rank', y='Number of Matches')

    fig.update_layout(
        title = "Number of Matches by Rank",
        yaxis_title = "Number of Matches"
    )

    st.plotly_chart(fig)
    st.caption("Add caption here.")
        
    
    cursor.close()

def headshot_line():
    cursor = conn.cursor()
    ranks = []
    hdsht_prcnt = []
    tier_rank = []
    query = "SELECT "\
                "R.RANK_NAME as rank_name "\
                ",AVG(HEADSHOT_PRCNT) as avg_hs_prcnt "\
            "FROM "\
                "GUN_STATS as GS, RANKS as R "\
            "WHERE "\
                "GS.NUM_RANK = R.NUM_RANK "\
                "AND GS.GUN_NAME in ('Vandal', 'Phantom') "\
                "AND GS.LIST_DATE = CURRENT_DATE() "\
            "GROUP BY "\
                "R.RANK_NAME "\
                ",R.NUM_RANK "\
            "ORDER BY "\
                "R.NUM_RANK"\
            ";"

    cursor.execute(query)

    for row in cursor.fetchall():
        ranks.append(row[0])
        hdsht_prcnt.append(row[1])

    for num_rank in range(3, 28):
        if num_rank <= 11:
            tier_rank.append(rank_tier_names[0])
        elif num_rank <= 20:
            tier_rank.append(rank_tier_names[1])
        else:
            tier_rank.append(rank_tier_names[2])

    line_data = {
        'Rank': ranks,
        'Headshot Percentage': hdsht_prcnt,
        'Rank Tier': tier_rank
    }

    df = pd.DataFrame(line_data)

    fig = px.line(df, x='Rank', y='Headshot Percentage', color='Rank Tier', markers=True)

    fig.update_layout(
        title = "Average Headshot Percentage with Vandal & Phantom by Rank"
    )


    st.plotly_chart(fig)
    st.caption("Add caption here.")

    cursor.close()


def map_win_prcnt_scatter():
    cursor = conn.cursor()

    agent_names = []
    agent_types = []
    map_names = []
    avg_win_prcnt = []
    tier_rank = []
    for rank_tier_num in range(0, len(rank_tiers)):
        query = "SELECT "\
                    "AST.AGENT_NAME "\
                    ",AT.AGENT_TYPE "\
                    ",AST.MAP_NAME "\
                    ",AVG(AST.WIN_PRCNT) "\
                "FROM "\
                    "AGENT_STATS AS AST "\
                    ",AGENT_TYPE AS AT "\
                "WHERE "\
                    "AST.AGENT_NAME = AT.AGENT_NAME "\
                    f"AND AST.NUM_RANK BETWEEN {rank_tiers[rank_tier_num]} "\
                    "AND AST.LIST_DATE = CURRENT_DATE() "\
                "GROUP BY "\
                    "AST.MAP_NAME "\
                    ",AST.AGENT_NAME "\
                    ",AT.AGENT_TYPE "\
                "ORDER BY "\
                    "AST.MAP_NAME "\
                    ",AST.AGENT_NAME"\
                ";"
        
        cursor.execute(query)

        for row in cursor.fetchall():
            agent_names.append(row[0])
            agent_types.append(row[1])
            map_names.append(row[2])
            avg_win_prcnt.append(row[3])
            tier_rank.append(rank_tier_names[rank_tier_num])

    scatter_data = {
        'Agent Name': agent_names,
        'Agent Type': agent_types,
        'Map': map_names,
        'Average Win Percentage': avg_win_prcnt,
        'Rank Tier': tier_rank
    }

    df = pd.DataFrame(scatter_data)
    

    fig = px.scatter(df, y='Average Win Percentage', x='Map', color='Rank Tier', symbol='Agent Type', hover_data=['Agent Name'])
    fig.update_layout(
        scattermode="group",
        yaxis_range=[38, 60]
        )


    st.plotly_chart(fig)
    st.caption("Add caption here.")


    cursor.close()



# Call the function to render the chart in Streamlit app

map_atk_win_prcnt()
win_pick_scatter()
num_matches_histogram()
headshot_line()
map_win_prcnt_scatter()



# # CODE USED TO READ IN CSV FILE OF HOUSE LISTINGS
# file_path = '/Users/timothylee/Documents/PythonProjects/valorant_map_stats.txt'
# file_name = "valorant_map_stats.txt"
# stage_name = 'TEMP_STAGE'
# table_name = 'MAP_STATS'

# # Create a Snowflake cursor
# cursor = conn.cursor()

# # Create a temporary stage for file upload
# cursor.execute(f"CREATE TEMPORARY STAGE {stage_name}")

# # Upload the CSV file to the stage
# cursor.execute(f"PUT 'file://{file_path}' @{stage_name}")

# # Load data from the staged CSV file into the table
# cursor.execute(f"COPY INTO {table_name} FROM @{stage_name}/{file_name} FILE_FORMAT=(TYPE=CSV)")

# # Close the cursor
# cursor.close()

# Close the connection
conn.close()