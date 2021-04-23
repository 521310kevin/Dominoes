from copy import copy, deepcopy


class GameAI:
    def __init__(self):
        pass

    def isEnd(self):
        print()

    def makeProbabilisticMove(self, player, move):
        print()

    def undoMove(self, player, move):
        print()

    def possible_actions(self, player):
        print()

    def evaluate(self, player):
        print()

    def getNextPlayer(self, player):
        print()


class Dominoes(GameAI):
    def __init__(self, gameTiles, myTiles, starter):
        self.tiles = set(map(lambda x: Domino(*x), gameTiles))
        self.myTiles = set(map(lambda x: Domino(*x), myTiles))
        self.starter = starter
        self.dominos_played = []
        self.lastPlay = 0
        self.ends = [None, None]
        self.probabilities = {d: ([0, 1./3, 1./3, 1./3] if d not in self.myTiles else [1, 0, 0, 0]) for d in self.tiles}
        self.currentPlayer = (starter) % 4
        self.undoable_probs = []
        self.undoable = []

    def playedTile(self, tile):
        tile = self.dominos_played[(tile-self.starter) % 4::4]
        played = sum(map(lambda x: not x == Domino(-1, -1), tile))
        return played

    def isEnd(self):
        playerCount = 4
        for i in range(0, playerCount):
            if self.playedTile(i) == 7:
                return True
        currentTiles = len(self.tiles)
        if currentTiles == 0:
            return True
        if self.lastPlay > 3:
            return all(map(lambda x: x == Domino(-1, -1), self.dominos_played[self.lastPlay-3:self.lastPlay+1]))
        return False

    def makeProbabilisticMove(self, player, move):
        placement = move[1]
        move = move[0]
        self.undoable.append(copy(self.ends))
        prob_of_move = self._assign_prob(move, player)
        self.undoable_probs.append(deepcopy(self.probabilities))
        self.update(move, player, placement)
        return prob_of_move

    def undoMove(self, player, move):
        move = move[0]
        self.dominos_played.pop()
        if not move == Domino(-1, -1):
            self.tiles.add(move)
        self.probabilities = self.undoable_probs.pop()
        self.ends = self.undoable.pop()
        self.currentPlayer = player
        self.lastPlay -= 1

    def possible_actions(self, currentPlayer=None, placements_included=True):
        if currentPlayer is None:
            currentPlayer = self.currentPlayer
        possible_moves = []
        for t in self.tiles:
            if self._is_valid(t) and self.probabilities[t][currentPlayer] > 0:
                if not self.dominos_played:
                    if placements_included:
                        possible_moves.append((t, None))
                    else:
                        possible_moves.append(t)
                    continue
                if placements_included:
                    if not (self.ends[0] in t) ^ (self.ends[1] in t) \
                            & (self.ends[0] != self.ends[1]):
                        possible_moves.append((t, 0))
                        possible_moves.append((t, 1))
                    else:
                        possible_moves.append((t, None))
                else:
                    possible_moves.append(t)
        if not possible_moves:
            return [(Domino(-1, -1), None)] if placements_included else [Domino(-1, -1)]
        return possible_moves

    def evaluate(self, player):
        expectation_opp = 0
        expectation_us = 0
        for d in self.probabilities:
            if d not in self.dominos_played:
                probs = self.probabilities[d]
                value = sum(d.vals)
                expectation_opp += value * probs[(player + 1) % 4] + value*probs[(player + 3) % 4]
                expectation_us += value * probs[player] + value*probs[(player + 2) % 4]
        return expectation_opp - expectation_us

    def _count_pieces(self, player):
        rel_players = [(player + i) % 4 for i in range(4)]
        pieces_player = [self.playedTile(p) for p in rel_players]
        return (pieces_player[0] + pieces_player[2], pieces_player[1] + pieces_player[3])

    def get_next_player(self, player):
        return (player + 1) % 4

    def debugging(self):
        print(self.tiles)

    def get_player(self, curr_play):
        return (curr_play + self.starter) % 4

    def _is_valid(self, t):
        return self.ends[0] in t or self.ends[1] in t or len(self.dominos_played) == 0

    def _assign_prob(self, domino, player):
        if domino in self.probabilities:
            return self.probabilities[domino][player]
        else:
            return 1

    def probability_actions(self, currentPlayer=None):
        if currentPlayer is None:
            currentPlayer = self.currentPlayer
        possible_moves = self.possible_actions(currentPlayer)

        def ap(d):
            return (d, self._assign_prob(d[0], currentPlayer))
        return map(ap, possible_moves)

    def _get_score(self, player):
        expectation_opp = 0
        for d in self.probabilities:
            if d not in self.dominos_played:
                probs = self.probabilities[d]
                value = sum(d.vals)
                expectation_opp += value * \
                    (probs[(player+1) % 4]+probs[(player+3) % 4])
        return expectation_opp

    def win_score(self, player):
        if not self.isEnd():
            return False
        player_me = player
        player_teammate = (player+2) % 4
        player_opp1 = (player+1) % 4
        player_opp2 = (player+3) % 4

        if self.playedTile(player_me) == 7 or self.playedTile(player_teammate) == 7:
            return self._get_score(player_me)
        if self.playedTile(player_opp1) == 7 or self.playedTile(player_opp2) == 7:
            return -self._get_score(player_opp1)

    def _update_probs(self, move, curr_player):
        def uncertain(d):
            return d != [1, 0, 0, 0] and d != [0, 1, 0, 0] \
                and d != [0, 0, 1, 0] and d != [0, 0, 0, 1]
        if move == Domino(-1, -1):
            possible_moves = self.possible_actions(placements_included=False)
            for t in possible_moves:
                if not t == Domino(-1, -1) and self.probabilities[t][curr_player] != 1:
                    self.probabilities[t][curr_player] = 0
                    self.probabilities[t] = normalize(self.probabilities[t])
        else:
            self.probabilities[move] = [0]*4
            self.probabilities[move][curr_player] = 1
        slots_per_person = {}
        for i in range(1, 4):
            played = self.dominos_played[(i - self.starter) % 4::4]
            slots_per_person[i] = 7 - \
                len(played) + played.count(Domino(-1, -1))
        for d in self.probabilities:
            if uncertain(self.probabilities[d]):
                for i in range(1, 4):
                    if self.probabilities[d][i] > 0:
                        self.probabilities[d][i] = slots_per_person[i]
                self.probabilities[d] = normalize(self.probabilities[d])

    def update(self, move, currentPlayer=None, placement=None):
        if currentPlayer is None:
            currentPlayer = self.currentPlayer
        if type(move) == tuple:
            move = Domino(move)
        if move == Domino(-1, -1):
            self.dominos_played.append(Domino(-1, -1))
        else:
            if not self.dominos_played:
                self.ends[0] = move.vals[0]
                self.ends[1] = move.vals[1]
            elif placement is None:
                if self.ends[0] in move:
                    self.ends[0] = move._get_other(self.ends[0])
                else:
                    self.ends[1] = move._get_other(self.ends[1])
            else:
                self.ends[placement] = move._get_other(self.ends[placement])
            self.dominos_played.append(move)
            self.tiles.remove(move)
        self._update_probs(move, currentPlayer)
        self.currentPlayer = (currentPlayer + 1) % 4
        self.lastPlay += 1


class Domino():
    def __init__(self, a, b):
        self.vals = (a, b) if a < b else (b, a)
        self.currentHash = hash(self.vals)

    def __hash__(self):
        return self.currentHash

    def __eq__(self, other):
        if other is None:
            return False
        if type(other) is tuple:
            other = Domino(*other)
        if other == 'PASS' or other.vals[0] < 0:
            return self.vals[0] < 0
        return self.vals == other.vals

    def __leq__(self, other):
        return self.vals[0]+self.vals[1] <= other.vals[0]+other.vals[1]

    def __str__(self):
        return str(self.vals) if self.vals[0] >= 0 else 'PASS'

    def __contains__(self, a):
        return a in self.vals

    def _get_other(self, a):
        return self.vals[0] if self.vals[1] == a else self.vals[1]

    def __repr__(self):
        return str(self)


def normalize(arr):
    total = float(sum(arr))
    maping = map(lambda x: x/total, arr)
    return maping
