from abc import ABC, abstractmethod

class BaseClient(ABC):
    @abstractmethod
    def chat(self, *args, **kwargs):
        pass

    @abstractmethod
    def embed(self, *args, **kwargs):
        pass

    @abstractmethod
    def image(self, *args, **kwargs):
        pass
