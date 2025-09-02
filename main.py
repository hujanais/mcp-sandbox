import json
import os
import sys

module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "mcp_terminal"))
sys.path.append(module_path)

from mcp_terminal.database.db_utils import DBUtils  # noqa: E402

if __name__ == "__main__":
    try:
        db_utils = DBUtils()
        models = db_utils.get_model(None)
        for model in models:
            print(json.dumps(model.__dict__, indent=4))
    except Exception as e:
        print(f"Error: {e}")