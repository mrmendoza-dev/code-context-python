import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import BooleanVar
from utils import insert_tree_items, count_words_characters
import os
import json

class DirectoryTreeApp:
	def __init__(self, root):
		self.max_words = 1100
		self.max_characters = 12000

		self.root = root
		self.root.title("Code Context Manager")

		self.main_frame = ttk.Frame(self.root)
		self.main_frame.grid(row=0, column=0, sticky="nsew")

		self.main_frame.grid_rowconfigure(0, weight=3)  # Increase weight to allocate more space for the Treeview
		self.main_frame.grid_columnconfigure(0, weight=1)

		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)

		self.tree_frame = ttk.Frame(self.main_frame)
		self.tree_frame.grid(row=0, column=0, sticky="nsew")

		self.tree_frame.grid_rowconfigure(0, weight=3)  # Increase weight to allocate more space for the Treeview
		self.tree_frame.grid_columnconfigure(0, weight=1)

		self.tree = ttk.Treeview(self.tree_frame, selectmode="extended")
		self.tree.grid(row=0, column=0, sticky="nsew")

		self.yscrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
		self.yscrollbar.grid(row=0, column=1, sticky="ns")

		self.tree.configure(yscrollcommand=self.yscrollbar.set)

		self.content_frame = ttk.Frame(self.main_frame)
		self.content_frame.grid(row=0, column=1, sticky="nsew")

		self.content_text = tk.Text(self.content_frame, wrap="none")
		self.content_text.pack(fill="both", expand=True)

		self.button_frame = ttk.Frame(self.root)
		self.button_frame.grid(row=1, column=0, sticky="ew")

		self.choose_button = ttk.Button(self.button_frame, text="Choose Folder", command=self.choose_folder)
		self.choose_button.grid(row=0, column=0)

		self.copy_button = ttk.Button(self.button_frame, text="Copy", command=self.copy_to_clipboard)
		self.copy_button.grid(row=0, column=1, padx=10)

		# Expand and Collapse buttons
		self.expand_button = ttk.Button(self.tree_frame, text="Expand All", command=self.expand_all)
		self.expand_button.grid(row=1, column=0, padx=10, sticky="w")

		self.collapse_button = ttk.Button(self.tree_frame, text="Collapse All", command=self.collapse_all)
		self.collapse_button.grid(row=1, column=1, padx=10, sticky="e")

		# Bind TreeviewSelect event to update label
		self.tree.bind("<<TreeviewSelect>>", self.update_content)

		self.folder_label = ttk.Label(self.tree_frame, text="")
		self.folder_label.grid(row=2, column=0, pady=5)

		self.word_count_label = ttk.Label(self.button_frame, text="")
		self.word_count_label.grid(row=0, column=2, padx=10)

		self.selected_folder = None

		self.exclude_var = BooleanVar()
		self.exclude_var.set(True)
		self.blacklist = [".git", "node_modules", "build", "dist", "venv", "env", "target", "bin", "out", "cache",
						  "temp",
						  "tmp", "temp", "logs", "log"]
		self.exclude_check = ttk.Checkbutton(self.tree_frame, text="Exclude", variable=self.exclude_var,
											 command=self.apply_exclude_filter)
		self.exclude_check.grid(row=2, column=1, padx=10)

	def apply_exclude_filter(self):
		if self.selected_folder:
			self.update_tree(self.selected_folder)

	def choose_folder(self):
		folder = filedialog.askdirectory()
		if folder:
			self.selected_folder = folder
			folder_name = os.path.basename(folder)
			self.folder_label.config(text=f"Selected folder: {folder_name}")
			self.update_tree(folder)

	def update_tree(self, folder):
		self.tree.delete(*self.tree.get_children())
		insert_tree_items(self.tree, "", folder, self.exclude_var, self.blacklist)
		self.tree.item("", open=True)

	def update_content(self, event):
		selected_items = self.tree.selection()
		total_words = 0
		total_characters = 0

		if selected_items:
			for item in selected_items:
				selected_file_path = self.tree.item(item)["values"][0]



				if os.path.isfile(selected_file_path):
					with open(selected_file_path, "r", encoding="utf-8", errors="ignore") as file:
						contents = file.read()
						self.content_text.delete(1.0, tk.END)
						self.content_text.insert(tk.END, contents)

					words, characters = count_words_characters(selected_file_path)
					total_words += words
					total_characters += characters

			if total_words > self.max_words or total_characters > self.max_characters:
				self.word_count_label.config(text=f"Words: {total_words}, Characters: {total_characters}",
											 foreground="red")
			else:
				self.word_count_label.config(text=f"Words: {total_words}, Characters: {total_characters}",
											 foreground="black")

		else:
			self.word_count_label.config(text="")

	def copy_to_clipboard(self):
		selected_items = self.tree.selection()
		file_infos = []

		for item in selected_items:
			selected_file_path = self.tree.item(item)["values"][0]
			selected_file_name, selected_file_ext = os.path.splitext(self.tree.item(item)["text"])

			if os.path.isfile(selected_file_path):
				with open(selected_file_path, "r", encoding="utf-8", errors="ignore") as file:
					contents = file.read()
					file_info = {
						"fileName": selected_file_name,
						"fileType": selected_file_ext,
						"filePath": os.path.join(os.path.basename(self.selected_folder),
												 os.path.relpath(selected_file_path, self.selected_folder)),
						"content": contents
					}
					file_infos.append(file_info)

		if file_infos:
			formatted_info = json.dumps(file_infos, indent=2)
			self.root.clipboard_clear()
			self.root.clipboard_append(formatted_info)
			self.root.update()

	def expand_all(self):
		def expand_children(item):
			children = self.tree.get_children(item)
			for child in children:
				self.tree.item(child, open=True)
				expand_children(child)

		expand_children("")

	def collapse_all(self):
		def collapse_children(item):
			children = self.tree.get_children(item)
			for child in children:
				self.tree.item(child, open=False)
				collapse_children(child)

		collapse_children("")