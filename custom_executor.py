class CustomExecutor: 

    # static methods used as nodes in the graph
    def input_node_fcn(state): 
        print("What is your question?")
        result=input()
        state['messages'].append(result)
        state['question']=result
        return state

    def __init__(self):
        print("Custom executor initialized")


