# foosball sim
this straight up does not work yet. i coded it very badly once upon a time and i am trying to make this one a little more approachable.

There is a set of *real* games that were played in original_results.csv and the *real* final stats from those games in original_stats.csv. original_stats.csv might actually be calculated from the results in an attempt to make sure the math was lining up with the original spreadsheet

## Game Plan

*The following makes no guarantee that this is how things actually run yet.* The original code is not very good. It involves a lot of repetition, hard coding, etc. The following process is my description of what I would like the general function of this program to be.

If I had planned it out like this in the first place it would probably be a little more manageable!

### Initialization
The process loads a sequential list of foosball games from a csv file. It will use these games to calculate initial stats.

### Game Generation
The process will use these initial stats to calculate the outcome of new games using a Poisson distribution function on the average of each players points scored versus their opponents points allowed.

```
pointsScoredByPlayerA(playerA, PlayerB) = randomPoissonDistributedNumber(
    ( playerA.avgPointsScored + playerB.avgPointsAllowed ) / 2
)
```

### Stat Feedback
This is the area where the first iteration is the clunkiest. There are two ways this could be done:
1. Update the stats after each game, using these new stats to calculate future games.
2. Use the original *real* stats to calculate all games, but creating updated cosmetic stats after each game.

The original code has #1 hardcoded, but I think it should be an option on which way to go. Implementing this as an option will make the Initialization, Game Generation, and Stat Feedback stages more compartmentalized.

### Entry Points
The two main use-cases are:
1. One off foosball games are triggered between arbitrary players. This would be a slash command from slack.
2. Running games are played in one ongoing "league." In slack (or on a website), this would be like a scheduled daily event.