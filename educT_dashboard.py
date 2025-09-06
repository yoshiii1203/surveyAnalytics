import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Educational Tour Survey Dashboard", layout="wide", page_icon="🎓")

# Password authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form("login_form"):
        password = st.text_input("Enter password to access the dashboard", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if password == "admin123":
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect password. Access denied.")
    st.stop()

# Set style for better visualizations
plt.style.use('default')
sns.set_palette("husl")

# Load and process data
@st.cache_data
def load_data():
    df = pd.read_csv('109.csv', encoding='utf-8')
    # Clean column names
    df.columns = [
        'Timestamp', 'Name', 'Email', 'Program', 'Section',
        'Tour_Location_Preference', 'Affordability_Rating', 'Most_Important_Factor',
        'Previous_Vote_Mattered', 'Non_Student_Factors', 'Manila_Willingness',
        'Barriers', 'Additional_Comments', 'Preferred_Package'
    ]
    # Process Barriers
    all_barriers = []
    for barriers_str in df['Barriers'].dropna():
        if pd.notna(barriers_str) and barriers_str.strip():
            barriers_list = [b.strip() for b in str(barriers_str).split(';') if b.strip()]
            all_barriers.extend(barriers_list)
    unique_barriers = list(set(all_barriers))
    for barrier in unique_barriers:
        df[f'Barrier_{barrier.replace("/", "_").replace(" ", "_")}'] = df['Barriers'].apply(
            lambda x: 1 if pd.notna(x) and barrier in str(x) else 0
        )
    return df, unique_barriers

df, unique_barriers = load_data()

# Sidebar filters
st.sidebar.title("Filters")
selected_program = st.sidebar.multiselect("Select Program", options=df['Program'].unique(), default=df['Program'].unique())
selected_section = st.sidebar.multiselect("Select Section", options=df['Section'].unique(), default=df['Section'].unique())

# Filter data
filtered_df = df[df['Program'].isin(selected_program) & df['Section'].isin(selected_section)]

# Main title
st.title("🎓 Educational Tour Survey Dashboard")
st.markdown("---")

# Key Metrics
st.subheader("📊 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Responses", len(filtered_df))
with col2:
    st.metric("Programs", filtered_df['Program'].nunique())
with col3:
    st.metric("Sections", filtered_df['Section'].nunique())
with col4:
    expensive_pct = len(filtered_df[filtered_df['Affordability_Rating'].isin(['Expensive', 'Very Expensive'])]) / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
    st.metric("Find Expensive", f"{expensive_pct:.1f}%")
with col5:
    willing_pct = len(filtered_df[filtered_df['Manila_Willingness'] == 'Yes, definitely']) / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
    st.metric("Definitely Willing", f"{willing_pct:.1f}%")

st.markdown("---")
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "Overview", "Location Preference", "Affordability", "Important Factors", 
    "Voting Power", "Non-Student Factors", "Manila Willingness", "Barriers", 
    "Comments", "Preferred Package", "Sentiment Analysis", "Program-Section Summary"
])

