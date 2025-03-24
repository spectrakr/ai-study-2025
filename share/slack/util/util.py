import ast
import os
import re


class Util(object):

    @staticmethod
    def replace_ids_with_names(text, user_dict):
        pattern = r"@([A-Z0-9]+)"

        def replace_function(match):
            user_id = match.group(1)
            return f"@{user_dict.get(user_id, user_id)}"

        return re.sub(pattern, replace_function, text)

    @staticmethod
    def get_members_dict():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "../", "members.txt")
        with open(file_path, "r") as file:
            txt = file.read()
        return ast.literal_eval(txt)
