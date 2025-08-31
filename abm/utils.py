import time
from typing import Callable, Any, TypeVar, cast

F = TypeVar('F', bound=Callable[..., Any])

def medir_tempo_execucao(func: F) -> F:
    """
    Decorador para medir o tempo de execução de uma função.
    
    Este decorador imprime o tempo de execução de uma função em segundos.
    Útil para análise de desempenho e otimização.
    
    Args:
        func: A função a ser decorada
        
    Returns:
        A função decorada que mede o tempo de execução
        
    Exemplo:
        @medir_tempo_execucao
        def funcao_demorada():
            # código que leva tempo para executar
            pass
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fim = time.time()
        print(f"[⏱️] Tempo de execução de {func.__name__}: {fim - inicio:.2f}s")
        return resultado
    return cast(F, wrapper)
