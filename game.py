import bee
import board

if __name__ == "__main__":
    b = bee.Bee(100,True)
    b.printname()
    print(b.to_string())
    b.baixar_vida(120)
    print(b.to_string())
    b.pujar_vida(120)
    print(b.to_string())
    board = board.Board(8,8)
    print(b.next_moves(board,[0,0]))
