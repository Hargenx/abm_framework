from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING, Dict, List, Callable

if TYPE_CHECKING:
    from .agent import AgenteBase
    from .world import MundoBase

def processar_agente(agente: 'AgenteBase', ambiente: 'MundoBase') -> int:
    """
    Processa um único agente, fazendo-o decidir e agir no ambiente.
    
    Args:
        agente: O agente a ser processado
        ambiente: O ambiente onde o agente está inserido
        
    Returns:
        int: O ID do agente processado
    """
    agente.decidir(ambiente)
    agente.agir(ambiente)
    return agente.id  # Para log, se desejar

class Simulacao:
    """
    Classe responsável por gerenciar a execução da simulação.
    
    Esta classe controla o ciclo de simulação, a execução paralela ou sequencial
    dos agentes e a coleta de dados durante a simulação.
    """
    
    def __init__(self, mundo: 'MundoBase', ciclos: int = 100, paralelo: bool = True, max_workers: int = None) -> None:
        """
        Inicializa uma nova simulação.
        
        Args:
            mundo: O ambiente onde a simulação ocorrerá
            ciclos: Número de ciclos a serem executados
            paralelo: Se True, executa os agentes em paralelo; se False, executa sequencialmente
            max_workers: Número máximo de workers para execução paralela (None = automático)
        """
        self.mundo = mundo
        self.ciclos = ciclos
        self.paralelo = paralelo
        self.max_workers = max_workers

    def executar_ciclo(self) -> None:
        """
        Executa um único ciclo de simulação.
        
        Processa todos os agentes (em paralelo ou sequencialmente),
        atualiza o estado do mundo e coleta dados.
        """
        if self.paralelo:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(processar_agente, agente, self.mundo): agente for agente in self.mundo.agentes}
                for future in as_completed(futures):
                    future.result()  # Você pode fazer logging aqui se quiser
        else:
            for agente in self.mundo.agentes:
                processar_agente(agente, self.mundo)

        self.mundo.atualizar()
        self.mundo.coletar_dados()

    def executar(self) -> None:
        """
        Executa a simulação completa por todos os ciclos definidos.
        
        Ao final, exporta os resultados coletados durante a simulação.
        """
        for _ in range(self.ciclos):
            self.executar_ciclo()

        self.mundo.exportar_resultados()
