import streamlit as st
import altair as alt
import requests
import pandas as pd
import plotly_express as px
import numpy as np
import lxml


def main():

# Set configs
    st.set_page_config(
	layout="centered",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
	page_title='LiguedDatas App',  # String or None. Strings get appended with "• Streamlit". 
	page_icon=None,  # String, anything supported by st.image, or None.
    )
    

# Load Data
    df = Please_wait_load_data()

# Set Sidebar
    st.sidebar.title('Navigation onglet')
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Defense", "Passes", "Dribbles", "Shots", "Exploration"])
    st.sidebar.title('Generals filters')
    sel_country = st.sidebar.multiselect('Select country', sorted(df['Nation'].unique()))
    sel_league = st.sidebar.multiselect('Select league', sorted(df['League'].unique()))
    sel_team = st.sidebar.multiselect('Select team', sorted(df['Squad'].unique()))
    sel_player = st.sidebar.multiselect('Select player', sorted(df['Player']))
    slider_games = st.sidebar.slider('Played Minutes', float(df['Minutes played divided by 90'].min()), float(df['Minutes played divided by 90'].max()), (float(df['Minutes played divided by 90'].min()), float(df['Minutes played divided by 90'].max())))
    st.sidebar.title('Graphics options')
    st.sidebar.write('\n')
    check_label = st.sidebar.checkbox('With labels')
    by_color = st.sidebar.selectbox('Color by', ['None', 'Nation', 'League', 'Squad'])

# Configure generals filters
    df_country = multi_filter(df, sel_country, 'Nation')    
    df_league = multi_filter(df, sel_league, 'League')
    df_team = multi_filter(df, sel_team, 'Squad')
    df_player = multi_filter(df, sel_player, 'Player')

    df_games = df[df['Minutes played divided by 90'].between(slider_games[0],slider_games[1])]

    general_select = df[df.isin(df_country) & df.isin(df_league) & df.isin(df_team) & df.isin(df_player) & df.isin(df_games)].dropna()


    
# Page 1
    if page == "Homepage":
        st.title('Interractive dashboard for Football ⚽')
        st.write("\n")
        st.write('You can navigate on page with the sidebar on the left')


# Page 2
    elif page == "Defense":
        st.title("Defense")
        st.write("\n")
        st.header("Tackle")
        slide_scatter(general_select, 'Tackles/90', 'Tackles Won/90', check_label, by_color)
        st.write("\n")
        st.header("Pressing")
        slide_scatter(general_select, 'Successful Pressures %', 'Pressures/90', check_label, by_color)
        st.write("\n")
        st.header("Aerial Duels")
        slide_scatter(general_select, 'Aerials won %', 'Aerials won/90', check_label, by_color)


# Page 3
    elif page == "Passes":
        st.title("Passes")
        st.write("\n")
        st.header("Passes Completion")
        slide_scatter(general_select, 'Pass Completion %', 'Passes Completed/90', check_label, by_color)
        st.write("\n")
        st.header("Forwards Passes")
        slide_scatter(general_select, 'Progressive Passes/90', 'Passes into Final Third/90', check_label, by_color)
        st.write("\n")
        st.header("Offensives Passes")
        slide_scatter(general_select, 'Assists/90', 'Key Passes/90', check_label, by_color)
	

# Page 4
    elif page == "Dribbles":
        st.title("Dribbles")
        st.write("\n")
        st.header("Dribbles Completion")
        slide_scatter(general_select, 'Dribble Completion %', 'Dribbles Completed/90', check_label, by_color)
        st.write("\n")
        st.header("Forward touches")
        slide_scatter(general_select, 'Forward dribbling %', 'Progressive Distance with Ball (yd)/90', check_label, by_color)
        st.write("\n")
        st.header("Keys Dribbles")
        slide_scatter(general_select, 'Dribbles lead to GCA/90', 'Dribbles lead to SCA/90', check_label, by_color)


# Page 5
    elif page == "Shots":
        st.title("hots")
        st.write("\n")
        st.header("Precision shots")
        slide_scatter(general_select, 'Shots on Target %', 'Shots on Target/90', check_label, by_color)
        st.write("\n")
        st.header("Forward touches")
        slide_scatter(general_select, 'Goals/90', 'Goals/Shot', check_label, by_color)


