"""
Component system for particles.
Components are modular behaviors that can be attached to particles.
"""


class Component:
    """Base class for all particle components."""
    
    def __init__(self, particle):
        self.particle = particle
    
    def update(self, dt):
        """
        Update the component.
        
        Returns:
            bool: True if component should be removed, False otherwise
        """

        return self._update(dt)
    
    def _update(self, dt):
        """Override this in subclasses."""
        return False
    
    def on_add(self):
        """Called when component is added to particle."""
        pass
    
    def on_remove(self):
        """Called when component is removed from particle."""
        pass
