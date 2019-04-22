Bot module receives user message, parse it to collect information and prepares an answer to send back to the user.

How it works:
1. Dispatcher_app receives the Rest message and pass it to 'logic'.
2. 'logic' handles different types of messages and in case of text message it passes it to 'message_parser'.
3. 'message_parser' creates message object and collects direct information from it.
4. Each message has 'user' assigned to it. 
5. 'respond' tries to collect indirect information and based on conversation flow asks the right question.
6. Questions and all the answers are in 'responses_PL' file.
7. 'Cognition' contains functions to parse user message like 'recognize_location'.
8. Message is being send using send functions from 'facebook_webhooks'.