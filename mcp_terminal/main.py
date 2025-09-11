import json
import os
import sys

module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(module_path)

from database.db_utils import DBUtils  # noqa: E402

if __name__ == "__main__":
    try:
        db_utils = DBUtils()

        allTasks = db_utils.get_task()
        for task in allTasks:
            print(task)

        resp = db_utils.create_task(model_id=12334, dataset_ids=[])
        print(resp) 

        # # Create a new model
        # print('----- Create a new model -----')
        # new_model = db_utils.create_model("bert-base-uncased")
        # model_id = new_model.data.model_id
        
        # models = db_utils.get_model(model_id)
        # for model in models:
        #     print(json.dumps(model.__dict__, indent=4))

        # # Update the model name
        # print('----- Update the new model -----')
        # updated_model = db_utils.update_model(model_id, "new_model_name")

        # models = db_utils.get_model(model_id)
        # for model in models:
        #     print(json.dumps(model.__dict__, indent=4))

        # print('----- Delete the new model -----')
        # db_utils.delete_model(model_id)
        
        # models = db_utils.get_model(None)
        # for model in models:
        #     print(json.dumps(model.__dict__, indent=4))
        
    except Exception as e:
        print(f"Error: {e}")