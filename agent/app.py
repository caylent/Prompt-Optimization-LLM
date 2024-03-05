import tools
import json


def lambda_handler(event, context):
    # Print the received event to the logs
    print("Received event: ")
    print(event)

    # Initialize response code to None
    response_code = None

    # Extract the action group, api path, and parameters from the prediction
    action = event["actionGroup"]
    api_path = event["apiPath"]
    inputText = event["inputText"]
    httpMethod = event["httpMethod"]



    # Check the api path to determine which tool function to call
    if api_path == "/get_summary_instruction":
        # Call the summary_gen_tool from the tools module 
        body = tools.summary_gen_tool()
        # Create a response body with the result
        response_code = 200
    elif api_path == "/get_sentiment_instruction":
        # Call the sentiment_gen_tool from the tools module
        body = tools.sentiment_gen_tool()
        # Create a response body with the result
        response_code = 200
    elif api_path == "/get_other_question_instruction":
        # Call the general_gen_tool from the tools module
        body = tools.other_question_gen_tool()
        # Create a response body with the result
        response_code = 200
    elif api_path == "/gen_conversation":
        parameters = event['parameters']
        for parameter in parameters:
            if parameter["name"] == "ConversationId":
                id_ = parameter["value"]
            if parameter["name"] == "question":
                question = parameter["value"]
            if parameter["name"] == "instruction":
                instruction = parameter["value"] 
        # Call the get_conversation_tool from the tools module with the query
        body = tools.get_conversation_tool(id_, question, instruction)
        # Create a response body with the result
        response_code = 200
    else:
        # If the api path is not recognized, return an error message
        body = {"{}::{} is not a valid api, try another one.".format(action, api_path)}
        response_code = 400
        
    response_body = {"application/json": {"body": json.dumps(body)}}

    # Print the response body to the logs
    print(f"Response body: {response_body}")

    # Create a dictionary containing the response details
    action_response = {
        "actionGroup": action,
        "apiPath": api_path,
        "httpMethod": httpMethod,
        "httpStatusCode": response_code,
        "responseBody": response_body,
    }

    # Return the list of responses as a dictionary
    api_response = {"messageVersion": "1.0", "response": action_response}

    return api_response
