import csv
import random

class TreeNode:
    """
    A node in a binary decision tree for a 20 Questions-style guessing game.

    Each node can be:
    - A question node: stores a yes/no classification question (trait) and points to:
        - left: the subtree for "yes" answers
        - right: the subtree for "no" answers
    - A leaf node: stores a final guess (e.g., a city name) and has no branches.

    The tree is built recursively using binary classification traits.
    During gameplay, the tree is traversed by asking questions until a guess is reached.
    """

    def __init__(self, question=None, guess=None):
        self.question = question  # The yes/no question to ask at this node
        self.guess = guess        # Final guess if this is a leaf node
        self.left = None          # "Yes" branch (TreeNode)
        self.right = None         # "No" branch (TreeNode)

    def is_leaf(self):
        return self.guess is not None



def load_data(filename):
    """
    Reads a CSV file and returns a list of dictionaries representing the dataset,
    along with the name of the identifier column.

    Args:
        filename (str): Path to the CSV file with:
            - The first column as an identifier (e.g., "City", "Animal", etc.)
            - Subsequent columns as binary traits (expected to be 0 or 1)

    Returns:
        tuple:
            - data (list of dict): The parsed dataset as a list of dictionaries.
            - traits (list of str): The list of trait column names (all except the first column).
            - identifier_key (str): The name of the identifier column (the first column).
            
    Raises:
        ValueError: If there are missing values or conversion errors in the data
        FileNotFoundError: If the specified CSV file is not found
    """

    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            if not reader.fieldnames:
                raise ValueError("Empty CSV file")
                
            data = []
            trait_columns = reader.fieldnames[1:]  # All columns after first
            
            for row_num, row in enumerate(reader, 1):
                try:
                    record = {reader.fieldnames[0]: row[reader.fieldnames[0]]}  # Keep identifier as string
                    
                    for col in trait_columns:
                        value = row[col]
                        if value.strip() == '':
                            raise ValueError(f"Missing value for {col}")
                        record[col] = int(value)
                        
                    data.append(record)
                    
                except ValueError as e:
                    raise ValueError(f"Row {row_num}: {str(e)}") from e
                    
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")

    identifier_key = reader.fieldnames[0]
    traits = reader.fieldnames[1:]

    return data, traits, identifier_key



# ____helper function____
def choose_best_split_trait(data, traits):
    """
    Chooses the trait that gives the most balanced split of the dataset.

    Args:
        data (list of dict): The dataset to split.
        traits (list of str): List of available traits.

    Returns:
        str: The trait that produces the most balanced yes/no split.
    """
    best_trait, best_diff = None, float('inf')
    for t in traits:
        yes_count = sum(item[t] for item in data)
        no_count = len(data) - yes_count
        diff = abs(yes_count - no_count)
        if diff < best_diff:
            best_diff = diff
            best_trait = t
    return best_trait




def build_tree(data, traits, identifier_key):
    """
    Recursively constructs a binary decision tree for a 20 Questions-style guessing game.

    At each step, this function selects the trait that best splits the dataset into 
    balanced "yes" and "no" groups, and builds left and right subtrees accordingly.

    Base cases:
    - If only one item remains, it returns a leaf node with that guess.
    - If no traits remain to split on, it randomly selects one of the remaining items as the guess.

    Args:
        data (list of dict): A list of items, where each item is a dictionary with:
                - one identifier key (e.g., "City") and 
                - multiple binary trait keys (0 or 1 values).
        traits (list of str): The list of available traits to use as splitting questions.
        identifier_key (str): The name of the identifier field (e.g., "City") used for the final guess.

    Returns:
        TreeNode: The root node of the binary decision tree.
    """

    # Base case: only one item or no traits left
    if len(data) == 1 or not traits:
        return TreeNode(guess=random.choice(data)[identifier_key])

    # Find the trait that yields the most balanced split
    best_trait = choose_best_split_trait(data, traits)

    # Split data into "yes" and "no" subsets
    yes_data = [item for item in data if item[best_trait] == 1]
    no_data = [item for item in data if item[best_trait] == 0]

    node = TreeNode(question=best_trait)
    remaining_traits = [t for t in traits if t != best_trait]

    # Recursively build subtrees (fallback to random guess from current data if branch is empty)
    node.left = build_tree(yes_data, remaining_traits, identifier_key) if yes_data else TreeNode(guess=random.choice(data)[identifier_key])
    node.right = build_tree(no_data, remaining_traits, identifier_key) if no_data else TreeNode(guess=random.choice(data)[identifier_key])

    return node




