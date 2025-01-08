from itertools import combinations

from typing import Dict, List, TypeVar, Any

# Create a type variable that will represent the key type in the dictionary
K = TypeVar('K')


def find_matching_entries(dictionary: Dict[K, List[Any]], threshold: int) -> List[K]:
    """
    Function to find X entries in the dictionary D where the combined values form a set of size X.

    Args:
        dictionary (dict): A dictionary where keys are objects and values are lists of objects.
        threshold (int): The number of entries to select and the target number of distinct elements in the combined set.

    Returns:
        list: A list of X entries from D whose combined values form a set with exactly X elements.
        None: If no such combination exists.
    """
    # Filter out dictionary entries where the list length is greater than X
    filtered_dict = {k: v for k, v in dictionary.items() if len(v) <= threshold}

    # Generate all combinations of X entries from the filtered dictionary
    for selected_entries in combinations(filtered_dict.items(), threshold):
        # Combine all lists of the selected entries
        combined_values = set()
        for _, value_list in selected_entries:
            combined_values.update(value_list)

        # If the size of the combined set is equal to X, return the combination
        if len(combined_values) == threshold:
            return [entry[0] for entry in selected_entries]

    # If no valid combination is found
    return None
