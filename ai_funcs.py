import os

import google.generativeai as genai


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")


def safety_check(content: str):

    prompt = f"""
        I am sending you a message\n 
        here is the text of the message {content}. 
        Your task is to determine whether this text contains uncensored language. 
        Response format: True if there is no non-censored language, False if there is non-censored language
    """

    response = model.generate_content(prompt)

    if not response.candidates or not response.candidates[0].content.parts:
        raise ValueError("The response from the model is incomplete or empty.")

    is_safety = response.candidates[0].content.parts[0].text.split()[0]
    print(is_safety)

    if is_safety == "False":
        return False
    else:
        return True


def auto_comment_answer(post_text: str, comment_text: str):

    prompt = f"""
        Post: {post_text}\nComment: {comment_text}\n
        your answer should only contain a response to the comment, 
        taking into account the context of the post and comment
    """

    response = model.generate_content(prompt)

    return response.candidates[0].content.parts[0].text.strip()
