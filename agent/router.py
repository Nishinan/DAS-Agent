def route(state):

    if state["intent"] == "data_analysis":

        return "schema"

    return "insight"