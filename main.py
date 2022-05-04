# Importing required libraries

import streamlit as st
import matplotlib.pyplot as plt 
import random 
import numpy as np
import pandas as pd
from datetime import *
from collections import Counter



# -------------------------------------------------------------- #
#  Sidebar filters are written on upper section of code so we can 
#  access their variables in lower section and update the right panel.
# -------------------------------------------------------------- #


# Configuring the Streamlit UI
plt.rcParams['font.size'] = 5.0
st.set_page_config(layout="wide",page_title='UFO sightings', page_icon='🛸')
styles_sheet = open("style.css",'r',encoding="utf-8").read()
st.markdown(f"<style> {styles_sheet} </style>",unsafe_allow_html=True,)

# importing csv file
main_df=None
def readCSVFile():
    global main_df
    main_df = pd.read_csv("data.csv", error_bad_lines=False)
    # main_df = pd.read_csv("data.csv",low_memory=False)
readCSVFile()

# Sorting df by country
main_df = main_df.sort_values(by=['country'], ascending=True)

# Some functions to extract/manipulate data from csv file. linked with filters 
def generateDateTimeValue(x,month=False):
    index = -1 if not month else -3
    if '/' in str(x):
        return int(str(x).split(" ")[0].split("/")[index])
    else:
        if index==-3:
            return datetime.fromtimestamp(int(x)).month
        return datetime.fromtimestamp(int(x)).year
        
        
def convertToFloat(x):
    try:
        return float(x)
    except:
        return 0

def getStackedBarChartData(year_slide_range):
    df = main_df[(main_df.year >=year_slide_range[0] ) & (main_df.year <= year_slide_range[-1])]  

    map_df = pd.DataFrame(
        [     ],
        columns=['lat', 'lon']
    ) 
    map_df['lat'] = df['latitude'].values.tolist()
    map_df['lon'] = df['longitude'].values.tolist()
    map_df['country'] = df['country'].values.tolist()
    
    countries = [x for x in list(set(df['country'].values.tolist())) if str(x)!='nan']
    ufo_shapes = [x for x in list((df['shape'].values.tolist())) if str(x)!='nan']
    ufo_shapes = list(dict(Counter(ufo_shapes))) [:4]
    df =  df[df['shape'].str.contains("|".join(ufo_shapes), na=False)]
    
     
    data_container = []
    for shape in ufo_shapes:
        shape_container = [] 
        for country in countries: 
            record = df[(df['shape'].str.contains(shape)  ) & (df['country'].str.contains(country))].shape[0] 
            shape_container.append(record)
        data_container.append({shape:shape_container} )
    return {
        'countries': countries,
        'shape_container': data_container,
        'map_df': map_df,
    }



# Reshaping dataframe for required functionality -  making more reliable 
main_df['year'] = main_df.apply(lambda x: generateDateTimeValue(x['datetime']), axis=1)
main_df['month'] = main_df.apply(lambda x: generateDateTimeValue(x['datetime'],True), axis=1)
main_df = main_df[main_df['latitude'].notna()]
main_df = main_df[main_df['longitude'].notna()]
main_df['longitude'] = main_df.apply(lambda x: convertToFloat(x['longitude']), axis=1)
main_df['latitude'] = main_df.apply(lambda x: convertToFloat(x['latitude']), axis=1)


# Function to extract data for pie chart - linked with hemisphere(s) filter too
def getPieChartData(hemispheres):   
    df = main_df
    print("-"*50)
    print("hemispheres - ", hemispheres)
    print("- main shape = ", df.shape)
    if len(hemispheres)!=1:
        pass
    else:
         
        if hemispheres[0]=='Northern':
            df = df[(df.latitude <0 ) ]
            print("- child shape = ", df.shape)
        else:
            df = df[(df.latitude >0 ) ] 
            print("- child shape = ", df.shape)
     
    
    print("- final shape = ", df.shape)
    res= {
        "Spring": df[(df.month >2 ) & (df.month < 6)].shape[0],
        "Summer": df[(df.month >5 ) & (df.month < 9)].shape[0],
        "Fall": df[(df.month >8 ) & (df.month < 12)].shape[0],
        "Winter": df[(df.month >11 ) | (df.month < 3)].shape[0] ,
    }
    print(res)
    return res




# ---------------------------------------- Start: Sidebar -----------------------------------

# Hemisphere filter - Point 1 filter
hemisphere = ('Northern', 'Southern',)
hemisphere_multi_select = st.sidebar.multiselect(
    'Please select hemisphere(s)',
    hemisphere
)

# Year range slider - Point 2 filter
available_years = list(dict.fromkeys(main_df['year']))
available_years.sort()
year_slide_range = st.sidebar.select_slider('Please select year Range',  options=available_years, value=(available_years[0], available_years[-1]))


# Radio buttons - Point 3 filter
country_vs_state_option = st.sidebar.radio(
    'Please select an option:',
    (
        "Countries",
        "States",
    )
)

st.sidebar.markdown(f"<span>You have selected  <b>  <u> {country_vs_state_option} </u></b></span>",unsafe_allow_html=True)
st.sidebar.markdown(f"<span>Please select 2  <b>  <u> {country_vs_state_option} </u></b></span>",unsafe_allow_html=True)
 

# Making list of options text (Coutires / States)
option_states = [str(x).upper() for x in list(set(main_df['state'])) if str(x)!='nan']
option_countries = [str(x).upper() for x in list(set(main_df['country'])) if str(x)!='nan']
if country_vs_state_option=='Countries':
    option_menu_src = option_countries
else:
    option_menu_src = option_states