# Page 6    
    elif page == "Exploration":
        st.title("Data Exploration")
        x_axis = st.selectbox("Choose a variable for the x-axis", df.columns, index=11)
        y_axis = st.selectbox("Choose a variable for the y-axis", df.columns, index=12)
        slide_scatter(general_select, x_axis, y_axis, check_label, by_color)
	
	
# Bottom page
    st.write("\n") 
    st.write("\n")
    st.info("""By : Ligue des Datas [Instagram](https://www.instagram.com/ligueddatas/) / [Twitter](https://twitter.com/ligueddatas) | Data source : [Sport Reference Data](https://www.sports-reference.com/)""")


def load_data(url, information):
    html = requests.get(url).content
    df_list = pd.read_html(html)
    df = df_list[0]
    col_names = []
    for i in range(len(df.columns)):
        col_names.append((df.columns[i][1]))
    df.columns = col_names
    df = df[df['Rk'] != 'Rk'] # Remove headlines
    df = df.set_index('Rk') # Define id
    df = df.drop(labels=['Born','Matches'], axis=1) # Remove last column
    info = df.iloc[:,:7] # Keep information players 
    info.Player = info.Player.str.encode("latin1").str.decode("utf-8",errors='replace') # Encode Player
    info.Squad = info.Squad.str.encode("latin1").str.decode("utf-8",errors='replace') # Encode Squad
    info.Age = info.Age.str.replace('-','.').astype(float) # Clean Age
    info['90s'] = info['90s'].astype(float)
    values = df.iloc[:,7:].astype(float) # Select values as float
    values = values.fillna(0) # Replace NaN to 0
    if information == True:
        return info
    else: 
        return values

@st.cache
def Please_wait_load_data():
    info = load_data('https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2FBig5%2Fshooting%2Fplayers%2FBig-5-European-Leagues-Stats&div=div_stats_shooting', information = True)
    shot = load_data('https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2FBig5%2Fshooting%2Fplayers%2FBig-5-European-Leagues-Stats&div=div_stats_shooting', information = False).iloc[:,:8].drop(labels=['Sh/90', 'SoT/90'], axis=1)
    passes = load_data('https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2FBig5%2Fpassing%2Fplayers%2FBig-5-European-Leagues-Stats&div=div_stats_passing', information = False).drop(labels=['xA', 'A-xA'], axis=1)
    creation = load_data('https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2FBig5%2Fgca%2Fplayers%2FBig-5-European-Leagues-Stats&div=div_stats_gca', information = False).drop(labels=['SCA90','Sh', 'Fld', 'Def','GCA90','OG'], axis=1)
    dribble = load_data('https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2FBig5%2Fpossession%2Fplayers%2FBig-5-European-Leagues-Stats&div=div_stats_possession', information = False).loc[:,['Touches', 'Succ', 'Att', 'Succ%', 'TotDist', 'PrgDist']]
    defense = load_data('https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2FBig5%2Fdefense%2Fplayers%2FBig-5-European-Leagues-Stats&div=div_stats_defense', information = False).loc[:,['Tkl', 'TklW', 'Press', 'Succ', '%', 'Int']]
    fun = load_data('https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2FBig5%2Fmisc%2Fplayers%2FBig-5-European-Leagues-Stats&div=div_stats_misc', information = False).loc[:,['CrdY', 'CrdR', 'Fls', 'Fld', 'Crs', 'Won', 'Lost', 'Won%']]
    df = pd.concat([info, shot, passes, creation, dribble, defense, fun], axis=1)
    df.columns = ['Player', 'Nation', 'Pos', 'Squad', 'League', 'Age', 'Minutes played divided by 90',
              'Goals', 'Shots', 'Shots on Target', 'Shots on Target %', 'Goals/Shot', 'Goals/Shot on Target',
              'Passes Completed', 'Passes Attempted', 'Pass Completion %', 'Passes Total Distance (yd)', 'Passes Progressive Distance (yd)', 'sCmp', 'sAtt', 'sCmp%', 'sCmp', 'sAtt', 'sCmp%', 'sCmp', 'sAtt', 'sCmp%', 'Assists', 'Key Passes', 'Passes into Final Third', 'Passes into Penalty Area', 'Crosses into Penalty Area', 'Progressive Passes',
              'Shot-Creating Actions', 'Passes Live lead to SCA', 'Passes Dead lead to SCA', 'Dribbles lead to SCA', 'Goal-Creating Actions', 'Passes Live lead to GCA', 'Passes Dead lead to GCA', 'Dribbles lead to GCA',
              'Touches', 'Dribbles Completed', 'Dribbles Attempted', 'Dribble Completion %', 'Distance with Ball (yd)', 'Progressive Distance with Ball (yd)',
              'Tackles', 'sTkl', 'Tackles Won', 'Pressures', 'Successful Pressures', 'Successful Pressures %', 'Interceptions', 
              'Yellow Cards', 'Red Cards', 'Fouls Committed', 'Fouls Drawn', 'Crosses', 'Aerials won', 'Aerials lost', 'Aerials won %']
    df = df.drop(labels=['sCmp', 'sAtt', 'sCmp%', 'sTkl'], axis=1)
    df["Forward dribbling %"] = (df['Progressive Distance with Ball (yd)']/df['Distance with Ball (yd)'])*100
    exclude = ['Shots on Target %', 'Goals/Shot', 'Goals/Shot on Target', 'Pass Completion %', 'Dribble Completion %', 'Forward dribbling %', 'Successful Pressures %', 'Aerials won %']
    per90 = df.iloc[:,7:].loc[:, ~df.iloc[:,7:].columns.isin(exclude)].div(df['Minutes played divided by 90'], axis=0)
    per90 = per90.replace([np.inf], np.nan).fillna(0)
    per90names = []
    for i in range(len(list(per90.columns))):
        per90names.append(list(per90.columns)[i] + "/90")
    per90.columns = per90names
    final = pd.concat([df,per90], axis = 1)

    final["None"] = ""
    return final

