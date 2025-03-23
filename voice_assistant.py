import sys
import os

# Ajoute le dossier src au path Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "src"))

from main import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nErreur lors du démarrage: {str(e)}")
        import traceback

        traceback.print_exc()
        input("\nAppuyez sur Entrée pour fermer...")
