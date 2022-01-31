Python script that utilizes a UCI engine to annotate a PGN game and generate a LaTeX report.


Requires:
* python-chess
->  pip3 install chess
* UCI engine (recommend latest stockfish)

Tuning:
* Included is a default preference file (prefs.json).  This allows you to specify what parameters
  you would like to use.
  * Hash: Hash memory allocated
  * Engine: Engine executable name, defaults to ./stockfish
  * Depth: Ply depth (?)
  * SyzygyPath: Path to your syzygy egtb files
  * SyzygyEnable: Whether to used egtbs or not (1 yes, 2 no)
  * Your own polyglot book (?) annotate will skip analysis on any moves in the book. Reason for this is that 
    the engine (without a book) will always have a preferce and dont want it to annotate the first couple moves just because 
    you wanted to try a different opening than just e2e4.



Notes:
* Used a ECO based polyglot, if you want the engine to ignore custom openings you can use your own polyglot book.
  polyglot make-book -pgn eco.pgn

-=-=-=-=-=-=-
