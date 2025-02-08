from datetime import date
from math import floor
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# --------------------------------------------------------------------
# Access Data

# day_df = pd.read_csv('data/new-day.csv')
hour_df = pd.read_csv('data/new-hour.csv')

# day_df.dteday = pd.to_datetime(day_df.dteday)
hour_df.dteday = pd.to_datetime(hour_df.dteday)

# --------------------------------------------------------------------
# Function Definition

def meanFloor(series):
   return floor(series.mean())

def getUserBy(by, method={ 'casual':meanFloor, 'registered':meanFloor, 'cnt':meanFloor }):
   return range_df.groupby(by).agg(method).reset_index() 

# --------------------------------------------------------------------

range_df = hour_df[hour_df.yr == 1]

with st.sidebar:

   startDate, endDate = st.date_input(
      label = 'Range Date',
      min_value = hour_df.dteday.min(),
      max_value = hour_df.dteday.max(),
      value = (range_df.dteday.min(), range_df.dteday.max())
   )

   range_df = hour_df[(hour_df.dteday >= str(startDate)) & (hour_df.dteday <= str(endDate))]

# --------------------------------------------------------------------
# EDA
#! Diletakkan dibawah sidebar supaya bisa ter-update

user_day_df = getUserBy('dteday', { 'cnt': 'sum' })
user_season_df = getUserBy(['season', 'season_new'])
user_weekday_df = getUserBy(['weekday', 'weekday_new'])
user_hour_df = getUserBy('hr')
user_temp_df = getUserBy('temp')

title = f'{range_df.dteday.min().date()} -> {range_df.dteday.max().date()}'

# --------------------------------------------------------------------
# Sidebar

st.title('Bike Sharing Data')

cols = st.columns(3)

with cols[0]:
   st.metric('Casual', range_df.casual.sum())
with cols[1]:
   st.metric('Registered', range_df.registered.sum())
with cols[2]:
   st.metric('Casual & Registered', range_df.cnt.sum())

# --------------------------------------------------------------------
#* Visualize Data
# Terlalu malas membuat DRY function untuk grafik 😓

fig = plt.figure(figsize=(10, 5))

plt.plot(
   user_day_df.dteday,
   user_day_df.cnt,
   color = 'green',
   label = 'Total'
)
plt.title(title)
plt.legend()

st.header('Bike Rent Per Day')
st.pyplot(fig)

# --------------------------------------------------------------------

width = 0.2
fig = plt.figure(figsize = (10, 5))

plt.bar(
   user_season_df.index - width,
   user_season_df.casual,
   label = 'Casual',
   width = width
)
plt.bar(
   user_season_df.index,
   user_season_df.registered,
   label = 'Registered',
   width = width
)
plt.bar(
   user_season_df.index + width,
   user_season_df.cnt,
   label = 'Total',
   width = width
)

plt.xticks(user_season_df.index, user_season_df.season_new)
plt.title(title)
plt.legend()

st.header('Average Bike Rent Per Season')
st.pyplot(fig)

# --------------------------------------------------------------------

fig = plt.figure(figsize = (10, 5))

plt.bar(
   user_weekday_df.index - width,
   user_weekday_df.casual,
   label = 'Casual',
   width = width
)
plt.bar(
   user_weekday_df.index,
   user_weekday_df.registered,
   label = 'Registered',
   width = width
)
plt.bar(
   user_weekday_df.index + width,
   user_weekday_df.cnt,
   label = 'Total',
   width = width
)

plt.xticks(user_weekday_df.index, user_weekday_df.weekday_new)
plt.title(title)
plt.legend()

st.header('Average Bike Rent Per Weekday')
st.pyplot(fig)

# --------------------------------------------------------------------

fig = plt.figure(figsize = (10, 5))

plt.plot(
   user_hour_df.hr,
   user_hour_df.casual,
   label = 'Casual',
)
plt.plot(
   user_hour_df.hr,
   user_hour_df.registered,
   label = 'Registered',
)
plt.plot(
   user_hour_df.hr,
   user_hour_df.cnt,
   label = 'Total',
   marker = 'o'
)

for i, value in enumerate(user_hour_df.cnt):
   plt.annotate(value, (i, value), textcoords="offset points", xytext=(0, 8), ha='center')

plt.xticks(user_hour_df.hr)
plt.title(title)
plt.legend()

st.header('Average Bike Rent Per Hour')
st.pyplot(fig)

# --------------------------------------------------------------------

fig = plt.figure(figsize = (10, 5))

plt.bar(
   user_temp_df.temp,
   user_temp_df.cnt,
   color='purple'
)

plt.title(title)

st.header('Average Bike Rent Per Temperature')
st.pyplot(fig)

st.caption(f'Copyright (c) Gibran {date.today().year}')