import json

msg_ideal_pairs_set = [

    # eg 0
    {'customer_msg': """Which TV can I buy if I'm on a budget?""",
     'ideal_answer': {
         'Televisions and Home Theater Systems': {'CineView 4K TV', 'SoundMax Home Theater', 'CineView 8K TV',
                                                  'SoundMax Soundbar', 'CineView OLED TV'}}
     },

    # eg 1
    {'customer_msg': """I need a charger for my smartphone""",
     'ideal_answer': {
         'Smartphones and Accessories': {'MobiTech PowerCase', 'MobiTech Wireless Charger', 'SmartX EarBuds'}}
     },
    # eg 2
    {'customer_msg': f"""What computers do you have?""",
     'ideal_answer': {
         'Computers and Laptops': {'TechPro Ultrabook', 'BlueWave Gaming Laptop', 'PowerLite Convertible',
                                   'TechPro Desktop', 'BlueWave Chromebook'}
     }
     },

    # eg 3
    {'customer_msg': f"""tell me about the smartx pro phone and \
    the fotosnap camera, the dslr one.\
    Also, what TVs do you have?""",
     'ideal_answer': {
         'Smartphones and Accessories': {'SmartX ProPhone'},
         'Cameras and Camcorders': {'FotoSnap DSLR Camera'},
         'Televisions and Home Theater Systems': {'CineView 4K TV', 'SoundMax Home Theater', 'CineView 8K TV',
                                                  'SoundMax Soundbar', 'CineView OLED TV'}
     }
     },

    # eg 4
    {'customer_msg': """tell me about the CineView TV, the 8K one, Gamesphere console, the X one.
I'm on a budget, what computers do you have?""",
     'ideal_answer': {
         'Televisions and Home Theater Systems': {'CineView 8K TV'},
         'Gaming Consoles and Accessories': {'GameSphere X'},
         'Computers and Laptops': {'TechPro Ultrabook', 'BlueWave Gaming Laptop', 'PowerLite Convertible',
                                   'TechPro Desktop', 'BlueWave Chromebook'}
     }
     },

    # eg 5
    {'customer_msg': f"""What smartphones do you have?""",
     'ideal_answer': {
         'Smartphones and Accessories': {'SmartX ProPhone', 'MobiTech PowerCase', 'SmartX MiniPhone',
                                         'MobiTech Wireless Charger', 'SmartX EarBuds'}
     }
     },
    # eg 6
    {'customer_msg': f"""I'm on a budget.  Can you recommend some smartphones to me?""",
     'ideal_answer': {
         'Smartphones and Accessories': {'SmartX EarBuds', 'SmartX MiniPhone', 'MobiTech PowerCase', 'SmartX ProPhone',
                                         'MobiTech Wireless Charger'}}
     },

    # eg 7 # this will output a subset of the ideal answer
    {'customer_msg': f"""What Gaming consoles would be good for my friend who is into racing games?""",
     'ideal_answer': {
         'Gaming Consoles and Accessories': {'GameSphere X', 'ProGamer Controller', 'GameSphere Y',
                                             'ProGamer Racing Wheel', 'GameSphere VR Headset'}}
     },
    # eg 8
    {'customer_msg': f"""What could be a good present for my videographer friend?""",
     'ideal_answer': {
         'Cameras and Camcorders': {'FotoSnap DSLR Camera', 'ActionCam 4K', 'FotoSnap Mirrorless Camera',
                                    'ZoomMaster Camcorder', 'FotoSnap Instant Camera'}}
     },

    # eg 9
    {'customer_msg': f"""I would like a hot tub time machine.""",
     'ideal_answer': []
     }

]

def eval_response_with_ideal(response,
                             ideal,
                             debug=False):
    """Evaluate test cases by comparing to the ideal answers"""
    if debug:
        print("response")
        print(response)

    # json.loads() expects double quotes, not single quotes
    json_like_str = response.replace("'", '"')

    # parse into a list of dictionaries
    l_of_d = json.loads(json_like_str)

    # special case when response is empty list
    if l_of_d == [] and ideal == []:
        return 1

    # otherwise, response is empty
    # or ideal should be empty, there's a mismatch
    elif l_of_d == [] or ideal == []:
        return 0

    correct = 0

    if debug:
        print("l_of_d is")
        print(l_of_d)
    for d in l_of_d:

        cat = d.get('category')
        prod_l = d.get('products')
        if cat and prod_l:
            # convert list to set for comparison
            prod_set = set(prod_l)
            # get ideal set of products
            ideal_cat = ideal.get(cat)
            if ideal_cat:
                prod_set_ideal = set(ideal.get(cat))
            else:
                if debug:
                    print(f"did not find category {cat} in ideal")
                    print(f"ideal: {ideal}")
                continue

            if debug:
                print("prod_set\n", prod_set)
                print()
                print("prod_set_ideal\n", prod_set_ideal)

            if prod_set == prod_set_ideal:
                if debug:
                    print("correct")
                correct += 1
            else:
                print("incorrect")
                print(f"prod_set: {prod_set}")
                print(f"prod_set_ideal: {prod_set_ideal}")
                if prod_set <= prod_set_ideal:
                    print("response is a subset of the ideal answer")
                elif prod_set >= prod_set_ideal:
                    print("response is a superset of the ideal answer")

    # count correct over total number of items in list
    pc_correct = correct / len(l_of_d)

    return pc_correct