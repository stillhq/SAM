import pickle

QUEUE_LOCATION = "/var/run/sam_queue"


def get_queue_dicts():
    try:
        with open(QUEUE_LOCATION, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return None
    except EOFError:
        return None
    except Exception as e:
        print(e)
        return None


def get_current_queue_item():
    try:
        with open(QUEUE_LOCATION, "rb") as file:
            queue = pickle.load(file)
            if queue is None:
                return None
            return queue[0]
    except FileNotFoundError:
        return None
    except EOFError:
        return None
    except Exception as e:
        print(e)
        return None