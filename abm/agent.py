from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from .world import MundoBase

class AgenteBase:
    """
    Classe base para todos os agentes em simulações baseadas em agentes.
    
    Esta classe define a interface básica que todos os agentes devem implementar.
    Deve ser estendida para criar agentes específicos para diferentes tipos de simulação.
    """
    
    def __init__(self, id_agente: int) -> None:
        """
        Inicializa um novo agente com ID único e recursos vazios.
        
        Args:
            id_agente: Identificador único do agente
        """
        self.id = id_agente
        self.recursos: Dict[str, Any] = {}  # Recursos gerais, como saldo, energia, etc.
    
    def decidir(self, ambiente: 'MundoBase') -> None:
        """
        Toma decisões com base no estado atual do ambiente.
        
        Este método deve ser implementado por subclasses para definir
        o comportamento de tomada de decisão específico do agente.
        
        Args:
            ambiente: Referência ao mundo onde o agente está inserido
            
        Raises:
            NotImplementedError: Se o método não for sobrescrito pela subclasse
        """
        raise NotImplementedError("Implementar decisão do agente na subclasse.")
    
    def agir(self, ambiente: 'MundoBase') -> None:
        """
        Executa ações no ambiente com base nas decisões tomadas.
        
        Este método deve ser implementado por subclasses para definir
        o comportamento de ação específico do agente.
        
        Args:
            ambiente: Referência ao mundo onde o agente está inserido
            
        Raises:
            NotImplementedError: Se o método não for sobrescrito pela subclasse
        """
        raise NotImplementedError("Implementar ação do agente na subclasse.")
