# import sqlite3
#
#
# def create_table(conn):
#     conn.execute('''
#     CREATE TABLE IF NOT EXISTS student_info(
#         first_name TEXT,
#         last_name TEXT,
#         credit INTEGER,
#         gpa REAL
#     );''')
#     print("Table created successfully")
#
#
# def clear_table(conn):
#     conn.execute('DELETE FROM student_info;')
#     print("Table cleared successfully")
#
#
# def write_table(conn):
#     # Use parameterized queries to insert data
#     data = [
#         ('Kate', 'Perry', 120, 3.3),
#         ('Kelvin', 'Harris', 50, 3.0),
#         ('Bin', 'Diesel', 250, 3.5),
#         ('nick', 'Cage', 22, 2.8),
#         ('Shawn', 'Carter', 100, 3.7),
#         ('Lucy', 'Lu', 200, 3.8),
#         ('John', 'Senna', 0, 0.0),
#         ('Syd', 'Barrett', 183, 2.8),
#         ('Peter', 'Chao', 111, 2.3),
#         ('Shang', 'abi', 64, 3.1)
#     ]
#
#     # Use executemany to insert multiple rows at once
#     conn.executemany("INSERT INTO student_info VALUES (?, ?, ?, ?);", data)
#     print("Data inserted successfully")
#
#
# def read_table(conn):
#     cursor = conn.execute('SELECT * FROM student_info;')
#     for row in cursor:
#         print(row)
#
#
# # Connect to the database using with statement
# with sqlite3.connect('test.db') as conn:
#     create_table(conn)
#     clear_table(conn)
#     write_table(conn)
#     read_table(conn)
import sqlite3


def retrieve_students():
    try:
        conn = sqlite3.connect('test.db')
        print("Opened database successfully");

        # with sqlite3.connect('test.db') as conn:
        query = '''
            SELECT first_name
            FROM student_info
            WHERE credit < 150 AND gpa > 3.0;
        '''
        cursor = conn.execute(query)
        result = cursor.fetchall()

        if not result:
            print("No matching records found.")
        else:
            print("Filtered Results:")
            for row in result:
                print(row[0])

    except sqlite3.Error as e:
        print(f"Error: {e}")
        raise NotImplementedError("Error occurred during data retrieval.")


retrieve_students()

import re

import re


def valid_email_list(email_list):
    valid_emails_ids = []

    try:
        for email_id in email_list:
            if '.edu.com' in email_id:
                continue

            modified_email = email_id.replace('[dot]', '.').replace('[at]', '@')
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(pattern, modified_email):
                valid_emails_ids.append(modified_email)

        return valid_emails_ids

    except Exception as e:
        print(f"Error: {str(e)}")
        raise NotImplementedError("Error occurred during processing.")


email_list = ['John[dot]Wick[at]rutgers[dot]edu',
              'Nancy@rutgers.edu.com',
              'Toby.Chavez.edu',
              'dfe.edu'
              'Steve[at]Peterson[at]rutgers[dot]edu',
              'Sydney[at]Lucas[at]rutgers[dot]edu',
              'Sydney[at][at]rutgers[dot]edu',
              'Byron.Dennis@umd.edu',
              'Nancy.Ruell@rutgers.edu',
              'Benjamin[dot]Conner[at]rutgers[dot]edu',
              'Nancy@rutgersedu',
              'dfe.edu.com',
              'dfe.edu.[]',
              ]

try:
    valid_emails = valid_email_list(email_list)
    print("Valid Emails:")
    for email in valid_emails:
        print(email)

except NotImplementedError as nie:
    print(f"NotImplementedError: {str(nie)}")
except Exception as e:
    print(f"Error: {str(e)}")

import pandas as pd

df = pd.read_csv('EuCitiesTemperatures.csv')

# Calculate average latitude and longitude for each country
avg_lat_lon_by_country = df.groupby('country')[['latitude', 'longitude']].mean()

