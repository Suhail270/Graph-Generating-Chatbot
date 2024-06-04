import os
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from apikey import apikey

# Set OpenAI API Key
os.environ['OPENAI_API_KEY'] = apikey

# Initialize the language model and the database chain
llm = OpenAI (temperature=0)
db_chain = SQLDatabaseChain (llm=llm, database=db, verbose=True)

sample_texts = [
    "what is the salary of the employee with id 10084",
    "is the employee with id 10084 married?",
    "what's the name of employee with id 10088?",
    "what is alagbe,trina's salary?",
    "what is trina alagbe's data of birth?",
    "who are my most productive employee's"
]

text = """\in the database dates are stored in the following format: "<lastname>,<firstname>" with no whitespace. the sql query should ignore all whitespace. """
text += sample_texts[5]
for i in range(len(text)):
    if i >= len(text):
        break
    if text[i] == ',':
        if text[i + 1] == ' ':
            text = text[:i + 1] + text[i + 1 + 1:]

resp = db_chain.run(text)
print(resp)

# # Query the number of rows in the tracks table
# resp= db_chain.run("How many rows is in the tracks table of this db?")
# print (resp)
# # Describe the employees table
# resp = db_chain.run("Describe the employees table")
# print (resp)
# # Query the top 3 customers in terms of total invoice payments
# resp= db_chain.run("What are the top 3 customers (names, lastname, invoice id, Total) who are paying Total invoices?")
# print (resp)