
from openai import OpenAI
import os
import time
from def_tools import *
import json

# Import API keys
import a_env_vars

os.environ["OPENAI_API_KEY"] = a_env_vars.OPENAI_API_KEY

# Create assistant

client = OpenAI()
assist_name ='Market.00'

# --------------------------------------------------------------------
def initiate_assistant():

    system_msg = '''
    - You are an expert stock data market analyst
    - You can fetch reliable data through the funcions available
    - Always use get_todays_date function when you need to know today's date or a relative date
    '''
    # check for existing assistants
    my_assistants = client.beta.assistants.list(
        order="desc",
        limit="5",
        )

    result = fetch_assistant_by_name(my_assistants.data, assist_name)
    if result is None:
        my_assistant = client.beta.assistants.create(
            instructions=system_msg,
            name=assist_name,
            tools=ftools,
            model="gpt-3.5-turbo",
        )
    else:
        my_assistant = client.beta.assistants.retrieve(result.id)

    return my_assistant

# -------------------------------------------
def fetch_assistant_by_name(data, assist_name):
    for assistant in data:
        if assistant.name == assist_name:
            return assistant
    return None


# ---------------------------------------------------------------------
def open_thread():
    new_thread = client.beta.threads.create()
    return new_thread   

# --------------------------------------------------------------------
# add user message to current thread
def add_query(thread, query):
    thread_message = client.beta.threads.messages.create(
    thread.id,
    role="user",
    content=query,
    )
    return thread_message

# ---------------------------------------------------------------------------------------
def runOpenai(thread_id,assistant_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id= assistant_id,
    )
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run.status == 'completed':
            break
        elif run.status == 'requires_action':
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = callTools(tool_calls)
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )    
        elif run.status == 'failed':                
            print(run.last_error)
        time.sleep(.5) 
    return run

# ------------------------------------------------------------------------------------------------------------
def callTools(tool_calls):
    tool_outputs = []
    for t in tool_calls:
        functionName = t.function.name
        attributes = json.loads(t.function.arguments)
        args = list(attributes.values()) 
        # Get the real function from its name
        function = globals().get(functionName)
        try:
            if args:
                functionResponse = function(*args)
            else:
                functionResponse = function()
        except Exception as e:
            functionResponse = { "status" : 'Error in function call ' + functionName + '(' + t.function.arguments + ')', "error": str(e) }        
        tool_outputs.append({ "tool_call_id": t.id , "output": json.dumps(functionResponse) })
    return tool_outputs


# ---------------- main logic -----------------------------------------
my_assistant = initiate_assistant()

thread = open_thread()

while True:
    query = input("Enter your query: ")
    message = add_query(thread, query)

    run = runOpenai(thread.id, my_assistant.id)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    response = messages.data[0].content[0].text.value

    print(response)
