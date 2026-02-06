# 📡 Grant Scanner — Abraji

**Automated Grant Opportunity Monitor for Investigative Journalism and Media**

An intelligent GitHub Actions workflow that automatically scans and reports funding opportunities for investigative journalism, media organizations, and related initiatives. Runs Monday through Friday at 9:00 AM BRT and delivers curated reports via email.

---

## 🎯 Overview

Grant Scanner leverages Google's Gemini AI to continuously monitor and analyze funding opportunities across multiple categories relevant to investigative journalism. The system automatically:

- 🔍 Searches for new grant opportunities daily
- 🤖 Analyzes and categorizes findings using AI
- 📧 Delivers formatted reports via email
- 📊 Archives reports for future reference

Built specifically for [Abraji](https://abraji.org.br/) (Brazilian Association of Investigative Journalism), but adaptable for any journalism organization or media initiative.

---

## ✨ Features

- **Automated Daily Scanning**: Runs Monday-Friday at 09:00 BRT (12:00 UTC)
- **AI-Powered Analysis**: Uses Google Gemini to identify and categorize opportunities
- **Comprehensive Coverage**: Monitors multiple funding categories:
  - Investigative journalism
  - Environmental journalism
  - Data journalism and AI tools
  - Press freedom and media development
  - Fact-checking and misinformation
  - Climate journalism and more
- **Email Delivery**: Automated reports sent to configured recipients
- **Report Archiving**: 90-day retention of all reports as GitHub artifacts
- **Manual Trigger**: On-demand execution for testing or immediate updates

---

## 🚀 Quick Start

### Prerequisites

- GitHub repository with Actions enabled
- Google Gemini API key ([get one here](https://makersuite.google.com/app/apikey))
- Gmail account with App Password ([setup guide](https://support.google.com/accounts/answer/185833))

### Installation

1. **Clone or fork this repository**
```bash
git clone https://github.com/reichaves/grant-scanner.git
cd grant-scanner
```

2. **Configure GitHub Secrets**

Go to your repository Settings → Secrets and Variables → Actions, and add:

- `GEMINI_API_KEY`: Your Google Gemini API key
- `GMAIL_APP_PASSWORD`: Gmail App Password for sending emails

3. **Customize the scanner** (optional)

Edit `grant_scanner.py` to:
- Change recipient email addresses
- Modify search categories
- Adjust report formatting
- Update search parameters

4. **Enable GitHub Actions**

The workflow will automatically run Monday-Friday at 9 AM BRT. You can also trigger it manually from the Actions tab.

---

## 📋 How It Works

### Workflow Schedule
```yaml
schedule:
  # 09:00 BRT = 12:00 UTC
  # Runs Monday through Friday only
  - cron: "0 12 * * 1-5"
```

### Execution Flow

1. **Setup** (Steps 1-3)
   - Checkout repository
   - Install Python 3.12
   - Install dependencies

2. **Scanning** (Step 4)
   - Load environment variables
   - Execute grant scanner
   - Generate markdown report

3. **Delivery & Archiving** (Step 5)
   - Send email report
   - Upload report artifact
   - Retain for 90 days

---

## 🛠️ Configuration

### Email Settings

Edit the following variables in `grant_scanner.py`:
```python
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAIL = "recipient@example.com"
```

### Search Categories

Modify the `CATEGORIES` list to focus on specific areas:
```python
CATEGORIES = [
    "investigative journalism grants",
    "environmental journalism funding",
    "data journalism and AI tools",
    # Add or remove categories as needed
]
```

### AI Model Configuration

Adjust Gemini parameters in `grant_scanner.py`:
```python
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config={
        "temperature": 0.7,
        "top_p": 0.95,
        # Modify as needed
    }
)
```

---

## 📊 Report Format

Reports are generated in Markdown format and include:

- **Header**: Date and report metadata
- **Executive Summary**: Key findings and highlights
- **Categorized Opportunities**: Organized by funding type
  - Grant name and organization
  - Application deadline
  - Funding amount
  - Eligibility requirements
  - Application link
- **Footer**: Disclaimer and contact information

Example report structure:
```markdown
# 📡 Relatório de Oportunidades de Financiamento
**Data**: 2026-02-06

## 🎯 Resumo Executivo
[AI-generated summary]

## 📚 Oportunidades por Categoria

### Jornalismo Investigativo
- **Grant Name** | Organization
  - Deadline: [date]
  - Amount: [funding range]
  - [Link]

[...]
```

---

## 🔒 Security Considerations

- **Never commit API keys** to the repository
- Use GitHub Secrets for all sensitive credentials
- Rotate Gmail App Passwords periodically
- Review and limit repository access permissions
- Monitor workflow execution logs for anomalies

---

## 🐛 Troubleshooting

### Workflow Not Running

- Check if Actions are enabled in repository settings
- Verify cron schedule matches your timezone expectations
- Review workflow execution logs in Actions tab

### Email Not Sending

- Verify `GMAIL_APP_PASSWORD` secret is correctly set
- Ensure 2-factor authentication is enabled on Gmail
- Check sender email is correct in code
- Review SMTP connection logs

### API Errors

- Confirm `GEMINI_API_KEY` is valid and active
- Check API quota limits
- Review error messages in workflow logs

### No Opportunities Found

- AI may not have found relevant results that day
- Try adjusting search categories or parameters
- Run manual trigger to test immediately

---

## 📈 Usage Examples

### Manual Trigger

1. Go to Actions tab in GitHub
2. Select "📡 Grant Scanner — Abraji"
3. Click "Run workflow"
4. Check email and artifacts

### View Past Reports

1. Go to Actions tab
2. Select a completed workflow run
3. Download artifact: `grant-report-{run_number}`

### Customize Search
```python
# Example: Focus on climate journalism
CATEGORIES = [
    "climate journalism grants 2026",
    "environmental reporting funding",
    "COP30 media grants"
]
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- **Abraji** - Brazilian Association of Investigative Journalism
- **Google Gemini** - AI-powered grant analysis
- **GitHub Actions** - Workflow automation

---

## 📞 Contact

**Project Maintainer**: Reinaldo Chaves  
**Organization**: [Abraji](https://abraji.org.br/)  
**Repository**: [github.com/reichaves/grant-scanner](https://github.com/reichaves/grant-scanner)

For questions or suggestions, please [open an issue](https://github.com/reichaves/grant-scanner/issues).

---

## 🗓️ Roadmap

- [ ] Add support for multiple languages
- [ ] Integrate with Slack notifications
- [ ] Implement grant deadline reminders
- [ ] Add historical trending analysis
- [ ] Create web dashboard for reports
- [ ] Support for custom RSS feeds

---

**Made with ❤️ for investigative journalism**
