# LoL Data Analyzer

A League of Legends game analysis tool built with Streamlit for interactive data visualization and statistics.

## Features

- 📊 **Single Game Analysis**: Detailed analysis of individual matches
- 🌌 **Global Stats**: Multi-game comparison and player rankings
- 🦦 **Marmotte Flip**: Team performance analysis
- 👤 **Player Profile**: Comprehensive player statistics
- 🔍 **Player Search**: Quick search across all game data

## Deployment on Streamlit Community Cloud

This application is optimized for deployment on [Streamlit Community Cloud](https://streamlit.io/cloud).

### Quick Deploy

1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Set the main file path to: `streamlit_app.py`
6. Click "Deploy"

### File Structure

The application follows Streamlit Community Cloud requirements:

```
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── data/                    # Game data files (JSON)
├── models/                  # Data models and analyzers
├── views/streamlit/         # Streamlit pages and components
├── utils/                   # Utility functions
├── static/                  # Static assets
├── requirements.txt         # Python dependencies
├── streamlit_app.py        # Main entry point for Streamlit
└── README.md               # This file
```

### Local Development

To run locally:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Data Format

The application expects League of Legends game data in JSON format in the `data/` directory. Each file should contain the complete match data from the Riot Games API.

## Technology Stack

- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation and analysis
- **Matplotlib**: Additional plotting capabilities
- **NumPy**: Numerical computing

## Version

Current version: 1.0.0

## License

This project is for educational and personal use.
