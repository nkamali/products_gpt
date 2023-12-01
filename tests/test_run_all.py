import asyncio

from app.products import get_products_and_category, find_category_and_product_v2
from .utils import eval_response_with_ideal, msg_ideal_pairs_set

score_accum = 0
for i, pair in enumerate(msg_ideal_pairs_set):
    print(f"example {i}")

    customer_msg = pair['customer_msg']
    ideal = pair['ideal_answer']

    # print("Customer message",customer_msg)
    # print("ideal:",ideal)
    products_and_category = get_products_and_category()
    response = asyncio.run(find_category_and_product_v2(customer_msg, products_and_category))

    # print("products_by_category",products_by_category)
    score = eval_response_with_ideal(response, ideal, debug=False)
    print(f"{i}: {score}")
    score_accum += score

n_examples = len(msg_ideal_pairs_set)
fraction_correct = score_accum / n_examples
print(f"Fraction correct out of {n_examples}: {fraction_correct}")
