import pandas as pd
import plotly_express as px
import streamlit as st
import plotly.graph_objects as go
import calendar
from streamlit_option_menu import option_menu

# Define function to perform common operations
def preprocess_data(df):
    df['event_date'] = pd.to_datetime(df['event_date'], format='%Y%m%d')
    df['year'] = df['event_date'].dt.year.astype(str)
    df['month'] = df['event_date'].dt.month.astype(str)
    df['month_name'] = df['event_date'].dt.strftime('%b')
    return df

# Read data frames using relative file paths
df = pd.read_csv('users_sessions.csv')
df_sales = pd.read_csv('sales_items.csv')
df_traffic = pd.read_csv('traffic.csv')
df_device = pd.read_csv('devices.csv')
df_pages = pd.read_csv('most_visited_pages.csv')

# Preprocess data frames
df = preprocess_data(df)
df_sales = preprocess_data(df_sales)
df_traffic = preprocess_data(df_traffic)
df_device = preprocess_data(df_device)
df_pages = preprocess_data(df_pages)

# Replace missing values and none as direct traffic type
df_traffic['medium'] = df_traffic['medium'].fillna('direct')
df_traffic['medium'] = df_traffic['medium'].replace('(none)', 'direct')

# Set page config
st.set_page_config(page_title="GA4", page_icon=":barchart:", layout="wide")

# Define options for sidebar
options = ["Website performance", "Store performance"]

# Define dictionary to map numeric month values to month names
month_names = {i: calendar.month_name[i] for i in range(1,13)}

# Sidebar
st.sidebar.header("GA4 dashboard")
st.sidebar.text("You can switch between\nWebsite and Store\nperformance dashboards")
with st.sidebar:
    with st.sidebar:
            selected = option_menu(
                menu_title=None,
                options=["Website performance", "Store performance"],
                default_index=0
                )

    st.header("Filters:")
    year = st.multiselect("Select year:", options=df['year'].unique(), default=df['year'].unique())
    month = st.multiselect("Select month:", options=df['month_name'].unique(), default=df['month_name'].unique())


# Apply filters
df_filtered = df.query('year == @year & month_name == @month')
df_sales_filtered = df_sales.query('year == @year & month_name == @month')
df_traffic_filtered = df_traffic.query('year == @year & month_name == @month')
df_device_filtered = df_device.query('year == @year & month_name == @month')
df_pages_filtered = df_pages.query('year == @year & month_name == @month')



#----------------------------------------------------------------------------------------
# Creating blocks on the page for KPIs
first_col, second_col, third_col, forth_col = st.columns(4)
st.markdown('---')

# Blocks first row
left_column, right_column = st.columns(2)

# Blocks second row
left_column_2, right_column_2 = st.columns(2)

# Blocks 2 page
col_1, col_2, col_3 = st.columns(3)

#------------
#Creating brand and category filters
if selected == "Store performance":
    with left_column:
        item_brand = st.selectbox(
            "Select brand:",
            options=df_sales_filtered['item_brand'].unique(),
            index=0
            )



item_category_list = list(df_sales_filtered['item_category'].unique())

# Add "Select all" option to the top of the list
item_category_list = ['Select all'] + item_category_list 
select_all=item_category_list[:]
select_all.append('Select all')

if selected == "Store performance":
    with right_column:
        category_dropdown = st.multiselect(
            'Select item category',
            select_all,
            default='Select all'
            )
if selected == "Store performance":
    if 'Select all' in category_dropdown :
        category_dropdown=item_category_list

#Applying filters Website performance
if selected == "Store performance":
    df_sales_filtered_item = df_sales_filtered.query(
        'item_brand == @item_brand & item_category == @category_dropdown')






# ----------------- KPI Website performance -----------------------------------
# Creating variables
total_users = df_filtered['users'].sum()

total_new_users = df_filtered['new_users'].sum()

total_sessions = df_filtered['sessions'].sum()

total_pageviews = df_filtered['pageviews'].sum()



if selected == "Website performance":
    with first_col:
        st.subheader('Total users')
        st.subheader(f'{total_users:,}')

    with second_col:
        st.subheader('Total new users')
        st.subheader(f'{total_new_users:,}')

    with third_col:
        st.subheader('Total sessions')
        st.subheader(f'{total_sessions:,}')

    with forth_col:
        st.subheader('Total pageviews')
        st.subheader(f'{total_pageviews:,}')


