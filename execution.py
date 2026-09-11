class ExecutionLayer:
    def __init__(self,simulation_only=True): self.simulation_only=simulation_only
    def execute(self,proposal):
        if self.simulation_only: raise RuntimeError('Exécution réelle verrouillée : V1 est en simulation.')
        raise RuntimeError('Aucune intégration live officiellement autorisée n’est configurée.')
