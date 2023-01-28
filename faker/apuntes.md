# Faker

## Providers 
[Link](https://faker.readthedocs.io/en/master/providers.html)

# memory usage
```
worker_df.info()
worker_df.info(memory_usage="deep")
worker_df.memory_usage(deep=True)
```
 - always use deep bc it actaully counts string columns where memory is extremely variable
 - 1 string that's 20 characters is way less memory than a string that has 5000+ characters in it.