# KPIs Store performance
# Total revenue, total n of purchases, total sessions, conversion rate
if selected == "Store performance":

    total_revenue = int(df_sales_filtered['item_revenue_in_usd'].sum())
    number_purchase = int(df_sales_filtered['quantity'].sum())
    conversion_rate = number_purchase/total_sessions
    conversion_rate_formatted = "{:.2%}".format(conversion_rate)


    with first_col:
        st.subheader('Total revenue')
        st.subheader(f'{total_revenue:,}')
        
    with second_col:
        st.subheader('Number of purchases')
        st.subheader(f'{number_purchase:,}')
        
    with third_col:
        st.subheader('Total sessions')
        st.subheader(f'{total_sessions:,}')       
        
    with forth_col:
        st.subheader('Conversion rate')
        st.subheader(conversion_rate_formatted) 
        
 




# ---- Body ----

# Create the bar chart

# Monthly total users and new users

total_users_by_month = (
    df_filtered.groupby(by=['month']).sum()[['users', 'new_users']].sort_values(by=['month'])
)

# Define dictionary to map numeric month values to month names
month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
               7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

# Convert 'month' column to numeric
total_users_by_month.index = total_users_by_month.index.astype(int)

# Convert numeric month values to month names
total_users_by_month.index = total_users_by_month.index.map(month_names)


fig_users_by_month = go.Figure()

fig_users_by_month.add_trace(
    go.Bar(
        x=total_users_by_month.index,
        y=total_users_by_month['users'],
        name='Total Users',
        marker_color='#008080',
        text=total_users_by_month['users'],
        texttemplate='%{text:.2s}',
        textposition='outside',
    )
)

fig_users_by_month.add_trace(
    go.Bar(
        x=total_users_by_month.index,
        y=total_users_by_month['new_users'],
        name='New Users',
        marker_color='#f9c7a1',
        text=total_users_by_month['new_users'],
        texttemplate='%{text:.2s}',
        textposition='outside',
    )
)

# Update the layout

# Get the maximum user count
max_users = max(total_users_by_month[['users', 'new_users']].values.ravel())

fig_users_by_month.update_layout(
    title='Monthly Total Users and New Users',
    xaxis_title='Month',
    yaxis_title='Total Users',
    yaxis_range=[0, max_users + 10000],
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False),  # Remove x-axis gridlines
    yaxis=dict(showgrid=False),  # Remove y-axis gridlines
    legend=dict(
        x=1.02,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    margin=dict(
        r=80,  # Add padding to the right for the legend
    ),
    #height = 550
)

# Adjust label positions and font size
fig_users_by_month.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')




# -- Line chart -- 
# Plot the line chart

# Group the data by medium and date, and sum the events for each group
df_traffic_grouped = df_traffic_filtered.groupby(['medium', 'event_date']).sum()['sessions'].reset_index()

# Rename the 'events' column to 'traffic'
df_traffic_grouped = df_traffic_grouped.rename(columns={'sessions': 'traffic'})

fig_line = px.line(df_traffic_grouped, 
                   x='event_date', 
                   y='traffic', 
                   color='medium', 
                   title='Traffic by Medium')


# Display the charts
 

if selected == "Website performance":
    left_column.plotly_chart(fig_users_by_month, 
                         use_container_width=True
                         )

    right_column.plotly_chart(fig_line, 
                          use_container_width=True
                          )



# Pie chart

# Group the data by category and count the number of events for each category
df_event_counts = df_device_filtered.groupby(by=['category']).sum()['events']

# Convert the groupby object to a data frame
df_event_counts = df_event_counts.reset_index()

# st.dataframe(df_event_counts)

# Create the pie chart
fig_pie = px.pie(
    df_event_counts, 
    values='events', 
    names='category',
    title='Devices used',
    hole=0.7
    ) 

# Display the pie chart
# st.plotly_chart(fig_pie, use_container_width=True)




# Group the data by medium and date, and sum the events for each group
df_pages_grouped = df_pages_filtered.groupby(['title']).sum()['n'].reset_index()

# Sort the data by the 'n' column in descending order
df_pages_grouped_sorted = df_pages_grouped.sort_values(by='n', ascending=False)

# Filter the dataframe to keep only the top 10 rows
df_top10 = df_pages_grouped_sorted.head(10)


# Create a bar chart
fig_bar_pages = go.Figure()

# Add horizontal bar trace
fig_bar_pages.add_trace(
    go.Bar(
        x=df_top10['n'], 
        y=df_top10['title'], 
        orientation='h',
        text=df_top10['n'],
        marker=dict(color='#008080'),
        texttemplate='%{text:.2s}',
        textposition='outside'
    )
)

