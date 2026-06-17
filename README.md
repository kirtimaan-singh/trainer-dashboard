# 📅 Trainer Calendar Dashboard

A comprehensive Streamlit-based dashboard for tracking trainer activities, hours, and progress toward training targets.

## ✨ Features

### 📊 Overview
- **KPI Metrics**: Total activities, trainers, hours, average duration, activity types
- **Progress Tracking**: Visual cards showing trainer progress toward 160-hour targets
- **Color-coded Status**: Green (Completed), Orange (On Track), Red (Behind)
- **Progress Bars**: Visual indicators for completion percentage

### 📈 Visualizations
- **Stacked Bar Chart**: Completed vs. Remaining hours by trainer
- **Pie Chart**: Hours breakdown by activity type
- **Distribution Chart**: Activity count by trainer and type
- **Utilization Rate**: Efficiency gauge for each trainer
- **Timeline View**: Gantt chart showing when trainers are active
- **Trend Analysis**: Daily hours trend over time

### 🔍 Filtering & Search
- Filter by trainer name
- Filter by activity type
- Filter by date range
- Search functionality in data table

### 📥 Export Options
- Download filtered data as CSV
- Export multi-sheet Excel reports (Activities + Summary)
- Timestamped file names

### 📊 Analytics
- Most active trainer
- Most common activity type
- Date range statistics
- Detailed activity data table

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kirtimaan-singh/trainer-dashboard.git
   cd trainer-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit pandas plotly openpyxl numpy
   ```

3. **Generate sample data (optional)**
   ```bash
   python generate_sample_data.py
   ```
   This creates `Enhanced Trainer Activity Log (2).xlsx` with sample data.

4. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

   The app will open in your browser at `http://localhost:8501`

## 📋 Data Format

The app expects an Excel file named `Enhanced Trainer Activity Log (2).xlsx` with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| Date | DateTime | Activity date |
| Trainer Name | String | Name of the trainer |
| Activity Type | String | Type of activity (e.g., Training, Mentoring) |
| Start Time | Time | Activity start time |
| End Time | Time | Activity end time |
| Duration (Hours) | Float | Duration in hours |

## 🎯 Usage

1. **Prepare your data**
   - Create an Excel file with the columns listed above
   - Name it `Enhanced Trainer Activity Log (2).xlsx`
   - Place it in the same directory as `app.py`

2. **Run the app**
   ```bash
   streamlit run app.py
   ```

3. **Use the filters**
   - Select trainers from the sidebar
   - Choose activity types
   - Set date range
   - Use search to find specific activities

4. **Export data**
   - Download filtered data as CSV
   - Export Excel report with multiple sheets

## 🔧 Configuration

You can customize the target hours by modifying the `TARGET_HOURS` variable in `app.py`:

```python
TARGET_HOURS = 160  # Change this value as needed
```

## 📦 Project Structure

```
trainer-dashboard/
├── app.py                                  # Main Streamlit application
├── generate_sample_data.py                 # Sample data generator
├── Enhanced Trainer Activity Log (2).xlsx  # Data file (generated or provided)
└── README.md                               # This file
```

## 🛠️ Built With

- **Streamlit** - Web app framework
- **Pandas** - Data manipulation
- **Plotly** - Interactive visualizations
- **OpenPyXL** - Excel file handling
- **NumPy** - Numerical computing

## 📊 Sample Dashboard Views

### Overview Section
- Total activities count
- Total trainers count
- Total training hours
- Average activity duration
- Activity type count

### Trainer Progress Cards
- Individual trainer performance
- Completed vs. remaining hours
- Progress bars
- Status indicators

### Analytics Charts
- Stacked bar charts
- Pie charts
- Distribution charts
- Trend lines

## 🐛 Troubleshooting

### "Excel file not found" error
- Make sure `Enhanced Trainer Activity Log (2).xlsx` is in the same directory as `app.py`
- Run `python generate_sample_data.py` to create sample data

### Port already in use
- Run on a different port: `streamlit run app.py --server.port 8502`

### Missing dependencies
- Install all requirements: `pip install streamlit pandas plotly openpyxl numpy`

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

**kirtimaan-singh**

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest enhancements
- Submit pull requests

## 💡 Future Enhancements

- [ ] Database integration instead of Excel
- [ ] User authentication
- [ ] Role-based access control
- [ ] Email notifications
- [ ] Schedule exports
- [ ] Custom report generation
- [ ] Performance benchmarking
- [ ] Historical data comparison

---

**Happy tracking! 🎯**
