# -*- coding: utf-8 -*-
"""finalproject.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ffo_xi7B03KIxfaEhYABDeaTocfo3VKy
"""
import pandas as pd
import numpy as np
import sqlite3
from sqlite3 import connect
import streamlit as st
from PIL import Image

image = Image.open('Logo-KDT-JU.webp')
st.image(image)

conn= connect('ecsel_database.db')

# Read data from the different tables
df_project = pd.read_sql('SELECT * FROM PROJECTS', conn)
df_participants = pd.read_sql('SELECT * FROM PARTICIPANTS', conn)
df_countries = pd.read_sql('SELECT * FROM COUNTRIES', conn)

# Merge data from different tables into df2
df2 = pd.read_sql('''
    SELECT p.*, pj.*, c.Country 
    FROM PARTICIPANTS AS p, PROJECTS AS pj, COUNTRIES AS c
    WHERE p.projectID=pj.projectID AND p.country=c.Acronym
''', conn)
df2 = df2.rename(columns={'country': 'Acronym'})
df2 = df2.rename(columns={'acronym': 'organization_acronym'})

st.title('Partner Search App')

country_list = df2['Country'].unique()  # Selecting the unique country names list
country_acronyms = {'Belgium': 'BE', 'Bulgaria': 'BG', 'Czechia': 'CZ', 'Denmark': 'DK', 'Germany':
                    'DE', 'Estonia': 'EE', 'Ireland': 'IE', 'Greece': 'EL', 'Spain': 'ES', 'France': 'FR',
                    'Croatia': 'HR', 'Italy': 'IT', 'Cyprus': 'CY', 'Latvia': 'LV', 'Lithuania': 'LT',
                    'Luxembourg': 'LU', 'Hungary': 'HU', 'Malta': 'MT', 'Netherlands': 'NL', 'Austria': 'AT',
                    'Poland': 'PL', 'Portugal': 'PT', 'Romania': 'RO', 'Slovenia': 'SI', 'Slovakia': 'SK',
                    'Finland': 'FI', 'Sweden': 'SE'}
#selecting different countries using a multiselect box from the keys of the dictionary
countnames = st.multiselect('Choose Countries', sorted(country_acronyms.keys()))  

def countries_to_acronyms(countnames):  #we created a function which appends the country names selected into a list in order to have those acronyms saved for the dataframes displayed.
    acronyms = []
    for countname in countnames:
        if countname in country_acronyms.keys(): #find the Country name selected
            acronyms.append(country_acronyms[countname]) #append to the acronyms list the respective accronym
    return acronyms

acronym_c = countries_to_acronyms(countnames) #assigning the list of acronyms a variable


st.write('The selected countries are:', ', '.join(acronym_c))  # Display selected countries as well as their acronyms string 

#Generate a dataframe of partner contributions
st.text('Table of Partner Contributions per Country Selected')
def display_dataframe(df2, acronyms): #creating a function for a dataframe of partner contributions per country
    df2 = df2[df2['Acronym'].isin(acronyms)] #filtering by the countries selected
    df2_part = df2.groupby(['name','shortName', 'activityType', 'organizationURL']).agg({'ecContribution':['sum']}) #grouping a dataframe by different attributes and aggregating by the sum of Ec Contribution
    df2_part = df2_part.reset_index() 
    df2_part = df2_part.sort_values(by=('ecContribution', 'sum'), ascending=False)  # Sorting by sum of ecContribution in descending order
    return df2_part

participants = display_dataframe(df2, acronym_c) #calling the dataframe from the function a variable 'participants'
st.write(participants, index=False) #displaying the dataframe

# Generate a new project dataframe with project coordinators from the selected countries and order it in ascending order by 'shortName'
st.text('Table of Project Coordinators per Country Selected')
df2 = df2[df2['Acronym'].isin(acronym_c)] #filtering by chosen countries
df2['Coordinator'] = (df2['role'] == 'coordinator') * 1 #selecting those which have a coordinator role and transforming it into integer
pjc_df = df2.groupby(['name','shortName', 'activityType', 'organizationURL']).agg({'Coordinator': ['sum']}) #display by aggregation of coordinator
pjc_df = pjc_df[pjc_df[('Coordinator', 'sum')] > 0].reset_index() #only visualize those which have been coordinators at least onc
pjc_df = pjc_df.sort_values('shortName')  #ordering by shortName

st.write(pjc_df, index=False) #displaying the dataframe 

#Creating CSV files for both data frames created
st.text('Download the Data Below')
#Button 1: Dataframe 1 - Participants and Total EcContribution per countries selected
@st.cache  # IMPORTANT: Cache the conversion to prevent computation on every rerun
def convert_participants(participants):
    return participants.to_csv().encode('utf-8')
st.download_button(label="Participants CSV", data=convert_participants(participants), file_name='participants.csv', mime='text/csv')

#Button 2: Dataframe 2 - Coordinators per countries selected. 
@st.cache  # IMPORTANT: Cache the conversion to prevent computation on every rerun
def convert_projectcoordinators(pjc_df):
    return pjc_df.to_csv().encode('utf-8')
st.download_button(label="Project Coordinators CSV", data=convert_projectcoordinators(pjc_df), file_name='projectcoordinators.csv', mime='text/csv')

#Optional - Interactivity
for country in countnames: #creating a loop to show graphs per country selected
    st.subheader(f"Total Contributions Evolution for {country}")
    selected_country_data = df2[df2['Country'] == country] #filtering per country in the select box 
    selected_country_data['year'] = selected_country_data['year'].astype(int) #so that the year is displayed as 2023 not 2,023
    selected_country_data['year'] = selected_country_data['year'].astype(str)

    # Group by year and activity type to get total contributions
    contributions_by_year_activity = selected_country_data.groupby(['year', 'activityType'])['ecContribution'].sum().unstack()

    # Plotting
    st.bar_chart(contributions_by_year_activity)

    #Selecting by activity type
    option = st.selectbox('Choose to see the specific activity', selected_country_data['activityType'].unique())

    #plotting the options of each country per activity type 
    st.bar_chart(contributions_by_year_activity[option])
    



conn.close()
