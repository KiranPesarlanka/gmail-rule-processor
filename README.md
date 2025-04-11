# gmail-rule-processor

Python utility to extract emails from Gmail using the Gmail API and process them based on user-defined rules.

### Setup Instructions
Follow the steps below to set up and run the application:

#### Step 1: Create a Virtual Environment
```
python3 -m venv venv
```
#### Step 2: Activate the Virtual Environment

On macOS/Linux:
```
source venv/bin/activate
```
On Windows:
```
venv\Scripts\activate
```
#### Step 3: Install Required Packages
```
pip install -r requirements.txt
```
#### Step 4: Enable Gmail API and Create Credentials
1. Visit the Google Cloud Console.
2. Enable the Gmail API.
3. Create OAuth 2.0 Client ID credentials.
4. Download the credentials.json file.
5. Place the downloaded credentials.json file inside the src directory.
More detailed instructions can be found in the Gmail API Python Quickstart Guide.

### Extracting Emails
Run the Email Extraction Script
```
cd src
python extract_emails.py
```
This will:
Open an OAuth screen for authorization.
Start extracting emails from your Gmail account.
Save the data into emails.db using SQLite for simplicity.

### Defining Rules
Create a Rules File
Rules are defined in JSON format.
Example rule file: rule1.json (available in the src directory).

### Processing Emails
Run the Rule Processor
```
python process_emails.py
```
This script:
Loads rules from the JSON file.
Applies them on the extracted emails.
Updates the entries in emails.db.
