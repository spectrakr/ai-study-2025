from datetime import datetime


@staticmethod
def format_date_simple(date_str):
    original_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    target_format = "%Y-%m-%d %H:%M"

    date_obj = datetime.strptime(date_str, original_format)
    converted_date_str = date_obj.strftime(target_format)

    return converted_date_str


def extract_content_type(data):
    if "content" in data:
        for content in data["content"]:
            return content["type"]
    else:
        return None


def extract_text(data):
    result = []
    if "content" in data:
        # return result.extend(extract_content(data))

        for content in data["content"]:
            result.extend(extract_content(content))

    return result


def extract_list_item(list_item_type, data):
    texts = []

    def recursive_extract(node, depth=-3):
        if isinstance(node, dict):
            if "type" in node and node["type"] == "text" and "text" in node:
                texts.append(" " * depth + "- " + node["text"] + "\n")
            for key in node:
                recursive_extract(node[key], depth + 1)
        elif isinstance(node, list):
            for item in node:
                recursive_extract(item, depth)

    recursive_extract(data)
    return texts


def parse_paragraph(content):
    result = []
    for sub_content in content["content"]:
        if sub_content["type"] == "text":
            result.append(sub_content["text"])
        elif sub_content["type"] == "emoji":
            result.append(sub_content["attrs"]["text"])
        elif sub_content["type"] == "inlineCard":
            result.append(sub_content["attrs"]["url"])
        elif sub_content["type"] == "hardBreak":
            result.append("\n")
        elif sub_content["type"] == "mention":
            result.append(sub_content["attrs"]["text"])

    return result


def extract_content(content):
    result = []
    # print(f"[extract_content][{content["type"]}]", content)
    if content["type"] == "paragraph":
        result.extend(parse_paragraph(content))
        result.append("\n")
    elif content["type"] == "panel":
        # print("__ panel", content)
        result.append("\n")
        for sub_content in content["content"]:
            # result.extend(parse_paragraph(sub_content))
            result.extend(extract_content(sub_content))
        result.append("\n")
    elif content["type"] == "codeBlock":
        result.append("\n")
        for sub_content in content["content"]:
            result.append(sub_content["text"])
    elif content["type"] == "bulletList":
        # print("__ bulletList")
        result.append("\n")
        result.extend(extract_list_item(content["type"], content))
    elif content["type"] == "orderedList":
        result.append("\n")
        result.extend(extract_list_item(content["type"], content))
    elif content["type"] == "table":
        for sub_content in content["content"]:
            for table_row in sub_content["content"]:
                for table_cell in table_row["content"]:
                    result.extend(parse_paragraph(table_cell))
            result.append("\n")
        result.append("\n")
        # result.extend(extract_list_item(content["type"], content))

    return result


def extract_texts(json_data):
    result = []

    # print("extract_texts", json_data)
    if isinstance(json_data, dict):
        contents = json_data["content"]
        for content in contents:
            result.extend(extract_content(content))

    elif isinstance(json_data, list):
        for item in json_data:
            # print(f"list [{item}]")
            result.extend(extract_texts(item))
    return result


def get_customfield_name(field, customfields):
    for key, value in customfields.items():
        if field in key:
            return value


def get_customfield_values(issue, customfields):
    customefield_text = ""
    for field, value in issue["fields"].items():
        if field.startswith("customfield_"):
            if value is not None:
                customfield_name = get_customfield_name(field, customfields)
                if isinstance(value, (str, dict, list)):
                    text = " ".join(extract_text(value))
                    # print(f"[customfield_name] {customfield_name} : {text}")
                    if text.strip() != "":
                        customefield_text += f"\n{customfield_name}\n {text}"
    return customefield_text


def get_comments_text(json_data):
    result = []

    for content in json_data["content"]:
        result.extend(extract_content(content))
    return result


def valid_issue_document(issue):
    description_text = issue["description_text"]
    comment_text = issue["comment_text"]

    if len(description_text) > 10 or len(comment_text) > 10:
        return True
    else:
        return False


def format_issue_document(issue):
    issue_document = f"""
[{issue["key"]}] {issue["summary"]}
[설명] 
{issue["description_text"]}
{issue["customfields_text"]}

{issue["comment_text"]}"""

    return issue_document
