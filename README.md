# Electronic Products Chatbot

## Table of Contents
- [Electronic Products Chatbot](#project-name)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Scripts](#running-the-scripts)
    - [Evaluation Module](#evaluation-module)
  - [Usage](#usage)
  - [Testing](#testing)
  - [Known Issues](#known-issues)
  - [License](#license)

## Description
These scripts act as a Chatbot which allows the user to ask any questions about fictitious electronic products.
The conversation is moderated and the AI for this Chatbot is trained to only answer electronic related questions.
These scripts use OpenAI's LLM and train its model on the user's questions, fictitious Product database and 
responses by the AI itself for subsequent user question. Here we train it on how to respond for various inputs. 

## Prerequisites
Before you begin, ensure you have met the following requirements:
- Python 3.x installed
- Git (for cloning the repository)

## Installation

Clone the repository:
```bash
git clone [repository URL]
cd [repository directory]
```

Create your Python virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install the required dependencies
```bash
pip install -r requirements.txt
```
## Configuration

Create a `.env` file in the root directory of the project.
```bash
touch .env  # On Windows, use `type nul > .env`
```

Add your OpenAI API key to the `.env` file
```bash
OPENAI_API_KEY=your_api_key_here
```

## Evaluation Module

The evaluation module is the most comprehensive one. As an example in its main function
the first question is answered by the AI 

Run it by executing:

```bash
python -m app.evaluation
```

## Testing

The tests are a WIP as the model needs to be further trained to handle various inputs mainly
since this is a fake project and I needed to think more about what the requirements around products should be.
I'll leave it as an exercise to get all of the tests passing after modifying the code to match the tests' expectations.

Here's how you run the tests for each of the examples in the test. 
You should achieve an overall fractional average score of "1.0" here:

```bash
python -m tests.test_run_all
```

## Known Issues

It's a WIP to add a while loop. If you notice in app/evaluation.py there's a while loop that's commented out.
Feel free to try to fix that. When I tried to add it, the completion call to OpenAI became hung.
I didn't have a chance to debug this yet.

## License

MIT License

Copyright (c) 2023 Navid Kamali

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
...
