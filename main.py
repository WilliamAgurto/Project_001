from fastapi import FastAPI
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
app = FastAPI(title='API FILMS',description='Here, I will recomend you the bes movies', version='1.1')
#http://127.0.0.1:8000
'''''
Deben crear 6 funciones para los endpoints que se consumirán en la API, recuerden que deben tener un decorador por cada una (@app.get(‘/’)).
'''
@app.get("/")
async def welcome():
    return "WELCOME!!! HERE YOU WILL FIND THE BEST MOVIES EVER !!!"

@app.get("/index")
async def index():
    return "Function for searching: 1. peliculas_mes 2. peliculas_dia, 3. franquicia, 4. peliculas_pais, 5.productoras  y 6.retorno"

#loading Data
df_movies= pd.read_csv("datasets//new_movies_dataset.csv" ,parse_dates=['release_date'])
df_credits = pd.read_csv('datasets//new_credits.csv')
'''''
1. 'Se ingresa el mes y la funcion retorna la cantidad de peliculas que se estrenaron ese mes (nombre del mes, en str, ejemplo 'enero') 
historicamente'
'''

@app.get('/cantidad_filmaciones_mes/{mes}')
def cantidad_filmaciones_mes(mes:str):
    try:
        df_movies_copy = df_movies.copy()
        df_movies_copy['month'] = df_movies_copy.release_date.dt.month_name()
        # Dicctionary traduction
        translation_dict = {'January': 'enero', 'February': 'febrero', 'March': 'marzo', 'April': 'abril', 'May': 'mayo',
                            'June':'junio','July':'julio','August': 'agosto','September': 'septiembre','October': 'octubre',
                            'November': 'noviembre','December': 'diciembre'}
        # Applying traduction
        df_movies_copy['month'] = df_movies_copy['month'].replace(translation_dict)
        df_movies_copy = df_movies_copy.applymap(lambda x: x.lower() if isinstance(x, str) else x)
        result = df_movies_copy[df_movies_copy.month==mes]['title'].count()
        return {'month':mes,'quantity':int(result)}
    except Exception as e:
        return {'error': str(e)}
'''''    
#2. 'Se ingresa el dia y la funcion retorna la cantidad de peliculas que se estrenaron ese dia (de la semana, en str, ejemplo 'lunes')
 historicamente' 
'''
@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia:str):
    try: 
        df_movies_copy = df_movies.copy()
        df_movies_copy['day'] = df_movies_copy.release_date.dt.day_name()
        # Dicctionary traduction
        translation_dict = {'Monday': 'lunes',
                            'Tuesday': 'martes',
                            'Wednesday': 'miercoles',
                            'Thursday': 'jueves',
                            'Friday': 'viernes',
                            'Saturday': 'sabado',
                            'Sunday': 'domingo'}
        # Applying traduction
        df_movies_copy['day'] = df_movies_copy['day'].replace(translation_dict)
        df_movies_copy = df_movies_copy.applymap(lambda x: x.lower() if isinstance(x, str) else x)
        result = df_movies_copy[df_movies_copy.day==dia]['title'].count()
        return {'day':dia,'quantity':int(result)}
    except Exception as e:
        return {'error': str(e)}
'''
3. Se ingresa la franquicia, retornando la cantidad de peliculas, ganancia total y promedio
'''
@app.get("/score_titulo/{titulo}")
def score_titulo(titulo:str):
    try: 
        df_movies_copy = df_movies.copy()
        year = df_movies_copy.release_year[df_movies_copy.title == titulo].iloc[0]
        popularity = df_movies_copy.popularity[df_movies_copy.title == titulo].iloc[0]
        return {'title': titulo, 'year':int(year), 'popularity':float(popularity)}
    except Exception as e:
        return {'error': str(e)}
