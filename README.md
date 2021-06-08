# The MovieBot

for this project we have use python 3.7 with pip 21.1.1

The Packages required to run this project are:
    
    
    - ansicolor                            0.3.2 


    - en-core-web-md                       3.0.0 


    - en-core-web-sm                       2.3.1 


    - fuzzywuzzy                           0.18.0 


    - jupyter                              1.0.0 


    - nltk                                 3.5 


    - numpy                                1.18.5 


    - pandas                               1.1.4 


    - pickle5                              0.0.11 


    - pyTelegramBotAPI                     3.7.7 


    - rasa                                 2.6.0 


    - rasa-nlu                             0.15.1 


    - rasa-sdk                             2.6.0 


    - requests                             2.25.1 


    - scipy                                1.6.1 


    - scikit-learn                         0.24.2 


    - youtube-search-python                1.4.5 


    - nltk                                 3.5 



in order to run this project you first have to run : 

```
    rasa train
```

while this process is running open another terminal and execute ngrok on it using the command:

```
    ngrok.exe http 5005
```

then from the output copy the url that looks like this:

https://1fd73f3c8217.ngrok.io

and replace the base link in the file credentials.yml with it.


Then once the training process is done you to run these commands on the two different terminals (make sure that ngrok is running at all times). On one terminal run:

```
    rasa run actions
```

and on the other run:

```
    rasa run -m models -p 5005 --connector telegram --credentials credentials.yml
```

then you will be able to open Telegram and search for @wall_eTheBot (the display name is : TheMovieBot). Finally, you will be able to chat with the movie bot!