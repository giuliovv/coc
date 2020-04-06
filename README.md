# Clash of Clans API reader
Clash of Clans api python reader.
Suggest clan wars attack order, still acquiring data to figure out parameter's weight.
Clan Wars League not implemented yet.

### Getting started:
- Get api key on https://developer.clashofclans.com/
- Put key on new file apikeys.py and name it hdr, ex:

```python
hdr = {'authorization' : 'Bearer API_KEY'}
```
## Example:
See folder "Examples".
  
## Documentation:
#### Get clan members:
```python
import CoC
tag = "CLAN_TAG"

CoC.clan_members(tag)
```

#### Get warlog:
```python
tag = "CLAN_TAG"

ok, isPublic = CoC.public_warlog(tag)

# If not ok isPublic is an error (golang docet)
if not ok:
  raise isPublic
  
# If warlog is not public it can't be read.
if isPublic:
  print(warlog(tag))
```

#### Get specific war:
```python
tag = "WAR_TAG"

ok, war = CoC.getwar(tag)
  
war
```

#### Get user's data:
```python
tag = "USER_TAG"

ok, user = CoC.data_user(tag)
  
user
```

#### Get specific user data:
```python
tag = "USER_TAG"

user = CoC.User(tag)
  
# Get user's home heroes levels
user.getHeroes(selected="home")

# Get user's builder base heroes levels
user.getHeroes(selected="builderBase")

# Get user's home spells levels
user.getSpells(selected="home")

# Get user's builder base spells levels
user.getSpells(selected="builderBase")

# Get user's home troops levels
user.getTroops(selected="home")

# Get user's builder base troops levels
user.getTroops(selected="builderBase")
```

## Current war data:
```python
tag = "CLAN_TAG"

# If clan state is "not_in_war" it raises a ValueError
cWar = CoC.currentWar(tag)
```

#### Get current war attacks
```python
# Tag's clan attacks
cWar.getClanAttacks()

# Opponent clan attacks:
cWar.getOpponentAttacks()
```

#### Get current war clan members
```python
# Tag's clan members
cWar.getClanMembers()

# Opponent clan members:
cWar.getOpponentMembers()
```

#### Get current war clan members stats
```python
# Tag's clan members stats:
cWar.getClanMembersStats()

# Opponent clan members stats:
cWar.getOpponentMembersStats()
```

#### Get current war clan troops level
```python
# Tag's clan troops level:
cWar.getClanTroopsLevel()

# Opponent clan troops level:
cWar.getOpponentTroopsLevel()
```

## Experimental, weights could be really really better with more data:
#### Compare clans
```python
cWar.compare()
```
#### Plot compare
```python
cWar.plotCompare()
```

#### Better attack order:
```python
cWar.getBetterOrder()
```

#### Plot better attack order:
```python
cWar.plotBetterOrder()
```

#### Plot attacks:
```python
cWar.plotClanAttack()
```


## Disclaimer
This content is not affiliated with, endorsed, sponsored, or specifically approved by Supercell and Supercell is not responsible for it. For more information see Supercell’s Fan Content Policy: https://supercell.com/en/fan-content-policy/
