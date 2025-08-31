from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:
    from .agent import AgenteBase

class MundoBase:
    """
    Classe base para o ambiente onde os agentes interagem.
    
    Esta classe gerencia agentes, recursos globais, tempo de simulação
    e coleta de dados durante a execução da simulação.
    """
    
    def __init__(self) -> None:
        """
        Inicializa um novo mundo com lista de agentes vazia, 
        recursos vazios e tempo inicial zero.
        """
        self.agentes: List['AgenteBase'] = []
        self.recursos: Dict[str, Any] = {}
        self.tempo: int = 0
        self.coletor_dados: List[Dict[str, Any]] = []

    def adicionar_agente(self, agente: 'AgenteBase') -> None:
        """
        Adiciona um agente ao mundo.
        
        Args:
            agente: O agente a ser adicionado ao mundo
        """
        self.agentes.append(agente)

    def atualizar(self) -> None:
        """
        Atualiza o estado global do mundo após cada ciclo de simulação.
        
        Este método deve ser implementado por subclasses para definir
        a lógica específica de atualização do ambiente.
        """
        # Lógica para atualizar o estado global do mundo
        pass

    def coletar_dados(self) -> None:
        """
        Coleta um snapshot do estado atual do mundo e dos agentes.
        
        O snapshot inclui o tempo atual, o estado dos recursos globais
        e o estado de cada agente no mundo.
        """
        snapshot = {
            'tempo': self.tempo,
            'estado_mundo': self.recursos.copy(),
            'estado_agentes': [vars(agente) for agente in self.agentes]
        }
        self.coletor_dados.append(snapshot)

    def exportar_resultados(self, caminho: str = 'resultados.json') -> None:
        """
        Exporta os dados coletados durante a simulação para um arquivo JSON.
        
        Args:
            caminho: Caminho do arquivo onde os resultados serão salvos
        """
        import json
        with open(caminho, 'w') as f:
            json.dump(self.coletor_dados, f, indent=4)
