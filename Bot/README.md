
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

[X] [logic] added $okoń$dropme and $okoń$showme method etc.

[A] [Cognition] nie rozumie jak piszemy "ma garaż" bo błąd nr 007





[ ] [parser] loca

[A] [flow] na koniec pytanie czy od nowa czy kolejne oferty

[ ] [parser] napraw sticker

[A] [flow] Zacznij od nowa button

[A] [flow] test replying messge

[A] [flow] test add sticker to messge

[K] [flow] dodaj funkcję resetującą usera

[ ] [...] tłumacz offer features (ma garaż itd)

[ ] [...] nie dodaje np. Mokotów tylko miasto lub ulice 




[ ] [...] zawez wyszukiwanie lokacji do kraju a potem miasta

[ ] [...] jesli to problem to zastap SLEEP np. timestamp checkerem

[A] [user/cognition] ma dawać dzielnice osobną funkcją

[A] [fb webhooks] dopracuj karuzelę 3 ofert i podobne generic message - łatwe funkcje

[ ] [Bot] Zastąp wszystkie Print'y w BOTcie.

[ ] [pyany] Postaw na pyany i zobacz jak reaguje po czasie i na kilka osób

[ ] [data] Połącz z Jupyterem żeby wyświetlać dane np o ofertach

[K] [parser] best offer doskonalić

***** Test na bliskich znajomych *****


[ ] [importy] uproscic importy do pliku glownego (obecnie circular importy)

[ ] [feedback] zobaczyć co intuicyjnie ludzie piszą - przerobić flow

[ ] [strategy] Ustalić
    - problem/rozwiązanie, kim są klienci
    - zarabianie? 
    - cele biznesowe
    - pomiary
    - rozpisać założenia

[ ] [???] legal

[ ] [feedback] spotkać się z Kubikiem

[ ] [???] (czy warto) rozdzielić na osobne obiekty: User i Query (jeden user może mieć kilka "zapytań")

[ ] [Bot] Czy lepsze funkcje reactions czy tabela (np. json) i parser (np rozpoznajacy quick replies)?

[ ] [logic] po udanym szukaniu dopytuj dalej lub nowe wyszukiwanie

[ ] [Bot] Usprawnić hamburger - obecnie placeholdery.

[ ] [logic] pytania powinny być na bazie klastrowania - czyli, że pyta o konkretną cechę jeżeli wie że to mu zawęzi wyszukiwanie (Akinator)

[ ] [Python] learn testing (unitary tests, automated testing)
        -> simplified test: zobaczyć czy działa jak user wyśle okejke, naklejke, gifa, w innym języku, wiele odpowiedzi pod rząd itd.
[ ] [check this out] https://realpython.com/testing-third-party-apis-with-mocks/
[ ] [check this out] https://seminar.io/2013/09/27/testing-your-rest-client-in-python/
[ ] [check this out] https://semaphoreci.com/community/tutorials/bdd-testing-a-restful-web-application-in-python

***** Test na wielu znajomych *****

[ ] [logic] wizualizacja grafu odpowiedzi (jak graf na szkoleniu z ML)

[ ] [strategia] weryfikacja przyjętych założeń:
 
***** Pivot? *****

[ ] [marketing]
    - napędzenie użytkowników do używania za darmo
    - lej marketingowy (dużo osób przypadkowych, dla zabawy, potem część faktycznie szuka, a niewielka ilość chce np. płatną analizę)
    - konwersja na płatne usługi
    - kohorty
    - content marketing - ciekawe statystyki mieszkań w polsce, na fanpage
    - płatny ruch (fb ads, google ads)

***** Feedback od ludzi napędzonych z ads *****
