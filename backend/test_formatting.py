# Intentional formatting errors for pre-commit hook testing
def badly_formatted_function(x,y,z):
    return x+y+z

class   PoorlySpaced:
    def __init__(self,value):
        self.value=value
        
unused_variable = "This should trigger a linting warning"
