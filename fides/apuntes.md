# Fides

Fides (fee-dez) is an open source privacy management platform which can be used to fulfill data privacy requests. With this tool, you can allow your users to request their data to be deleted.

Sometimes, a company may opt to anonymize the user data after it's been requested to be deleted, so that you can still have the general record for analytics and reporting.

- Example: you had 100 users in the month of March 2024, but 50 of those users requested their data to be deleted by July 2024.
- If you wanted to run historical analytics after July 2024 and you actually deleted all of that data, your records would only show 50% of their true value between that period.


## Fides Example

``` sh
poetry install
poetry shell

fides deploy up

```

- User Landing Page: `http://localhost:3000/landing`
- User Privacy Center: `http://localhost:3001`
- Admin UI: `http://localhost:8080`
  - Username: `root_user`
  - Password: `Testpassword1!`


