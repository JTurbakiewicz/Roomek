
The Bot module receives user message, parses it to collect information and prepares an answer to send back to the user.

How it works:   ________________________________________________________________________________________
1. Dispatcher_app receives the Rest message and pass it to 'logic'.
2. 'logic' handles different types of messages and in case of text message it passes it to 'message_parser'.
3. 'message_parser' creates message object and collects direct information from it.
4. Each message has 'user' assigned to it. 
5. 'respond' tries to collect indirect information and based on conversation flow asks the right question.
6. Questions and all the answers are in 'responses_PL' file.
7. 'Cognition' contains functions to parse user message like 'recognize_location'.
8. Message is being send using send functions from 'facebook_webhooks'.

TODO - Dziennik zadań (zacznij od góry):   _____________________________________________________________

[!] [user/cognition] fix location error

[ ] [user/cognition] ma dawać dzielnice osobną funkcją

[+/-] [Postman] learn postman api calls - can we talk without facebook?

[+/-] [PyCharm] learn debugging

[ ] [Cognition] wydobadz wiecej info z jednej wypowiedzi.

[ ] [logic] dojść do zwracania 3 ofert jako linki
     
[ ] [pyany] Postaw na pyany i zobacz jak reaguje po czasie i na kilka osób

[ ] [fb webhooks] dopracuj karuzelę 3 ofert i podobne generic message

[ ] [fb webhooks] dodaj hamburgera (może z Postmana?)

[ ] [???] (czy warto) rozdzielić na osobne obiekty: User i Query (jeden user może mieć kilka "zapytań")

[ ] [logic] po udanym szukaniu dopytuj dalej lub nowe wyszukiwanie

[ ] [Python] learn testing (unitary tests)

[ ] [logic] wizualizacja grafu odpowiedzi (jak graf na szkoleniu z ML)

[ ] [logic] pytania powinny być na bazie klastrowania - czyli, że pyta o konkretną cechę jeżeli wie że to mu zawęzi wyszukiwanie (Akinator)

[ ] [check this out] https://realpython.com/testing-third-party-apis-with-mocks/
[ ] [check this out] https://seminar.io/2013/09/27/testing-your-rest-client-in-python/
[ ] [check this out] https://semaphoreci.com/community/tutorials/bdd-testing-a-restful-web-application-in-python
