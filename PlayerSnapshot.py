# This stores limited information about a player and is meant to be stored by a game object

class PlayerSnapshot:
    
    def __init__(self, player): # first argument to methods is self
        self.name = player.name
        
        self.wins = player.wins
        self.losses = player.losses
        
        self.winning_run = player.winning_run
        self.run = player.run

        self.avg_points_scored = player.avg_points_scored
        self.avg_points_allowed = player.avg_points_allowed
        self.avg_margin_victory = player.avg_margin_victory
        self.avg_margin_loss = player.avg_margin_loss

        self.win_percent = player.win_percent
        self.elo = player.elo

        self.king = player.king
    
    def str_header(self):
        return ''.join([
            'PLAYER'.ljust(8) + '|',
            'W'.rjust(5),
            'L'.rjust(5),
            'RUN'.rjust(4),
            'PS/G'.rjust(6),
            'PA/G'.rjust(6),
            'AM+'.rjust(6),
            'AM-'.rjust(6),
            'WIN%'.rjust(7),
            'ELO'.rjust(7),
            'KING'.rjust(5)
        ])

    def __str__(self):

        king_string = ''
        if self.king:
            king_string = ' K'
        
        if self.winning_run:
            run_string = 'W'
        else:
            run_string = 'L'
        
        return ''.join([
            self.name.ljust(8),
            '|',
            str(self.wins).rjust(5),
            str(self.losses).rjust(5),
            (str(self.run)+run_string).rjust(4),
            "{0:.2f}".format(self.avg_points_scored).rjust(6),
            "{0:.2f}".format(self.avg_points_allowed).rjust(6),
            "{0:.2f}".format(self.avg_margin_victory).rjust(6),
            "{0:.2f}".format(self.avg_margin_loss).rjust(6),
            "{0:.3f}".format(self.win_percent).rjust(7),
            "{0:.1f}".format(self.elo).rjust(7),
            king_string
        ])
    
    def to_json(self):
        return {
            'name': self.name,
            
            'wins': self.wins,
            'losses': self.losses,
            'streak': {
                'winning': self.winning_run,
                'count': self.run
            },
            
            'psg': self.avg_points_scored,
            'pag': self.avg_points_allowed,
            'amv': self.avg_margin_victory,
            'aml': self.avg_margin_loss,

            'winpct': self.win_percent,
            'elo': self.elo,
            'king': self.king
        }