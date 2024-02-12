#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
from datetime import datetime, timedelta

# Calculate the dates for the dropdown options
def calculate_dates():
    # Today's date
    today = datetime.today()

    # End of this month: Find the last day of the current month
    if today.month == 12:
        end_of_this_month = datetime(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_this_month = datetime(today.year, today.month + 1, 1) - timedelta(days=1)

    # End of last month: Find the last day of the previous month
    if today.month == 1:
        end_of_last_month = datetime(today.year - 1, 12, 31)
    else:
        end_of_last_month = datetime(today.year, today.month, 1) - timedelta(days=1)

    return today, end_of_this_month, end_of_last_month

# Define the options and corresponding dates
today, end_of_this_month, end_of_last_month = calculate_dates()
options = {
    "Today": today,
    "End of this month": end_of_this_month,
    "End of last month": end_of_last_month,
    "Custom date": None  # Placeholder for the custom date option
}

# Streamlit app
def main():
    st.title('Date Selector')

    # Create the dropdown menu
    option = st.selectbox("Choose a date", options.keys())

    # Initialize selected_date variable
    selected_date = None

    # Check if the user selected 'Custom date'
    if option == "Custom date":
        # Use Streamlit's date_input widget to allow the user to pick a date
        custom_date = st.date_input("Pick a custom date", min_value=datetime(2000, 1, 1))
        selected_date = custom_date
        st.write("Selected Custom Date:", selected_date.strftime('%d %b %Y'))
    else:
        # Use the predefined date for the selected option
        selected_date = options[option]
        st.write("Selected Date:", selected_date.strftime('%d %b %Y'))

if __name__ == "__main__":
    main()


# In[ ]:




