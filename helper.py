import numpy as np
import pandas as pd


def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    elif year == 'Overall':
        temp_df = medal_df[medal_df['region'] == country]
    elif country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    else:
        temp_df = medal_df[(medal_df['Year'] == int(year)) & (medal_df['region'] == country)]

    medal_count = temp_df.groupby(['Team', 'NOC', 'region']).sum()[['Gold', 'Silver', 'Bronze']].reset_index()
    medal_count['Total'] = medal_count['Gold'] + medal_count['Silver'] + medal_count['Bronze']
    medal_count = medal_count.sort_values(by='Total', ascending=False)

    return medal_count



def most_successful_countrywise(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == country]

    # Count medals for each athlete and select the top athletes
    top_athletes = (temp_df.groupby('Name')
                    .size()
                    .reset_index(name='Medals')
                    .sort_values(by='Medals', ascending=False)
                    .head(10))

    # Merge with original data to add sport and region information
    merged_data = (top_athletes
                   .merge(df[['Name', 'Sport', 'region']].drop_duplicates(), on='Name', how='left'))

    return merged_data



def country_event_heatmap(df, country):
    df = df.dropna(subset=['Medal']).drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    df = df[df['region'] == country]
    return df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)


def country_year_list(df):
    years = sorted(df['Year'].unique().tolist())
    countries = sorted(df['region'].dropna().unique().tolist())
    return ['Overall'] + years, ['Overall'] + countries


def data_over_time(df, col):
    return df.drop_duplicates(['Year', col]).groupby('Year').size().reset_index(name=col).rename(
        columns={'Year': 'Edition'})


def most_successful(df, sport='Overall', limit=15):
    if sport != 'Overall':
        df = df[df['Sport'] == sport]
    return df.dropna(subset=['Medal']).groupby('Name').size().reset_index(name='Medals').sort_values(by='Medals',
                                                                                                     ascending=False).head(
        limit).merge(df[['Name', 'Sport', 'region']].drop_duplicates(), on='Name').drop_duplicates(subset='Name')


def yearwise_medal_tally(df, country):
    df = df.dropna(subset=['Medal']).drop_duplicates(
        subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    return df[df['region'] == country].groupby('Year').count()['Medal'].reset_index()


def weight_v_height(df, sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    athlete_df['Medal'].fillna('No Medal', inplace=True)
    return athlete_df[athlete_df['Sport'] == sport] if sport != 'Overall' else athlete_df


def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()
    return men.merge(women, on='Year', how='left').rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}).fillna(0)
