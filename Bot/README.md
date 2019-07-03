
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

Milestones:   __________________________________________________________________________________________
- dojść do zwracania 3 ofert (obecnie problem z user.confirmeddata)
- 3 oferty jako linki
- 3 oferty jako generic message
- ma umieć zbierać kilka informacji na raz ("szukam mieszkania na wynajem w Warszawie" -> apartment, rent, Warszawa)
- poprawić zbieranie np. lokalizacji.
- ułatwić przyszłe zmiany struktury.
- Postawić to na pyany
- Sprawdzić jak sobie radzi z wieloma użytkownikami
- Przejrzeć bazę danych o użytkownikach i rozmowach.
- rozdzielić na osobne obiekty: User i Query (jeden user może mieć kilka "zapytań")
- po udanym szukaniu dopytuj dalej lub nowe wyszukiwanie
- wizualizacja grafu odpowiedzi (jak graf na szkoleniu z ML)
- rozdzielić user i query (user może mieć kilka query)

TODO - Dziennik zadań (od najnowszych):   _____________________________________________________________
zacznij od:
- [cognition 83] # TODO MAJOR FUCKUP: no user in message!
potem:
- [wymaga Kuby] Spraw aby dodawał usera do bazy   
- [Cognition] wydobadz wiecej info z jednej wypowiedzi.
- [fb webhooks] dopracuj karuzelę 3 ofert
- 