# ____helper function____
def _get_yes_no(prompt):
    """
    Helper function to validate user input.
    Repeatedly prompts until the user answers 'yes' or 'no' (case-insensitive).
    """
    while True:
        response = input(prompt).strip().lower()
        if response in ("yes", "y"):
            return True
        elif response in ("no", "n"):
            return False
        else:
            print("Please answer 'yes' or 'no'.")





def traverse_tree(root, data, identifier_key):
    """
    Runs an interactive 20 Questions-style game by traversing the binary decision tree.

    Tracks user responses to trait questions, enforces a 20-question limit, and makes a final guess
    based on consistent dataset filtering. If the tree's guess contradicts prior answers, it falls
    back to the most likely valid guess.

    Args:
        root (TreeNode): The root node of the pre-built decision tree.
        data (list of dict): Full dataset used to cross-check answers and apply fallback logic.
        identifier_key (str): Name of the field used to identify the item (e.g., "City").

    Returns:
        None
    """

    while True:
        current_node = root
        guess_count = 0

        # Dictionary to store the user's yes/no answers so far: {trait: 0 or 1}
        answers_so_far = {}

        # Traverse down the tree, asking classification questions
        while not current_node.is_leaf():
            if guess_count >= 20:
                print("I couldn't guess in 20 questions. You win!")
                break  # Exit the 'while not current_node.is_leaf()' loop

            guess_count += 1
            trait = current_node.question
            prompt = f"Does it have the following classification: {trait}? (yes/no) "

            user_says_yes = _get_yes_no(prompt)
            answers_so_far[trait] = 1 if user_says_yes else 0

            # Move left if user says yes, right if user says no
            current_node = current_node.left if user_says_yes else current_node.right

        else:
            # If we did NOT break, we've reached a leaf node normally
            if guess_count < 20:
                guess_count += 1

                # Filter the entire dataset to find all items consistent with the user’s answers so far
                matching_items = []
                for item in data:
                    # For every trait answered, check if this item’s trait matches the user's answer
                    if all(item[t] == val for t, val in answers_so_far.items()):
                        matching_items.append(item)

                if not matching_items:
                    # No valid item matches the user’s answers, so we surrender
                    print("I couldn't guess it. Well played!")
                    print("Would you like to play again?")
                else:
                    # Either exactly one match or multiple; pick one at random if multiple
                    if len(matching_items) == 1:
                        final_guess = matching_items[0][identifier_key]
                    else:
                        final_guess = random.choice(matching_items)[identifier_key]

                    # Ask the final guess question
                    final_guess_prompt = f"Is your object {final_guess}? (yes/no) "
                    if _get_yes_no(final_guess_prompt):
                        print(f"Good game! I won in {guess_count} guesses. Would you like to play again?")
                    else:
                        print("I couldn't guess it. Well played!")
                        print("Would you like to play again?")
            else:
                # guess_count == 20 at a leaf node => out of questions
                print("I couldn't guess in 20 questions. You win!")

        # Ask if the user wants to play again
        if not _get_yes_no("(yes/no) "):
            print("Goodbye!")
            break



def main():
    """
    Main driver function that loads the dataset, builds the decision tree, 
    and starts the 20 Questions-style guessing game. 
    Assumes the input CSV file is properly formatted and located in the same directory.
    """
    filename = "test_small_set.csv"
    data, traits, identifier_key = load_data(filename)
    root = build_tree(data, traits, identifier_key)
    traverse_tree(root, data, identifier_key)            


if __name__ == "__main__":
    main()
