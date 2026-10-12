# Genero un script para que desde consola podamos elegir los k resultados y un filtro de categoría y nos devuleva lo necesario
import argparse
from buscador import buscar

# Defnimos la función que nos da los resultados de forma "bonita"

def mostrar_resultados(resultados: list[dict])-> None:
    """MUESTRA LOS RESULTADOS DE FORMA LEGIBLE"""
    if  not  resultados:
        print(" No se han encontrado resultados")
        return
    
    print("\n" + "=" * 65)
    print("RESULTADOS DE LA BÚSQUEDA SEMÁNTICA")
    print("=" * 65)

    for i, resultado in enumerate(resultados, start=1):
        print(f"\nResultado {i}")
        print(f"  ID:         {resultado['id']}")
        print(f"  Categoría:  {resultado['categoria']}")
        print(f"  Similitud:  {resultado['similitud']:.4f}")
        print(f"  Texto:      {resultado['texto']}")
        print("-" * 65)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Buscador semántico de documentos con ChromaDB"
    )

    parser.add_argument(
        "pregunta",
        type=str,
        help="Pregunta que quieres buscar"
    )

    parser.add_argument(
        "-k",
        type=int,
        default=5,
        help="Número de resultados que devolver (por defecto: 5)"
    )

    parser.add_argument(
        "--categoria",
        type=str,
        default=None,
        help="Filtrar por categoría (por defecto: sin filtro)"
    )

    args = parser.parse_args()

    if args.k < 1:
        parser.error("-k debe ser un entero mayor que cero")

    resultados = buscar(
        pregunta=args.pregunta,
        k=args.k,
        categoria=args.categoria
    )

    mostrar_resultados(resultados)


if __name__ == "__main__":
    main()

