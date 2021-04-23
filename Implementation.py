from DominoesGame import Dominoes, Domino
import random


class NegaMax:
    def __init__(self, currentGame):
        self.currentGame = currentGame

    def negamax(self, initial, depth, alpha, beta, player):
        cg = self.currentGame
        if depth == 0:
            return None, cg.evaluate(player)
        
        if cg.isEnd():
            q = cg.win_score(player)
            if not q:
                return None, cg.evaluate(player)
            return None, q

        maxMove, maxScore = None, None
        for move in sorted(cg.possible_actions(player), key=lambda x: -sum(x[0].vals)):
            prob = cg.makeProbabilisticMove(player, move)
            _, currentScore = self.negamax(initial, depth-1, -beta, -alpha, cg.get_next_player(player))
            currentScore = -prob * currentScore
            if maxScore is None or currentScore > maxScore:
                maxMove, maxScore = move, currentScore
            alpha = max(alpha, currentScore)
            cg.undoMove(player, move)
            if alpha >= beta:
                break
        return maxMove, maxScore


def setupGame(r):
    tiles = []
    for i in range(7):
        for j in range(i, 7):
            tiles.append((i, j))
    random.shuffle(tiles)
    my_tiles = tiles[:7]
    players_tiles = {}
    players_tuples = [None]*4
    players_tiles[0] = set(map(lambda x: Domino(*x), my_tiles))
    players_tuples[0] = my_tiles
    for i in range(1, 4):
        this_players_tiles = tiles[7*i:7*(i+1)]
        players_tiles[i] = set(map(lambda x: Domino(*x), this_players_tiles))
        players_tuples[i] = this_players_tiles
    starter = r % 4
    return ((Dominoes(tiles, my_tiles, starter), Dominoes(tiles, players_tuples[2], (starter+2) % 4)), players_tiles)


def greedyPlays(game, tiles):
    games = game
    game, ogame = games
    player = game.currentPlayer
    actions = game.possible_actions(None, False)
    my_tiles = tiles[player]
    possible_moves = [Domino(-1, -1)]
    for t in my_tiles:
        if t in actions:
            possible_moves.append(t)
    maximum = -1
    ret = possible_moves[0]
    for domino in possible_moves:
        if domino.vals[1] + domino.vals[0] > maximum:
            maximum = domino.vals[1] + domino.vals[0]
            ret = domino
    if (game.ends[0] in ret and game.ends[1] in ret and game.ends[0] != game.ends[1]):
        placement = random.choice((0, 1))
        game.update(ret, None, placement)
        ogame.update(ret, None, placement)
    else:
        game.update(ret, None)
        ogame.update(ret, None)
    if ret != Domino(-1, -1):
        tiles[player].remove(ret)
    return tiles


def negamaxPlays(game, tiles, player):
    player /= 2
    currentGame = game[int(player)]
    otherGame = game[int(1-player)]
    actions = currentGame.possible_actions(0)
    if len(actions) == 1:
        currentGame.update(actions[0][0])
        otherGame.update(actions[0][0])
        if not actions[0][0] == Domino(-1, -1):
            tiles[2*player].remove(actions[0][0])
    else:
        pnm = NegaMax(currentGame)
        max_move, _ = pnm.negamax(10, 10, 4, .3, 0)

        currentGame.update(max_move[0], placement=max_move[1])
        otherGame.update(max_move[0], placement=max_move[1])
        if not max_move[0] == Domino(-1, -1):
            tiles[2*player].remove(max_move[0])
    return tiles


def printScore(game, players_tiles):
    player_pips = [0]*4
    for t in game.myTiles:
        if t not in game.dominos_played:
            player_pips[0] += sum(t.vals)
    for i in range(1, 4):
        for t in players_tiles[i]:
            if t not in game.dominos_played:
                player_pips[i] += sum(t.vals)
    if (player_pips[0] == 0 or player_pips[2] == 0 or
            player_pips[0]+player_pips[2] < player_pips[1] + player_pips[3]):
        return 'won'
    if (player_pips[1] == 0 or player_pips[3] == 0 or
            player_pips[0]+player_pips[2] > player_pips[1] + player_pips[3]):
        return 'lost'
    if player_pips[0]+player_pips[2] == player_pips[1] + player_pips[3]:
        return 'tie'


def revealTiles(games, players_tiles):
    for i in range(4):
        for t in players_tiles[i]:
            games[0].probabilities[t] = [0]*4
            games[0].probabilities[t][i] = 1
            games[1].probabilities[t] = [0]*4
            games[1].probabilities[t][(i+2) % 4] = 1


def main():
    results = []
    for r in range(100):
        games, playerTiles = setupGame(r)
        revealTiles(games, playerTiles)
        while not games[0].isEnd():
            player = games[0].currentPlayer
            tiles = greedyPlays(games, playerTiles) if player % 2 == 1 else negamaxPlays(
                games, playerTiles, player)
            games[0].debugging()
            games[1].debugging()
        results.append(printScore(games[0], playerTiles))
    print("RESULTS")
    print("Number of wins:", results.count("won"))
    print("Number of losses:", results.count("lost"))
    print("Number of ties:", results.count("tie"))


main()
