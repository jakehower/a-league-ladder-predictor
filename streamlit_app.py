import streamlit as st
import pandas as pd

# Load the fixture CSV
fixtures = pd.read_csv('aleague-men-2024-UTC.csv')

# Initialize the ladder
teams = fixtures['Home Team'].unique().tolist() + fixtures['Away Team'].unique().tolist()
teams = list(set(teams))  # Remove duplicates

# Create the ladder DataFrame with additional columns
ladder = pd.DataFrame({
    'Club': teams,
    'P': 0,
    'W': 0,
    'D': 0,
    'L': 0,
    'GF': 0,
    'GA': 0,
    'GD': 0,
    'PTS': 0,
    'LAST 5': [''] * len(teams)  # Initialize with empty strings
})

# Function to update the ladder based on user input
def update_ladder(user_results):
    global ladder
    for result in user_results:
        home_team, away_team, home_score, away_score = result
        
        # Update Played Matches
        ladder.loc[ladder['Club'] == home_team, 'P'] += 1
        ladder.loc[ladder['Club'] == away_team, 'P'] += 1
        
        # Update Goals For and Against
        ladder.loc[ladder['Club'] == home_team, 'GF'] += home_score
        ladder.loc[ladder['Club'] == home_team, 'GA'] += away_score
        ladder.loc[ladder['Club'] == away_team, 'GF'] += away_score
        ladder.loc[ladder['Club'] == away_team, 'GA'] += home_score
        
        # Determine Win, Loss, Draw
        if home_score > away_score:
            ladder.loc[ladder['Club'] == home_team, 'W'] += 1
            ladder.loc[ladder['Club'] == away_team, 'L'] += 1
            ladder.loc[ladder['Club'] == home_team, 'PTS'] += 3
            ladder.loc[ladder['Club'] == home_team, 'LAST 5'] += 'W, '
            ladder.loc[ladder['Club'] == away_team, 'LAST 5'] += 'L, '
        elif home_score < away_score:
            ladder.loc[ladder['Club'] == away_team, 'W'] += 1
            ladder.loc[ladder['Club'] == home_team, 'L'] += 1
            ladder.loc[ladder['Club'] == away_team, 'PTS'] += 3
            ladder.loc[ladder['Club'] == home_team, 'LAST 5'] += 'L, '
            ladder.loc[ladder['Club'] == away_team, 'LAST 5'] += 'W, '
        else:
            ladder.loc[ladder['Club'] == home_team, 'D'] += 1
            ladder.loc[ladder['Club'] == away_team, 'D'] += 1
            ladder.loc[ladder['Club'] == home_team, 'PTS'] += 1
            ladder.loc[ladder['Club'] == away_team, 'PTS'] += 1
            ladder.loc[ladder['Club'] == home_team, 'LAST 5'] += 'D, '
            ladder.loc[ladder['Club'] == away_team, 'LAST 5'] += 'D, '
        
        # Update Goal Difference
        ladder['GD'] = ladder['GF'] - ladder['GA']

# Function to sort the ladder based on A-League rules
def sort_ladder():
    # Sort by points, goal difference, goals for, wins, etc.
    ladder_sorted = ladder.sort_values(
        by=['PTS', 'GD', 'GF', 'W'],
        ascending=[False, False, False, False]
    ).reset_index(drop=True)

    # Add current position
    ladder_sorted.insert(0, 'Position', range(1, len(ladder_sorted) + 1))
    return ladder_sorted

# Streamlit UI
st.title("A-League Ladder Predictor")

# User input for expected results
rounds = st.number_input("Enter number of rounds:", min_value=1, max_value=10)

user_results = []
for round_number in range(rounds):
    st.subheader(f"Round {round_number + 1}")
    
    # Get fixtures for the selected round
    round_fixtures = fixtures[fixtures['Round Number'] == round_number + 1]
    
    for index, match in round_fixtures.iterrows():
        home_team = match['Home Team']
        away_team = match['Away Team']
        
        # Create two columns for scores
        col1, col2 = st.columns(2)
        
        with col1:
            home_score = st.number_input(f"{home_team} Score", min_value=0, step=1, format="%d", key=f"home_{round_number}_{index}")
        
        with col2:
            away_score = st.number_input(f"{away_team} Score", min_value=0, step=1, format="%d", key=f"away_{round_number}_{index}")
        
        user_results.append((home_team, away_team, home_score, away_score))

# Button to update the ladder
if st.button("Update Ladder"):
    update_ladder(user_results)
    
    # Display the updated ladder as a styled DataFrame
    sorted_ladder = sort_ladder()

    # Display all teams, including those with zero matches played
    st.dataframe(sorted_ladder, height=500)  # Set height to accommodate all teams
