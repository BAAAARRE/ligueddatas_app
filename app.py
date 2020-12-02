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
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Exploration", "Defense"])
    st.sidebar.title('Generals filters')
    sel_country = st.sidebar.multiselect('Select country', sorted(df['Nation'].unique()))
    sel_league = st.sidebar.multiselect('Select league', sorted(df['Comp'].unique()))
    sel_team = st.sidebar.multiselect('Select team', sorted(df['Squad'].unique()))
    sel_player = st.sidebar.multiselect('Select player', sorted(df['Player']))
    slider_games = st.sidebar.slider('Played Minutes', float(df['90s'].min()), float(df['90s'].max()), (float(df['90s'].min()), float(df['90s'].max())))
    check_label = st.sidebar.checkbox('With labels')

# Configure generals filters
    if len(sel_country) == 0:
        df_country = df
    elif len(sel_country) != 0:
        df_country = df[df['Nation'].isin(sel_country)]
    
    if len(sel_league) == 0:
        df_league = df
    elif len(sel_league) != 0:
        df_league = df[df['Comp'].isin(sel_league)]

    if len(sel_team) == 0:
        df_team = df
    elif len(sel_team) != 0:
        df_team = df[df['Squad'].isin(sel_team)]

    df_player = multi_filter(df, sel_player, 'Player')

    df_games = df[df['90s'].between(slider_games[0],slider_games[1])]

    general_select = df[df.isin(df_country) & df.isin(df_league) & df.isin(df_team) & df.isin(df_player) & df.isin(df_games)].dropna()


    
# Page 1
    if page == "Homepage":
        st.title('Interractive dashboard for Football ⚽')
        st.write("\n")
        st.write('You can navigate on page with the sidebar on the left')
        

# Page 2    
    elif page == "Exploration":
        st.title("Data Exploration")
        x_axis = st.selectbox("Choose a variable for the x-axis", df.columns, index=11)
        y_axis = st.selectbox("Choose a variable for the y-axis", df.columns, index=12)
        explore_df = slide_scatter(general_select, x_axis, y_axis, check_label)
        st.write(explore_df)


# Page 3
    elif page == "Defense":
        st.title("Defense")
        st.write("\n")
        st.header("Tackle")
        explore_df = slide_scatter(general_select, 'Tkl', 'TklW', check_label)
        st.write("\n")
        st.header("Pressing")
        explore_df = slide_scatter(general_select, 'Press_Succ%', 'Press', check_label)
        st.write("\n")
        st.header("Aerial Duels")
        explore_df = slide_scatter(general_select, 'Aerial_Won%', 'Aerial_Won', check_label)


# Bottom page
    st.write("\n") 
    st.write("\n")
    st.info("""By : [Ligue des Datas](https://www.instagram.com/ligueddatas/) | Source : [GitHub](https://github.com/BAAAARRE/ligueddatas_app) | Data source : [Sport Reference Data](https://www.sports-reference.com/)""")


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
    passes = load_data('https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2FBig5%2Fpassing%2Fplayers%2FBig-5-European-Leagues-Stats&div=div_stats_passing', information = False).drop(labels=['Ast', 'xA', 'A-xA'], axis=1)
    creation = load_data('https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2FBig5%2Fgca%2Fplayers%2FBig-5-European-Leagues-Stats&div=div_stats_gca', information = False).drop(labels=['SCA90','Sh', 'Fld', 'Def','GCA90','OG'], axis=1)
    defense = load_data('https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2FBig5%2Fdefense%2Fplayers%2FBig-5-European-Leagues-Stats&div=div_stats_defense', information = False).loc[:,['Tkl', 'TklW', 'Press', 'Succ', '%', 'Int']]
    dribble = load_data('https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2FBig5%2Fpossession%2Fplayers%2FBig-5-European-Leagues-Stats&div=div_stats_possession', information = False).loc[:,['Touches', 'Succ', 'Att', 'Succ%', 'Carries', 'TotDist', 'PrgDist']]
    fun = load_data('https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2FBig5%2Fmisc%2Fplayers%2FBig-5-European-Leagues-Stats&div=div_stats_misc', information = False).loc[:,['CrdY', 'CrdR', 'Fls', 'Fld', 'Crs', 'Won', 'Lost', 'Won%']]
    df = pd.concat([info, shot, passes, creation, dribble, defense, fun], axis=1)
    df.columns = ['Player', 'Nation', 'Pos', 'Squad', 'Comp', 'Age', '90s',
              'Gls', 'Sh', 'SoT', 'SoT%', 'G/Sh', 'G/SoT',
              'Pass_Cmp', 'Pass_Att', 'Pass_Cmp%', 'TotDist', 'PrgDist', 'sCmp', 'sAtt', 'sCmp%', 'sCmp', 'sAtt', 'sCmp%', 'sCmp', 'sAtt', 'sCmp%', 'KP', '1/3', 'PPA', 'CrsPA', 'Prog',
              'SCA', 'SCA_PassLive', 'SCA_PassDead', 'SCA_Drib', 'GCA', 'GCA_PassLive', 'GCA_PassDead', 'GCA_Drib',
              'Touches', 'Drib_Succ', 'Drib_Att', 'Drib_Succ%', 'Carries', 'Drib_TotDist', 'Drib_PrgDist',
              'Tkl', 'sTkl', 'TklW', 'Press', 'Press_Succ', 'Press_Succ%', 'Int', 
              'CrdY', 'CrdR', 'Fls', 'Fld', 'Crs', 'Aerial_Won', 'Aerial_Lost', 'Aerial_Won%']
    df = df.drop(labels=['sCmp', 'sAtt', 'sCmp%', 'sTkl'], axis=1)
    df["Labels"] = ""
    return df

def multi_filter(df, sel, var):
    if len(sel) == 0:
        df_sel = df
    elif len(sel) != 0:
        df_sel = df[df[var].isin(sel)]
    return df_sel


def scatter_plot(df, x_axis, y_axis, label):
    graph = px.scatter(df, x = x_axis, y = y_axis,
    text = label, 
    hover_name="Player",
    template = "simple_white",
    )
    graph.update_traces(textposition='top center')

    st.write(graph)

def slide_scatter(df, x_axis, y_axis, check):
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
            scatter_plot(explore_df, x_axis, y_axis, label = 'Labels')
        else:
            scatter_plot(explore_df, x_axis, y_axis, label = 'Player')
        
        with st.beta_expander("See data"):
            st.write(explore_df[['Player', x_axis, y_axis]])
        return explore_df



if __name__ == "__main__":
    main()