# Fill missing latitude and longitude values with the average for their respective countries
df[['latitude', 'longitude']] = df.groupby('country')[['latitude', 'longitude']].transform(lambda x: x.fillna(x.mean()))

# Round the values to 2 decimal places
df['latitude'] = df['latitude'].round(2)
df['longitude'] = df['longitude'].round(2)

filtered_cities = df[(df['latitude'] >= 40) & (df['latitude'] <= 60) & (df['longitude'] >= 15) & (df['longitude'] <= 30)]

# Find countries with the maximum number of cities in the geographical band
max_cities_by_country = filtered_cities['country'].value_counts()

# Identify countries with the maximum number of cities
max_countries = max_cities_by_country[max_cities_by_country == max_cities_by_country.max()].index.tolist()

# Print the result
print(f"Countries with the maximum number of cities in the geographical band: {', '.join(max_countries)}")

for index, row in df.iterrows():
    if pd.isna(row['temperature']):
        print(f"Row before update:\n{row}")  # Print row information before update
        similar_regions = df[(df['EU'] == row['EU']) & (df['coastline'] == row['coastline'])]
        average_temp = similar_regions['temperature'].mean()
        df.at[index, 'temperature'] = round(average_temp, 2) if not pd.isna(average_temp) else None
        print(f"Row after update:\n{df.loc[index]}")  # Print row information after update


# df.to_csv('output.csv', index=False)

# import pandas as pd
import matplotlib.pyplot as plt
#
# # Assuming df is your DataFrame
# df = pd.read_csv('EuCitiesTemperatures.csv')

# Create a bar chart for the number of cities in each region
region_counts = df['EU'].value_counts()
region_counts.plot(kind='bar', color='skyblue')

# Set labels and title
plt.xlabel('EU Membership')
plt.ylabel('Number of Cities')
plt.title('Number of Cities in EU and Non-EU Regions')

# Show the plot
plt.show()



import pandas as pd
import matplotlib.pyplot as plt

# Assuming df is your DataFrame
df = pd.read_csv('EuCitiesTemperatures.csv')

# Preprocess temperature values and assign colors
df['temperature_color'] = pd.cut(df['temperature'], bins=[-float('inf'), 6, 10, float('inf')],
                                 labels=['blue', 'orange', 'red'])

# Create a region_type column based on EU and coastline columns
df['region_type'] = df['EU'] + '_coast_' + df['coastline']

# Create subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Scatter Plots of Latitude vs. City for Different Region Types', fontsize=16)

# Iterate over region types
for region_type, ax in zip(['EU_yes_coast_yes', 'EU_yes_coast_no', 'EU_no_coast_yes', 'EU_no_coast_no'], axes.flatten()):
    region_df = df[df['region_type'] == region_type]

    # Assign city numbers within each region
    region_df['city_number'] = range(len(region_df))

    # Set xticks to city numbers
    ax.set_xticks(region_df['city_number'])
    ax.set_xticklabels(region_df['city'], rotation=45, ha='right')

    # Set labels and title
    ax.set_xlabel('City')
    ax.set_ylabel('Latitude')
    ax.set_title(f'Region Type: {region_type}')

    # Add legend for temperature colors
    legend_labels = {'blue': 'Temperature < 6', 'orange': '6 <= Temperature <= 10', 'red': 'Temperature > 10'}

    # Scatter plot with temperature-based colors
    scatter = ax.scatter(region_df['city_number'], region_df['latitude'], c=region_df['temperature_color'], alpha=0.7)

    # Get legend handles and create legend
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10) for color in
               legend_labels.keys()]
    ax.legend(handles=handles, labels=legend_labels.values(), bbox_to_anchor=(1.05, 1), loc='upper left')

# Adjust layout
plt.tight_layout(rect=[0, 0, 1, 0.96])

# Show the plot
plt.show()
a=1