with tab1:
    st.header("📊 Overview: Survey Questions & Analysis")
    
    st.markdown("""
    ### 📋 Survey Questions Asked:
    
    1. **Where do you personally want to have the educational tour?** → *Location Preference Tab*
    2. **How would you rate the affordability of the Manila package (PHP 22,000) for you and your family?** → *Affordability Tab*
    3. **If given a choice, which factor is MOST important in your tour decision?** → *Important Factors Tab*
    4. **Do you feel your previous vote for the tour location/package mattered, given that we are now re-evaluating the options?** → *Voting Power Tab*
    5. **Is the re-evaluation of the location/package happening now because it was affected on factors other than student preference?** → *Non-Student Factors Tab*
    6. **If Manila remains the final destination, are you still willing and able to join the educational tour?** → *Manila Willingness Tab*
    7. **What are the biggest barriers for you to join the tour as currently planned? (Check all that apply)** → *Barriers Tab*
    8. **Do you have any additional comments or suggestions regarding the tour destination, package, or decision process?** → *Comments Tab*
    9. **Select the package you prefer:** → *Preferred Package Tab*
    
    *📈 Overall sentiment analysis available in the Sentiment Analysis Tab*
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        program_counts = filtered_df['Program'].value_counts().reset_index()
        program_counts.columns = ['Program', 'Count']
        fig = px.bar(program_counts, x='Program', y='Count', title='Responses by Program', 
                     color='Program', color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("Show Voters by Program-Section"):
            filtered_df_copy = filtered_df.copy()
            filtered_df_copy['Program_Section'] = filtered_df_copy['Program'] + ' ' + filtered_df_copy['Section']
            for ps in sorted(filtered_df_copy['Program_Section'].unique()):
                st.write(f"**{ps}:**")
                voters = filtered_df_copy[filtered_df_copy['Program_Section'] == ps][['Name', 'Email']]
                st.dataframe(voters, use_container_width=True)

with tab2:
    st.header("🗺️ Tour Location Preference")
    st.markdown("**Question:** Where do you personally want to have the educational tour?")
    
    location_counts = filtered_df['Tour_Location_Preference'].value_counts().reset_index()
    location_counts.columns = ['Location', 'Count']
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(location_counts, values='Count', names='Location', title='Location Preference Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(location_counts, x='Location', y='Count', title='Location Preference Count')
        st.plotly_chart(fig, use_container_width=True)
    
    # Program-Section Breakdown Table
    st.subheader("📊 Breakdown by Program-Section")
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['Program_Section'] = filtered_df_copy['Program'] + ' ' + filtered_df_copy['Section']
    
    # Create crosstab for detailed breakdown
    location_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Tour_Location_Preference'], margins=True)
    st.dataframe(location_breakdown, use_container_width=True)
    
    # Percentage breakdown
    location_pct_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Tour_Location_Preference'], normalize='index') * 100
    location_pct_breakdown = location_pct_breakdown.round(1)
    st.subheader("📈 Percentage Breakdown by Program-Section")
    st.dataframe(location_pct_breakdown, use_container_width=True)
    
    # Visual breakdown
    loc_by_program_section = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Tour_Location_Preference'], normalize='index') * 100
    loc_by_program_section = loc_by_program_section.reset_index().melt(id_vars='Program_Section', var_name='Location', value_name='Percentage')
    fig = px.bar(loc_by_program_section, x='Program_Section', y='Percentage', color='Location', barmode='stack',
                 title='Location Preference by Program-Section (%)')
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 Detailed Voter List by Location and Program-Section"):
        for loc in location_counts['Location']:
            st.write(f"**{loc}:**")
            for ps in sorted(filtered_df_copy['Program_Section'].unique()):
                ps_voters = filtered_df_copy[(filtered_df_copy['Tour_Location_Preference'] == loc) & (filtered_df_copy['Program_Section'] == ps)][['Name', 'Email']]
                if not ps_voters.empty:
                    st.write(f"  *{ps}:* {len(ps_voters)} voters")
                    st.dataframe(ps_voters, use_container_width=True)

with tab3:
    st.header("💸 Affordability Analysis")
    st.markdown("**Question:** How would you rate the affordability of the Manila package (PHP 22,000) for you and your family?")
    
    affordability_counts = filtered_df['Affordability_Rating'].value_counts().reset_index()
    affordability_counts.columns = ['Rating', 'Count']
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(affordability_counts, x='Rating', y='Count', title='Affordability Rating Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(affordability_counts, values='Count', names='Rating', title='Affordability Rating Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Program-Section Breakdown
    st.subheader("📊 Breakdown by Program-Section")
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['Program_Section'] = filtered_df_copy['Program'] + ' ' + filtered_df_copy['Section']
    
    # Create crosstab for detailed breakdown
    afford_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Affordability_Rating'], margins=True)
    st.dataframe(afford_breakdown, use_container_width=True)
    
    # Percentage breakdown
    afford_pct_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Affordability_Rating'], normalize='index') * 100
    afford_pct_breakdown = afford_pct_breakdown.round(1)
    st.subheader("� Percentage Breakdown by Program-Section")
    st.dataframe(afford_pct_breakdown, use_container_width=True)
    
    # Affordability sentiment summary
    st.subheader("📈 Affordability Sentiment by Program-Section")
    afford_sentiment = []
    for ps in sorted(filtered_df_copy['Program_Section'].unique()):
        ps_df = filtered_df_copy[filtered_df_copy['Program_Section'] == ps]
        total = len(ps_df)
        expensive_count = len(ps_df[ps_df['Affordability_Rating'].isin(['Expensive', 'Very Expensive'])])
        affordable_count = len(ps_df[ps_df['Affordability_Rating'].isin(['Affordable', 'Very Affordable'])])
        expensive_pct = (expensive_count / total * 100) if total > 0 else 0
        affordable_pct = (affordable_count / total * 100) if total > 0 else 0
        
        afford_sentiment.append({
            'Program-Section': ps,
            'Total Students': total,
            'Find Expensive': f"{expensive_count} ({expensive_pct:.1f}%)",
            'Find Affordable': f"{affordable_count} ({affordable_pct:.1f}%)",
            'Sentiment': '😟 Concerned' if expensive_pct > 50 else '😐 Mixed' if expensive_pct > 25 else '😊 Positive'
        })
    
    afford_sentiment_df = pd.DataFrame(afford_sentiment)
    st.dataframe(afford_sentiment_df, use_container_width=True)
    
    # Visual breakdown
    afford_by_program_section = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Affordability_Rating'], normalize='index') * 100
    afford_by_program_section = afford_by_program_section.reset_index().melt(id_vars='Program_Section', var_name='Rating', value_name='Percentage')
    fig = px.bar(afford_by_program_section, x='Program_Section', y='Percentage', color='Rating', barmode='stack',
                 title='Affordability Rating by Program-Section (%)')
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 Detailed Voter List by Affordability and Program-Section"):
        for rating in affordability_counts['Rating']:
            st.write(f"**{rating}:**")
            for ps in sorted(filtered_df_copy['Program_Section'].unique()):
                ps_voters = filtered_df_copy[(filtered_df_copy['Affordability_Rating'] == rating) & (filtered_df_copy['Program_Section'] == ps)][['Name', 'Email']]
                if not ps_voters.empty:
                    st.write(f"  *{ps}:* {len(ps_voters)} voters")
                    st.dataframe(ps_voters, use_container_width=True)

with tab4:
    st.header("🏆 Most Important Tour Factors")
    st.markdown("**Question:** If given a choice, which factor is MOST important in your tour decision?")
    
    factor_counts = filtered_df['Most_Important_Factor'].value_counts().reset_index()
    factor_counts.columns = ['Factor', 'Count']
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(factor_counts, x='Count', y='Factor', orientation='h', title='Most Important Factors')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(factor_counts, values='Count', names='Factor', title='Factor Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Program-Section Breakdown
    st.subheader("📊 Breakdown by Program-Section")
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['Program_Section'] = filtered_df_copy['Program'] + ' ' + filtered_df_copy['Section']
    
    # Create crosstab for detailed breakdown
    factors_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Most_Important_Factor'], margins=True)
    st.dataframe(factors_breakdown, use_container_width=True)
    
    # Percentage breakdown
    factors_pct_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Most_Important_Factor'], normalize='index') * 100
    factors_pct_breakdown = factors_pct_breakdown.round(1)
    st.subheader("� Percentage Breakdown by Program-Section")
    st.dataframe(factors_pct_breakdown, use_container_width=True)
    
    # Priority analysis by program-section
    st.subheader("🎯 Priority Analysis by Program-Section")
    priority_analysis = []
    for ps in sorted(filtered_df_copy['Program_Section'].unique()):
        ps_df = filtered_df_copy[filtered_df_copy['Program_Section'] == ps]
        if len(ps_df) > 0:
            top_factor = ps_df['Most_Important_Factor'].value_counts().index[0]
            top_factor_count = ps_df['Most_Important_Factor'].value_counts().iloc[0]
            top_factor_pct = (top_factor_count / len(ps_df)) * 100
            
            priority_analysis.append({
                'Program-Section': ps,
                'Total Students': len(ps_df),
                'Top Priority': top_factor,
                'Top Priority Count': f"{top_factor_count} ({top_factor_pct:.1f}%)"
            })
    
    priority_df = pd.DataFrame(priority_analysis)
    st.dataframe(priority_df, use_container_width=True)
    
    # Visual breakdown
    factors_by_program_section = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Most_Important_Factor'], normalize='index') * 100
    factors_by_program_section = factors_by_program_section.reset_index().melt(id_vars='Program_Section', var_name='Factor', value_name='Percentage')
    fig = px.bar(factors_by_program_section, x='Program_Section', y='Percentage', color='Factor', barmode='stack',
                 title='Important Factors by Program-Section (%)')
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 Detailed Voter List by Factor and Program-Section"):
        for factor in factor_counts['Factor']:
            st.write(f"**{factor}:**")
            for ps in sorted(filtered_df_copy['Program_Section'].unique()):
                ps_voters = filtered_df_copy[(filtered_df_copy['Most_Important_Factor'] == factor) & (filtered_df_copy['Program_Section'] == ps)][['Name', 'Email']]
                if not ps_voters.empty:
                    st.write(f"  *{ps}:* {len(ps_voters)} voters")
                    st.dataframe(ps_voters, use_container_width=True)

with tab5:
    st.header("🗳️ Voting Power Perception")
    st.markdown("**Question:** Do you feel your previous vote for the tour location/package mattered, given that we are now re-evaluating the options?")
    
    voting_counts = filtered_df['Previous_Vote_Mattered'].value_counts().reset_index()
    voting_counts.columns = ['Response', 'Count']
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(voting_counts, x='Response', y='Count', title='Vote Mattered Perception')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(voting_counts, values='Count', names='Response', title='Vote Perception Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Program-Section Breakdown
    st.subheader("📊 Breakdown by Program-Section")
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['Program_Section'] = filtered_df_copy['Program'] + ' ' + filtered_df_copy['Section']
    
    # Create crosstab for detailed breakdown
    voting_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Previous_Vote_Mattered'], margins=True)
    st.dataframe(voting_breakdown, use_container_width=True)
    
    # Percentage breakdown
    voting_pct_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Previous_Vote_Mattered'], normalize='index') * 100
    voting_pct_breakdown = voting_pct_breakdown.round(1)
    st.subheader("� Percentage Breakdown by Program-Section")
    st.dataframe(voting_pct_breakdown, use_container_width=True)
    
    # Voting confidence analysis
    st.subheader("📈 Voting Confidence by Program-Section")
    voting_confidence = []
    for ps in sorted(filtered_df_copy['Program_Section'].unique()):
        ps_df = filtered_df_copy[filtered_df_copy['Program_Section'] == ps]
        total = len(ps_df)
        dissatisfied = len(ps_df[ps_df['Previous_Vote_Mattered'].isin(['Disagree', 'Strongly Disagree'])])
        satisfied = len(ps_df[ps_df['Previous_Vote_Mattered'].isin(['Agree', 'Strongly Agree'])])
        dissatisfied_pct = (dissatisfied / total * 100) if total > 0 else 0
        satisfied_pct = (satisfied / total * 100) if total > 0 else 0
        
        confidence = '😟 Low Confidence' if dissatisfied_pct > 50 else '😐 Mixed Confidence' if dissatisfied_pct > 25 else '😊 High Confidence'
        
        voting_confidence.append({
            'Program-Section': ps,
            'Total Students': total,
            'Dissatisfied': f"{dissatisfied} ({dissatisfied_pct:.1f}%)",
            'Satisfied': f"{satisfied} ({satisfied_pct:.1f}%)",
            'Confidence Level': confidence
        })
    
    voting_confidence_df = pd.DataFrame(voting_confidence)
    st.dataframe(voting_confidence_df, use_container_width=True)
    
    # Visual breakdown
    voting_by_program_section = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Previous_Vote_Mattered'], normalize='index') * 100
    voting_by_program_section = voting_by_program_section.reset_index().melt(id_vars='Program_Section', var_name='Response', value_name='Percentage')
    fig = px.bar(voting_by_program_section, x='Program_Section', y='Percentage', color='Response', barmode='stack',
                 title='Voting Power Perception by Program-Section (%)')
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 Detailed Voter List by Voting Perception"):
        for response in voting_counts['Response']:
            st.write(f"**{response}:**")
            voters = filtered_df[filtered_df['Previous_Vote_Mattered'] == response][['Name', 'Email', 'Program', 'Section']]
            st.dataframe(voters, use_container_width=True)

with tab6:
    st.header("⚖️ Non-Student Factors Perception")
    st.markdown("**Question:** Is the re-evaluation of the location/package happening now because it was affected on factors other than student preference?")
    
    factors_counts = filtered_df['Non_Student_Factors'].value_counts().reset_index()
    factors_counts.columns = ['Response', 'Count']
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(factors_counts, x='Response', y='Count', title='Non-Student Factors Influence')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(factors_counts, values='Count', names='Response', title='Perception Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Program-Section Breakdown
    st.subheader("📊 Breakdown by Program-Section")
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['Program_Section'] = filtered_df_copy['Program'] + ' ' + filtered_df_copy['Section']
    
    # Create crosstab for detailed breakdown
    nsfactors_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Non_Student_Factors'], margins=True)
    st.dataframe(nsfactors_breakdown, use_container_width=True)
    
    # Percentage breakdown
    nsfactors_pct_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Non_Student_Factors'], normalize='index') * 100
    nsfactors_pct_breakdown = nsfactors_pct_breakdown.round(1)
    st.subheader("� Percentage Breakdown by Program-Section")
    st.dataframe(nsfactors_pct_breakdown, use_container_width=True)
    
    # Trust analysis
    st.subheader("📈 Process Trust by Program-Section")
    trust_analysis = []
    for ps in sorted(filtered_df_copy['Program_Section'].unique()):
        ps_df = filtered_df_copy[filtered_df_copy['Program_Section'] == ps]
        total = len(ps_df)
        believes_external = len(ps_df[ps_df['Non_Student_Factors'] == 'Yes'])
        believes_external_pct = (believes_external / total * 100) if total > 0 else 0
        
        trust_level = '😟 Low Trust' if believes_external_pct > 60 else '😐 Mixed Trust' if believes_external_pct > 30 else '😊 High Trust'
        
        trust_analysis.append({
            'Program-Section': ps,
            'Total Students': total,
            'Believes External Influence': f"{believes_external} ({believes_external_pct:.1f}%)",
            'Trust Level': trust_level
        })
    
    trust_analysis_df = pd.DataFrame(trust_analysis)
    st.dataframe(trust_analysis_df, use_container_width=True)
    
    # Visual breakdown
    nsfactors_by_program_section = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Non_Student_Factors'], normalize='index') * 100
    nsfactors_by_program_section = nsfactors_by_program_section.reset_index().melt(id_vars='Program_Section', var_name='Response', value_name='Percentage')
    fig = px.bar(nsfactors_by_program_section, x='Program_Section', y='Percentage', color='Response', barmode='stack',
                 title='Non-Student Factors Perception by Program-Section (%)')
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 Detailed Voter List by Non-Student Factors Perception"):
        for response in factors_counts['Response']:
            st.write(f"**{response}:**")
            voters = filtered_df[filtered_df['Non_Student_Factors'] == response][['Name', 'Email', 'Program', 'Section']]
            st.dataframe(voters, use_container_width=True)

with tab7:
    st.header("🚦 Manila Willingness Analysis")
    st.markdown("**Question:** If Manila remains the final destination, are you still willing and able to join the educational tour?")
    
    willingness_counts = filtered_df['Manila_Willingness'].value_counts().reset_index()
    willingness_counts.columns = ['Response', 'Count']
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(willingness_counts, values='Count', names='Response', title='Manila Willingness Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(willingness_counts, x='Response', y='Count', title='Manila Willingness Count')
        st.plotly_chart(fig, use_container_width=True)
    
    # Program-Section Breakdown
    st.subheader("📊 Breakdown by Program-Section")
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['Program_Section'] = filtered_df_copy['Program'] + ' ' + filtered_df_copy['Section']
    
    # Create crosstab for detailed breakdown
    will_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Manila_Willingness'], margins=True)
    st.dataframe(will_breakdown, use_container_width=True)
    
    # Percentage breakdown
    will_pct_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Manila_Willingness'], normalize='index') * 100
    will_pct_breakdown = will_pct_breakdown.round(1)
    st.subheader("� Percentage Breakdown by Program-Section")
    st.dataframe(will_pct_breakdown, use_container_width=True)
    
    # Willingness sentiment analysis
    st.subheader("📈 Willingness Sentiment by Program-Section")
    willingness_sentiment = []
    for ps in sorted(filtered_df_copy['Program_Section'].unique()):
        ps_df = filtered_df_copy[filtered_df_copy['Program_Section'] == ps]
        total = len(ps_df)
        definitely_yes = len(ps_df[ps_df['Manila_Willingness'] == 'Yes, definitely'])
        probably_yes = len(ps_df[ps_df['Manila_Willingness'] == 'Yes, probably'])
        positive_response = definitely_yes + probably_yes
        positive_pct = (positive_response / total * 100) if total > 0 else 0
        definitely_pct = (definitely_yes / total * 100) if total > 0 else 0
        
        sentiment = '😊 Very Positive' if definitely_pct > 60 else '🙂 Positive' if positive_pct > 60 else '😐 Mixed' if positive_pct > 40 else '😟 Concerning'
        
        willingness_sentiment.append({
            'Program-Section': ps,
            'Total Students': total,
            'Definitely Willing': f"{definitely_yes} ({definitely_pct:.1f}%)",
            'Total Positive': f"{positive_response} ({positive_pct:.1f}%)",
            'Sentiment': sentiment
        })
    
    willingness_sentiment_df = pd.DataFrame(willingness_sentiment)
    st.dataframe(willingness_sentiment_df, use_container_width=True)
    
    # Visual breakdown
    will_by_program_section = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Manila_Willingness'], normalize='index') * 100
    will_by_program_section = will_by_program_section.reset_index().melt(id_vars='Program_Section', var_name='Response', value_name='Percentage')
    fig = px.bar(will_by_program_section, x='Program_Section', y='Percentage', color='Response', barmode='stack',
                 title='Manila Willingness by Program-Section (%)')
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 Detailed Voter List by Willingness and Program-Section"):
        for response in willingness_counts['Response']:
            st.write(f"**{response}:**")
            for ps in sorted(filtered_df_copy['Program_Section'].unique()):
                ps_voters = filtered_df_copy[(filtered_df_copy['Manila_Willingness'] == response) & (filtered_df_copy['Program_Section'] == ps)][['Name', 'Email']]
                if not ps_voters.empty:
                    st.write(f"  *{ps}:* {len(ps_voters)} voters")
                    st.dataframe(ps_voters, use_container_width=True)

with tab8:
    st.header("🛑 Barriers Analysis")
    st.markdown("**Question:** What are the biggest barriers for you to join the tour as currently planned? (Check all that apply)")
    
    barrier_counts = {}
    for barrier in unique_barriers:
        col_name = f'Barrier_{barrier.replace("/", "_").replace(" ", "_")}'
        if col_name in filtered_df.columns:
            barrier_counts[barrier] = filtered_df[col_name].sum()
    
    barrier_df = pd.DataFrame(list(barrier_counts.items()), columns=['Barrier', 'Count'])
    barrier_df = barrier_df.sort_values('Count', ascending=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(barrier_df, x='Count', y='Barrier', orientation='h', title='Barriers to Joining')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(barrier_df, values='Count', names='Barrier', title='Barrier Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Program-Section Breakdown
    st.subheader("📊 Barriers by Program-Section")
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['Program_Section'] = filtered_df_copy['Program'] + ' ' + filtered_df_copy['Section']
    
    # Create barrier analysis by program-section
    barrier_analysis = []
    for ps in sorted(filtered_df_copy['Program_Section'].unique()):
        ps_df = filtered_df_copy[filtered_df_copy['Program_Section'] == ps]
        total_students = len(ps_df)
        
        # Count barriers for this program-section
        barrier_counts_ps = {}
        for barrier in unique_barriers:
            col_name = f'Barrier_{barrier.replace("/", "_").replace(" ", "_")}'
            if col_name in filtered_df.columns:
                count = ps_df[col_name].sum()
                if count > 0:
                    barrier_counts_ps[barrier] = count
        
        # Get top barrier
        if barrier_counts_ps:
            top_barrier = max(barrier_counts_ps, key=barrier_counts_ps.get)
            top_barrier_count = barrier_counts_ps[top_barrier]
            top_barrier_pct = (top_barrier_count / total_students) * 100
        else:
            top_barrier = "None reported"
            top_barrier_count = 0
            top_barrier_pct = 0
        
        barrier_analysis.append({
            'Program-Section': ps,
            'Total Students': total_students,
            'Top Barrier': top_barrier,
            'Top Barrier Count': f"{top_barrier_count} ({top_barrier_pct:.1f}%)",
            'Total Barriers Reported': sum(barrier_counts_ps.values())
        })
    
    barrier_analysis_df = pd.DataFrame(barrier_analysis)
    st.dataframe(barrier_analysis_df, use_container_width=True)
    
    # Detailed barrier breakdown table
    st.subheader("📈 Detailed Barrier Breakdown by Program-Section")
    barrier_by_program_section = {}
    for ps in sorted(filtered_df_copy['Program_Section'].unique()):
        ps_df = filtered_df_copy[filtered_df_copy['Program_Section'] == ps]
        barrier_by_program_section[ps] = {}
        for barrier in unique_barriers:
            col_name = f'Barrier_{barrier.replace("/", "_").replace(" ", "_")}'
            if col_name in filtered_df.columns:
                barrier_by_program_section[ps][barrier] = ps_df[col_name].sum()
    
    barrier_ps_df = pd.DataFrame(barrier_by_program_section).fillna(0).T
    st.dataframe(barrier_ps_df, use_container_width=True)
    
    # Visual breakdown
    barrier_ps_viz = barrier_ps_df.reset_index().melt(id_vars='index', var_name='Barrier', value_name='Count')
    barrier_ps_viz = barrier_ps_viz[barrier_ps_viz['Count'] > 0]
    if not barrier_ps_viz.empty:
        fig = px.bar(barrier_ps_viz, x='index', y='Count', color='Barrier', barmode='stack',
                     title='Barriers by Program-Section')
        fig.update_layout(xaxis_title='Program-Section', xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 Detailed Voter List by Barrier and Program-Section"):
        for barrier in barrier_df['Barrier']:
            st.write(f"**{barrier}:**")
            col_name = f'Barrier_{barrier.replace("/", "_").replace(" ", "_")}'
            for ps in sorted(filtered_df_copy['Program_Section'].unique()):
                ps_voters = filtered_df_copy[(filtered_df_copy[col_name] == 1) & (filtered_df_copy['Program_Section'] == ps)][['Name', 'Email']]
                if not ps_voters.empty:
                    st.write(f"  *{ps}:* {len(ps_voters)} voters")
                    st.dataframe(ps_voters, use_container_width=True)

with tab9:
    st.header("💬 Student Comments")
    st.markdown("**Question:** Do you have any additional comments or suggestions regarding the tour destination, package, or decision process?")
    
    comments_df = filtered_df[['Name', 'Program', 'Section', 'Additional_Comments']].copy()
    comments_df = comments_df[comments_df['Additional_Comments'].notna()]
    comments_df = comments_df[comments_df['Additional_Comments'].str.strip() != '']
    comments_df['Program_Section'] = comments_df['Program'] + ' ' + comments_df['Section']
    
    if len(comments_df) > 0:
        st.subheader(f"📝 All Comments ({len(comments_df)} total)")
        
        # Show summary by program-section
        comments_summary = comments_df.groupby('Program_Section').size().reset_index(name='Comment Count')
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Comments by Program-Section:**")
            st.dataframe(comments_summary, use_container_width=True)
        
        with col2:
            # Create word cloud if comments exist
            all_comments = ' '.join(comments_df['Additional_Comments'].astype(str))
            try:
                wordcloud = WordCloud(width=400, height=200, background_color='white').generate(all_comments)
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title('Word Cloud of Comments', fontsize=14)
                st.pyplot(fig)
            except:
                st.write("Word cloud could not be generated")
        
        st.subheader("📋 All Student Comments")
        
        # Group comments by program-section for better organization
        for ps in sorted(comments_df['Program_Section'].unique()):
            ps_comments = comments_df[comments_df['Program_Section'] == ps]
            if not ps_comments.empty:
                with st.expander(f"{ps} - {len(ps_comments)} comments"):
                    for idx, row in ps_comments.iterrows():
                        st.write(f"**{row['Name']}** ({row['Program_Section']}):")
                        st.write(f"_{row['Additional_Comments']}_")
                        st.write("---")
        
        # Show all comments in a searchable table
        st.subheader("🔍 Searchable Comments Table")
        st.dataframe(
            comments_df[['Name', 'Program_Section', 'Additional_Comments']], 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.write("No comments found in the filtered data.")

with tab10:
    st.header("📦 Package Preference Analysis")
    st.markdown("**Question:** Select the package you prefer:")
    
    package_counts = filtered_df['Preferred_Package'].value_counts().reset_index()
    package_counts.columns = ['Package', 'Count']
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(package_counts, values='Count', names='Package', title='Package Preference Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(package_counts, x='Package', y='Count', title='Package Preference Count')
        st.plotly_chart(fig, use_container_width=True)
    
    # Program-Section Breakdown
    st.subheader("📊 Breakdown by Program-Section")
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['Program_Section'] = filtered_df_copy['Program'] + ' ' + filtered_df_copy['Section']
    
    # Create crosstab for detailed breakdown
    package_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Preferred_Package'], margins=True)
    st.dataframe(package_breakdown, use_container_width=True)
    
    # Percentage breakdown
    package_pct_breakdown = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Preferred_Package'], normalize='index') * 100
    package_pct_breakdown = package_pct_breakdown.round(1)
    st.subheader("� Percentage Breakdown by Program-Section")
    st.dataframe(package_pct_breakdown, use_container_width=True)
    
    # Package preference analysis
    st.subheader("📈 Package Preference Analysis by Program-Section")
    package_analysis = []
    for ps in sorted(filtered_df_copy['Program_Section'].unique()):
        ps_df = filtered_df_copy[filtered_df_copy['Program_Section'] == ps]
        if len(ps_df) > 0:
            top_package = ps_df['Preferred_Package'].value_counts().index[0]
            top_package_count = ps_df['Preferred_Package'].value_counts().iloc[0]
            top_package_pct = (top_package_count / len(ps_df)) * 100
            
            package_analysis.append({
                'Program-Section': ps,
                'Total Students': len(ps_df),
                'Top Choice': top_package,
                'Top Choice Count': f"{top_package_count} ({top_package_pct:.1f}%)"
            })
    
    package_analysis_df = pd.DataFrame(package_analysis)
    st.dataframe(package_analysis_df, use_container_width=True)
    
    # Visual breakdown
    package_by_program_section = pd.crosstab(filtered_df_copy['Program_Section'], filtered_df_copy['Preferred_Package'], normalize='index') * 100
    package_by_program_section = package_by_program_section.reset_index().melt(id_vars='Program_Section', var_name='Package', value_name='Percentage')
    fig = px.bar(package_by_program_section, x='Program_Section', y='Percentage', color='Package', barmode='stack',
                 title='Package Preference by Program-Section (%)')
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 Detailed Voter List by Package and Program-Section"):
        for pkg in package_counts['Package']:
            st.write(f"**{pkg}:**")
            for ps in sorted(filtered_df_copy['Program_Section'].unique()):
                ps_voters = filtered_df_copy[(filtered_df_copy['Preferred_Package'] == pkg) & (filtered_df_copy['Program_Section'] == ps)][['Name', 'Email']]
                if not ps_voters.empty:
                    st.write(f"  *{ps}:* {len(ps_voters)} voters")
                    st.dataframe(ps_voters, use_container_width=True)

with tab11:
    st.header("� Comprehensive Sentiment Analysis")
    
    # Overall sentiment metrics
    col1, col2, col3 = st.columns(3)
    
    expensive_students = len(filtered_df[filtered_df['Affordability_Rating'].isin(['Expensive', 'Very Expensive'])])
    willing_students = len(filtered_df[filtered_df['Manila_Willingness'] == 'Yes, definitely'])
    dissatisfied_vote = len(filtered_df[filtered_df['Previous_Vote_Mattered'].isin(['Disagree', 'Strongly Disagree'])])
    
    financial_sentiment = (100 - expensive_students/len(filtered_df)*100) if len(filtered_df) > 0 else 0
    participation_sentiment = willing_students/len(filtered_df)*100 if len(filtered_df) > 0 else 0
    process_sentiment = (100 - dissatisfied_vote/len(filtered_df)*100) if len(filtered_df) > 0 else 0
    overall_sentiment = (financial_sentiment + participation_sentiment + process_sentiment) / 3
    
    with col1:
        st.metric("Financial Sentiment", f"{financial_sentiment:.1f}/100", 
                 help="Higher score = More students find tour affordable")
    with col2:
        st.metric("Participation Willingness", f"{participation_sentiment:.1f}/100",
                 help="Percentage of students definitely willing to join Manila tour")
    with col3:
        st.metric("Process Trust", f"{process_sentiment:.1f}/100",
                 help="Higher score = Students feel their votes mattered")
    
    # Overall sentiment gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_sentiment,
        title={'text': "Overall Sentiment Score"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "darkblue"},
               'steps': [
                   {'range': [0, 33], 'color': "lightcoral"},
                   {'range': [33, 66], 'color': "lightyellow"},
                   {'range': [66, 100], 'color': "lightgreen"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 50}}))
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Program-Section Analysis
    st.subheader("📊 Detailed Sentiment Analysis by Program-Section")
    
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['Program_Section'] = filtered_df_copy['Program'] + ' ' + filtered_df_copy['Section']
    
    sentiment_analysis = []
    for ps in sorted(filtered_df_copy['Program_Section'].unique()):
        ps_df = filtered_df_copy[filtered_df_copy['Program_Section'] == ps]
        total = len(ps_df)
        
        # Financial sentiment
        expensive_count = len(ps_df[ps_df['Affordability_Rating'].isin(['Expensive', 'Very Expensive'])])
        financial_score = ((total - expensive_count) / total * 100) if total > 0 else 0
        
        # Participation sentiment
        willing_count = len(ps_df[ps_df['Manila_Willingness'] == 'Yes, definitely'])
        participation_score = (willing_count / total * 100) if total > 0 else 0
        
        # Process sentiment
        dissatisfied_count = len(ps_df[ps_df['Previous_Vote_Mattered'].isin(['Disagree', 'Strongly Disagree'])])
        process_score = ((total - dissatisfied_count) / total * 100) if total > 0 else 0
        
        # Overall sentiment
        overall_score = (financial_score + participation_score + process_score) / 3
        
        # Sentiment classification
        if overall_score >= 70:
            sentiment_status = "😊 Very Positive"
        elif overall_score >= 50:
            sentiment_status = "🙂 Positive"
        elif overall_score >= 30:
            sentiment_status = "😐 Mixed"
        else:
            sentiment_status = "😟 Concerning"
        
        sentiment_analysis.append({
            'Program-Section': ps,
            'Total Students': total,
            'Financial Score': f"{financial_score:.1f}%",
            'Participation Score': f"{participation_score:.1f}%",
            'Process Score': f"{process_score:.1f}%",
            'Overall Score': f"{overall_score:.1f}%",
            'Sentiment Status': sentiment_status
        })
    
    sentiment_df = pd.DataFrame(sentiment_analysis)
    st.dataframe(sentiment_df, use_container_width=True)
    
    # Visual representation of sentiment scores
    st.subheader("📈 Sentiment Scores Visualization")
    
    # Prepare data for visualization
    sentiment_viz_data = []
    for _, row in sentiment_df.iterrows():
        sentiment_viz_data.append({
            'Program-Section': row['Program-Section'],
            'Metric': 'Financial',
            'Score': float(row['Financial Score'].replace('%', ''))
        })
        sentiment_viz_data.append({
            'Program-Section': row['Program-Section'],
            'Metric': 'Participation',
            'Score': float(row['Participation Score'].replace('%', ''))
        })
        sentiment_viz_data.append({
            'Program-Section': row['Program-Section'],
            'Metric': 'Process',
            'Score': float(row['Process Score'].replace('%', ''))
        })
    
    sentiment_viz_df = pd.DataFrame(sentiment_viz_data)
    
    fig = px.bar(sentiment_viz_df, x='Program-Section', y='Score', color='Metric',
                 title='Sentiment Scores by Program-Section', barmode='group')
    fig.update_layout(xaxis_tickangle=45, yaxis_title='Score (%)', yaxis_range=[0, 100])
    fig.add_hline(y=50, line_dash="dash", line_color="gray", 
                  annotation_text="Neutral Line (50%)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.subheader("🔍 Key Insights")
    
    # Find sections with concerning sentiment
    concerning_sections = sentiment_df[sentiment_df['Overall Score'].str.replace('%', '').astype(float) < 40]
    if not concerning_sections.empty:
        st.warning("⚠️ **Sections with Concerning Sentiment (< 40%):**")
        for _, row in concerning_sections.iterrows():
            st.write(f"- **{row['Program-Section']}**: {row['Overall Score']} overall sentiment")
    
    # Find sections with very positive sentiment
    positive_sections = sentiment_df[sentiment_df['Overall Score'].str.replace('%', '').astype(float) >= 70]
    if not positive_sections.empty:
        st.success("✅ **Sections with Very Positive Sentiment (≥ 70%):**")
        for _, row in positive_sections.iterrows():
            st.write(f"- **{row['Program-Section']}**: {row['Overall Score']} overall sentiment")
    
    # Summary statistics
    st.subheader("📊 Summary Statistics")
    col1, col2, col3 = st.columns(3)
    
    overall_scores = sentiment_df['Overall Score'].str.replace('%', '').astype(float)
    
    with col1:
        st.metric("Highest Sentiment Score", f"{overall_scores.max():.1f}%")
    with col2:
        st.metric("Lowest Sentiment Score", f"{overall_scores.min():.1f}%")
    with col3:
        st.metric("Average Sentiment Score", f"{overall_scores.mean():.1f}%")

with tab12:
    st.header("📋 Comprehensive Program-Section Summary")
    st.markdown("*This tab provides a complete analysis overview for each program-section with all survey responses and visualizations.*")
    
    # Create Program-Section selector
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['Program_Section'] = filtered_df_copy['Program'] + ' ' + filtered_df_copy['Section']
    
    selected_ps = st.selectbox(
        "Select Program-Section for Detailed Analysis:",
        options=sorted(filtered_df_copy['Program_Section'].unique()),
        help="Choose a program-section to see detailed analysis"
    )
    
    if selected_ps:
        ps_df = filtered_df_copy[filtered_df_copy['Program_Section'] == selected_ps]
        
        st.markdown(f"## 📊 Complete Analysis for **{selected_ps}**")
        st.markdown(f"**Total Students:** {len(ps_df)}")
        
        # Show students in this program-section
        st.subheader("👥 Students in this Program-Section")
        students_list = ps_df[['Name', 'Email']].reset_index(drop=True)
        students_list.index += 1  # Start numbering from 1
        st.dataframe(students_list, use_container_width=True)
        
        st.markdown("---")
        
        # 1. LOCATION PREFERENCE ANALYSIS
        st.subheader("🗺️ Q1: Where do you personally want to have the educational tour?")
        
        location_data = ps_df['Tour_Location_Preference'].value_counts()
        if not location_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(values=location_data.values, names=location_data.index, 
                           title=f'Location Preferences - {selected_ps}')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                location_summary = []
                for loc, count in location_data.items():
                    pct = (count / len(ps_df)) * 100
                    location_summary.append({
                        'Location': loc,
                        'Count': count,
                        'Percentage': f"{pct:.1f}%"
                    })
                st.write("**Breakdown:**")
                st.dataframe(pd.DataFrame(location_summary), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 2. AFFORDABILITY ANALYSIS
        st.subheader("💸 Q2: How would you rate the affordability of the Manila package (PHP 22,000)?")
        
        afford_data = ps_df['Affordability_Rating'].value_counts()
        if not afford_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(x=afford_data.index, y=afford_data.values, 
                           title=f'Affordability Ratings - {selected_ps}')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                expensive_count = len(ps_df[ps_df['Affordability_Rating'].isin(['Expensive', 'Very Expensive'])])
                affordable_count = len(ps_df[ps_df['Affordability_Rating'].isin(['Affordable', 'Very Affordable'])])
                expensive_pct = (expensive_count / len(ps_df)) * 100
                affordable_pct = (affordable_count / len(ps_df)) * 100
                
                st.metric("Find it Expensive", f"{expensive_count} ({expensive_pct:.1f}%)")
                st.metric("Find it Affordable", f"{affordable_count} ({affordable_pct:.1f}%)")
                
                sentiment = '😟 Concerned' if expensive_pct > 50 else '😐 Mixed' if expensive_pct > 25 else '😊 Positive'
                st.write(f"**Affordability Sentiment:** {sentiment}")
        
        st.markdown("---")
        
        # 3. IMPORTANT FACTORS ANALYSIS
        st.subheader("🏆 Q3: Which factor is MOST important in your tour decision?")
        
        factors_data = ps_df['Most_Important_Factor'].value_counts()
        if not factors_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(y=factors_data.index, x=factors_data.values, orientation='h',
                           title=f'Most Important Factors - {selected_ps}')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("**Top Priority Analysis:**")
                top_factor = factors_data.index[0]
                top_count = factors_data.iloc[0]
                top_pct = (top_count / len(ps_df)) * 100
                
                st.metric("Top Priority", top_factor)
                st.metric("Students who chose this", f"{top_count} ({top_pct:.1f}%)")
        
        st.markdown("---")
        
        # 4. VOTING POWER ANALYSIS
        st.subheader("🗳️ Q4: Do you feel your previous vote for the tour location/package mattered?")
        
        voting_data = ps_df['Previous_Vote_Mattered'].value_counts()
        if not voting_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(values=voting_data.values, names=voting_data.index,
                           title=f'Voting Power Perception - {selected_ps}')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                dissatisfied = len(ps_df[ps_df['Previous_Vote_Mattered'].isin(['Disagree', 'Strongly Disagree'])])
                satisfied = len(ps_df[ps_df['Previous_Vote_Mattered'].isin(['Agree', 'Strongly Agree'])])
                dissatisfied_pct = (dissatisfied / len(ps_df)) * 100
                satisfied_pct = (satisfied / len(ps_df)) * 100
                
                st.metric("Dissatisfied with Vote Impact", f"{dissatisfied} ({dissatisfied_pct:.1f}%)")
                st.metric("Satisfied with Vote Impact", f"{satisfied} ({satisfied_pct:.1f}%)")
                
                confidence = '😟 Low Confidence' if dissatisfied_pct > 50 else '😐 Mixed Confidence' if dissatisfied_pct > 25 else '😊 High Confidence'
                st.write(f"**Voting Confidence:** {confidence}")
        
        st.markdown("---")
        
        # 5. NON-STUDENT FACTORS ANALYSIS
        st.subheader("⚖️ Q5: Is the re-evaluation affected by factors other than student preference?")
        
        nsfactors_data = ps_df['Non_Student_Factors'].value_counts()
        if not nsfactors_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(x=nsfactors_data.index, y=nsfactors_data.values,
                           title=f'Non-Student Factors Perception - {selected_ps}')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                believes_external = len(ps_df[ps_df['Non_Student_Factors'] == 'Yes'])
                believes_external_pct = (believes_external / len(ps_df)) * 100
                
                st.metric("Believe External Influence", f"{believes_external} ({believes_external_pct:.1f}%)")
                
                trust_level = '😟 Low Trust' if believes_external_pct > 60 else '😐 Mixed Trust' if believes_external_pct > 30 else '😊 High Trust'
                st.write(f"**Process Trust Level:** {trust_level}")
        
        st.markdown("---")
        
        # 6. MANILA WILLINGNESS ANALYSIS
        st.subheader("🚦 Q6: If Manila remains the final destination, are you still willing to join?")
        
        willingness_data = ps_df['Manila_Willingness'].value_counts()
        if not willingness_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(values=willingness_data.values, names=willingness_data.index,
                           title=f'Manila Willingness - {selected_ps}')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                definitely_yes = len(ps_df[ps_df['Manila_Willingness'] == 'Yes, definitely'])
                probably_yes = len(ps_df[ps_df['Manila_Willingness'] == 'Yes, probably'])
                positive_response = definitely_yes + probably_yes
                positive_pct = (positive_response / len(ps_df)) * 100
                definitely_pct = (definitely_yes / len(ps_df)) * 100
                
                st.metric("Definitely Willing", f"{definitely_yes} ({definitely_pct:.1f}%)")
                st.metric("Total Positive Response", f"{positive_response} ({positive_pct:.1f}%)")
                
                sentiment = '😊 Very Positive' if definitely_pct > 60 else '🙂 Positive' if positive_pct > 60 else '😐 Mixed' if positive_pct > 40 else '😟 Concerning'
                st.write(f"**Willingness Sentiment:** {sentiment}")
        
        st.markdown("---")
        
        # 7. BARRIERS ANALYSIS
        st.subheader("🛑 Q7: What are the biggest barriers for you to join the tour?")
        
        # Count barriers for this program-section
        barrier_counts_ps = {}
        for barrier in unique_barriers:
            col_name = f'Barrier_{barrier.replace("/", "_").replace(" ", "_")}'
            if col_name in ps_df.columns:
                count = ps_df[col_name].sum()
                if count > 0:
                    barrier_counts_ps[barrier] = count
        
        if barrier_counts_ps:
            col1, col2 = st.columns(2)
            with col1:
                barrier_df_ps = pd.DataFrame(list(barrier_counts_ps.items()), columns=['Barrier', 'Count'])
                barrier_df_ps = barrier_df_ps.sort_values('Count', ascending=True)
                fig = px.bar(barrier_df_ps, x='Count', y='Barrier', orientation='h',
                           title=f'Barriers to Joining - {selected_ps}')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                top_barrier = max(barrier_counts_ps, key=barrier_counts_ps.get)
                top_barrier_count = barrier_counts_ps[top_barrier]
                top_barrier_pct = (top_barrier_count / len(ps_df)) * 100
                
                st.metric("Top Barrier", top_barrier)
                st.metric("Students affected", f"{top_barrier_count} ({top_barrier_pct:.1f}%)")
                st.metric("Total Barriers Reported", sum(barrier_counts_ps.values()))
        else:
            st.info("No barriers reported by students in this section.")
        
        st.markdown("---")
        
        # 8. COMMENTS ANALYSIS
        st.subheader("💬 Q8: Additional comments or suggestions")
        
        ps_comments = ps_df[ps_df['Additional_Comments'].notna() & (ps_df['Additional_Comments'].str.strip() != '')]
        
        if not ps_comments.empty:
            st.write(f"**{len(ps_comments)} students provided comments:**")
            
            # Show word cloud if comments exist
            try:
                all_comments_ps = ' '.join(ps_comments['Additional_Comments'].astype(str))
                wordcloud = WordCloud(width=600, height=300, background_color='white').generate(all_comments_ps)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title(f'Word Cloud of Comments - {selected_ps}', fontsize=14)
                st.pyplot(fig)
            except:
                st.write("Word cloud could not be generated")
            
            # Show all comments
            for idx, row in ps_comments.iterrows():
                st.write(f"**{row['Name']}:** _{row['Additional_Comments']}_")
                st.write("---")
        else:
            st.info("No comments provided by students in this section.")
        
        st.markdown("---")
        
        # 9. PACKAGE PREFERENCE ANALYSIS
        st.subheader("📦 Q9: Select the package you prefer")
        
        package_data = ps_df['Preferred_Package'].value_counts()
        if not package_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(values=package_data.values, names=package_data.index,
                           title=f'Package Preferences - {selected_ps}')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                top_package = package_data.index[0]
                top_package_count = package_data.iloc[0]
                top_package_pct = (top_package_count / len(ps_df)) * 100
                
                st.metric("Preferred Package", top_package)
                st.metric("Students who chose this", f"{top_package_count} ({top_package_pct:.1f}%)")
                
                package_summary = []
                for pkg, count in package_data.items():
                    pct = (count / len(ps_df)) * 100
                    package_summary.append({
                        'Package': pkg,
                        'Count': count,
                        'Percentage': f"{pct:.1f}%"
                    })
                st.write("**Breakdown:**")
                st.dataframe(pd.DataFrame(package_summary), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 10. OVERALL SENTIMENT ANALYSIS
        st.subheader("📈 Overall Sentiment Analysis")
        
        # Calculate sentiment scores
        expensive_count = len(ps_df[ps_df['Affordability_Rating'].isin(['Expensive', 'Very Expensive'])])
        financial_score = ((len(ps_df) - expensive_count) / len(ps_df) * 100) if len(ps_df) > 0 else 0
        
        willing_count = len(ps_df[ps_df['Manila_Willingness'] == 'Yes, definitely'])
        participation_score = (willing_count / len(ps_df) * 100) if len(ps_df) > 0 else 0
        
        dissatisfied_count = len(ps_df[ps_df['Previous_Vote_Mattered'].isin(['Disagree', 'Strongly Disagree'])])
        process_score = ((len(ps_df) - dissatisfied_count) / len(ps_df) * 100) if len(ps_df) > 0 else 0
        
        overall_score = (financial_score + participation_score + process_score) / 3
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Financial Sentiment", f"{financial_score:.1f}%")
        with col2:
            st.metric("Participation Willingness", f"{participation_score:.1f}%")
        with col3:
            st.metric("Process Trust", f"{process_score:.1f}%")
        with col4:
            st.metric("Overall Sentiment", f"{overall_score:.1f}%")
        
        # Sentiment classification
        if overall_score >= 70:
            sentiment_status = "😊 Very Positive"
            st.success(f"**Overall Assessment:** {sentiment_status}")
        elif overall_score >= 50:
            sentiment_status = "🙂 Positive"
            st.success(f"**Overall Assessment:** {sentiment_status}")
        elif overall_score >= 30:
            sentiment_status = "😐 Mixed"
            st.warning(f"**Overall Assessment:** {sentiment_status}")
        else:
            sentiment_status = "😟 Concerning"
            st.error(f"**Overall Assessment:** {sentiment_status}")
        
        # Summary insights
        st.subheader("🔍 Key Insights & Recommendations")
        
        insights = []
        
        # Location insight
        if not location_data.empty:
            top_location = location_data.index[0]
            location_pct = (location_data.iloc[0] / len(ps_df)) * 100
            insights.append(f"**Location Preference:** {location_pct:.1f}% prefer {top_location}")
        
        # Affordability insight
        if expensive_count > len(ps_df) * 0.5:
            insights.append(f"**⚠️ Financial Concern:** {(expensive_count/len(ps_df)*100):.1f}% find the tour expensive - consider financial assistance")
        
        # Participation insight
        if willing_count < len(ps_df) * 0.6:
            insights.append(f"**⚠️ Participation Risk:** Only {(willing_count/len(ps_df)*100):.1f}% are definitely willing to join Manila tour")
        
        # Voting confidence insight
        if dissatisfied_count > len(ps_df) * 0.4:
            insights.append(f"**⚠️ Trust Issue:** {(dissatisfied_count/len(ps_df)*100):.1f}% feel their votes didn't matter")
        
        # Barriers insight
        if barrier_counts_ps:
            top_barrier = max(barrier_counts_ps, key=barrier_counts_ps.get)
            insights.append(f"**Main Barrier:** {top_barrier} affects {barrier_counts_ps[top_barrier]} students")
        
        for insight in insights:
            st.write(f"• {insight}")
        
        if not insights:
            st.write("• Overall positive sentiment with no major concerns identified")
    
    # Section comparison overview
    st.markdown("---")
    st.subheader("📊 Quick Comparison Across All Program-Sections")
    
    comparison_data = []
    for ps in sorted(filtered_df_copy['Program_Section'].unique()):
        ps_data = filtered_df_copy[filtered_df_copy['Program_Section'] == ps]
        
        # Calculate key metrics
        total = len(ps_data)
        expensive_pct = len(ps_data[ps_data['Affordability_Rating'].isin(['Expensive', 'Very Expensive'])]) / total * 100 if total > 0 else 0
        willing_pct = len(ps_data[ps_data['Manila_Willingness'] == 'Yes, definitely']) / total * 100 if total > 0 else 0
        
        # Top preferences
        top_location = ps_data['Tour_Location_Preference'].mode().iloc[0] if not ps_data['Tour_Location_Preference'].empty else "N/A"
        top_package = ps_data['Preferred_Package'].mode().iloc[0] if not ps_data['Preferred_Package'].empty else "N/A"
        
        comparison_data.append({
            'Program-Section': ps,
            'Total Students': total,
            'Find Expensive (%)': f"{expensive_pct:.1f}%",
            'Definitely Willing (%)': f"{willing_pct:.1f}%",
            'Preferred Location': top_location,
            'Preferred Package': top_package
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)