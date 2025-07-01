import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells.copy() # set return a copy
        return set() # if they are not all mines set returns as  an empty set
        

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
         # If the count of mines in this sentence is 0,
        if self.count == 0:
             # then all cells in this sentence are known to be safe.
            # Return a copy of the cells set to avoid external modification.
            return self.cells.copy()
               # Otherwise, if count is not 0, we cannot definitively say any are safe from this sentence alone.
        # Return an empty set.
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
          # Check if the given cell is part of this sentence's cells.
        if cell in self.cells:
            # If it is, remove the cell from the set of unknown cells.
            self.cells.remove(cell)
            # Since this cell was a mine, decrement the count of mines in this sentence.
            self.count -= 1
    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
       # Check if the given cell is part of this sentence's cells.
        if cell in self.cells:
            # If it is, remove the cell from the set of unknown cells.
            self.cells.remove(cell)
            # The count is NOT decremented here because a safe cell does not contribute to the mine count.


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
       
        # 1) Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) Mark the cell as safe (this will update self.safes and other Sentences)
        self.mark_safe(cell)

        # 3) Add a new sentence to the AI's knowledge base
        
        # Collect unknown neighbor cells for the new sentence
        neighbors_for_new_sentence = set()
        
        # The count will be adjusted if there are known mines among neighbors
        adjusted_count = count 

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                
                neighbor_cell = (i, j)

                # 1. Ignore the cell itself (the one that was just clicked)
                if neighbor_cell == cell:
                    continue

                # 2. Ensure the neighbor cell is within board bounds
                if 0 <= i < self.height and 0 <= j < self.width:
                    
                    # 3. Ignore cells that are already known as mines or safes
                    if neighbor_cell in self.mines:
                        adjusted_count -= 1 # If known mine, decrement the count
                        continue # Skip to the next neighbor

                    if neighbor_cell in self.safes:
                        continue # If known safe, skip to the next neighbor
                    
                    # 4. If the cell is still unknown, add it to the neighbors set for the new Sentence
                    neighbors_for_new_sentence.add(neighbor_cell)
        
        # Now, create the new Sentence with the collected neighbors and adjusted count
        new_sentence = Sentence(neighbors_for_new_sentence, adjusted_count)
        
        # Ensure the Sentence is not empty and not already in knowledge before adding
        if len(new_sentence.cells) > 0 and new_sentence not in self.knowledge:
            self.knowledge.append(new_sentence)

        # **** Start of Inference Loop ****
        # Loop continues as long as new information is being inferred
        change_made = True 
        while change_made:
            change_made = False # Assume no changes are made in this iteration

            # Collect newly discovered safes and mines in this iteration
            safes_to_add_in_loop = set()
            mines_to_add_in_loop = set()
            
            # Step 4: Mark any additional cells as safe or as mines (Direct Inferences)
            # Iterate over a copy of knowledge, as it might be modified during inference
            for sentence in list(self.knowledge): 
                # Check for known safes
                known_safes_from_sentence = sentence.known_safes()
                for safe_cell in known_safes_from_sentence:
                    if safe_cell not in self.safes: # Only if it's genuinely new
                        safes_to_add_in_loop.add(safe_cell)
                        change_made = True 

                # Check for known mines
                known_mines_from_sentence = sentence.known_mines()
                for mine_cell in known_mines_from_sentence:
                    if mine_cell not in self.mines: # Only if it's genuinely new
                        mines_to_add_in_loop.add(mine_cell)
                        change_made = True 
            
            # Apply newly discovered safes from this iteration
            for safe_cell in safes_to_add_in_loop:
                self.mark_safe(safe_cell) # This will update self.safes and all Sentences

            # Apply newly discovered mines from this iteration
            for mine_cell in mines_to_add_in_loop:
                self.mark_mine(mine_cell) # This will update self.mines and all Sentences

            # Clean up knowledge base: Remove sentences that are empty or fully resolved (no longer useful)
            sentences_to_remove = []
            for sentence in self.knowledge:
                if len(sentence.cells) == 0: # If a sentence has no cells left, it's useless
                    sentences_to_remove.append(sentence)
            
            # Remove marked sentences from the knowledge base
            for sentence_to_remove in sentences_to_remove:
                # Check again if it's still in self.knowledge, as it might have been removed by another inference
                if sentence_to_remove in self.knowledge:
                    self.knowledge.remove(sentence_to_remove)
                    change_made = True # Removing a sentence counts as a change


            # Step 5: Add any new sentences if they can be inferred from existing knowledge (Subset Rule)
            inferred_sentences_to_add = []
            # Iterate over all unique pairs of sentences from the current knowledge base
            # Use list(self.knowledge) to iterate over a copy as knowledge might change
            for s1 in list(self.knowledge):
                for s2 in list(self.knowledge):
                    # Skip if sentences are the same (same object in memory)
                    if s1 == s2:
                        continue

                    # If s1 is a subset of s2, infer new sentence: (s2.cells - s1.cells) = (s2.count - s1.count)
                    if s1.cells.issubset(s2.cells):
                        # Ensure s1 is strictly smaller (to avoid redundant inferences) and s2 is not empty
                        if s1.cells != s2.cells and len(s2.cells) > 0:
                            new_cells = s2.cells - s1.cells
                            new_count = s2.count - s1.count
                            
                            # Only create new sentence if it results in valid cells and is not already known
                            if len(new_cells) > 0: # Ensure the new sentence has cells
                                inferred_sentence = Sentence(new_cells, new_count)
                                # Add only if not already in knowledge and not just inferred in this loop
                                if inferred_sentence not in self.knowledge and inferred_sentence not in inferred_sentences_to_add:
                                    inferred_sentences_to_add.append(inferred_sentence)
                                    change_made = True # A new inference has been made
            
            # Add all newly inferred sentences to self.knowledge
            for inferred_s in inferred_sentences_to_add:
                self.knowledge.append(inferred_s)

           


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
      # Iterate over all cellules known to be safe (self.safes)
        for cellule in self.safes:
            # Check if this safe cellule has not been clicked on yet
            if cellule not in self.moves_made:
                # If it's a new safe cellule to click, return it
                return cellule
        # If no safe and un-clicked cellules are found, return None
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
     # Create a list to store possible random moves
        possible_moves = []
        
        # Iterate over all possible cells on the board
        for i in range(self.height):
            for j in range(self.width):
                cellule = (i, j)
                # Check if the cellule has not been clicked on yet AND is not a known mine
                if cellule not in self.moves_made and cellule not in self.mines:
                    possible_moves.append(cellule)
        
        # If there are any possible random moves, choose one randomly
        if possible_moves:
            return random.choice(possible_moves)
        else:
            # If no possible moves are found, return None
            return None
