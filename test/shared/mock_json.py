# pylint: skip-file

def get_json_data():
    return {
        "results": [
            {
                "id": 1,
                "name": "Link 1"
            },
            {
                "id": 2,
                "name": "Link 2"
            },
            {
                "id": 3,
                "name": "Link 3"
            }
        ],
        "pagination": {
            "next_page": "http://address.com/item?page=3",
            "last_page": "http://address.com/item?page=1"
        },
        "end_page": "http://address.com/item?page=100"
    }
