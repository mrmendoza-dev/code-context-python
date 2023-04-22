import os


def insert_tree_items(tree, parent, path, exclude_var, blacklist):
    for item in os.listdir(path):
        if exclude_var.get() and item in blacklist:
            continue
        item_path = os.path.join(path, item)
        item_name = os.path.basename(item_path)
        if os.path.isdir(item_path):
            has_children = any(os.path.isdir(os.path.join(item_path, sub_item)) or os.path.isfile(
                os.path.join(item_path, sub_item)) for sub_item in os.listdir(item_path))
            tree_item = tree.insert(parent, "end", text=item_name, open=False, values=[item_path])
            if has_children:
                insert_tree_items(tree, tree_item, item_path, exclude_var, blacklist)
        else:
            tree.insert(parent, "end", text=item_name, values=[item_path])


# ... (Move the insert_tree_items function from the class here)


def count_words_characters(file_path):
	with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
		content = file.read()
		words = len(content.split())
		characters = len(content)
	return words, characters