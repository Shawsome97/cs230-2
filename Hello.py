import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import calendar

CSV = "bostoncrime.csv"
days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
default_month = [5]


# read in CSV file
def read_data():
    return pd.read_csv(CSV).set_index("INCIDENT_NUMBER")


# filters data for map use
def map_filter(offense, day, month):
    df = read_data()
    df = df.loc[df['OFFENSE_DESCRIPTION'].isin(offense)]
    df = df.loc[df['DAY_OF_WEEK'].isin(day)]
    df = df.loc[df['MONTH'].isin(month)]
    return df


# finds the 5 streets with most crime and 5 with the least
def top_5_streets():
    df = read_data()
    df_filtered = df[~df['STREET'].str.contains("&", case=False)]
    df2 = df_filtered['STREET'].value_counts()[:5]
    df3 = df_filtered['STREET'].value_counts().tail(5)
    return df2, df3


# creates a list of all the streets to be used in dropdown box for selection
def all_streets():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row['STREET'] not in lst:
            lst.append(row['STREET'])
    return lst


# creates a list of all offenses recorded to be used in dropdown box for selection
def all_offenses():
    df = read_data()
    lst = []
    for ind, row in df.iterrows():
        if row['OFFENSE_DESCRIPTION'] not in lst:
            lst.append(row['OFFENSE_DESCRIPTION'])
    return lst


# collects user entered streets and adds to dict to be added to bar chart
def street_bar(inp1):
    df = read_data()
    street_list = df['STREET'].to_list()
    sdict = {}
    inp = inp1.split(", ")  # creates a list of the user inputted streets
    for s1 in inp:
        s = s1.upper()  # matches the case to the streets list (all caps)
        if s in street_list:
            for street in street_list:
                if s not in sdict and s == street:  # counts the number of streets using a dictionary
                    sdict[s] = 1
                elif s == street:
                    sdict[s] += 1
        else:
            pass

    # creates bar chart with x and y lists from keys / values
    x = list(sdict.keys())
    y = list(sdict.values())
    plt.figure()
    plt.bar(x, y, color="skyblue")
    plt.xticks(rotation=45)
    plt.ylabel('Frequency of crimes')
    plt.title('Crimes committed on specified streets in 2023')
    return plt


# creates map based on df which is later specified by user inputs & the filter function
# ***code style taken from instructional CIS sandbox video***
def generate_map(df):
    map_df = df.filter(['OFFENSE_DESCRIPTION', 'Lat', 'Long'])
    st.write(map_df)
    view_state = pdk.ViewState(latitude=map_df['Lat'].mean(), longitude=map_df['Long'].mean(), zoom=12)

    layer = pdk.Layer("ScatterplotLayer", data=map_df,
                      get_position='[Long, Lat]',
                      get_radius=75,
                      get_color=[100, 150, 300],
                      pickable=True)

    tool_tip = {'html': 'Offense:<br/> <b>{OFFENSE_DESCRIPTION}</b>', 'style': {'backgroundColor': 'steelblue',
                'color': 'white'}}

    map1 = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9', initial_view_state=view_state, layers=[layer],
                    tooltip=tool_tip)
    st.pydeck_chart(map1)


# used to add frequency counts to top ten pie chart
# inspiration from stack overflow:
# https://stackoverflow.com/questions/59644751/show-both-value-and-percentage-on-a-pie-chart
def format_pct(x):
    df = read_data()
    total = df['OFFENSE_DESCRIPTION'].value_counts().values.sum()
    return '{:.1f}%\n({:.0f})'.format(x, total*x/100)


# pie chart of top ten most common crimes in data
def top_ten_pie():
    df = read_data()
    # creates lists of crime type and their associated counts of total occurrences
    crimes_list = df['OFFENSE_DESCRIPTION'].drop_duplicates().to_list()
    crimes_count = df['OFFENSE_DESCRIPTION'].value_counts().get(crimes_list, 0).to_list()
    # sorts the zipped list of tuples and only observes the top 10
    combined = sorted(list(zip(crimes_count, crimes_list)), reverse=True)[:10]
    frequency, crime_type = zip(*combined)
    ten_count = list(frequency)
    ten_name = list(crime_type)
    plt.figure()
    plt.pie(ten_count, labels=ten_name, autopct=format_pct, labeldistance=1, startangle=80, textprops={'fontsize': 8})
    plt.title('Top 10 Crime Types by Frequency')
    return plt


