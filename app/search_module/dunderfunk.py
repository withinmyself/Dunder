
import re
import random

genrePrefix = [
               'post', 'atmospheric', 'ambient',
               'instrumental', 'epic',
               ]
genreMain = [
             'metal', 'black metal', 'rock', 'progressive rock',
             'punk rock', 'hardcore punk', 'progressive metal',
             'speed metal', 'thrash metal', 'doom metal',
             'heavy metal', 'glam rock', 'black metal', 'folk metal'
             ]             
countryOfOrigin = ['swedish', 'german', 'norwegian', 'french', 'british', 'greece', 'israeli',
                   'american', ]

def random_genre (
                  genrePrefix=genrePrefix,
                  genreMain=genreMain,
                  countryOfOrigin=countryOfOrigin
                  ):
    randomPrefix = random.choice(genrePrefix)
    randomGenre = random.choice(genreMain)
    randomCountry = random.choice(countryOfOrigin)
    return (
            str('{}'.format(randomPrefix)) + ' ' +
            str('{}'.format(randomGenre)) +  ' ' +
            str('{}'.format(randomCountry))
            )