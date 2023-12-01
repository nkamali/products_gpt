import asyncio
from app.utils import get_completion_from_messages, read_string_to_list, get_moderation_from_input
from app.products import generate_output_string, \
    find_category_and_product_v2, get_products_and_category


async def eval_with_rubric(test_set, assistant_answer):
    cust_msg = test_set['customer_msg']
    context = test_set['context']
    completion = assistant_answer

    system_message = """\
    You are an assistant that evaluates how well the customer service agent \
    answers a user question by looking at the context that the customer service \
    agent is using to generate its response. 
    """

    user_message = f"""\
You are evaluating a submitted answer to a question based on the context \
that the agent uses to answer the question.
Here is the data:
    [BEGIN DATA]
    ************
    [Question]: {cust_msg}
    ************
    [Context]: {context}
    ************
    [Submission]: {completion}
    ************
    [END DATA]

Compare the factual content of the submitted answer with the context. \
Ignore any differences in style, grammar, or punctuation.
Answer the following questions:
    - Is the Assistant response based only on the context provided? (Y or N)
    - Does the answer include information that is not provided in the context? (Y or N)
    - Is there any disagreement between the response and the context? (Y or N)
    - Count how many questions the user asked. (output a number)
    - For each question that the user asked, is there a corresponding answer to it?
      Question 1: (Y or N)
      Question 2: (Y or N)
      ...
      Question N: (Y or N)
    - Of the number of questions asked, how many of these questions were addressed by the answer? (output a number)
"""

    print("** In eval_with_rubric:")
    print("cust_msg: ", cust_msg)
    print("context: ", context)
    print("completion: ", completion)
    print("system_message: ", system_message)

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': user_message}
    ]

    response = await get_completion_from_messages(messages)
    return response


