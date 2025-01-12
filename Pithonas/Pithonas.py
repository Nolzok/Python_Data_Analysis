import string
from turtle import width
import pandas
import xlrd
import matplotlib
import tkinter
from tkinter import ttk
from sqlalchemy import create_engine
from tkinter import scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sqlite3
import mysql.connector



def first():
    global cursor
    #diavazoume meso tou df ta collumns me ta onomata pou theloume
    weekend_nights=df['stays_in_weekend_nights'] 
    daily_nights=df['stays_in_week_nights']

    cancellations = df['previous_cancellations']
    no_cancellations=df["previous_bookings_not_canceled"]
    hotel_names=df["hotel"]

    #dimiourgoume ta DataFrames gia na xeirizomaste pio eukola kai aneta ta data tou csv
    data_nights=pandas.DataFrame({
        'hotel':hotel_names,
        'stays_in_weekend_nights':weekend_nights,
        'stays_in_week_nights':daily_nights
        })
    
    data = pandas.DataFrame({
        'hotel': hotel_names,
        'previous_cancellations': cancellations,
        'no_cancellations': no_cancellations
    })

    #kanoume group ta hotel
    grouped_data = data.groupby('hotel').sum()
    #kanoume group to total ton cancellation data pou exoume
    grouped_data['total'] = grouped_data['previous_cancellations'] + grouped_data['no_cancellations']
    #kai vriskoume to pososto
    grouped_data['cancellation_percentage'] = (grouped_data['previous_cancellations'] / grouped_data['total']) * 100

    #kanoume akrivos to idio alla gia ta pososta diamonis
    grouped_nights = data_nights.groupby('hotel').mean()
    grouped_nights['average_nights']=( grouped_nights['stays_in_weekend_nights'] + grouped_nights['stays_in_week_nights'] ) / 2 

    #pairnoume ta unique onomata tou hotel collumn
    unique_hotel_names = data['hotel'].unique()

    #ftiaxnoume ena grafima
    fig, ax = plt.subplots(figsize=(4, 5))  #orizoume to megethos
    #orizoume to data,to xroma kai to width
    ax.bar(range(len(unique_hotel_names)), grouped_data['cancellation_percentage'], color='red', width=0.05)
    #titlos grafimatos
    ax.set_title('Percentage of Previous Cancellations by Hotel')
    #titlos tou x axona
    ax.set_xlabel('Hotel Names')
    #titlos tou y axona
    ax.set_ylabel('Percentage (%)')

    #gia kathe unique onoma vazoume ticks
    ax.set_xticks(range(len(unique_hotel_names)))
    #gia kathe unique onoma vazoume label
    ax.set_xticklabels(unique_hotel_names, rotation=45, ha='right')

    #allazoume to megethos tou plot gia na xoraei sto window (an tixon einai mikrotero)
    plt.margins(0.05)
    plt.subplots_adjust(left=0.2, right=0.8, top=0.95, bottom=0.25)
    
    #kanoume to xrona lightblue oste na einai idio me to backgroud colour
    fig.patch.set_facecolor('lightblue')

    #vazoume to plot sto tkinter window mas
    canvas = FigureCanvasTkAgg(fig, master=frequency)
    canvas.draw()
    #allazoume topothesia tou graph
    canvas.get_tk_widget().place(x=1000, y=0)

    #to idio opos kai parapano
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.bar(range(len(unique_hotel_names)), grouped_nights['average_nights'], color='blue', width=0.05)
    ax2.set_title('Average Stays in Nights by Hotel')
    ax2.set_xlabel('Hotel Names')
    ax2.set_ylabel('Average Nights')
    ax2.set_xticks(range(len(unique_hotel_names)))
    ax2.set_xticklabels(unique_hotel_names, rotation=45, ha='right')

    plt.margins(0.01)
    plt.subplots_adjust(left=0.2, right=0.6, top=0.95, bottom=0.25)
    fig2.patch.set_facecolor('lightblue')

    canvas2 = FigureCanvasTkAgg(fig2, master=root)
    canvas2.draw()
    canvas2.get_tk_widget().place(x=200, y=0) 
    
    #gia na ftiaxnetai to table kathe fora pou trexoume to programma
    cursor.execute ('DROP TABLE IF EXISTS first' )
    #kanoume create ena table sto database pou exoume idi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS first (
            hotel VARCHAR(255) PRIMARY KEY NOT NULL,
            cancellation_percentage REAL,
            average_nights REAL
        )
    ''')
    
    #vazoume to cancellation percentage sto table mas
    for index, row in grouped_data.iterrows():
        cursor.execute('''
            INSERT INTO first (hotel, cancellation_percentage)
            VALUES (%s, %s)
        ''', (index, row['cancellation_percentage']))

    #to idio kai me ton meso oro ton bookings
    for index, row in grouped_nights.iterrows():
        cursor.execute('''
            UPDATE first 
            SET average_nights = %s
            WHERE hotel = %s
        ''', (row['average_nights'], index))

    conn.commit()
    
    grouped_data.to_csv('first.csv', index=False)

    
    

def second():
    
    #TA SIMEIA TOU KODIKA POU DEN EXOUN SXOLIA EINAI TA IDIA ME TA SXOLIA TOU "def first():"
    
    global cursor
    #diavazoume meso tou df ta collumns me ta onomata pou theloume
    hotel_names = df['hotel']
    arrival_month = df['arrival_date_month']
    weekend_nights = df['stays_in_weekend_nights']
    week_nights = df['stays_in_week_nights']

    data = pandas.DataFrame({
        'hotel': hotel_names,
        'arrival_date_month': arrival_month,
        'stays_in_weekend_nights': weekend_nights,
        'stays_in_week_nights': week_nights
    })

    
    grouped_data = data.groupby(['hotel', 'arrival_date_month']).sum().reset_index()

    unique_hotel_names = data['hotel'].unique()
    unique_months = data['arrival_date_month'].unique()

    fig, axs = plt.subplots(len(unique_hotel_names), 1, figsize=(10, len(unique_hotel_names) * 5), sharex=True)

    #gia kathe unique hotel kanoume insert to data
    for i, hotel in enumerate(unique_hotel_names):
        hotel_data = grouped_data[grouped_data['hotel'] == hotel]
        axs[i].bar(hotel_data['arrival_date_month'], hotel_data['stays_in_weekend_nights'], label='Weekend Nights', color='blue', alpha=0.7)
        axs[i].bar(hotel_data['arrival_date_month'], hotel_data['stays_in_week_nights'], label='Week Nights', color='orange', alpha=0.7, bottom=hotel_data['stays_in_weekend_nights'])
        axs[i].set_title(f'Bookings Distribution for {hotel}')
        axs[i].set_ylabel('Number of Nights')
        axs[i].legend()

    average_nights=hotel_data['stays_in_week_nights'] + hotel_data['stays_in_weekend_nights']
    
    axs[-1].set_xlabel('Arrival Month')
    plt.xticks(unique_months,rotation=45)
    plt.tight_layout()
    
    plt.margins(0.01)
    plt.subplots_adjust(left=0.2, right=0.8, top=0.95, bottom=0.25)
    fig.patch.set_facecolor('lightblue')

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)
    
    cursor.execute('DROP TABLE IF EXISTS second')

    cursor.execute('''
        CREATE TABLE second (
            hotel VARCHAR(255),
            arrival_date_month VARCHAR(255),
            stays_in_weekend_nights INT,
            stays_in_week_nights INT
        )
    ''')
    
    for index, row in grouped_data.iterrows():
        cursor.execute('''
            INSERT INTO second (hotel, arrival_date_month, stays_in_weekend_nights, stays_in_week_nights)
            VALUES (%s, %s, %s, %s)
        ''', (row['hotel'], row['arrival_date_month'], row['stays_in_weekend_nights'], row['stays_in_week_nights']))

        # Commit after each insertion if needed
        conn.commit()
        
        grouped_data.to_csv('second.csv', index=False)


       
    

def third():
    
       #TA SIMEIA TOU KODIKA POU DEN EXOUN SXOLIA EINAI TA IDIA ME TA SXOLIA TOU "def first():" i tou "def second():"

    global cursor

    #diavazoume meso tou df ta collumns me ta onomata pou theloume
    hotel_names = df['hotel']
    room_type = df['reserved_room_type']
    weekend_nights = df['stays_in_weekend_nights']
    week_nights = df['stays_in_week_nights']
    
    data = pandas.DataFrame({
        'hotel': hotel_names,
        'reserved_room_type': room_type,
        'stays_in_weekend_nights': weekend_nights,
        'stays_in_week_nights': week_nights
    })

    
    grouped_data = data.groupby(['hotel', 'reserved_room_type']).sum().reset_index()

    unique_hotel_names = data['hotel'].unique()
    unique_rooms = data['reserved_room_type'].unique()
  
    fig, axs = plt.subplots(len(unique_hotel_names), 1, figsize=(10, len(unique_hotel_names) * 5), sharex=True)

    for i, hotel in enumerate(unique_hotel_names):
        hotel_data = grouped_data[grouped_data['hotel'] == hotel]
        axs[i].bar(hotel_data['reserved_room_type'], hotel_data['stays_in_weekend_nights'], label='Weekend Nights', color='blue', alpha=0.7)
        axs[i].bar(hotel_data['reserved_room_type'], hotel_data['stays_in_week_nights'], label='Week Nights', color='orange', alpha=0.7, bottom=hotel_data['stays_in_weekend_nights'])
        axs[i].set_title(f'Bookings Distribution for {hotel}')
        axs[i].set_ylabel('Number of Nights')
        axs[i].legend()

    axs[-1].set_xlabel('Room Type')
    plt.xticks(unique_rooms,rotation=45)
    plt.tight_layout()
    
    plt.margins(0.01)
    plt.subplots_adjust(left=0.2, right=0.8, top=0.95, bottom=0.25)
    fig.patch.set_facecolor('lightblue')

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)

    cursor.execute('DROP TABLE IF EXISTS third')

    # Create the table schema
    cursor.execute('''
        CREATE TABLE third (
            hotel VARCHAR(255),
            reserved_room_type VARCHAR(255),
            stays_in_weekend_nights INT,
            stays_in_week_nights INT
        )
    ''')
    
    for index, row in grouped_data.iterrows():
        cursor.execute('''
            INSERT INTO third (hotel, reserved_room_type, stays_in_weekend_nights, stays_in_week_nights)
            VALUES (%s, %s, %s, %s)
        ''', (row['hotel'], row['reserved_room_type'], row['stays_in_weekend_nights'], row['stays_in_week_nights']))

        # Commit after each insertion if needed
        conn.commit()
        
        grouped_data.to_csv('third.csv', index=False)




def fourth():
        
        #TA SIMEIA TOU KODIKA POU DEN EXOUN SXOLIA EINAI TA IDIA ME TA SXOLIA TOU "def first():" i tou "def second():"

    global cursor

    #diavazoume meso tou df ta collumns me ta onomata pou theloume
    adults = df['adults'].astype(int)
    children = df['children'].astype(int)
    babies = df['babies'].astype(int)
    weekend_nights = df['stays_in_weekend_nights'].astype(int)
    week_nights = df['stays_in_week_nights'].astype(int)

    #ftiaxoume categories analoga me ta dedomena pou theloume opos gia paradeigma an theloume
    #ena couple tote tha einai mono 2 atoma xoris paidia, an theloume tin epoxi summer tha einai oi mines
    #june,july kai august
    
    categories = []
    for i in range(len(adults)):
        if children[i] > 0 or babies[i] > 0:
            categories.append('Family')
        elif adults[i] == 2 and children[i] == 0 and babies[i] == 0:
            categories.append('Couples')
        elif adults[i] == 1 and children[i] == 0 and babies[i] == 0:
            categories.append('Alone')
        else:
            categories.append('Others')

    data = pandas.DataFrame({
        'category': categories,
        'stays_in_weekend_nights': weekend_nights,
        'stays_in_week_nights': week_nights
    })

    grouped_data = data.groupby('category').sum().reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))

    bar_width = 0.35
    index = range(len(grouped_data))

    bar1 = ax.bar(index, grouped_data['stays_in_weekend_nights'], bar_width, label='Weekend Nights', color='blue')
    bar2 = ax.bar([i + bar_width for i in index], grouped_data['stays_in_week_nights'], bar_width, label='Week Nights', color='orange')

    ax.set_title('Bookings Distribution by Category')
    ax.set_xlabel('Category')
    ax.set_ylabel('Number of Nights')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(grouped_data['category'])
    ax.legend()

    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)
    
    cursor.execute('DROP TABLE IF EXISTS fourth')

    cursor.execute('''
        CREATE TABLE fourth (
            category VARCHAR(255),
            stays_in_weekend_nights INT,
            stays_in_week_nights INT
        )
    ''')
    
    for index, row in grouped_data.iterrows():
        cursor.execute('''
            INSERT INTO fourth (category, stays_in_weekend_nights, stays_in_week_nights)
            VALUES (%s, %s, %s)
        ''', (row['category'], row['stays_in_weekend_nights'], row['stays_in_week_nights']))

        conn.commit()
        
        grouped_data.to_csv('fourth.csv', index=False)



def fifth():
        
        #TA SIMEIA TOU KODIKA POU DEN EXOUN SXOLIA EINAI TA IDIA ME TA SXOLIA TOU "def first():" i tou "def second():" i tou "def fourth():"

    global cursor

    #diavazoume meso tou df ta collumns me ta onomata pou theloume
    hotel_names = df['hotel']
    arrival_year = df['arrival_date_year']
    weekend_nights = df['stays_in_weekend_nights']
    week_nights = df['stays_in_week_nights']

    data = pandas.DataFrame({
        'hotel': hotel_names,
        'arrival_date_year': arrival_year,
        'stays_in_weekend_nights': weekend_nights,
        'stays_in_week_nights': week_nights
    })

    
    grouped_data = data.groupby(['hotel', 'arrival_date_year']).sum().reset_index()

    unique_hotel_names = data['hotel'].unique()
    unique_years = data['arrival_date_year'].unique()
  
    fig, axs = plt.subplots(len(unique_hotel_names), 1, figsize=(10, len(unique_hotel_names) * 5), sharex=True)

    for i, hotel in enumerate(unique_hotel_names):
        hotel_data = grouped_data[grouped_data['hotel'] == hotel]
        axs[i].bar(hotel_data['arrival_date_year'], hotel_data['stays_in_weekend_nights'], label='Weekend Nights', color='blue', alpha=0.7,width=0.2)
        axs[i].bar(hotel_data['arrival_date_year'], hotel_data['stays_in_week_nights'], label='Week Nights', color='orange', alpha=0.7,width=0.2, bottom=hotel_data['stays_in_weekend_nights'])
        axs[i].set_title(f'Bookings Distribution for {hotel}')
        axs[i].set_ylabel('Number of Nights')
        axs[i].legend()

    axs[-1].set_xlabel('Arrival Year')
    plt.xticks(unique_years,rotation=45)
    plt.tight_layout()
    
    plt.margins(0.01)
    plt.subplots_adjust(left=0.2, right=0.8, top=0.95, bottom=0.25)
    fig.patch.set_facecolor('lightblue')

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)

    cursor.execute('DROP TABLE IF EXISTS fifth')
    cursor.execute('''
        CREATE TABLE fifth (
            hotel VARCHAR(255),
            arrival_date_year INT,
            stays_in_weekend_nights INT,
            stays_in_week_nights INT
        )
    ''')

    for index, row in grouped_data.iterrows():
        cursor.execute('''
            INSERT INTO fifth (hotel, arrival_date_year, stays_in_weekend_nights, stays_in_week_nights)
            VALUES (%s, %s, %s, %s)
        ''', (row['hotel'], row['arrival_date_year'], row['stays_in_weekend_nights'], row['stays_in_week_nights']))
    conn.commit()

    grouped_data.to_csv('fifth.csv', index=False)




def sixth():
            
        #TA SIMEIA TOU KODIKA POU DEN EXOUN SXOLIA EINAI TA IDIA ME TA SXOLIA TOU "def first():" i tou "def second():" i tou "def fourth():"

    global cursor

    #diavazoume meso tou df ta collumns me ta onomata pou theloume
    months = df['arrival_date_month'].astype(str)
    weekend_nights = df['stays_in_weekend_nights'].astype(int)
    week_nights = df['stays_in_week_nights'].astype(int)
    cancellations=df['previous_cancellations'].astype(int)
    
    categories = []
    for i in range(len(months)):
        if  months[i] == "December" or months[i]=="January" or months[i]=="February":
            categories.append('Winter')
        elif months[i]=="March" or months[i]=="April" or months[i]=="May":
            categories.append('Spring')
        elif months[i]=="June" or months[i]=="July" or months[i]=="August":
            categories.append('Summer')
        elif months[i]=="September" or months[i]=="October" or months[i]=="November":
            categories.append('Autumn')
        else:
            categories.append('Others')

    data = pandas.DataFrame({
        'category': categories,
        'stays_in_weekend_nights': weekend_nights,
        'stays_in_week_nights': week_nights,
        'previous_cancellations': cancellations
    })

    grouped_data = data.groupby('category').sum().reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))

    bar_width = 0.25
    index = range(len(grouped_data))

    bar1 = ax.bar(index, grouped_data['stays_in_weekend_nights'], bar_width, label='Weekend Nights', color='blue')
    bar2 = ax.bar([i + bar_width for i in index], grouped_data['stays_in_week_nights'], bar_width, label='Week Nights', color='orange')
    bar3 = ax.bar([i + 2*bar_width for i in index], grouped_data['previous_cancellations'], bar_width, label='Cancelled', color='red')

    ax.set_title('Bookings Distribution by Category')
    ax.set_xlabel('Category')
    ax.set_ylabel('Number of Bookings + Cancellations')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(grouped_data['category'])
    ax.legend()

    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)
    
    cursor.execute('DROP TABLE IF EXISTS sixth')
    cursor.execute('''
        CREATE TABLE sixth (
            category VARCHAR(255),
            stays_in_weekend_nights INT,
            stays_in_week_nights INT,
            previous_cancellations INT
        )
    ''')

    for index, row in grouped_data.iterrows():
        cursor.execute('''
            INSERT INTO sixth (category, stays_in_weekend_nights, stays_in_week_nights, previous_cancellations)
            VALUES (%s, %s, %s, %s)
        ''', (row['category'], row['stays_in_weekend_nights'], row['stays_in_week_nights'], row['previous_cancellations']))
    conn.commit()
    
    grouped_data.to_csv('sixth.csv', index=False)




def frequency_window():
    global root,frequency
    #an iparxei to arxiko window tote to katastrefoume
    if root is not None:
        root.destroy()
        root=None
    frequency = tkinter.Tk()
    frequency.geometry("1600x1000") #orizoume to size tou window
    frequency.configure(bg="lightblue") #allazoume to xroma
    frequency.title("Frequency") #onomazoume to window
    #pame piso sto arxiko window
    button=tkinter.Button(frequency,text="Go to Root",command=go_to_old_window,height=2,width=18,bg="lightblue",fg="black",relief="raised")
    button.place(x=10,y=10)
    sixth()

def tendencies_window():
    global root,tendencies
    #an iparxei to arxiko window tote to katastrefoume
    if root is not None:
        root.destroy()
        root=None
    tendencies = tkinter.Tk()
    tendencies.geometry("1600x1000") #orizoume to size tou window
    tendencies.configure(bg="lightblue") #allazoume to xroma
    tendencies.title("Tendencies") #onomazoume to window
    #pame piso sto arxiko window
    button=tkinter.Button(frequency,text="Go to Root",command=go_to_old_window,height=2,width=18,bg="lightblue",fg="black",relief="raised")
    button.place(x=10,y=10)
    fifth()

def family_window():
    global root,family
    #an iparxei to arxiko window tote to katastrefoume
    if root is not None:
        root.destroy()
        root=None
    family = tkinter.Tk()
    family.geometry("1600x1000") #orizoume to size tou window
    family.configure(bg="lightblue") #allazoume to xroma
    family.title("Family") #onomazoume to window
        #pame piso sto arxiko window
    button=tkinter.Button(frequency,text="Go to Root",command=go_to_old_window,height=2,width=18,bg="lightblue",fg="black",relief="raised")
    button.place(x=10,y=10)
    fourth()

def rooms_window():
    global root,rooms
    #an iparxei to arxiko window tote to katastrefoume
    if root is not None:
        root.destroy()
        root=None
    rooms = tkinter.Tk()
    rooms.geometry("1600x1000") #orizoume to size tou window
    rooms.configure(bg="lightblue") #allazoume to xroma
    rooms.title("Rooms") #onomazoume to window
        #pame piso sto arxiko window
    button=tkinter.Button(frequency,text="Go to Root",command=go_to_old_window,height=2,width=18,bg="lightblue",fg="black",relief="raised")
    button.place(x=10,y=10)
    third()

def basic_statistics_window():
    global root,basic_statistics
        #an iparxei to arxiko window tote to katastrefoume
    if root is not None:
        root.destroy()
        root=None
    basic_statistics = tkinter.Tk()
    basic_statistics.geometry("1600x1000") #orizoume to size tou window
    basic_statistics.configure(bg="lightblue") #allazoume to xroma
    basic_statistics.title("Basic Statistics") #onomazoume to window
        #pame piso sto arxiko window
    button=tkinter.Button(frequency,text="Go to Root",command=go_to_old_window,height=2,width=18,bg="lightblue",fg="black",relief="raised")
    button.place(x=10,y=10)
    first()
    

def months_seasons_window():
    global root,months_seasons
    #an iparxei to arxiko window tote to katastrefoume
    if root is not None:
        root.destroy()
        root=None
    months_seasons = tkinter.Tk()
    months_seasons.geometry("1600x1000") #orizoume to size tou window
    months_seasons.configure(bg="lightblue") #allazoume to xroma
    months_seasons.title("Months + Seasons") #onomazoume to window
        #pame piso sto arxiko window
    button=tkinter.Button(frequency,text="Go to Root",command=go_to_old_window,height=2,width=18,bg="lightblue",fg="black",relief="raised")
    button.place(x=10,y=10)
    second()
    
def go_to_old_window():
    global root,basic_statistics,months_seasons,rooms,family,tendencies,frequency
    #an tixon iparxoun ta alla windows ta katastrefoume me kathe if entoli
    if basic_statistics is not None:
        basic_statistics.destroy()
        basic_statistics=None
    if months_seasons is not None:
        months_seasons.destroy()
        months_seasons=None
    if rooms is not None:
        rooms.destroy()
        rooms=None
    if family is not None:
        family.destroy()
        family=None
    if tendencies is not None:
        tendencies.destroy()
        tendencies=None
    if frequency is not None:
        frequency.destroy()
        frequency=None
    
    root=tkinter.Tk() #ftiaxnoume to arxiko window
    root.geometry("1600x1000") #orizoume to size tou arxikou window
    root.configure(bg="lightblue") #allazoume to xroma
    root.title("Hotel Info") #onomazoume to arxiko window
    
    label=tkinter.Label(root,text="Welcome to Hotel Analytics!",font=("Comic Sans MS",20),fg="black",bg="lightblue") #ftiaxnoume ena label - text
    label.place(x=550,y=10)

    label=tkinter.Label(root,text="The buttons in the left side of \n the window will guide you \n through the hotel's database.",
                        font=("Times",16),fg="black",bg="lightblue")
    label.place(x=1100,y=150)
    
    label=tkinter.Label(root,text="Basic Statistics=First Subquestion\nMonths+Seasons=Second Subquestion\nRooms=Third Subquestion\nFamily=Fourth Subquestion\nTendencies=Fifth Subquestion\nFrequency=Sixth Subquestion",
                        font=("Times",16),fg="black",bg="lightblue")
    label.place(x=1100,y=500)
    
    #ftiaxnoume buttons gia kathe window kai anoigoume neo window me to command=window...
    button=tkinter.Button(root,text="Go to Basic Statistics",height=2,width=18,command=basic_statistics_window, bg="lightblue", fg="black",relief="raised")
    button.place(x=10,y=100)
    
    button=tkinter.Button(root,text="Go to Months + Seasons",height=2,width=18,command=months_seasons_window, bg="lightblue", fg="black",relief="raised")
    button.place(x=160,y=100)
    
    button=tkinter.Button(root,text="Go to Rooms",height=2,width=18,command=rooms_window, bg="lightblue", fg="black",relief="raised")
    button.place(x=10,y=200)
    
    button=tkinter.Button(root,text="Go to Family",height=2,width=18,command=family_window, bg="lightblue", fg="black",relief="raised")
    button.place(x=160,y=200)
    
    button=tkinter.Button(root,text="Go to Tendencies",height=2,width=18,command=tendencies_window, bg="lightblue", fg="black",relief="raised")
    button.place(x=10,y=300)
    
    button=tkinter.Button(root,text="Go to Frequency",height=2,width=18,command=frequency_window, bg="lightblue", fg="black",relief="raised")
    button.place(x=160,y=300)
    
    #thetoume global to df oste na mporei na ginei access apo ta ipoloipa windows
    global df
    csv_file_path = "~/Downloads/hotel_booking.csv"  #diavazoume to arxeio
    df = pandas.read_csv(csv_file_path, dtype={"column_name": str})  
    #metatrepoume to data type tou collumn 'children' se int gia na mporoume na to xrisimopoiisoume meta
    df['children'] = df['children'].fillna(0).astype(int) 

def connect_to_database():
    global conn, cursor
    #kanoume connect sto database mas
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='python'
    )
    cursor = conn.cursor()


#thetoume ola ta windows mas se None gia na dieukolinthoume sto deletion tous
root=None   
basic_statistics=None
months_seasons=None
label=None
rooms=None
family=None
tendencies=None
frequency=None

connect_to_database()
go_to_old_window() #anoigoume to arxiko window
root.mainloop()