def multi_filter(df, sel, var):
    if len(sel) == 0:
        df_sel = df
    elif len(sel) != 0:
        df_sel = df[df[var].isin(sel)]
    return df_sel


def scatter_plot(df, x_axis, y_axis, label, color):
    graph = px.scatter(df, x = x_axis, y = y_axis,
    text = label, 
    hover_name="Player",
    hover_data=['Squad','Minutes played divided by 90'],
    color = color,
    template = "simple_white",
    )
    graph.update_traces(textposition='top center')
    st.write(graph)

def slide_scatter(df, x_axis, y_axis, check, color_choice):
    if len(df) == 1:
        slider_x_explore = st.slider(x_axis, float(df[x_axis].min()), float(df[x_axis].max()+1), (float(df[x_axis].min()), float(df[x_axis].max())))
        slider_y_explore = st.slider(y_axis, float(df[y_axis].min()), float(df[y_axis].max()+1), (float(df[y_axis].min()), float(df[y_axis].max())))
    elif len(df) == 0:
        st.write('\n')
        st.error('Error yours filters are incompatibles')
    else:
        slider_x_explore = st.slider(x_axis, float(df[x_axis].min()), float(df[x_axis].max()), (float(df[x_axis].min()), float(df[x_axis].max())))
        slider_y_explore = st.slider(y_axis, float(df[y_axis].min()), float(df[y_axis].max()), (float(df[y_axis].min()), float(df[y_axis].max())))

    if len(df) != 0:
        explore_df = df[df[x_axis].between(slider_x_explore[0],slider_x_explore[1]) & df[y_axis].between(slider_y_explore[0],slider_y_explore[1])]
        if check == False:
            scatter_plot(explore_df, x_axis, y_axis, label = 'None', color = color_choice)
        else:
            scatter_plot(explore_df, x_axis, y_axis, label = 'Player', color = color_choice)
        
        with st.beta_expander("See data"):
            st.write(explore_df[['Player', x_axis, y_axis]])

if __name__ == "__main__":
    main()
