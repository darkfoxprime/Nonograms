from typing import Iterable, Union, Dict, Any, Tuple, TypeVar
import itertools
import sys

NB = TypeVar('NB', bound='NonoBoard')

class NonoBoard(object):
    def __init__(
                self,
                size: int,
                rowspecs: Iterable[Iterable[int]] = None,
                colspecs: Iterable[Iterable[int]] = None,
            ):
        self._size = size
        self._board = [False] * (size*size)
        self._index = 0
        if rowspecs is not None:
            for index, spec in zip(itertools.count(), rowspecs):
                self.spec_row(spec, index)
        if colspecs is not None:
            for index, spec in zip(itertools.count(), colspecs):
                self.spec_col(spec, index)

    @property
    def size(self) -> int:
        return self._size

    @property
    def is_solved(self) -> bool:
        for i in self._board:
            if isinstance(i, dict): return False
        return True

    @property
    def board(self, graphical=False) -> Tuple[str]:
        (unknown, black, white) = (
            ' ',
            '\u2588' if graphical else '#',
            '\u00b7' if graphical else '.',
        )
        return tuple(
                    ''.join(
                        unknown if not isinstance(self._board[x], bool)
                        else black if self._board[x]
                        else white
                        for x in range(x0, x0+self._size)
                    )
                    for x0 in range(0, self._size*self._size, self._size)
                )

    def spec_row(
                self,
                spec: Iterable[int],
                index: int,
            ) -> None:
        self._spec_board(spec, index*self._size, 1)

    def spec_col(
                self,
                spec: Iterable[int],
                index: int,
            ) -> None:
        self._spec_board(spec, index, self._size)

    def _spec_board(
                self,
                spec: Iterable[int],
                first: int,
                delta: int,
            ) -> None:
        horiz = (delta == 1)
        speclist = []
        i = 0
        for span in spec:
            speclist.append( [i, span] )
            i += span + 1
        while speclist[-1][0] + speclist[-1][1] <= self._size:
            self._index += 1
            if horiz:
                spec_index = self._index
            else:
                spec_index = -self._index
            i = 0
            for x in range(self._size):
                if x < speclist[i][0]:
                    val = False
                elif x < speclist[i][0] + speclist[i][1]:
                    val = True
                else:
                    val = False
                    if i < len(speclist) - 1:
                        i += 1
                if isinstance(self._board[first + delta*x], dict):
                    self._board[first + delta*x][spec_index] = val
                else:
                    self._board[first + delta*x] = {spec_index: val}
            i = len(speclist) - 1
            _max = self._size
            while i > 0 and speclist[i][0] + speclist[i][1] == _max:
                _max -= speclist[i][1] + 1
                i -= 1
            speclist[i][0] += 1
            while i < len(speclist)-1:
                speclist[i+1][0] = speclist[i][0] + speclist[i][1] + 1
                i += 1

    def resolve_once(self : NB) -> Union[NB, bool]:
        i = self._size*self._size
        mark = {}
        remove = []
        resolved = False
        while i > 0:
            i -= 1
            if isinstance(self._board[i], dict):
                cell = self._board[i]
                # check if all positive indices or all negative indices have the same value
                vals = {val for idx,val in cell.items() if idx > 0}
                if len(vals) != 1:
                    vals = {val for idx,val in cell.items() if idx < 0}
                if len(vals) == 1:
                    val = vals.pop()
                    for idx in cell:
                        if cell[idx] != val:
                            remove.append(idx)
                    mark[i] = val
                    resolved = True
        if resolved:
            new_board = NonoBoard(self.size)
            new_board._board = self._board[:]
            for idx in mark:
                new_board._board[idx] = mark[idx]
            if remove:
                for i in range(new_board._size*new_board._size):
                    if isinstance(new_board._board[i], dict):
                        for r in remove:
                            if r in new_board._board[i]:
                                del new_board._board[i][r]
            return new_board
        return False

    @staticmethod
    def resolve(board : NB) -> NB:
        next_board = board
        while next_board:
            board = next_board
            next_board = board.resolve_once()
        return board

if __name__ == '__main__':
    b = NonoBoard(
                15,
                (
                    (2,2),
                    (2,3,1),
                    (5,3),
                    (2,6,1),
                    (1,3,1),
                    (2,2),
                    (3,4,1),
                    (11,1),
                    (12,),
                    (9,2),
                    (7,1,1),
                    (3,1,2),
                    (3,2,2),
                    (1,2,2),
                    (2,1),
                ),
                (
                    (2,),
                    (4,1),
                    (9,),
                    (2,7),
                    (2,8),
                    (2,4,2),
                    (2,4),
                    (9,),
                    (10,2),
                    (2,2,8),
                    (1,3),
                    (1,2,2),
                    (2,4),
                    (1,1,3),
                    (6,),
                )
            )

    b = NonoBoard.resolve(b)
    print('\n'.join(b.board))
