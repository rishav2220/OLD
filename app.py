import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import helper
import preprocessor

st.set_page_config(page_title='Olympics Analysis', page_icon='🏅', layout='wide')

# 3D Metric Cards
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f0f0;
        border-radius: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        padding: 10px;
        text-align: center;
        font-size: 1.2em;
    }
    .metric-label {
        color: #333;
        font-weight: bold;
    }
    .metric-value {
        color: #007bff;
        font-weight: bold;
        font-size: 1.5em;
    }
    .stApp {
        background: url("https://wallpaperaccess.com/full/1232656.jpg");
        background-size: cover;
    }
    </style>
    """, unsafe_allow_html=True)

# Preprocess data
df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')
df = preprocessor.preprocess(df, region_df)

st.sidebar.title("Olympics Analysis")
st.sidebar.image(
    'https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png')
user_menu = st.sidebar.radio('Select an Option',
                             ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete wise Analysis'))

if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")
    years, countries = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", countries)
    title = f"{selected_country} performance in {selected_year} Olympics" if selected_year != 'Overall' else f"{selected_country} overall performance" if selected_country != 'Overall' else "Overall Tally"

    st.title(title)

    # Dropdown to select display options
    display_options = st.selectbox("Select Display Option", ["Top 10", "Top 20", "Top 100", "Full List"])

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    # Limit data based on the selected display option
    if display_options == "Top 10":
        medal_tally = medal_tally.head(10)
    elif display_options == "Top 20":
        medal_tally = medal_tally.head(20)
    elif display_options == "Top 100":
        medal_tally = medal_tally.head(100)

    st.table(medal_tally)


elif user_menu == 'Overall Analysis':
    st.title("Overall Analysis")
    stats = {
        "Editions": df['Year'].nunique() - 1,
        "Hosts": df['City'].nunique(),
        "Sports": df['Sport'].nunique(),
        "Events": df['Event'].nunique(),
        "Athletes": df['Name'].nunique(),
        "Nations": df['region'].nunique()
    }
    col1, col2, col3 = st.columns(3)
    for i, (stat, value) in enumerate(stats.items()):
        col = col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3
        col.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{stat}</div>
                <div class="metric-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)

    nations_over_time = helper.data_over_time(df, 'region')
    fig = px.line(nations_over_time, x='Edition', y='region', title='Participating Nations over the years')
    st.plotly_chart(fig)

    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(events_over_time, x='Edition', y='Event', title='Events over the years')
    st.plotly_chart(fig)

    athlete_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athlete_over_time, x='Edition', y='Name', title='Athletes over the years')
    st.plotly_chart(fig)

    st.title("No. of Events over time (by Sport)")
    sport_events_heatmap = df.drop_duplicates(['Year', 'Sport', 'Event']).pivot_table(index='Sport', columns='Year',
                                                                                      values='Event',
                                                                                      aggfunc='count').fillna(0)
    fig = px.imshow(sport_events_heatmap, text_auto=True, aspect='auto')
    st.plotly_chart(fig)

    st.title("Most successful Athletes")
    sports_list = ['Overall'] + sorted(df['Sport'].unique().tolist())
    selected_sport = st.selectbox('Select a Sport', sports_list)
    successful_athletes = helper.most_successful(df, selected_sport)
    st.table(successful_athletes)

elif user_menu == 'Country-wise Analysis':
    st.sidebar.title('Country-wise Analysis')
    countries_list = sorted(df['region'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox('Select a Country', countries_list)
    st.title(f"{selected_country} Medal Tally over the years")
    country_medal_tally = helper.yearwise_medal_tally(df, selected_country)
    fig = px.line(country_medal_tally, x='Year', y='Medal', title=f"{selected_country} Medal Tally")
    st.plotly_chart(fig)

    st.title(f"{selected_country} excels in the following sports")
    country_heatmap = helper.country_event_heatmap(df, selected_country)
    fig = px.imshow(country_heatmap, text_auto=True, aspect='auto')
    st.plotly_chart(fig)

    st.title(f"Top 10 athletes of {selected_country}")
    top_athletes = helper.most_successful_countrywise(df, selected_country)
    st.table(top_athletes)

elif user_menu == 'Athlete wise Analysis':
    st.title("Athlete wise Analysis")
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    medal_ages = {"Overall Age": athlete_df['Age'].dropna(),
                  "Gold Medalist": athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna(),
                  "Silver Medalist": athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna(),
                  "Bronze Medalist": athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()}
    fig = go.Figure()

    for name, ages in medal_ages.items():
        fig.add_trace(go.Histogram(x=ages, name=name, hoverinfo="x+y"))
    fig.update_layout(barmode='overlay', title='Distribution of Age', xaxis_title='Age', yaxis_title='Frequency')
    fig.update_traces(opacity=0.75)
    st.plotly_chart(fig)

    sports_list = ['Overall'] + sorted(df['Sport'].unique().tolist())
    selected_sport = st.selectbox('Select a Sport', sports_list)
    height_weight_data = helper.weight_v_height(df, selected_sport)

    # 3D scatter plot with hoverinfo
    fig = px.scatter_3d(height_weight_data, x='Weight', y='Height', z='Age', color='Medal', symbol='Sex', size_max=18,
                        hover_name='Name', hover_data={'Sport': True, 'region': True})
    fig.update_layout(title='Height vs Weight vs Age',
                      scene=dict(xaxis_title='Weight', yaxis_title='Height', zaxis_title='Age'))
    st.plotly_chart(fig)

    st.title("Men vs Women Participation Over the Years")
    men_women_df = helper.men_vs_women(df)
    fig = px.line(men_women_df, x="Year", y=["Male", "Female"], title="Men vs Women Participation Over the Years")
    st.plotly_chart(fig)
