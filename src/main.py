import cli
import data
    

def main():
    data.load_java250_data()
    cli.run()


if __name__ == "__main__":
    main()