# creates histogram of common times
def histogram():
    plt.figure()
    df = read_data()
    bins = [0, 4, 8, 12, 16, 20, 24]  # Specify bin edges
    plt.hist(df["HOUR"], bins=bins, edgecolor="blue", align='left')
    plt.xlabel('Hour')
    ticks = [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)]  # Center-aligned ticks
    tick_labels = ['4 am', '8 am', '12 pm', '4 pm', '8 pm', '12 am']
    plt.xticks(ticks, tick_labels)
    plt.ylabel('Frequency')
    plt.title('Common Crime Times')
    return plt


# bar chart of common days
def bar_days():
    df = read_data()
    day_list = df['DAY_OF_WEEK'].to_list()

    # Get the abbreviated days of the week
    abbreviated_days = [day[:3] for day in calendar.day_name]

    # dict comprehension
    ddict = {day: 0 for day in abbreviated_days}

    for d in day_list:
        # Check for the abbreviation and update the count
        abbreviation = d[:3]
        if abbreviation in ddict:
            ddict[abbreviation] += 1

    x_vals = list(ddict.keys())
    y_vals = list(ddict.values())

    plt.figure()
    plt.xticks(range(len(abbreviated_days)), abbreviated_days)
    plt.xlabel('Day of Week')
    plt.ylabel('Frequency')
    plt.title('Frequency of Crime on Given Day')
    plt.bar(x_vals, y_vals, color='blue')
    return plt


# same as bar_day but for months
def bar_months():
    df = read_data()
    month_list = df['MONTH'].to_list()

    mdict = {mon: 0 for mon in month_list}

    for m in month_list:
        if m in mdict:
            mdict[m] += 1

    x_vals = list(mdict.keys())
    y_vals = list(mdict.values())

    # Sort the x-axis values (months) in ascending order
    sorted_months = sorted(x_vals, key=lambda x: (int(x), x))
    print(sorted_months)
    plt.figure()
    plt.xticks(range(1, 12), sorted_months)
    plt.xlabel('Month')
    plt.ylabel('Frequency')
    plt.title('Frequency of Crime in Given Month')
    plt.bar(x_vals, y_vals, color='blue')
    return plt


# displays the top 10 most frequent crimes for a given street
# *** referenced this https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf ***
# *** https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html ***
# *** https://stackoverflow.com/questions/68254094/python-pie-chart-font-size ***
def street_view(st1):
    df = read_data()

    for street_name in st1:
        crimes_on_street = df[df['STREET'] == street_name]

        # adds day of the week and month in the new DataFrame
        crimes_on_street['DAY_OF_WEEK'] = pd.to_datetime(crimes_on_street['OCCURRED_ON_DATE']).dt.day_name()
        crimes_on_street['MONTH'] = pd.to_datetime(crimes_on_street['OCCURRED_ON_DATE']).dt.month_name()

        # Count the occurrences of each crime on that street and in each month
        crime_counts = crimes_on_street.groupby(['OFFENSE_DESCRIPTION', 'MONTH']).size().reset_index(name='Frequency')

        # Create a DataFrame for the top 10 crimes
        top_10_crimes = crime_counts.nlargest(10, 'Frequency')

        # Plot a pie chart for each street
        plt.figure()
        plt.pie(top_10_crimes['Frequency'], labels=top_10_crimes['OFFENSE_DESCRIPTION'], autopct='%.2f%%',
                labeldistance=1, startangle=80, textprops={'fontsize': 8})
        plt.title(f'Top 10 Crimes on {street_name}')
    return plt


# method to filter the most common day and month crimes where committed on a street
# *** https://pandas.pydata.org/docs/reference/api/pandas.Categorical.html ***
def other_filter(st1):
    df = read_data()
    filtered_df = df[df['STREET'].isin(st1)]
    if not filtered_df.empty:
        months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                        'October', 'November', 'December']
        filtered_df['MONTH'] = pd.Categorical(filtered_df['MONTH'], categories=months_order, ordered=True)

        most_common_month = filtered_df['MONTH'].value_counts().idxmax()
        most_common_day = filtered_df['DAY_OF_WEEK'].value_counts().idxmax()
        return most_common_day, most_common_month
    else:
        return None, None