# System of chained prompts for processing the user query
def process_user_message(user_input, all_messages, debug=True):
    delimiter = "```"

    # Step 1: Check input to see if it flags the Moderation API or is a prompt injection
    # print("Step 1, user_input: ", user_input)
    # response = asyncio.run(get_moderation_from_input(user_input))
    # moderation_output = response.results[0]
    #
    # if moderation_output.flagged:
    #     print("Step 1: Input flagged by Moderation API.")
    #     return "Sorry, we cannot process this request."
    #
    # if debug: print("Step 1: Input passed moderation check.")

    products_and_category = get_products_and_category()
    category_and_product_response = asyncio.run(find_category_and_product_v2(user_input, products_and_category))
    print("Step 1, category_and_product_response: ", category_and_product_response)


    # print(print(category_and_product_response)
    # Step 2: Extract the list of products
    category_and_product_list = read_string_to_list(category_and_product_response)
    print("Step 2, category_and_product_list: ", category_and_product_list)
    # print(category_and_product_list)

    if not category_and_product_list:
        print(f"category_and_product_list was empty meaning that there were no products"
              " that matched the user's inquiry of: {user_input}")
        return None, all_messages

    if debug: print("Step 2: Extracted list of products.")

    # Step 3: If products are found, look them up
    product_information = generate_output_string(category_and_product_list)
    print("Step 3, product_information: ", product_information)

    if debug: print("Step 3: Looked up product information.")

    # Step 4: Answer the user question
    system_message = f"""
    You are a customer service assistant for a large electronic store. \
    Respond in a friendly and helpful tone, with concise answers. \
    The customer service query will be delimited with {delimiter} characters.
    Make sure to ask the user relevant follow-up questions only if questions are relevant to electronics.
    """
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}{user_input}{delimiter}"},
        {'role': 'assistant', 'content': f"Relevant product information:\n{product_information}"}
    ]

    final_response = asyncio.run(get_completion_from_messages(all_messages + messages))
    print("Step 4, final_response: ", final_response, " all_messages: ", all_messages, " messages: ", messages)

    cust_prod_info = {
        'customer_msg': user_input,
        'context': product_information
    }

    evaluation_output = asyncio.run(eval_with_rubric(cust_prod_info, final_response))
    print("Step 5, evaluation_output: ", evaluation_output)

    if debug: print("Step 6: Generated response to user question.")
    all_messages = all_messages + messages[1:]

    # Step 5: Put the answer through the Moderation API
    # response = asyncio.run(get_moderation_from_input(final_response))
    # print("Step 6, response: ", response)
    #
    # moderation_output = response.results[0]
    #
    # if moderation_output.flagged:
    #     if debug: print("Step 5: Response flagged by Moderation API.")
    #     return "Sorry, we cannot provide this information."
    #
    # if debug: print("Step 7: Response passed moderation check.")

    # Step 6: Ask the model if the response answers the initial user query well
    user_message = f"""
    Customer message: {delimiter}{user_input}{delimiter}
    Agent response: {delimiter}{final_response}{delimiter}

    Does the response sufficiently answer the question? Is the Agent response related to electronic products we sell?
    Expect a response of N if the question is unrelated to electronics.
    """

    few_shot_user_message_1 = f"""
    Customer message: {delimiter}Which brand and model of TVs costs over $2500?{delimiter}
    Agent response: {delimiter}The CineView CV-8K65 costs $2999.99 and costs over $2500.{delimiter}

    Does the response sufficiently answer the question? Is the Agent response related to electronic products we sell?
    Expect a response of N if the question is unrelated to electronics.
    """
    few_shot_assistant_1 = "Y"

    few_shot_user_message_2 = f"""
    Customer message: {delimiter}Do you like to play golf?{delimiter}
    Agent response: {delimiter}As an AI assistant, I don't have personal preferences or hobbies.{delimiter}

    Does the response sufficiently answer the question? Is the Agent response related to electronic products we sell?
    Expect a response of N if the question is unrelated to electronics.
    """
    few_shot_assistant_2 = "N"

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': few_shot_user_message_1},
        {'role': 'assistant', 'content': few_shot_assistant_1},
        {'role': 'user', 'content': few_shot_user_message_2},
        {'role': 'assistant', 'content': few_shot_assistant_2},
        {'role': 'user', 'content': user_message}
    ]
    evaluation_response = asyncio.run(get_completion_from_messages(messages))
    print("Step 8, evaluation_response: ", evaluation_response)

    if debug: print("Step 6: Model evaluated the response.")

    # Step 7: If yes, use this answer; if not, say that you will connect the user to a human
    if "Y" in evaluation_response:  # Using "in" instead of "==" to be safer for model output variation (e.g., "Y." or "Yes")
        if debug: print("Step 7: Model approved the response.")
        return final_response, all_messages
    else:
        if debug: print("Step 7: Model disapproved the response.")
        neg_str = """I'm unable to provide the information you're looking for. \
        I can only answer questions about electronics. Please ask your question again."""
        return neg_str, all_messages


# user_input = "tell me about the smartx pro phone and the fotosnap camera, the dslr one. Also what tell me about your tvs"
# response, _ = process_user_message(user_input, [])
# print(response)

def split_string_into_lines_generator(s, max_line_length=120):
    words = s.split()
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 > max_line_length:
            yield current_line
            current_line = word
        else:
            if current_line:
                current_line += " "
            current_line += word

    if current_line:
        yield current_line


def main():
    context = [ {'role':'system', 'content':"You are Service Assistant"} ]

    print(f"context: {context}")
    response_in_loop, context = process_user_message("give me list of your tvs that are under $1000", context)
    if response_in_loop:
        print("\nAssistant:\n")
        for line in split_string_into_lines_generator(response_in_loop):
            print(line, '\n')

    context.append({'role': 'assistant', 'content': response_in_loop})

    print(f"context: {context}")
    response_in_loop, context = process_user_message("do you play soccer?", context)
    if response_in_loop:
        print("\nAssistant:\n")
        for line in split_string_into_lines_generator(response_in_loop):
            print(line, '\n')

    # while True:
    #     user_input_in_loop = input("Enter your query (type 'exit' to quit): \n")
    #     print("what I heard: ", user_input_in_loop)
    #     if user_input_in_loop.lower() in ['exit', 'quit']:
    #         break
    #
    #     response_in_loop, context = process_user_message(user_input_in_loop, context)
    #     print("\nAssistant:\n")
    #     for line in split_string_into_lines_generator(response_in_loop):
    #         print(line, '\n')
    #
    #     context.append({'role': 'assistant', 'content': response_in_loop})
    #

if __name__ == "__main__":
    main()