# Options Checkboxes - Dynamic based on country_vs_state_option and option_menu_src
option_1 = st.sidebar.checkbox(option_menu_src[0], key='option_1',value=True)
option_2 = st.sidebar.checkbox(option_menu_src[1], key='option_2',value=True)
option_3 = st.sidebar.checkbox(option_menu_src[2], key='option_3',)
option_4 = st.sidebar.checkbox(option_menu_src[3], key='option_4',)
option_5 = st.sidebar.checkbox(option_menu_src[4], key='option_5',)

# Min. and Max. Year inout boxes
min_year_line_chart  = st.sidebar.number_input('Enter Min. Year',value=available_years[0],min_value=available_years[0],max_value=available_years[-1])
max_year_line_chart = st.sidebar.number_input('Enter Max. Year',value=available_years[-1],min_value=available_years[0],max_value=available_years[-1])

# ---------------------------------------- End: Sidebar -----------------------------------


# ---------------- Start: Main Panel / Visual Components / Charts and Maps ----------------

# Pie Chart Main Section
st.markdown("<h3 style='margin-top:5%'></h3>", unsafe_allow_html=True)
pie_chart_data = getPieChartData(hemispheres=hemisphere_multi_select)
pie_chart_values =pie_chart_data.values()
pie_chart_figure = plt.figure(figsize = (5, 2) ,alpha=0.8)
pie_chart_labels = pie_chart_data.keys()
plt.pie(pie_chart_values, labels = pie_chart_labels,textprops={'fontsize': 8}) 
plt.title("                     UFO sightings Pie Chart                    ",fontsize=20)
patches, texts = plt.pie(pie_chart_values)
plt.legend(patches, pie_chart_labels, bbox_to_anchor=(.90,0.5), loc="center right", fontsize=8, bbox_transform=plt.gcf().transFigure)
plt.subplots_adjust(left=0.0, bottom=0.1,  )
st.pyplot(pie_chart_figure)








# Stacked Bar Chart and Map Section
stacked_bar_chart_data_container = getStackedBarChartData(list(year_slide_range))

# Map
st.map(stacked_bar_chart_data_container['map_df'])

# Stacked bar chart
stacked_bar_chart_figure = plt.figure(figsize = (6, 3) , )
N = 4
barWidth = .5
xloc = range(N) 
for index,country in enumerate(stacked_bar_chart_data_container['countries']):
    currect_bar = [list(x.values())[0][index]  for x in stacked_bar_chart_data_container['shape_container'] ]
    if index==0:
        plt.bar(xloc, np.array(currect_bar), width=barWidth)
    else:
        previous_lists = [[list(x.values())[0][sub_index]  for x in stacked_bar_chart_data_container['shape_container'] ] for sub_index in range(index) ]
        previous_lists = np.array(sum( [np.array(x) for x in previous_lists]))
        plt.bar(xloc, np.array(currect_bar), bottom=previous_lists, width=barWidth)
        
plt.ylabel('UFO frequency')
plt.xlabel('UFO Shapes')
plt.title('                          Stacked Bar Chart                          ',fontsize=20)
plt.xticks(xloc, [list(x.keys())[0] for x in stacked_bar_chart_data_container['shape_container']] )
# plt.yticks(range(0, 41, 5)) 
countries = stacked_bar_chart_data_container['countries'] 
plt.legend(  tuple(countries), bbox_to_anchor=(1.02,0.5), loc="center right",fontsize=7,   bbox_transform=plt.gcf().transFigure)
plt.subplots_adjust(left=0.0, bottom=0.1,  )
st.pyplot(stacked_bar_chart_figure)











line_chart_data = main_df[(main_df.year >=min_year_line_chart ) & (main_df.year <= max_year_line_chart)] 
select_options_container = [option_1,option_2,option_3,option_4,option_5]
valid_option_indexes = [index+1 for index,x in enumerate(select_options_container) if x][:2]
invalid_option_indexes = [index+1 for index,x in enumerate(select_options_container) if index+1 not in valid_option_indexes]   


# Restricting selection of only 2 options
if len([x for x in select_options_container if x])>2:
    print("-    Resetting")
    st.warning(f'Cannot show manipulate more than 2 {country_vs_state_option}')
    


# Line chart
# Dynamically creating lines based on selected options
line_chart_figure = plt.figure(figsize = (6, 3) , ) 
line_chart_x_axis =   range(int(min_year_line_chart),int(max_year_line_chart)+1 )
for  valid_index in valid_option_indexes:
    required_key  =option_menu_src[valid_index-1]
    if country_vs_state_option == 'Countries':
        temp_df_line_chart = main_df[(main_df.country ==required_key.lower()  )]
    else:
        temp_df_line_chart = main_df[(main_df.state ==required_key.lower()  )]
     
    temp_line_chart_data_container = []
    for year in range(int(min_year_line_chart),int(max_year_line_chart)+1):
        temp_line_chart_data_container.append(temp_df_line_chart[(temp_df_line_chart.year == year)].shape[0])
    
        
    plt.plot(line_chart_x_axis,  temp_line_chart_data_container , label = required_key, linestyle="-")
    pass
  

plt.ylabel('UFO frequency')
plt.xlabel('UFO Shapes')
plt.title('                                Line Chart                                ',fontsize=20)
plt.legend(  tuple([x for index,x in enumerate(option_menu_src) if index+1 in valid_option_indexes ]), bbox_to_anchor=(1.02,0.5), loc="center right",fontsize=7,   bbox_transform=plt.gcf().transFigure)
plt.subplots_adjust(left=0.0, bottom=0.1,  )

# plt.legend()


st.pyplot(line_chart_figure)



 