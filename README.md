# D&D Damage Calculator Web App

A fully interactive web application for calculating D&D 5e damage probabilities built with **Streamlit**.

🔗 **[Live Demo](https://share.streamlit.io/yourusername/dnd-damage-calculator/main/app.py)**

## Features

✅ **Two Calculation Modes**
- Spell Damage (Saving Throw) - Full/half damage based on save success
- Attack Roll Damage - Hit chance, average damage, critical hits

✅ **Interactive Controls**
- Enemy ability scores (6 inputs)
- Advantage/disadvantage mechanics
- Homebrew crit rules (Normal vs Crunchy)
- Real-time calculation

✅ **Beautiful Visualizations**
- Probability distribution charts
- Mean and standard deviation display
- Statistics display (hit chance, avg damage)
- Dark mode theme

✅ **Fully Responsive**
- Mobile-friendly interface
- Works on desktop, tablet, phone

## Local Development

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Run the app:
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Deployment on Streamlit Cloud

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/dnd-damage-calculator.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"New app"**
3. Paste your GitHub repo URL
4. Select branch: `main`
5. Set main file path: `app.py`
6. Click **"Deploy"**

That's it! Your app will be live in seconds. 🚀

**Share your app URL:** `https://share.streamlit.io/yourusername/dnd-damage-calculator/main/app.py`

## Project Structure

```
dnd_streamlit_app/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .gitignore         # Git ignore rules
```

## D&D 5e Rules Implemented

- **Ability modifier**: (score - 10) // 2
- **Saving throws**: d20 + modifier vs DC, with half damage on success
- **Advantage/Disadvantage**: Applied to both saves and attacks
- **Attack rolls**: d20 + bonus vs AC, with nat 1 auto-miss and nat 20 auto-crit
- **Crits**: Normal (double dice) or Crunchy (add max roll)

## Why Streamlit?

- ✅ Instant deployment to Streamlit Cloud (free!)
- ✅ Zero frontend code needed
- ✅ Hot reload during development
- ✅ Beautiful UI out of the box
- ✅ Great for data apps and calculators

## License

MIT License

---

**Built with Streamlit** | D&D 5th Edition
