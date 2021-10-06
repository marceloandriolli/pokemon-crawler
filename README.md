# Pokemon Crawler

Project started from https://docs.docker.com/compose/django/

Some useful commands:

* `docker-compose up`
* `docker-compose exec web bash`
* `docker-compose exec web python -m pip install -r requirements.txt`


## Proposed Solution:
The proposed solution was thought to be simple as possible to be finished in two hours. But it was not possible implemented the whole solution in two hours, was only implemented the first crawler. The main idea is presented bellow.

### Crawler:
Analysing the Pokemon API, I realized that to get some characteristics of each pokemon I must to request all the pokemon details endpoints, so it means a lots of request to the API since that there are 1118 pokemons. So running the crawler with too many request synchronously could be super slow,  to avoid  it, was thought doing asynchronously  requests to the API. 

The crawler would be runned as a django command that could be  manually runned  or scheduled as a crontab job. To updated the DB with the new pokemons another django command could be runned scheduled as a crontab job once per week for example. This updated command basicaly will check it there are new pokemons present on API doing a API request to get the total number of pokemons and hit the DB to count the number pokemons currently stored  on stored. If the the number of pokemon in API is grether than the number of pokemons stored in DB, the BD must be updated. The updated process would be getting lasted pokemons ids present on list endpoints of pokemon API
the higher pokemons ids from the pokemon list endpoints, since the pokemon list endpoint returned pokemons order by ascending ids, so that would be (Count of pokemons in API - Count pokemons in DB), so the difference between it represent that lastests pokemon that gonna be updated from API.  For example if the pokemon list endpoint return count 1200 and the pokemon table count is 1118, the new pokemons must be the lastests 82 pokemons are new, so to get the lastest 82 pokemons it just do a request to the list endpoint using limit and offset query args. In that case the limit must be 82 and the offset must be 1036, in other words the offset must be (Count of pokemons in API - Difference between pokemon count from API count and pokemon count from DB).

## Application
The application in Django would be a Django Admin to present the crawled data with customs filters.
The database will have two tables, the pokemon table and characterists table:

```code
class Characterists(models.Model):
    stats = models.JsonField()
    abilities = models.JsonField()
    height = models.DecimalField(max_digits=3, decimal_places=2)
    weight = models.DecimalField(max_digits=3, decimal_places=2)


class Pokemon(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    characterists = models.OneToOneField(
        Characterists,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=['name', 'description']),
        ]

    def __str__(self):
        return f"Pokemon: {self.name}"
```