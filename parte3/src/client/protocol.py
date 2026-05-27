def create_join(username):
    return {"type": "JOIN", "username": username}

def create_place(x, y, structure_type, author):
    return {"type": "PLACE", "x": x, "y": y, "structure_type": structure_type, "author": author}

def create_remove(x, y):
    return {"type": "REMOVE", "x": x, "y": y}
