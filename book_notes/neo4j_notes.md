# Neo4j Graph Database
[guide](https://www.youtube.com/watch?v=8jNPelugC2s&t=4263s&ab_channel=LaithAcademy) 
i left off at 27:00

Graph databases are best used when you have lots of relationships.  ex. Social Media.

Made up of nodes (the circles) which can be literally anything.  ex. Players and Teams.  Then there could be verticies (the 1 DIRECTIONAL arrows) to show the relationships.

Nodes can have different properties (name: xx, weight: xx, height: xx).

Verticies connect the nodes together, but can also have properties IN the relationships itself.

# Queries
This returns everything
`MATCH (n) RETURN (n)`

This will only return the team nodes
`MATCH (n:TEAM) RETURN (n)`

This will return all of the players and all of the player relationships
`MATCH (player:PLAYER) RETURN player`

`MATCH (player:PLAYER) RETURN player.age, player.height` to get the attributes for player.

`MATCH (player:PLAYER) RETURN player.age as name, player.height as height` to rename the attributes.