'''
4. 'Ingresas el pais, retornando la cantidad de peliculas producidas en el mismo'
'''
@app.get("/votos_titulo/{titulo}")
def votos_titulo(titulo:str):
    try:
        df_movies_copy = df_movies.copy()
        vote_count_ = df_movies_copy.vote_count[df_movies_copy.title == titulo].iloc[0]
        vote_average_ = df_movies_copy.vote_average[df_movies_copy.title == titulo].iloc[0]
        if vote_count_< 2000 :
            return {'the amount of votes of this film are less than 2000'}
        else:
            return {'title': titulo, 'total vote':vote_count_, 'vote average':vote_average_}
    except Exception as e:
        return {'error': str(e)}
'''
5. Ingresas la productora, retornando la ganancia total y la cantidad de peliculas que produjeron''
'''
@app.get("/get_actor/{nombre_actor}")
def get_actor(nombre_actor:str):
    try:
        df_movies_copy = df_movies.copy()
        df_credits_copy = df_credits.copy()
        ids = df_credits_copy[df_credits_copy['cast'].str.contains(nombre_actor, na=False)]['id'].tolist() #ids film from actor
        quantity_films = len(ids)
        return_ = df_movies_copy['return'][df_movies_copy.id.isin(ids)]
        total_return = return_.sum()       
        average_return = return_.mean()       
        return {'actor':nombre_actor, 'cantidad_filmaciones':quantity_films, 
            'retorno_total':total_return, 'retorno_promedio':average_return}
    except Exception as e:
        return {'error': str(e)}
'''
6.Ingresas la pelicula, retornando la inversion, la ganancia, el retorno y el año en el que se lanzo''
'''
@app.get("/get_director/{nombre_director}")
def get_director(nombre_director:str):
    try:
        df_movies_copy = df_movies.copy()
        df_credits_copy = df_credits.copy()
        ids = df_credits_copy[df_credits_copy['crew'].str.contains(nombre_director, na=False)]['id'].tolist()
        return_film = df_movies_copy['return'][df_movies_copy.id.isin(ids)].tolist()
        name_film = df_movies_copy['title'][df_movies_copy.id.isin(ids)].tolist()
        date_film = df_movies_copy['release_year'][df_movies_copy.id.isin(ids)].tolist()
        budget_film = df_movies_copy['budget'][df_movies_copy.id.isin(ids)].tolist()
        revenue_film = df_movies_copy['revenue'][df_movies_copy.id.isin(ids)].tolist()
        total_return = df_movies_copy['return'][df_movies_copy.id.isin(ids)].sum()
        return{'director':nombre_director, 'total_return_director':total_return, 
        'films':name_film, 'year':date_film, 'film_retorn':return_film, 
        'budget_film':budget_film, 'revenue_film':revenue_film}
    except Exception as e:
        return {'error': str(e)}
##########recommendation function
@app.get('/recomendacion/{titulo}')
def recomendacion(titulo:str):
    try:
        df_movies_copy = df_movies.copy()
        # Loading just two columns from CSV file on pandas.
        overview = df_movies_copy[['title','overview']]
    
        # Getting the description of the movie title given.
        overview = df_movies_copy[df_movies_copy['title'] == titulo]['overview'].str.strip()[0]

        # Computing  TF-IDF features for all oveviews.
        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(df_movies_copy['overview'])

        # Computing cosine similarities between overview and movie titles and all the other overviews.
        tfidf_similarities = cosine_similarity(tfidf_matrix, tfidf.transform([overview]))

        # getting top 10 indexes of films wich best matech according to TF-IDF.
        tfidf_similar_movie_indices = tfidf_similarities.argsort(axis=0)[-10:][::-1].flatten()

        # Turn indexes into movie titles  
        tfidf_similar_movie_titles = df_movies_copy.loc[tfidf_similar_movie_indices, 'title'].tolist()
        respuesta = tfidf_similar_movie_titles[1:6]
        return {'recommendation list': respuesta}
    except Exception as e:
        return {'error': str(e)}
    