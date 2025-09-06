# 🎓 Educational Tour Survey Dashboard

A comprehensive Streamlit web application for analyzing educational tour survey responses with interactive visualizations and detailed insights.

## 📋 Overview

This dashboard provides a complete analysis of student survey responses regarding an educational tour. It includes location preferences, affordability analysis, voting power perception, barriers to participation, and comprehensive sentiment analysis broken down by program and section.

## ✨ Features

### 📊 Interactive Visualizations
- **Location Preferences**: Pie and bar charts showing tour destination preferences
- **Affordability Analysis**: Rating distributions for the PHP 22,000 Manila package
- **Important Factors**: Analysis of key decision-making factors
- **Voting Power**: Perception of previous vote influence
- **Non-Student Factors**: Analysis of external influences on decision-making
- **Manila Willingness**: Participation sentiment if Manila remains the destination
- **Barriers Analysis**: Identification of obstacles to tour participation
- **Comments Analysis**: Word clouds and individual student comments
- **Package Preferences**: Analysis of preferred tour packages

### 🎯 Advanced Analytics
- **Program-Section Breakdowns**: Detailed analysis for each academic section
- **Sentiment Scoring**: Financial, participation, and process trust metrics
- **Comparative Analysis**: Side-by-side comparison across all sections
- **Student Lists**: Complete roster with names and contact information
- **Automated Insights**: AI-generated recommendations and risk identification

### 🔧 Technical Features
- **Real-time Filtering**: Filter by program and section
- **Responsive Design**: Works on desktop and mobile devices
- **Interactive Charts**: Plotly-powered visualizations
- **Data Export**: CSV data export capabilities
- **Search Functionality**: Find specific students or responses

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project files**
   ```bash
   cd your-project-directory
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Place your data file**
   - Ensure `109.csv` is in the same directory as the dashboard
   - The CSV should contain the survey responses with the expected column structure

## 📖 Usage

### Running the Dashboard

1. **Start the Streamlit application**
   ```bash
   streamlit run educT_dashboard.py
   ```

2. **Access the dashboard**
   - Open your web browser to `***`
   - The dashboard will automatically load with your data

### Navigation Guide

#### 📊 Overview Tab
- General survey statistics and key metrics
- Program and section distribution
- Links to detailed analysis tabs

#### 🗺️ Location Preference Tab
- **Question**: Where do you personally want to have the educational tour?
- Interactive charts showing destination preferences
- Program-section breakdowns with percentages

#### 💸 Affordability Tab
- **Question**: How would you rate the affordability of the Manila package (PHP 22,000)?
- Cost perception analysis
- Financial sentiment indicators

#### 🏆 Important Factors Tab
- **Question**: Which factor is MOST important in your tour decision?
- Priority analysis by program-section
- Decision-making factor rankings

#### 🗳️ Voting Power Tab
- **Question**: Do you feel your previous vote mattered?
- Trust and confidence analysis
- Voting influence perception

#### ⚖️ Non-Student Factors Tab
- **Question**: Was re-evaluation affected by non-student factors?
- External influence analysis
- Process transparency assessment

#### 🚦 Manila Willingness Tab
- **Question**: Are you willing to join if Manila remains the destination?
- Participation sentiment analysis
- Alternative destination preferences

#### 🛑 Barriers Tab
- **Question**: What are the biggest barriers to joining?
- Obstacle identification and analysis
- Student concern prioritization

#### 💬 Comments Tab
- **Question**: Additional comments or suggestions?
- Word cloud visualization
- Individual student feedback with names

#### 📦 Preferred Package Tab
- **Question**: Select the package you prefer
- Package preference analysis
- Cost-benefit analysis

#### 📈 Sentiment Analysis Tab
- Comprehensive sentiment scoring
- Risk identification and recommendations
- Program-section comparison matrix

#### 📋 Program-Section Summary Tab
- **Interactive Analysis**: Select any program-section for detailed review
- **Complete Student Roster**: Names and contact information
- **All Survey Questions**: Consolidated analysis per section
- **Automated Insights**: AI-generated recommendations

## 📁 Project Structure

```
EDUCTOUR/
├── educT_dashboard.py      # Main Streamlit application
├── requirements.txt        # Python dependencies
├── 109.csv                # Survey data file
└── README.md              # This documentation
```

## 📊 Data Format

The dashboard expects a CSV file (`109.csv`) with the following columns:
- `Timestamp`
- `Name`
- `Email`
- `Program`
- `Section`
- `Tour_Location_Preference`
- `Affordability_Rating`
- `Most_Important_Factor`
- `Previous_Vote_Mattered`
- `Non_Student_Factors`
- `Manila_Willingness`
- `Barriers`
- `Additional_Comments`
- `Preferred_Package`

## 🔧 Customization

### Adding New Analysis
1. Add new columns to your CSV data
2. Update the data loading function in `educT_dashboard.py`
3. Create new tab content following the existing pattern
4. Add corresponding analysis in the Program-Section Summary tab

### Styling Modifications
- The dashboard uses default Streamlit themes
- Custom CSS can be added using `st.markdown()` with `<style>` tags
- Color schemes can be modified in the Plotly chart configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🆘 Support

If you encounter any issues:
1. Check that all dependencies are installed correctly
2. Ensure your CSV file matches the expected format
3. Verify that the file paths are correct
4. Check the browser console for any JavaScript errors

## 🎯 Use Cases

- **Educational Institutions**: Analyze student preferences for field trips
- **Event Planning**: Understand participant sentiment and barriers
- **Survey Analysis**: Comprehensive survey response visualization
- **Decision Making**: Data-driven insights for tour planning
- **Student Engagement**: Identify concerns and improve participation

## 📈 Future Enhancements

- [ ] Export functionality for individual reports
- [ ] Advanced filtering options
- [ ] Real-time data updates
- [ ] Mobile app version
- [ ] Multi-language support
- [ ] Integration with survey platforms

---

**Built with ❤️ using Streamlit, Pandas, Plotly, and Python**</content>
<parameter name="filePath">d:\User\Downloads\DiaTrack\DFU_Healing_ML\DiaTrack_DFU_Detection_Models\DS_Class\EDUCTOUR\README.md