def tab1():
    centered_title = '<h1 style="text-align: center;">Interactive Charts</h1><br>'
    st.markdown(centered_title, unsafe_allow_html=True)

    # first bar
    st.sidebar.markdown("<br>Compare frequency of crimes on streets:", unsafe_allow_html=True)
    list1 = st.sidebar.text_input("Enter streets, each followed by a comma: ")
    st.pyplot(street_bar(list1))

    # input for map parameters
    st.sidebar.markdown("<br>Select Map Parameters:", unsafe_allow_html=True)
    default_crime = st.sidebar.multiselect("Select Some Offenses: ", all_offenses())
    default_day = st.sidebar.multiselect("Select days in which offenses were committed: ", days_of_week)
    default_month.append(st.sidebar.slider("Month: ", 1, 12))

    data = map_filter(default_crime, default_day, default_month)
    generate_map(data)

    # selected street
    st.sidebar.markdown("<br>Select Street for Analysis:", unsafe_allow_html=True)
    selected_streets = st.sidebar.multiselect("Select a street: ", all_streets())

    # displays the filtered common month / day for the selected street
    day1, month1 = other_filter(selected_streets)
    if day1 is not None and month1 is not None:  # https://stackoverflow.com/questions/3965104/not-none-test-in-python
        st.pyplot(street_view(selected_streets))
        st.write(f'The day of the week {selected_streets} has the most crime is on {str(day1)}, and '
                 f'the month with the most is {str(month1)}')
    else:
        st.warning("No data available for the selected street.")  # https://docs.streamlit.io/library/cheatsheet


def tab2():
    centered_title = '<h1 style="text-align: center;">Additional Information</h1>'
    st.markdown(centered_title, unsafe_allow_html=True)

    centered_text = ('<div style="text-align: center;">This non-interactable information is general information '
                     'intended to aid those planning to visit Boston'
                     'on a specific time, day, or month.</div><br>')
    st.markdown(centered_text, unsafe_allow_html=True)

    # Display the histogram
    plt_histogram = histogram()
    st.pyplot(plt_histogram)

    # display top 5 best / worst data frames
    text1 = ('<div style="text-align: center;">The following data frames list the top 5 streets in Boston with the '
             'most offenses committed on them, as well as the top 5 with the least.</div><br>')
    st.markdown(text1, unsafe_allow_html=True)

    result_df2, result_df3 = top_5_streets()
    col1, col2 = st.columns(2)

    col1.dataframe(result_df2)
    col2.dataframe(result_df3)

    # bar of most common crime days
    text2 = ('<br><div style="text-align: center;">These are simple bar charts projecting the frequency of '
             'crimes committed on a given month or day during 2023.</div><br>')
    st.markdown(text2, unsafe_allow_html=True)

    st.pyplot(bar_days())

    # bar of most common crime months
    st.pyplot(bar_months())

    # top ten pie
    text3 = ('<br><div style="text-align: center;">The pie chart projects the top 10 most common crimes in Boston '
             'as well as the frequency of the crimes recorded so far in 2023.</div><br>')
    st.markdown(text3, unsafe_allow_html=True)

    st.pyplot(top_ten_pie())


def tab3():
    centered_title = '<h1 style="text-align: center;">Statement from Boston Police Department</h1>'
    st.markdown(centered_title, unsafe_allow_html=True)
    text2 = ('<br><div style="text-align: center;">"The Boston Police Department is '
             'dedicated to working in partnership with the community to fight crime. '
             'We work to improve the quality of life in our neighborhoods."</div><br>')
    st.markdown(text2, unsafe_allow_html=True)

    text3 = ('<br><div style="text-align: center;">"Through community policing, '
             'we want to be a reflection of the residents we serve. We aim to create '
             'a professional culture and inclusive environment that mirrors the best '
             'of all of us. Learn more about the history of our department, or visit '
             'police.boston.gov for the latest information."</div><br>')
    st.markdown(text3, unsafe_allow_html=True)

    image_url = "https://cloudfront-us-east-1.images.arcpublishing.com/advancelocal/5ZS2JKU4SZBKLE6OI5XEU53CB4.jpg"
    st.image(image_url, caption='https://www.boston.gov/departments/police', use_column_width=True)


# *** https://docs.streamlit.io/library/api-reference/layout/st.tabs ***
def main():
    # [theme]
    # primaryColor = "#00f5e7"
    # backgroundColor = "#89a8f1"
    # secondaryBackgroundColor = "#c0eaea"
    # textColor = "#000000"
    st.title('Crime Visualization for Boston 2023')

    # Create tabs
    tabs = ["Interactive Graphs", "Informative Graphs", "Boston PD Statement"]
    selected_tab = st.sidebar.radio("Select Tab", tabs)

    # Display the selected tab content
    if selected_tab == "Interactive Graphs":
        tab1()
    elif selected_tab == "Informative Graphs":
        tab2()
    elif selected_tab == "Boston PD Statement":
        tab3()


if __name__ == "__main__":
    main()

