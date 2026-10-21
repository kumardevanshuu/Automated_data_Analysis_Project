# Automated Data Analysis with LangChain

**🔗 Live app:** https://automateddataanalysisproject-nhufqg5iugqvywruk5bd84.streamlit.app

Ask questions about your spreadsheet in plain English. The app uses an LLM to write
pandas code for your question, runs it on your data, and shows you the answer along
with the matching rows from your file. No coding needed.

> **Try it in 30 seconds:** download the sample file
> [`data/International_Education_Costs.csv`](data/International_Education_Costs.csv),
> upload it to the live app, and ask one of the questions below.

<!-- Add a screenshot of the app here, e.g.: -->

![firstQuestion](/Users/devanshukumar/Desktop/firstQuestion.png)
![firstQuestion](/Users/devanshukumar/Desktop/FirstQuestion1.png)
![SecondQuestion](/Users/devanshukumar/Desktop/SecondQuestion.png)
![SecondQuestion](/Users/devanshukumar/Desktop/SecondQuestion1.png)
![SecondQuestion](/Users/devanshukumar/Desktop/SecondQuestion2.png)


## Example questions

For the sample dataset (907 programs across 71 countries):

- `Show all Master programs in the USA with tuition above 50000`
- `Which university has the highest tuition?`
- `What is the average tuition by country?`
- `List the cities in Japan`

## Features

- 📁 Upload **CSV, Excel (.xlsx) or Apple Numbers (.numbers)** files
- 💬 Ask questions in plain English
- ✅ Get the answer **and the matching rows from your file**, with a CSV download
- 🔍 See the exact pandas code the AI wrote, so the answer can be checked
- 🛡️ AI-written code is checked before it runs and executes on a copy of your data

## How it works

1. Your file is loaded into a pandas DataFrame.
2. Your question, the column types and the first 3 rows are sent to an LLM
   (`openai/gpt-oss-120b` on Groq) through LangChain.
3. The LLM replies with pandas code that stores the answer in `result` and the
   rows it used in `matched_rows`.
4. The code is checked (imports, file access, `eval` and `while` loops are blocked)
   and run on a copy of the data.
5. The app shows the result, the matching rows and the generated code.

## Tech stack

**Language:** Python
**Web app:** Streamlit
**LLM orchestration:** LangChain
**LLM:** Groq API (`openai/gpt-oss-120b`)
**Data:** pandas, NumPy, numbers-parser
**Hosting:** Streamlit Community Cloud

## Privacy and safety

- Your question, the column names and types, and the first 3 rows of your file are
  sent to Groq's API to generate the code. **Please don't upload sensitive data to the
  public demo.**
- The generated code is checked before it runs, but these checks reduce risk rather
  than provide a full sandbox.

## Run it locally

Requires Python 3.10 or newer and a free [Groq API key](https://console.groq.com).

```bash
git clone https://github.com/kumardevanshuu/Automated_data_Analysis_Project.git
cd Automated_data_Analysis_Project

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # Windows: copy .env.example .env
```

Open `.env` and set your key:

```
GROQ_API_KEY=your-groq-api-key
```

Start the app:

```bash
streamlit run app.py
```

To try it from the command line instead, run `python main.py`. It asks one example
question about the sample dataset.

## Project structure

```
.
├── app.py                 # Streamlit web app
├── main.py                # Command-line example
├── src/
│   ├── chain_runner.py    # Prompt, LLM call, code safety checks, code execution
│   ├── data_loader.py     # Loads CSV, Excel and Numbers files
│   ├── config.py          # Logging setup
│   └── utils.py           # Helper functions
├── data/
│   └── International_Education_Costs.csv   # Sample dataset
├── requirements.txt
└── .env.example
```

## Known limitations

- The first row of your file is used as the column names. If your file has no header
  row, add one first.
- Only the first sheet (Excel) or the first table of the first sheet (Numbers) is read.
- LLMs can make mistakes, so check the generated code for anything important.
- The free hosting plan puts the app to sleep when nobody is using it, so the first
  load can take a few seconds.

## Ideas for next steps

- Charts generated from questions
- Multi-sheet file support
- Conversation history