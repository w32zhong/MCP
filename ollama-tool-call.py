from ollama import ChatResponse, chat

use_model = 'qwen3:8b'


def add_two_numbers(a: int, b: int) -> int:
  """
  Add two numbers

  Args:
    a (int): The first number
    b (int): The second number

  Returns:
    int: The sum of the two numbers
  """
  return int(a) + int(b)

messages = [{'role': 'user', 'content': 'What is three plus one?'}]
available_functions = {
  'add_two_numbers': add_two_numbers
}
response: ChatResponse = chat(
  use_model,
  messages=messages,
  tools=[add_two_numbers],
)

if response.message.tool_calls:
  for tool in response.message.tool_calls:
    if function_to_call := available_functions.get(tool.function.name):
      output = function_to_call(**tool.function.arguments)
      print('Function output:', output)
    else:
      print('Function', tool.function.name, 'not found')

if response.message.tool_calls:
  messages.append(response.message)
  messages.append({'role': 'tool', 'content': str(output), 'name': tool.function.name})
  final_response = chat(use_model, messages=messages)
  print('Final response:', final_response.message.content)
else:
  print('No tool calls returned from model')
