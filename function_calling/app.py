import sys
from defusedxml import ElementTree
from collections import defaultdict
import os
from typing import Any
import tools
import boto3
import json
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

def create_prompt(tools_string, user_input):
    prompt_template = f"""
    \n\nHuman:
        You are an expert summarizer AI assistant that has been equipped with the following function(s) to help you answer user question with information about a given conversation history. Your goal is to answer the user's question to the best of your ability, using the function(s) to gather more information if necessary to better answer the question. The result of a function call will be added to the conversation history as an observation. 
        In this environment you have access to a set of tools you can use to answer the user's question.
        
        You may call them like this. Only invoke one function at a time and wait for the results before invoking another function:
        <function_calls>
        <invoke>
        <tool_name>$TOOL_NAME</tool_name>
        <parameters>
        <$PARAMETER_NAME>$PARAMETER_VALUE</$PARAMETER_NAME>
        ...
        </parameters>
        </invoke>
        </function_calls>
        
        Here are the tools available:
        <tools>
        {tools_string}
        </tools>
        
        first find the appropriate instruction from the get_general_instruction_description, get_sentiment_instruction_description or get_summary_instruction_description before running other function.
        if the question is not about the sentiment or summary of the conversasion then use instruction provided by get_general_instruction_description.
        
        {user_input}
        
        \n\nAssistant:
        """
    return prompt_template
    
def add_tools():
    tools_string = ""
    for tool_spec in tools.list_of_tools_specs:
        tools_string += tool_spec
    return tools_string
    
    
def call_function(tool_name, parameters):
    func = getattr(tools, tool_name)
    output = func(**parameters)
    return output
    
def format_result(tool_name, output):
    return f"""
            <function_results>
            <result>
            <tool_name>{tool_name}</tool_name>
            <stdout>
            {output}
            </stdout>
            </result>
            </function_results>
            """
            
def etree_to_dict(t) -> dict[str, Any]:
    d = {t.tag: {}}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(("@" + k, v) for k, v in t.attrib.items())
    if t.text and t.text.strip():
        if children or t.attrib:
            d[t.tag]["#text"] = t.text
        else:
            d[t.tag] = t.text
    return d
    
def run_loop(prompt):
    print(prompt)
    # Start function calling loop
    while True:
    # initialize variables to make bedrock api call
        bedrock = boto3.client(service_name='bedrock-runtime', region_name="us-east-1")
        modelId = 'anthropic.claude-v2:1'
        body = json.dumps({"prompt": prompt,
        "stop_sequences":["\n\nHuman:", "</function_calls>"],
        "max_tokens_to_sample": 700,
        "temperature": 0})
        accept = 'application/json'
        contentType = 'application/json'
        # bedrock api call with prompt
        partial_completion = bedrock.invoke_model(
        body=body, 
        modelId=modelId, 
        accept=accept, 
        contentType=contentType
    )
   
        response_body = json.loads(partial_completion.get('body').read())


        partial_completion= response_body.get('completion')
        stop_reason=response_body.get('stop_reason')
        stop_seq = partial_completion.rstrip().endswith("</invoke>")
        
        # Get a completion from Claude

        # Append the completion to the end of the prommpt
        prompt += partial_completion
        if stop_reason == 'stop_sequence' and stop_seq:
            # If Claude made a function call
            print(partial_completion)
            start_index = partial_completion.find("<function_calls>")
            if start_index != -1:
                # Extract the XML Claude outputted (invoking the function)
                extracted_text = partial_completion[start_index+16:]

                # Parse the XML find the tool name and the parameters that we need to pass to the tool
                xml = ElementTree.fromstring(extracted_text)
                tool_name_element = xml.find("tool_name")
                if tool_name_element is None:
                    print("Unable to parse function call, invalid XML or missing 'tool_name' tag")
                    break
                tool_name_from_xml = tool_name_element.text.strip()
                parameters_xml = xml.find("parameters")
                if parameters_xml is None:
                    print("Unable to parse function call, invalid XML or missing 'parameters' tag")
                    break
                param_dict = etree_to_dict(parameters_xml)
                parameters = param_dict["parameters"]
                

                # Call the tool we defined in tools.py
                output = call_function(tool_name_from_xml, parameters)


                # Add the stop sequence back to the prompt
                prompt += "</function_calls>"
                print("</function_calls>")

                # Add the result from calling the tool back to the prompt
                function_result = format_result(tool_name_from_xml, output)
                print(function_result)
                prompt += function_result
        else:
            # If Claude did not make a function call
            # outputted answer
            print(partial_completion)
            break
        

#user_input = "Can you summarize the conversion with id t_bde29ce2-4153-4056-9eb7-f4ad710505fe?"
user_input = "what is the sentiment of the conversation with id t_bde29ce2-4153-4056-9eb7-f4ad710505fe?"
#user_input = "how many turns of conversation exists in conversation with id t_bde29ce2-4153-4056-9eb7-f4ad710505fe?"


tools_string = add_tools()
prompt_data = create_prompt(tools_string, user_input)

#print(prompt_data)
run_loop(prompt_data)