# Set layout properties

# Get the maximum n
max_n = max(df_top10[['n']].values.ravel())

fig_bar_pages.update_layout(
    title='Most Visited Pages',
    xaxis_title='Number of Visits',
    yaxis_title='Page Title',
    xaxis_range= [0, max_n + 30000],
    height=500,
    yaxis=dict(autorange="reversed"),
    plot_bgcolor='rgba(0,0,0,0)'
    )


# Reverse the y-axis so that the bar with the highest n value is at the top
fig_bar_pages.update_yaxes(autorange="reversed")


# Display the charts


if selected == "Website performance":
    left_column_2.plotly_chart(fig_pie, 
                               use_container_width=True
                               )

    right_column_2.plotly_chart(fig_bar_pages, 
                                use_container_width=True
                                )


# -------------------------- Sales dashboard ----------------------------------


if selected == "Store performance":

# Group the data by event_date and item_brand
    df_sales_grouped = df_sales_filtered_item.groupby(['event_date']).agg({'item_revenue_in_usd': 'sum'}).reset_index()

# Create the line chart
    fig_sales_line = px.line(df_sales_grouped, 
                   x='event_date', 
                   y='item_revenue_in_usd', 
                   title='')


# Ploting the chart
#if selected == "Store performance":
#    st.plotly_chart(fig_sales_line, use_container_width=True)


# ---- Most popular items by revenue ----

# Bar chart items by revenue
# Group the data by item revenue
    df_sales_item_rev = df_sales_filtered_item.groupby(['item_name']).agg({'item_revenue_in_usd': 'sum'}).reset_index()
    df_sales_item_rev = df_sales_item_rev.sort_values(by='item_revenue_in_usd', ascending=False)
    df_sales_item_rev = df_sales_item_rev.head(10) # Selecting top 10 items
    df_sales_item_rev = df_sales_item_rev.sort_values(by='item_revenue_in_usd', ascending=True)

    max_rev = max(df_sales_item_rev[['item_revenue_in_usd']].values.ravel())

# Create the bar chart
    fig_bar_item_rev = go.Figure()

    fig_bar_item_rev.add_trace(
        go.Bar(
            x = df_sales_item_rev['item_revenue_in_usd'],
            y = df_sales_item_rev['item_name'],
            orientation='h',
            text=df_sales_item_rev['item_revenue_in_usd'],
            marker=dict(
                color=df_sales_item_rev['item_revenue_in_usd'],
                colorscale='darkmint' # set the color scale
                ),
            texttemplate='%{text:.2s}',
            textposition='outside',
            )
        )

# Add title
    fig_bar_item_rev.update_layout(
        title='Top 10 Items by Revenue',
        xaxis_range= [0, max_rev + 2000],
        )
    
#st.plotly_chart(fig_bar_item_rev, use_container_width=True)


# ---- Most popular items by quantity ----
# Group the data by items by quantity
    df_sales_item_q = df_sales_filtered_item.groupby(['item_name']).agg({'quantity': 'sum'}).reset_index()
    df_sales_item_q = df_sales_item_q.sort_values(by='quantity', ascending=False)
    df_sales_item_q = df_sales_item_q.head(10) # Selecting top 10 items
    df_sales_item_q = df_sales_item_q.sort_values(by='quantity', ascending=True)

    max_q = max(df_sales_item_q[['quantity']].values.ravel())

# Create the bar chart
    fig_bar_item_q = go.Figure()

    fig_bar_item_q.add_trace(
        go.Bar(
            x = df_sales_item_q['quantity'],
            y = df_sales_item_q['item_name'],
            orientation='h',
            text=df_sales_item_q['quantity'],
            marker=dict(
                color=df_sales_item_q['quantity'],
            colorscale='darkmint' # set the color scale
            ),
            texttemplate='%{text:.2s}',
            textposition='outside'
    )
)

# Add title
    fig_bar_item_q.update_layout(
        title='Top 10 Items by Quantity',
        xaxis_range= [0, max_q + 100],
        )
    
#st.plotly_chart(fig_bar_item_q, use_container_width=True)

# Displaying charts

if selected == "Store performance":
    col_1.plotly_chart(fig_sales_line, 
                       use_container_width=True
                       )

    col_2.plotly_chart(fig_bar_item_rev, 
                       use_container_width=True
                       )
    
    col_3.plotly_chart(fig_bar_item_q, 
                       use_container_width=True
                       )




# ---- HIDE STREAMLIT STYLE ----
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)




