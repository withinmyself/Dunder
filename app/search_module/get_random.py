
import re
import random

# 3 different lists to pull from
genrePrefix = ['post', 'atmospheric', 'ambient',
               'instrumental', 'epic']

genreMain = ['metal', 'black metal', 'rock', 'progressive rock',
             'punk rock', 'hardcore punk', 'progressive metal',
             'speed metal', 'thrash metal', 'doom metal',
             'heavy metal', 'glam rock', 'black metal', 'folk metal']
           
countryOfOrigin = ['swedish', 'german', 'norwegian', 'french', 'british', 'greece', 'israeli',
                   'american']

# Return a string with 1 random genre, 1 random sub-genre and 1 random country
def random_genre (genrePrefix=genrePrefix, genreMain=genreMain,
                               countryOfOrigin=countryOfOrigin):

    randomPrefix = random.choice(genrePrefix)
    randomGenre = random.choice(genreMain)
    randomCountry = random.choice(countryOfOrigin)
    return (str('{}'.format(randomPrefix)) + ' ' +
            str('{}'.format(randomGenre)) +  ' ' +
            str('{}'.format(randomCountry)))
