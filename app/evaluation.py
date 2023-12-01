import asyncio
from app.utils import get_completion_from_messages, read_string_to_list, get_moderation_from_input
from app.products import generate_output_string, \
    find_category_and_product_v2, get_products_and_category


class ModerationException(Exception):
    """Custom exception for moderation failures."""
    pass

def check_moderation(user_input, debug=True):
    try:
        print("Step 1, user_input: ", user_input)
        response = asyncio.run(get_moderation_from_input(user_input))
        moderation_output = response.results[0]

        if moderation_output.flagged:
            print("Step 1: Input flagged by Moderation API.")
            raise ModerationException("Input failed moderation.")

        if debug:
            print("Step 1: Input passed moderation check.")
    except Exception as e:
        # Handle other exceptions that might occur
        raise ModerationException(f"An error occurred during moderation: {e}")


# System of chained prompts for processing the user query
def process_user_message(user_input, all_messages, debug=True):
    delimiter = "```"

    try:
        check_moderation(user_input)
        print(f"Moderation passed for user input: {user_input}")
    except ModerationException as e:
        return f"Moderation failed: {e}"

    products_and_category = get_products_and_category()
    print("products_and_category: ", products_and_category)

    category_and_product_response = asyncio.run(find_category_and_product_v2(user_input, products_and_category))
    print("Step 1, category_and_product_response: ", category_and_product_response)

    # print(print(category_and_product_response)
    # Step 2: Extract the list of products
    category_and_product_list = read_string_to_list(category_and_product_response)
    print("Step 2, category_and_product_list: ", category_and_product_list)
    # print(category_and_product_list)

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

    if debug: print("Step 4: Generated response to user question.")
    all_messages = all_messages + messages[1:]

    # Step 5: Put the answer through the Moderation API
    try:
        check_moderation(final_response)
        print(f"Moderation passed for user input: {final_response}")
    except ModerationException as e:
        return f"Moderation failed: {e}"

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
    print("Step 6, evaluation_response: ", evaluation_response)

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


def print_response(response):
    for line in split_string_into_lines_generator(response):
        print(line, '\n')


def is_exit_command(user_input):
    return user_input.strip().lower() in ['exit', 'quit']


def main():
    context = [ {'role':'system', 'content':"You are Service Assistant"} ]

    print(f"context: {context}")
    response_in_loop, context = process_user_message("give me list of your tvs that are under $1000", context)
    print("\nAssistant:\n")
    for line in split_string_into_lines_generator(response_in_loop):
        print(line, '\n')

    # Notice: I purposely asked it a non electronics related question here below to see how it would handle it:
    # context.append({'role': 'assistant', 'content': response_in_loop})
    #
    # print(f"context: {context}")
    # response_in_loop, context = process_user_message("do you play soccer?", context)
    # print("\nAssistant:\n")
    # for line in split_string_into_lines_generator(response_in_loop):
    #     print(line, '\n')

    context.append({'role': 'assistant', 'content': response_in_loop})

    print(f"context: {context}")
    response_in_loop, context = process_user_message("give me a list of subwoofers between $110 and $300?", context)
    print("\nAssistant:\n")
    for line in split_string_into_lines_generator(response_in_loop):
        print(line, '\n')

    ########################################################
    # Feel free to try this loop instead and try to fix it. It wasn't working for me and call to OpenAI becamne hung.
    # context = [ {'role':'system', 'content':"You are Service Assistant"} ]
    #
    # while True:
    #     try:
    #         user_input = input("Enter your query (type 'exit' to quit): \n").strip()
    #
    #         if is_exit_command(user_input):
    #             break
    #         response_in_loop, context = process_user_message(user_input, context)
    #         print("\nAssistant:\n")
    #         for line in split_string_into_lines_generator(response_in_loop):
    #             print(line, '\n')
    #
    #         context.append({'role': 'assistant', 'content': response_in_loop})
    #     except Exception as e:
    #         print(f"An error occurred: {e}")

    ########################################################


if __name__ == "__main__":
    main()
